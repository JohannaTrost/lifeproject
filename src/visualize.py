from src.simulation import simulate_pop
import numpy as np
import matplotlib.pylab as plt
from matplotlib import cm


def show_multiple_gen_paths(gen_tracked_paths):
    # show paths for multiple generations
    coord_max = 0

    # find maximum coordinate for axis scaling
    for tracked_paths in gen_tracked_paths:
        for key in tracked_paths.keys():
            tracked_path = np.asarray(tracked_paths[key])
            if np.max(np.abs(tracked_path)) > coord_max:
                coord_max = np.max(np.abs(tracked_path))

    # ensure enough generations to be split in 5 plots
    if len(gen_tracked_paths) > 4:
        gens = list(range(0, len(gen_tracked_paths), int(len(gen_tracked_paths) / 5)))
    else:
        gens = list(range(len(gen_tracked_paths)))

    # ensure last generation is displayed
    if not gens[-1] == (len(gen_tracked_paths) - 1):
        gens += [len(gen_tracked_paths) - 1]

    # set plotting title according to selected or index
    for idx, tracked_paths in enumerate([gen_tracked_paths[gen] for gen in gens]):
        if gens is not None:
            gen = gens[idx]
        else:
            gen = idx

        # perform plotting
        show_path(tracked_paths, coord_max * 1.1, title='paths of gen {}'.format(gen))


def show_path(tracked_paths, ax_lim=None, title='paths of individuals'):
    # show paths for one generation
    plt.figure()
    plt.gcf().set_facecolor('black')

    # iterate over individuals
    for key in tracked_paths.keys():
        tracked_path = np.asarray(tracked_paths[key])

        if len(tracked_paths) > 1:
            plt.plot(tracked_path[:, 0], tracked_path[:, 1])
            plt.scatter(tracked_path[0, 0], tracked_path[0, 1])
            plt.title(title, color='white')
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
    if ax_lim is not None:
        plt.xlim((-ax_lim, ax_lim))
        plt.ylim((-ax_lim, ax_lim))
        plt.gca().set_aspect('equal', 'box')
    plt.show()


def show_stats(stats):
    # show summary of fitness over all generations (average and best performer)
    stats = np.asarray(stats)
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


def show_individual(gene_pool, duration):
    # show desired simulation
    return simulate_pop(gene_pool, fps=240, duration_in_sec=duration,
                        track_individuals=True, direct=False)
