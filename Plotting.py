import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
# pulled functions from pong.py and plot_test into one file


def plot_training_process(episode_number, reward_sum_conllect):
    plt.clf()
    x = np.array(range(episode_number))
    y = reward_sum_conllect
    if episode_number == 1:
        y_pred = y
    else:
        model = LinearRegression()
        # print("x:", x.reshape(-1,1))
        # print("y:", y)
        model.fit(x.reshape(-1,1), y)
        y_pred = model.predict(x.reshape(-1,1))
    plt.scatter(x, y, s=6)
    plt.plot(x, y_pred,  color='black')
    plt.xlabel("Episode")
    plt.ylabel("Net Rewards (points)")
    plt.pause(0.01)


def x_range(range):
    if range[1] < 0:
        val = 0 - range[1]
        return val/2
    else:
        return range[1]-5

def string_offsets(ranges):
    if ranges[0] < 0 and ranges[1] < 0:
        return ranges[1] + (ranges[0] - ranges[1]) / 5
    else:
        return ranges[0] + (ranges[1] - ranges[0]) / 5


def best_fit_linear(X, Y):

    xbar = sum(X)/len(X)
    ybar = sum(Y)/len(Y)
    n = len(X)

    numer = sum([xi*yi for xi,yi in zip(X, Y)]) - n * xbar * ybar
    denum = sum([xi**2 for xi in X]) - n * xbar**2

    b = numer / denum
    a = ybar - b * xbar

    # print('best fit line:\ny = {:.2f} + {:.2f}x'.format(a, b))

    return a, b


# helper function for determining which column of the given data is being used.  I wanted to pull the loop out of the
# plotting function
def metric_to_int(metric):
    while True:
        if metric == 'reward sum':
            return 1
        elif metric == 'mean':
            return 2
        elif metric == 'cost':
            return 3
        else:
            print('given metric does not match one of the options: reward sum, mean, or cost')


def mean_from_reward_sum(array):
    rewards = array[:, 1]
    r_sum = np.sum(rewards)
    final_ep = array[-1][0]
    mean = r_sum/final_ep
    print(mean)
    return mean

# takes in a filename and a metric to plot.  options are 'reward sum' 'mean' or 'cost' this metric is plotted on the
# y axis vs the episode numbers.  Currently it is on the caller to ensure the provided file contains the desired metric
# some older data collection files may not have all listed attributes
def plot_episode_vs_value(filename, value_to_plot):
    # open file and load into array
    f = open(filename, 'r')
    array = np.loadtxt(f)
    # find which metric is going to be the y axis
    # x = metric_to_int(value_to_plot)
    a, b = best_fit_linear(array[:, 0], array[:, 1])

    plt.scatter(array[:, 0], array[:, 1], s=6,c='g')
    yfit = [a + b * xi for xi in array[:, 0]]
    plt.plot(array[:, 0], yfit)
    plt.ylabel('Reward')
    plt.xlabel('Episodes')
    plt.title('Reward vs Episodes')
    # get ranges to scale best fit location
    plt.text(string_offsets(plt.xlim()), x_range(plt.ylim()),
             'best fit line:\ny = {:.2f} + {:.4f}x'.format(a, b))
    # plt.text(-5, 500, 'best fit line:\ny = {:.2f} + {:.4f}x'.format(a, b))
    plt.show()