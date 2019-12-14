import numpy as np
from src.individual import get_dist, _get_pos


def track_individual(ind, sim_id, tracker_list):
    # track x and y coordinates for specified individual
    x, y = _get_pos(ind, sim_id)
    tracker_list.append([x, y])
    return tracker_list


def avg_dist(pop, sim_id):
    # compute average distance for a population
    return np.mean([get_dist(ind, sim_id) for ind in pop])
