import numpy as np
from scipy import stats
import matplotlib.pylab as plt
import os, sys, inspect
sep = os.path.sep
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0,parent_dir)
from src.IO import read_evo_config, load_stats


def read_group_stats(experiment_folder):
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
    for experiment_sel in experiments:
        if not experiment_sel[0] == '_':
            results[experiment_sel] = {}
            trials = sorted(next(os.walk(experiment_folder + sep + experiment_sel))[1])
            for trial_sel in trials:
                curr_dir = experiment_folder + sep + experiment_sel + sep + trial_sel
                try:
                    results[experiment_sel][trial_sel] = load_stats(curr_dir + sep + 'stats.csv')
                except OSError:
                    print('no group stats for {}'.format(curr_dir))
    return results


def main():
    """Main function to display and store group statistics.

    Group statistics were precomputed on an HPC. For each experiment in `experiments` 30 trials were computed using the
    respective ``.json`` configuration files. That is simulating 80 individuals per generation for 150 generations and
    a simulation duration per individual of 40s.

    This function transforms the results into plots, displays them and stores corresponding ``.png`` files in
    `result_plots`. Files are read using :func:`experiments.group_stats.read_group_stats`.

    To run this function use the command line and type:

    ``python experiments/group_stats.py``
    """

    # select generations and significance level
    generations = 149
    stat_alpha = 0.05

    # read stats from file
    group_stats = read_group_stats(current_dir)

    # initialize result variables for plotting
    plot_data_sel_gen = []
    plot_data_over_gen = []
    labels = []

    for experiment in group_stats.keys():

        # obtain config for labelling
        config = read_evo_config(current_dir + sep + experiment + sep + 'evo_config.json')
        results_exp_sel_gen = []
        results_over_gen = []

        # collect data trial-wise
        for trial in group_stats[experiment].keys():
            results_exp_sel_gen.append(group_stats[experiment][trial][generations][1])
            results_over_gen.append(np.asarray(group_stats[experiment][trial])[:generations, 1])

        plot_data_sel_gen.append(results_exp_sel_gen)
        plot_data_over_gen.append(results_over_gen)
        labels.append('I = {:.2f}\nG = {:.2f}\nF = {:.2f}\nSym = {}'.format(
            config['evolution']['mutation_prob_ind'],
            config['evolution']['mutation_prob_gene'],
            config['evolution']['mutation_prob_feature'],
            config['individuals']['symmetric'] + 0))

    # box plots
    for y_limit in [(None, None), (0, 500)]:
        plt.figure(figsize=(16, 9))
        plt.boxplot(plot_data_sel_gen, patch_artist=True, labels=labels)
        plt.title('average distances for generation {}'.format(generations))
        plt.ylabel('average distances')
        plt.xlabel('mutation rates & symmetry')
        plt.ylim(y_limit)
        plt.gcf().subplots_adjust(bottom=0.175)
        plt.savefig(
            parent_dir + sep + 'result_plots' + sep + 'group_stats' + sep + 'box_plot_gen_{}_both_sym_ylim_{}.png'.format(
                generations, int(plt.ylim()[1])))
        plt.show()

    # line plots with standard error and significance index
    for index in [(0, int(len(plot_data_over_gen) / 2), 'non_sym'),
                  (int(len(plot_data_over_gen) / 2), len(plot_data_over_gen), 'sym')]:
        _, p_vals = stats.f_oneway(*plot_data_over_gen[index[0]:index[1]])

        plt.figure(figsize=(16, 9))
        for this_plot in plot_data_over_gen[index[0]:index[1]]:
            plt.fill_between(range(len(np.mean(this_plot, axis=0))), np.mean(this_plot, axis=0) - (
                np.std(this_plot, axis=0)) / 30**0.5, np.mean(this_plot, axis=0) + (np.std(this_plot, axis=0)) / 30**0.5,
                             alpha=0.5)

        for this_plot in plot_data_over_gen[index[0]:index[1]]:
            plt.plot(np.mean(this_plot, axis=0))

        # Holm-Bonferroni correction
        target_alphas_bonf = stat_alpha / (len(p_vals) - np.asarray(range(1, len(p_vals) + 1)) + 1)
        target_alphas_bonf = target_alphas_bonf[np.argsort(p_vals)]

        target_alphas = np.ones(len(p_vals)) * stat_alpha

        plt.plot(np.where(np.asarray(p_vals) < target_alphas)[0], np.ones(np.sum(np.asarray(p_vals) < target_alphas)), 'k.')
        plt.plot(np.where(np.asarray(p_vals) < target_alphas_bonf)[0], 4 * np.ones(np.sum(
            np.asarray(p_vals) < target_alphas_bonf)), 'r.')

        plt.title('mean and standard error for different mutation rates')
        plt.ylabel('distance')
        plt.xlabel('generation')
        legend = plt.legend(
            [label.replace('\n', ' | ') for label in labels[index[0]:index[1]]] + [
                '1 way ANOVA uncorrected p < .05'] + ['1 way ANOVA stepwise Bonferroni p < .05'],
            loc='upper left')
        legend.set_title('mutation rate')
        plt.gcf().subplots_adjust(bottom=0.175)
        plt.savefig(parent_dir + sep + 'result_plots' + sep + 'group_stats' + sep + 'line_plot_gen_{}_{}.png'.format(
            generations, index[2]))
        plt.show()


if __name__ == '__main__':
    main()
