import numpy as np
from src.individual import get_dist


def avg_dist(pop):
    return np.mean([get_dist(ind) for ind in pop])


def save_stats(stats, filename='src/results/latest_results.csv'):
    np.savetxt(filename, stats, delimiter=',')


def load_stats(filename='src/results/latest_results.csv'):
    return np.loadtxt(filename, delimiter=',')
