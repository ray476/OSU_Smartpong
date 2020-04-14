""" Trains an agent with (stochastic) Policy Gradients on Pong. Uses OpenAI Gym. """
import numpy as np
import _pickle as pickle
import gym
import Interface
import argparse
# import Plotting
import os
import matplotlib.pyplot as plt
import Database
from tensorflow import keras

# hyperparameters
H = 200  # number of hidden layer neurons
batch_size = 10  # every how many episodes to do a param update?
learning_rate = 1e-4
gamma = 0.99  # discount factor for reward
decay_rate = 0.99  # decay factor for RMSProp leaky sum of grad^2
num_episodes = 50
epsilon = 0.5
r_avg_list = []


resume = Interface.resume()  # resume from previous checkpoint?
render = Interface.render()
collection = Interface.dataCollection()
db_connection = Database.establishConnection()
hyper_params = [H, batch_size, learning_rate, gamma, decay_rate]

D = 80 * 80  # input dimensionality: 80x80 grid
filename = 'placeholder'
if resume:
    filename = Interface.askForResumeName()
    model = Database.retrieveModel(filename, db_connection)
    p_row = Database.retrieveParameters(filename, db_connection)
    for i in range(len(hyper_params)):
        hyper_params[i] = p_row[i]
    print('resumed from checkpoint')
else:
    filename = Interface.askForNewName()
    filename = filename + '.p'
    model = {}
    model['W1'] = np.random.randn(H, D) / np.sqrt(D)  # "Xavier" initialization
    model['W2'] = np.random.randn(H) / np.sqrt(H)
    pickle.dump(model, open(filename, 'wb'))

hyper_params = Interface.changeParams(hyper_params)

# model initialization

model = keras.Sequential(
    [
        keras.layers.InputLayer(input_shape=(1, 6400)),
        keras.layers.Dense(H, activation='relu'),
        keras.layers.Dense(2, activation='linear')

    ]
)
local_optimizer = keras.optimizers.RMSprop(learning_rate=learning_rate, rho='gamma', )
model.compile(optimizer=local_optimizer, loss='mse', metrics=['mse'])


def prepro(I):
    """ prepro 210x160x3 uint8 frame into 6400 (80x80) 1D float vector """
    I = I[35:195]  # crop
    I = I[::2, ::2, 0]  # downsample by factor of 2
    I[I == 144] = 0  # erase background (background type 1)
    I[I == 109] = 0  # erase background (background type 2)
    I[I != 0] = 1  # everything else (paddles, ball) just set to 1
    return I.astype(np.float).ravel()


env = gym.make("Pong-v0")

prev_x = None  # used in computing the difference frame
xs, hs, dlogps, drs = [], [], [], []
running_reward = None
reward_sum_conllect = []
episode_number = 0
if collection:
    data_collect = open(Interface.dcFilename(), 'w')
try:
    for i in range(num_episodes):
        observation = env.reset()
        epsilon *= decay_rate
        if i % 10 ==0:
            print('Episode {} of {}'.format(i+1, num_episodes))
        done = False
        reward_sum = 0
        if render: env.render()
        while not done:
            # preprocess the observation, set input to network to be difference image
            cur_x = prepro(observation)
            x = cur_x - prev_x if prev_x is not None else np.zeros(D)
            prev_x = cur_x

            # epsilon greedy action selection
            if np.random.random() < epsilon:
                action = np.random.randint(2,3)
            else:
                action = np.argmax(model.predict(x))

            observation, reward, done, info = env.step(action)
            reward_sum += reward
            target = reward + gamma * np.max(model.predict(x))
            target_vec = model.predict()

        drs.append(reward)  # record reward (has to be done after we call step() to get reward for previous action)

        if done:  # an episode finished
            if collection:
                data_collect.write('{} {} '.format(episode_number, reward_sum))

            episode_number += 1
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
            print('resetting env. episode reward total was %f. running mean: %f' % (reward_sum, running_reward))
            reward_sum_conllect.append(reward_sum)

            if collection: data_collect.write('{}\n'.format(running_reward))
            if episode_number % 100 == 0: Database.updateModel(model, filename, db_connection)
            reward_sum = 0
            prev_x = None

        if reward != 0:  # Pong has either +1 or -1 reward exactly when game ends.
            print('ep %d: game finished, reward: %f' % (episode_number, reward), '' if reward == -1 else ' !!!!!!!!')
finally:
    print('Program eneded, closing data collection files and pickling model')
    Database.updateModel(model, filename, db_connection)
    if collection:
        data_collect.close()
    graph_name = filename.split('.')[0] + str(episode_number) + '.png'
    # on the off chance this file somehow already exists add 1
    if Interface.fileExists(graph_name):
        graph_name = filename.split('.')[0] + str(episode_number + 1) + '.png'