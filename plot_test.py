import numpy as np
import matplotlib.pyplot as plt


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


f = open('./first_model/new_results', 'r')
array = np.loadtxt(f)

a, b = best_fit_linear(array[:, 0], array[:, 1])

plt.plot(array[:, 0], array[:, 1], 'g^')
yfit = [a + b * xi for xi in array[:, 0]]
plt.plot(array[:, 0], yfit)
plt.ylabel('Running Mean')
plt.xlabel('Episodes')
plt.title('Mean vs Episodes')
plt.text(200, -14, 'best fit line:\ny = {:.2f} + {:.4f}x'.format(a, b))
plt.show()

