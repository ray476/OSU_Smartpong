""" Trains an agent with (stochastic) Policy Gradients on Pong. Uses OpenAI Gym. """
import numpy as np
import _pickle as pickle
import gym
import Interface
# import Plotting
import os
import matplotlib.pyplot as plt
import Database
import time
import psycopg2


# hyperparameters
H = 200  # number of hidden layer neurons
batch_size = 10  # every how many episodes to do a param update?
learning_rate = 1e-4
gamma = 0.99  # discount factor for reward
decay_rate = 0.99  # decay factor for RMSProp leaky sum of grad^2

resume = Interface.resume()  # resume from previous checkpoint?

# establish database connection
db_connection = Database.Database()
hyper_params = [H, batch_size, learning_rate, gamma, decay_rate]

D = 80 * 80  # input dimensionality: 80x80 grid
model_name = 'placeholder'
if resume:
    model_name = Interface.askForResumeName(db_connection)
    model = db_connection.retrieveModel(model_name)
    episode_number = db_connection.lastEpisode(model_name)
    p_row = db_connection.retrieveParameters(model_name)
    for i in range(len(hyper_params)):
        hyper_params[i] = p_row[i]
    Interface.showParams(hyper_params)
else:
    model_name = Interface.askForNewName()
    model_name = model_name + '.p'
    episode_number = 0
    model = {}
    model['W1'] = np.random.randn(H, D) / np.sqrt(D)  # "Xavier" initialization
    model['W2'] = np.random.randn(H) / np.sqrt(H)
    pickle.dump(model, open(model_name, 'wb'))
    hyper_params = Interface.changeParams(hyper_params)

render = Interface.render()
# model initialization
grad_buffer = {k: np.zeros_like(v) for k, v in model.items()}  # update buffers that add up gradients over a batch
rmsprop_cache = {k: np.zeros_like(v) for k, v in model.items()}  # rmsprop memory


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))  # sigmoid "squashing" function to interval [0,1]


def prepro(I):
    """ prepro 210x160x3 uint8 frame into 6400 (80x80) 1D float vector """
    I = I[35:195]  # crop
    I = I[::2, ::2, 0]  # downsample by factor of 2
    I[I == 144] = 0  # erase background (background type 1)
    I[I == 109] = 0  # erase background (background type 2)
    I[I != 0] = 1  # everything else (paddles, ball) just set to 1
    return I.astype(np.float).ravel()


def discount_rewards(r):
    """ take 1D float array of rewards and compute discounted reward """
    discounted_r = np.zeros_like(r)
    running_add = 0
    for t in reversed(range(0, r.size)):
        if r[t] != 0: running_add = 0  # reset the sum, since this was a game boundary (pong specific!)
        running_add = running_add * gamma + r[t]
        discounted_r[t] = running_add
    return discounted_r


def policy_forward(x):
    h = np.dot(model['W1'], x)
    h[h < 0] = 0  # ReLU nonlinearity
    logp = np.dot(model['W2'], h)
    p = sigmoid(logp)
    return p, h  # return probability of taking action 2, and hidden state


def policy_backward(eph, epdlogp):
    """ backward pass. (eph is array of intermediate hidden states) """
    dW2 = np.dot(eph.T, epdlogp).ravel()
    dh = np.outer(epdlogp, model['W2'])
    dh[eph <= 0] = 0  # backpro prelu
    dW1 = np.dot(dh.T, epx)
    return {'W1': dW1, 'W2': dW2}


