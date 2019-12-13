from src.individual import _make_random_genome, get_dist, _make_size_dict, _interpolate_move_pattern, _make_limb_dict, \
    _move_pattern_size
import numpy as np
import random
import pickle


def save_gene_pool(gene_pool, filename='latest_gene_pool.pkl'):
    output = open(filename, 'wb')
    pickle.dump(gene_pool, output)
    output.close()


def load_gene_pool(filename='latest_gene_pool.pkl'):
    pkl_file = open(filename, 'rb')
    gene_pool = pickle.load(pkl_file)
    pkl_file.close()
    return gene_pool


def new_gene_pool(gene_pool, num_inds=10):
    if not isinstance(gene_pool, str):
        return _make_random_gene_pool(num_inds=num_inds)
    if isinstance(gene_pool, str):
        if gene_pool.lower() == 'random':
            return _make_random_gene_pool(num_inds=num_inds)
        else:
            return load_gene_pool(gene_pool)


def crossing(pairs, gene_pool, max_move_pattern=1000, mutation_prob_ind=0.05, mutation_prob_gene=0.05,
             mutation_prob_feature=0.05):

    gene_pool_out = []
    size_keys = _make_size_dict().keys()
    move_keys = _make_limb_dict().keys()
    # iterate over selected pairs
    for pair in pairs:
        child = [{}, {}]

        # make dummy genome for mutation
        rand_child = _make_random_genome()

        # assign probability for this genome to mutate
        child_mut_prob = np.random.rand()

        # iterate over chromosomes
        for idx, chromosomes in enumerate(zip(gene_pool[pair[0]], gene_pool[pair[1]])):

            # if dictionary iterate over genes
            if isinstance(chromosomes[0], dict):
                for gene in chromosomes[0].keys():

                    # vary moving pattern length
                    if gene in move_keys:

                        if child_mut_prob < mutation_prob_ind and np.random.rand() < mutation_prob_gene \
                                and np.random.rand() < mutation_prob_feature:
                            move_steps = _move_pattern_size()
                        else:
                            o = np.mean([len(chromosomes[0][gene]), len(chromosomes[1][gene])])
                            d = len(chromosomes[0][gene]) - len(chromosomes[1][gene])
                            move_steps = int(np.round(_randoms_between(_limit([o], [d])))[0])

                        chromosomes[0][gene] = _interpolate_move_pattern(chromosomes[0][gene], move_steps,
                                                                         max_size=max_move_pattern)
                        chromosomes[1][gene] = _interpolate_move_pattern(chromosomes[1][gene], move_steps,
                                                                         max_size=max_move_pattern)

                        # assure random child has same length
                        rand_child[idx][gene] = _interpolate_move_pattern(rand_child[idx][gene], move_steps,
                                                                          max_size=max_move_pattern)

                    # compute crossing function
                    o = np.mean([chromosomes[0][gene], chromosomes[1][gene]], axis=0)
                    d = np.asarray(chromosomes[0][gene]) - np.asarray(chromosomes[1][gene])
                    child[idx][gene] = _randoms_between(_limit(o, d))

                    # make sure to not have sizes greater than 0
                    if gene in size_keys:
                        child[idx][gene][child[idx][gene] <= 0] = 0.01

                    # mutate if probability allows
                    if child_mut_prob < mutation_prob_ind and np.random.rand() < mutation_prob_gene:
                        mut_features = np.random.rand(len(child[idx][gene])) < mutation_prob_feature
                        child[idx][gene][mut_features] = rand_child[idx][gene][mut_features]

        gene_pool_out.append(child)
    return gene_pool_out


def fitness(pop, sim_id):
    return [get_dist(ind, sim_id) for ind in pop]


def selection(sorted_pop):

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
def _limit(mid, diff, a=0.5):
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


def _make_random_gene_pool(num_inds=10):
    gene_pool = []
    for ind in range(num_inds):
        gene_pool.append(_make_random_genome())

    return gene_pool
