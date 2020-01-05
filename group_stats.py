from src.stats import read_group_stats
from src.IO import read_evo_config
import numpy as np
from scipy import stats
import matplotlib.pylab as plt
import os

generation = 149
stat_alpha = 0.05

group_stats = read_group_stats()
results_sel_gen = {}
results_over_gen = {}
plot_data_sel_gen = []
plot_data_over_gen = []
labels = []
for experiment in group_stats.keys():
    results_exp_sel_gen = []
    results_sel_gen[experiment] = {}
    results_over_gen[experiment] = []
    config = read_evo_config('experiments' + os.path.sep + 'all_gene_pools_param_comparison' +
                             os.path.sep + experiment + os.path.sep + 'evo_config.json')
    for trial in group_stats[experiment].keys():
        results_exp_sel_gen.append(group_stats[experiment][trial][generation][1])
        results_over_gen[experiment].append(np.asarray(group_stats[experiment][trial])[:, 1])
    if len(results_exp_sel_gen) > 0:
        results_sel_gen[experiment]['mean'] = np.mean(results_exp_sel_gen)
        results_sel_gen[experiment]['std'] = np.std(results_exp_sel_gen)
        results_sel_gen[experiment]['median'] = np.median(results_exp_sel_gen)
        results_sel_gen[experiment]['min'] = np.min(results_exp_sel_gen)
        results_sel_gen[experiment]['max'] = np.max(results_exp_sel_gen)
        results_sel_gen[experiment]['values'] = results_exp_sel_gen

        labels.append('I = {:.2f}\nG = {:.2f}\nF = {:.2f}'.format(
            config['evolution']['mutation_prob_ind'],
            config['evolution']['mutation_prob_gene'],
            config['evolution']['mutation_prob_feature']))
        plot_data_sel_gen.append(results_exp_sel_gen)
        tmp = results_over_gen[experiment]
        results_over_gen[experiment] = {'mean': np.mean(tmp, axis=0),
                                        'median': np.median(tmp, axis=0),
                                        'std': np.std(tmp, axis=0)}
        plot_data_over_gen.append(results_over_gen[experiment])

plt.figure()
for this_plot in plot_data_over_gen:
    plt.fill_between(range(len(this_plot['mean'])), this_plot['mean'] -
                     (this_plot['std']) / 30**0.5, this_plot['mean'] + (this_plot['std']) / 30**0.5, alpha=0.5)

for this_plot in plot_data_over_gen:
    plt.plot(this_plot['mean'])

plt.title('mean and standard error for different mutation rates')
plt.ylabel('distance')
plt.xlabel('generation')

p_values = []
for generation_sig in range(150):
    results_sel_gen = {}
    for experiment in group_stats.keys():
        results_sel_gen[experiment] = {}
        results_exp_sel_gen = []
        for trial in group_stats[experiment].keys():
            results_exp_sel_gen.append(group_stats[experiment][trial][generation_sig][1])
        if len(results_exp_sel_gen) > 0:
            results_sel_gen[experiment]['values'] = results_exp_sel_gen

    _, p = stats.f_oneway(results_sel_gen['a_all_gene_pools_nonsym_extremehigh']['values'],
                          results_sel_gen['c_all_gene_pools_nonsym_lower']['values'],
                          results_sel_gen['b_all_gene_pools_nonsym_higher']['values'],
                          results_sel_gen['d_all_gene_pools_nonsym_extremelow']['values'])
    p_values.append(p)

# Holm-Bonferroni correction
# target_alphas = stat_alpha / (len(p_values) - np.asarray(range(1, len(p_values) + 1)) + 1)
# target_alphas = target_alphas[np.argsort(p_values)]

target_alphas = np.ones(len(p_values)) * stat_alpha

plt.plot(np.where(np.asarray(p_values) < target_alphas)[0], np.ones(np.sum(np.asarray(p_values) < target_alphas)), 'k.')

legend = plt.legend([label.replace('\n', ' | ') for label in labels] + ['1 way ANOVA uncorr p < .05'])
legend.set_title('mutation rate')
plt.show()

plt.figure()
plt.title('average distances for generation {}'.format(generation))
plt.boxplot(plot_data_sel_gen, patch_artist=True, labels=labels)
plt.ylabel('average distances')
plt.xlabel('mutation rate')
plt.show()
