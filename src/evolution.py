from src.individual import make_random_genome, get_dist
import numpy as np
import random

def make_random_pop(num_inds=10, move_steps=240):
    genomes = []
    for ind in range(num_inds):
        genomes.append(make_random_genome(move_steps))

    return genomes


def selection(pop):

    # sort by fitness
    sorted_pop_inds = np.argsort([get_dist(ind) for ind in pop])[::-1]
    sorted_pop = [pop[best] for best in sorted_pop_inds]

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

    parents = []
    for this_survivor_id in survivor_ids:
        # pair each survivor with one randomly chosen survivor from the difference-set
        # between the selected survivor and the others
        not_this_survivor_ids = np.setdiff1d(survivor_ids, this_survivor_id)
        not_this_survivor_id = int(random.choice(not_this_survivor_ids))
        parents.append((sorted_pop[int(this_survivor_id)],
                        sorted_pop[not_this_survivor_id]))

    return parents
