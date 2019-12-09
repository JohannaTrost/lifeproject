from src.individual import make_random_genome, get_dist
import numpy as np

def make_random_pop(num_inds=10, move_steps=240):
    genomes = []
    for ind in range(num_inds):
        genomes.append(make_random_genome(move_steps))

    return genomes


def get_fitness(pop):
    return [get_dist(ind) for ind in pop]


def select(pop, fitness, num_selected=2):
    return [pop[best] for best in np.argsort(fitness)[::-1][:num_selected]]
