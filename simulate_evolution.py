from src.simulation import simulate_pop, reset_simulation, simulate_multicore
import src.evolution as evo
import src.stats as st
import argparse
import matplotlib.pylab as plt
import numpy as np


def main():

    # defaults for running as script
    motion_pattern_duration = 1
    fps = 240
    move_steps = int(motion_pattern_duration * fps)

    duration_per_simulation_in_sec = 10
    generations = 10
    individuals = 10
    cores = 8


    parser = argparse.ArgumentParser()
    parser.add_argument('--individuals', '-i', default=10, type=int,
                        help='number of individuals')
    parser.add_argument('--generations', '-g', default=10, type=int,
                        help='number of generations')
    parser.add_argument('--duration', '-d', default=10, type=int,
                        help='duration of each simulation in seconds')
    parser.add_argument('--fps', '-f', default=240, type=int,
                        help='frames per second')
    parser.add_argument('--pattern_duration', '-pd', default=1, type=int,
                        help='duration of motion pattern in seconds')
    parser.add_argument('--cores', '-c', default=1, type=int,
                        help='number of CPU cores (default=1) Set to -1 for all cores')
    args = parser.parse_args()

    print('Individuals : {}'.format(args.individuals))
    print('Generations: {}'.format(args.generations))
    print('Duration per simulation: {}s'.format(args.duration))
    print('FPS: {}'.format(args.fps))
    print('Motion pattern duration: {}s'.format(args.pattern_duration))
    print('Number of cores utilized: {}'.format(args.cores))
    print('')

    motion_pattern_duration = args.pattern_duration
    fps = args.fps
    move_steps = int(motion_pattern_duration * fps)

    duration_per_simulation_in_sec = args.duration
    generations = args.generations
    individuals = args.individuals
    cores = args.cores
    show_best = False

    stats = []
    all_gene_pools = []

    gene_pool = evo.new_gene_pool('random', num_inds=individuals, move_steps=move_steps)  # filename to load precomputed

    all_gene_pools.append(gene_pool)

    for generation in range(generations):
        if cores == 1:
            pop, sim_id = simulate_pop(gene_pool, fps=fps, duration_in_sec=duration_per_simulation_in_sec, direct=True)
            # evolute
            selected = evo.selection(np.argsort(evo.fitness(pop, sim_id)))
            avg_dist = st.avg_dist(pop, sim_id)

            # reset simulation
            reset_simulation(pop, sim_id)
        else:
            fitness = simulate_multicore(gene_pool, fps=fps,
                                         duration_in_sec=duration_per_simulation_in_sec, num_cores=cores)

            selected = evo.selection(np.argsort(fitness))
            avg_dist = np.mean(fitness)


        print('generation {} | avg distance {}'.format(generation, avg_dist))

        best = selected[0][0]
        gene_pool = evo.crossing(selected, gene_pool)

        all_gene_pools.append(gene_pool)
        # collect data on population
        stats.append([generations, avg_dist, best])

    plt.figure()
    plt.plot(stats[:, 1])
    plt.savefig('src/results/latest_results.jpg')

    st.save_stats(stats, filename='src/results/stats_{}gen_{}ind_{}dur_{}steps.pkl'.format(
                           generations, individuals, duration_per_simulation_in_sec, move_steps))
    st.save_stats(stats)

    # below can cause large files
    evo.save_gene_pool(all_gene_pools,
                       filename='src/results/all_gene_pools_{}gen_{}ind_{}dur_{}steps.pkl'.format(
                           generations, individuals, duration_per_simulation_in_sec, move_steps))

    evo.save_gene_pool(gene_pool)

    if show_best:
        # show best parent
        stats = st.load_stats()
        gene_pool = evo.load_gene_pool()
        simulate_pop([gene_pool[int(stats[-1, -1])]], fps=fps, duration_in_sec=-1, direct=False)


if __name__ == '__main__':
    main()
