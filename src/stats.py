import numpy as np
from src.individual import get_dist, _get_pos
from src.IO import load_stats
import os


def track_individual(ind, sim_id, tracker_list):
    # track x and y coordinates for specified individual
    x, y = _get_pos(ind, sim_id)
    tracker_list.append([x, y])
    return tracker_list


def avg_dist(pop, sim_id):
    # compute average distance for a population
    return np.mean([get_dist(ind, sim_id) for ind in pop])


def read_group_stats(experiment_folder='experiments'+os.path.sep+'all_gene_pools_param_comparison'):
    # read statistics for multiple trial experiments
    experiments = sorted(next(os.walk(experiment_folder))[1])
    results = {}
    for experiment in experiments:
        results[experiment] = {}
        trials = sorted(next(os.walk(experiment_folder + os.path.sep + experiment))[1])
        for trial in trials:
            curr_dir = experiment_folder + os.path.sep + experiment + os.path.sep + trial
            try:
                results[experiment][trial] = load_stats(curr_dir + os.path.sep + 'stats.csv')
            except OSError:
                print('no group stats for {}'.format(curr_dir))
    return results
