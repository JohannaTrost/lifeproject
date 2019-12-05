import numpy as np
import matplotlib.pylab as plt


def fetch_data(data_sets, path):
    avg_fitness_per_condition = []
    max_fitness_per_condition = []
    for mutation_rate in data_sets:
        data = np.loadtxt(path + str(mutation_rate) + ".csv", skiprows=1, delimiter=',')
        generations = data[:, 0]
        avg_fitness = []
        max_fitness = []
        for generation in np.unique(generations):
            avg_fitness.append(np.mean(data[generations == generation, 17]))
            max_fitness.append(np.max(data[generations == generation, 17]))
        avg_fitness_per_condition.append(avg_fitness)
        max_fitness_per_condition.append(max_fitness)

    return avg_fitness_per_condition, max_fitness_per_condition


def generate_color_plot(data_sets, avg_fitness, max_fitness, filename="", nb_individuals=None):
    plt.figure()
    plt.subplot(1, 2, 1)
    plt.imshow(avg_fitness, aspect='auto', extent=[0, 100, -0.5, 3.5])
    plt.yticks(range(len(data_sets)), data_sets[::-1])
    plt.ylabel("mutation rate")
    plt.xlabel("generation number")
    cb = plt.colorbar()
    cb.set_label("average fitness per generation")

    plt.subplot(1, 2, 2)
    plt.imshow(max_fitness, aspect='auto', extent=[0, 100, -0.5, 3.5])
    plt.yticks([])
    plt.xlabel("generation number")
    cb = plt.colorbar()
    cb.set_label("maximum fitness per generation")
    plt.suptitle("Evolution for different mutation rates")
    if nb_individuals is not None:
        plt.suptitle('{} individuals'.format(nb_individuals))
    if filename:
        plt.savefig(filename + ".png")


def generate_normal_plot(data_sets, avg_fitness, max_fitness, filename="", nb_individuals=None):
    plt.figure()
    # create plots over best and average performance of individuals
    plt.subplot(1, 2, 1)
    plt.plot(np.transpose(avg_fitness))
    plt.legend(data_sets)
    plt.title('average per generation')
    plt.ylabel('distance')
    plt.xlabel('generation')
    plt.subplot(1, 2, 2)
    plt.plot(np.transpose(max_fitness))
    plt.legend(data_sets)
    plt.title('best performer')
    plt.ylabel('distance')
    plt.xlabel('generation')
    if nb_individuals is not None:
        plt.suptitle('Evolution with different mutation rates for {} individuals'.format(nb_individuals))
    plt.tight_layout()
    if filename:
        plt.savefig(filename + ".png")
