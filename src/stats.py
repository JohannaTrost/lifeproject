import numpy as np
from src.individual import get_dist


def avg_dist(pop):
    return np.mean([get_dist(ind) for ind in pop])


def pop_stats(stats, pop, generation):
    """
    All data that is supposed to be collected could go in here.
    :param stats:
    :param pop:
    :param generation:
    :return:
    """
    stats.append([generation, avg_dist(pop)])
    return stats