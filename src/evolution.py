from src.individual import make_random_genome


def make_random_pop(num_inds=10, move_steps=240):
    genomes = []
    for ind in range(num_inds):
        genomes.append(make_random_genome(move_steps))

    return genomes
