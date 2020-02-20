import numpy as np
import matplotlib.pyplot as plt


f = open('./first_model/new_results', 'r')
array = np.loadtxt(f)

fig = plt.figure()
fig, ax = plt.subplots(1, 1)
out = ax.plot(array[:, 0], array[:, 1])

plt.plot(array[:, 0], array[:, 1])
plt.show()

