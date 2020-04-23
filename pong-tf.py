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
        keras.layers.Flatten(),
        keras.layers.Dense(H, activation='relu', input_shape=(1, 6400)),
        keras.layers.Dense(2, activation='linear', input_shape=(1, H)),
    ]
)
local_optimizer = keras.optimizers.RMSprop(learning_rate=learning_rate, rho='gamma', )
model.compile(optimizer=local_optimizer, loss='mse', metrics=['mse'])
model.summary()

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

env = gym.make("Pong-v0")
observation = env.reset()
dimen = 6400
num_actions = env.action_space.n
prev_x = None  # used in computing the difference frame
xs, hs, dlogps, drs = [], [], [], []
running_reward = None
reward_sum = 0
reward_sum_conllect = []
episode_number = 0
# placeholders
states = np.empty(0).reshape(0, dimen)
actions = np.empty(0).reshape(0, 1)
rewards = np.empty(0).reshape(0, 1)
discounted_rewards = np.empty(0).reshape(0, 1)
losses = []
if collection:
    data_collect = open(Interface.dcFilename(), 'w')
try:
    for i in range(num_episodes):
        # preprocess the observation, set input to network to be difference image
        cur_x = prepro(observation)
        x = cur_x - prev_x if prev_x is not None else np.zeros(D)
        prev_x = cur_x
        # Append the observations to our batch
        state = np.reshape(x, [1, dimen])

        predict = model.predict([x])[0]
        action = np.random.choice(range(num_actions), p=predict)

        # Append the observations and outputs for learning
        states = np.vstack([states, state])
        actions = np.vstack([actions, action])

        # Determine the oucome of our action
        observation, reward, done, _ = env.step(action)
        reward_sum += reward
        rewards = np.vstack([rewards, reward])

        if done:  # an episode finished
            if collection:
                data_collect.write('{} {} '.format(episode_number, reward_sum))

            episode_number += 1
            discounted_rewards_episode = discount_rewards(rewards)
            discounted_rewards = np.vstack([discounted_rewards, discounted_rewards_episode])
            rewards = np.empty(0).reshape(0, 1)

            if episode_number % batch_size == 0:
                discounted_rewards -= discounted_rewards.mean()
                discounted_rewards /= discounted_rewards.std()
                discounted_rewards = discounted_rewards.squeeze()
                actions = actions.squeeze().astype(int)

                actions_train = np.zeros([len(actions), num_actions])
                actions_train[np.arange(len(actions)), actions] = 1

                loss = model.train_on_batch([states, discounted_rewards], actions_train)
                losses.append(loss)

                # Clear out game variables
                states = np.empty(0).reshape(0, dimen)
                actions = np.empty(0).reshape(0, 1)
                discounted_rewards = np.empty(0).reshape(0, 1)

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
