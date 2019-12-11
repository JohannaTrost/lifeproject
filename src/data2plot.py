import numpy as np
import matplotlib.pylab as plt
from matplotlib import cm


def show_path(tracked_path):
    c_map = cm.get_cmap('viridis', 255)(np.linspace(0, 1,  len(tracked_path)))[:, 0:3]
    plt.figure()
    for data_point in range(len(tracked_path) - 1):
        plt.plot(tracked_path[data_point:(data_point+2), 0], tracked_path[data_point:(data_point+2), 1],
                 color=c_map[data_point, :])

    plt.scatter(tracked_path[0, 0], tracked_path[0, 1], color=c_map[0, :])
    plt.scatter(tracked_path[-1, 0], tracked_path[-1, 1], color=c_map[-1, :])
    plt.ylabel('y coordinate')
    plt.xlabel('x coordinate')
    plt.title('path of individual')


def show_stats(stats):
    plt.figure()
    plt.subplot(121)
    plt.plot(stats[:, 0], stats[:, 1])
    plt.xlabel('generation')
    plt.ylabel('fitness')
    plt.title('average performance over generations')

    plt.subplot(122)
    plt.plot(stats[:, 0], stats[:, 3])
    plt.xlabel('generation')
    plt.title('best performance over generations')