env = gym.make("Pong-v0")
observation = env.reset()
prev_x = None  # used in computing the difference frame
xs, hs, dlogps, drs = [], [], [], []
running_reward = None
reward_sum = 0
reward_sum_conllect = []
data_collect = open('local_data.txt', 'w')
print('------------------Starting Training------------------\n')
try:
    start_time = time.time()
    while True:
        if render: env.render()
        # preprocess the observation, set input to network to be difference image
        cur_x = prepro(observation)
        x = cur_x - prev_x if prev_x is not None else np.zeros(D)
        prev_x = cur_x

        # forward the policy network and sample an action from the returned probability
        aprob, h = policy_forward(x)
        # actions 0,1: nothing 2,4: go up, 3,5: go down
        action = 2 if np.random.uniform() < aprob else 3  # roll the dice!

        # record various intermediates (needed later for backprop)
        xs.append(x)  # observation
        hs.append(h)  # hidden state
        y = 1 if action == 2 else 0  # a "fake label"
        dlogps.append(
            y - aprob)  # grad that encourages the action that was taken to be taken (see http://cs231n.github.io/neural-networks-2/#losses if confused)

        # step the environment and get new measurements
        observation, reward, done, info = env.step(action)
        reward_sum += reward

        drs.append(reward)  # record reward (has to be done after we call step() to get reward for previous action)

        if done:  # an episode finished
            episode_number += 1
            elapsed_time = time.time() - start_time
            start_time = time.time()
            data_collect.write('{} {} '.format(episode_number, reward_sum))

            # stack together all inputs, hidden states, action gradients, and rewards for this episode
            epx = np.vstack(xs)
            eph = np.vstack(hs)
            epdlogp = np.vstack(dlogps)
            epr = np.vstack(drs)
            xs, hs, dlogps, drs = [], [], [], []  # reset array memory

            # compute the discounted reward backwards through time
            discounted_epr = discount_rewards(epr)
            # standardize the rewards to be unit normal (helps control the gradient estimator variance)
            discounted_epr -= np.mean(discounted_epr)
            discounted_epr /= np.std(discounted_epr)

            epdlogp *= discounted_epr  # modulate the gradient with advantage (PG magic happens right here.)
            grad = policy_backward(eph, epdlogp)
            for k in model: grad_buffer[k] += grad[k]  # accumulate grad over batch

            # perform rmsprop parameter update every batch_size episodes
            if episode_number % batch_size == 0:
                for k, v in model.items():
                    g = grad_buffer[k]  # gradient
                    rmsprop_cache[k] = decay_rate * rmsprop_cache[k] + (1 - decay_rate) * g ** 2
                    model[k] += learning_rate * g / (np.sqrt(rmsprop_cache[k]) + 1e-5)
                    grad_buffer[k] = np.zeros_like(v)  # reset batch gradient buffer

            # boring book-keeping
            running_reward = reward_sum if running_reward is None else running_reward * 0.99 + reward_sum * 0.01
            if reward_sum >= 0:
                print('\nGame {} is over, it took {} seconds.\nThe net score was {} so you won the game.\nThe current '
                      'running mean is {}\n'.format(episode_number-1, elapsed_time, reward_sum, running_reward))
            else:
                print('\nGame {} is over, it took {} seconds.\nThe net score was {} so you lost the game.\nThe '
                      'current running mean is {}\n'.format(episode_number, elapsed_time, reward_sum, running_reward))

            reward_sum_conllect.append(reward_sum)
            # Plotting.plot_training_process(episode_number, reward_sum_conllect)

            data_collect.write('{}\n'.format(running_reward))
            reward_sum = 0
            observation = env.reset()  # reset env
            prev_x = None

        if reward != 0:  # Pong has either +1 or -1 reward exactly when game ends.
            if reward == -1:
                print('game {}: rally finished, The opponent scored a point!!'.format(episode_number))
            elif reward == 1:
                print('game {}: rally finished, You scored a point!!'.format(episode_number))

finally:
    # since the program is stopped with a keyboard interrupt, this allows all open files and database connections
    # to be updated, then closed correctly
    print('\n-------------------Ending Training-------------------\n')

    print('Program eneded, closing data collection files and pickling model\n\n')
    if resume:
        db_connection.updateModel(model, model_name)
    else:
        model_name = model_name[:-2]
        db_connection.insertModel(model_name, hyper_params, model)
    data_collect.close()
    db_connection.insertData(model_name, 'local_data.txt')
    db_connection.connection.close()
