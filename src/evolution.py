from src.individual import _make_random_genome, get_dist, _make_size_dict, \
    _interpolate_move_pattern, _make_limb_dict, _move_pattern_size, _normalize_move_pattern
import numpy as np
import random


def crossing(pairs, gene_pool, evo_config):
    mutation_prob_ind = evo_config['evolution']['mutation_prob_ind']
    mutation_prob_gene = evo_config['evolution']['mutation_prob_gene']
    mutation_prob_feature = evo_config['evolution']['mutation_prob_feature']

    if evo_config['individuals']['max_move_pattern_size'] is None:
        max_move_pattern = evo_config['simulation']['fps'] * evo_config['simulation']['duration']
    else:
        max_move_pattern = evo_config['individuals']['max_move_pattern_size']

    # perform crossing of parents including mutation of a certain probability
    gene_pool_out = []
    size_keys = _make_size_dict(evo_config).keys()
    move_keys = _make_limb_dict().keys()
    # iterate over selected pairs
    for pair in pairs:
        child = [{}, {}]

        # make dummy genome for mutation
        rand_child = _make_random_genome(evo_config)

        # assign probability for this genome to mutate
        child_mut_prob = np.random.rand()

        # iterate over chromosomes
        for idx, chromosomes in enumerate(zip(gene_pool[pair[0]], gene_pool[pair[1]])):

            # if dictionary iterate over genes
            if isinstance(chromosomes[0], dict):
                for gene in chromosomes[0].keys():

                    # vary moving pattern length
                    if gene in move_keys:

                        # mutation for move pattern size
                        if child_mut_prob < mutation_prob_ind and np.random.rand() < mutation_prob_gene \
                                and np.random.rand() < mutation_prob_feature:
                            move_steps = _move_pattern_size(evo_config)
                        else:
                            o = np.mean([len(chromosomes[0][gene]), len(chromosomes[1][gene])])
                            d = len(chromosomes[0][gene]) - len(chromosomes[1][gene])
                            move_steps = int(np.round(_randoms_between(_limit([o], [d], evo_config)))[0])

                        chromosomes[0][gene] = _interpolate_move_pattern(chromosomes[0][gene], move_steps,
                                                                         max_size=max_move_pattern)
                        chromosomes[1][gene] = _interpolate_move_pattern(chromosomes[1][gene], move_steps,
                                                                         max_size=max_move_pattern)

                        # assure random child has same length
                        rand_child[idx][gene] = _interpolate_move_pattern(rand_child[idx][gene], move_steps,
                                                                          max_size=max_move_pattern)

                    # assure symmetry if demanded
                    if evo_config['individuals']['symmetric'] and 'right_' in gene and gene in size_keys:
                        child[idx][gene] = child[idx]['left_' + gene.split('right_')[1]]
                        continue

                    # compute crossing function
                    o = np.mean([chromosomes[0][gene], chromosomes[1][gene]], axis=0)
                    d = np.asarray(chromosomes[0][gene]) - np.asarray(chromosomes[1][gene])
                    child[idx][gene] = _randoms_between(_limit(o, d, evo_config))

                    # mutate if probability allows
                    if child_mut_prob < mutation_prob_ind and np.random.rand() < mutation_prob_gene:
                        mut_features = np.random.rand(len(child[idx][gene])) < mutation_prob_feature
                        child[idx][gene][mut_features] = rand_child[idx][gene][mut_features]

                    # make sure move patterns are normalized to sum to 2 pi if desired
                    if evo_config['individuals']['normalize_move_pattern'] and gene in move_keys:
                        child[idx][gene] = _normalize_move_pattern(child[idx][gene])

                    # make sure to not have sizes greater than 0
                    if gene in size_keys:
                        child[idx][gene][child[idx][gene] <= 0] = 0.01

        gene_pool_out.append(child)
    return gene_pool_out


def fitness(pop, sim_id):
    # compute fitness as distance to origin
    return [get_dist(ind, sim_id) for ind in pop]


def selection(sorted_pop):
    # perform parent selection based on sorted (according to fitness) population

    # want to keep 50% of the pop
    num_survivors = int(0.5 * len(sorted_pop))

    # calcul of select and k and value of coeff
    # from "Concepts fondamentaux des algorithmes évolutionnistes"
    # by Jean-Baptiste Mouret
    coeff = 1.1
    k = coeff ** (num_survivors + 1) - 1
    survivor_ids = list(np.round(num_survivors - (num_survivors / np.log(k + 1)) *
                                 np.log(k * np.random.rand(num_survivors) + 1)))

    survivor_ids += survivor_ids  # to ensure population length

    pairs = []
    for this_survivor_id in survivor_ids:
        # pair each survivor with one randomly chosen survivor from the difference-set
        # between the selected survivor and the others
        not_this_survivor_ids = np.setdiff1d(survivor_ids, this_survivor_id)
        not_this_survivor_id = int(random.choice(not_this_survivor_ids))
        pairs.append((sorted_pop[int(this_survivor_id)], sorted_pop[not_this_survivor_id]))
    return pairs


# define limit function
def _limit(mid, diff, evo_config):
    a = evo_config['evolution']['alpha_limits']
    limit_1 = np.asarray(mid) + np.asarray(diff) / 2 + a * np.asarray(diff)
    limit_2 = np.asarray(mid) - np.asarray(diff) / 2 - a * np.asarray(diff)
    # determine upper and lower bound
    limits_sorted = np.sort([limit_1, limit_2], axis=0)
    lower_bounds = np.array(limits_sorted[0])
    upper_bounds = np.array(limits_sorted[1])

    return lower_bounds, upper_bounds


def _randoms_between(limits):
    lows = np.array(limits[0])
    highs = np.array(limits[1])
    # abs difference to shift random distribution that is natively between 0 and 1
    # you modify the range of values by multiplying and shift the lowest values by adding
    # Example: if you want random values between 1 and 3 you say: rand * 2 + 1, etc

    # array of random values between 0 and 1
    rand_values = np.random.rand(len(highs))  # len(high) == len(low)
    differences = highs - lows
    # random values between lower bound of limits and bound of limits + abs_difference
    rand_in_limits = (rand_values * differences) + lows

    return rand_in_limits


def _make_random_gene_pool(evo_config):
    # create gene pool for specified number of individuals
    gene_pool = []
    num_inds = evo_config['simulation']['individuals']
    for ind in range(num_inds):
        gene_pool.append(_make_random_genome(evo_config))

    return gene_pool
