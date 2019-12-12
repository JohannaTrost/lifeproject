import numpy as np
import matplotlib.pylab as plt
from matplotlib import cm


def show_path(tracked_paths):
    plt.figure()
    plt.gcf().set_facecolor('black')
    for key in tracked_paths.keys():
        tracked_path = np.asarray(tracked_paths[key])
        if len(tracked_paths) > 1:
            plt.plot(tracked_path[:, 0], tracked_path[:, 1])
            plt.scatter(tracked_path[0, 0], tracked_path[0, 1])
            plt.title('paths of individuals', color='white')
        else:
            c_map = cm.get_cmap('viridis', 255)(np.linspace(0, 1, len(tracked_path)))[:, 0:3]
            for data_point in range(len(tracked_path) - 1):
                plt.plot(tracked_path[data_point:(data_point+2), 0], tracked_path[data_point:(data_point+2), 1],
                         color=c_map[data_point, :])
            plt.title('path of individual', color='white')

        plt.scatter(tracked_path[-1, 0], tracked_path[-1, 1], color='yellow')
        plt.scatter(tracked_path[0, 0], tracked_path[0, 1], color='white')
    plt.gca().set_facecolor('black')
    plt.gca().spines['bottom'].set_color('white')
    plt.gca().spines['top'].set_color('white')
    plt.gca().spines['left'].set_color('white')
    plt.gca().spines['right'].set_color('white')
    plt.gca().xaxis.label.set_color('white')
    plt.gca().tick_params(axis='x', colors='white')
    plt.gca().yaxis.label.set_color('white')
    plt.gca().tick_params(axis='y', colors='white')
    plt.ylabel('y coordinate')
    plt.xlabel('x coordinate')
    plt.show()


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
    plt.show()
