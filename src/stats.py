import numpy as np
from src.individual import get_dist, _get_pos
from src.IO import load_stats
import os
sep = os.path.sep


def track_individual(ind_id, sim_id, tracker_list):
    """Adds x and y coordinates of the current position of a given individual to the tracker_list.

    Parameters
    ----------
    ind_id : int
        Index pointing to the multi body of the respective simulation.
    sim_id : int
        Index pointing to the physics server of the respective simulation.
    tracker_list : list
        List of x and y coordinates for a given individual.

    Returns
    -------
    tracker_list : list
        Appended list of x and y coordinates for a given individual.
    """

    # track x and y coordinates for specified individual
    x, y = _get_pos(ind_id, sim_id)
    tracker_list.append([x, y])
    return tracker_list


def avg_dist(pop, sim_id):
    """Computes the average distance for a set of individuals in a given simulation.

    Parameters
    ----------
    pop : list
        List of ind_ids for multiple individuals.
    sim_id : int
        Index pointing to the physics server of the respective simulation.

    Returns
    -------
    avg_dist : float
        Average distance that selected individuals moved.
    """

    # compute average distance for a population
    return np.mean([get_dist(ind, sim_id) for ind in pop])


def read_group_stats(experiment_folder='experiments' + sep + 'all_gene_pools_param_comparison'):
    """Collects data for precomputed experiments.

    This function looks through the experiment folder and assumes each sub-directory being a different experiment.
    Within each subdirectory, sub-subdirectories are assumed to represent trials. Within each trial folder the function
    looks for the respective stats.csv and loads it. The result will be in form of a nested dictionary, where the first
    level keys are the name of directory defined for each experiment and the second level for each trial. Hence it is
    advisable to name experiment directories comprehensively and trial directories as increasing integers.

    Parameters
    ----------
    experiment_folder : str
        Path to directory where all experiments are stored.

    Returns
    -------
    results : dict
        Results of selected experiments. This is a nested dictionary, where the first level accepts keys according to
        the name of the experiment (i.e. name of directory where it was stored) and on the second level the trial, which
        again is the name of the directory.
    """

    # read statistics for multiple trial experiments
    experiments = sorted(next(os.walk(experiment_folder))[1])
    results = {}
    for experiment in experiments:
        results[experiment] = {}
        trials = sorted(next(os.walk(experiment_folder + sep + experiment))[1])
        for trial in trials:
            curr_dir = experiment_folder + sep + experiment + sep + trial
            try:
                results[experiment][trial] = load_stats(curr_dir + sep + 'stats.csv')
            except OSError:
                print('no group stats for {}'.format(curr_dir))
    return results
