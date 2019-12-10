from src.individual import make_random_genome, get_dist
import numpy as np
import random

def make_random_gene_pool(num_inds=10, move_steps=240):
    gene_pool = []
    for ind in range(num_inds):
        gene_pool.append(make_random_genome(move_steps))

    return gene_pool


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


def crossing(pairs, gene_pool, mutation_prob_ind=0.05, mutation_prob_gene=0.05, mutation_prob_feature=0.05):
    new_genome = []

    # iterate over selected pairs
    for pair in pairs:
        move_steps = gene_pool[pair[0]][-1]
        child = [{}, {}, move_steps]

        # make dummy genome for mutation
        rand_child = make_random_genome(move_steps)

        # assign probability for this genome to mutate
        child_mut_prob = np.random.rand()

        # iterate over chromosomes
        for idx, chromosomes in enumerate(zip(gene_pool[pair[0]], gene_pool[pair[1]])):

            # if dictionary iterate over genes
            if isinstance(chromosomes[0], dict):
                for gene in chromosomes[0].keys():

                    # compute crossing function
                    o = np.mean([chromosomes[0][gene], chromosomes[1][gene]], axis=0)
                    d = np.asarray(chromosomes[0][gene]) - np.asarray(chromosomes[1][gene])
                    child[idx][gene] = _randoms_between(_limit(o, d))

                    # mutate if probability allows
                    if child_mut_prob < mutation_prob_ind and np.random.rand() < mutation_prob_gene:
                        mut_features = np.random.rand(len(child[idx][gene])) < mutation_prob_feature
                        child[idx][gene][mut_features] = rand_child[idx][gene][mut_features]

        new_genome.append(child)
    return new_genome


def selection(pop):

    # sort by fitness
    sorted_pop = np.argsort([get_dist(ind) for ind in pop])[::-1]

    # want to keep 50% of the pop
    num_survivors = int(0.5 * len(sorted_pop))

    # calcul of select and k and value of coeff
    # from "Concepts fondamentaux des algorithmes évolutionnistes"
    # by Jean-Baptiste Mouret
    coeff = 1.1
    k = coeff ** (num_survivors + 1) - 1
    survivor_ids = list(np.round(num_survivors - (num_survivors / np.log(k + 1)) *
                            np.log(k * np.random.rand(num_survivors) + 1)))

    survivor_ids += survivor_ids # to ensure population length

    pairs = []
    for this_survivor_id in survivor_ids:
        # pair each survivor with one randomly chosen survivor from the difference-set
        # between the selected survivor and the others
        not_this_survivor_ids = np.setdiff1d(survivor_ids, this_survivor_id)
        not_this_survivor_id = int(random.choice(not_this_survivor_ids))
        pairs.append((sorted_pop[int(this_survivor_id)],
                        sorted_pop[not_this_survivor_id]))
    return pairs
