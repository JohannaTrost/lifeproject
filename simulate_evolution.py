from src.simulation import simulate_pop, simulate_multi_core, make_sim_env, reset_simulation
import src.evolution as evo
import src.stats as st
import src.data2plot as data2plot
import argparse
import numpy as np
import time
import os
from multiprocessing import cpu_count


def main():
    # argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument('--individuals', '-i', default=10, type=int,
                        help='number of individuals - In case visualization mode was chosen, a random set of i '
                             'individuals will be chosen')
    parser.add_argument('--generations', '-g', default=10, type=int,
                        help='number of generations')
    parser.add_argument('--duration', '-d', default=10, type=int,
                        help='duration of each simulation in seconds')
    parser.add_argument('--fps', '-f', default=240, type=int,
                        help='frames per second')
    parser.add_argument('--save_gene_pool', '-s', default='False', type=str,
                        help='Save all gene pools per generation to new folder - '
                             'If not set only last generation will be saved')
    parser.add_argument('--cores', '-c', default=1, type=int,
                        help='number of CPU cores (default=1) Set to -1 for all cores')
    parser.add_argument('--visualize', '-v', default='False', type=str,
                        help='visualize result specified')
    parser.add_argument('--stats', '-sf', default='', type=str,
                        help='evo stats file to use for visualization (default is latest file)')
    parser.add_argument('--gene_pool_file', '-gf', default='', type=str,
                        help='genome file to use for visualization (default is latest file)')
    parser.add_argument('--generation', '-gen', default=-1, type=int,
                        help='generation number to show - Set to -1 for last generation')
    parser.add_argument('--best_only', '-b', default='True', type=str,
                        help='whether to show only the best or multiple individuals')
    args = parser.parse_args()

    if args.cores == -1:
        args.cores = cpu_count()

    fps = args.fps

    duration_per_simulation_in_sec = args.duration
    generations = args.generations
    individuals = args.individuals
    save_results = True if args.save_gene_pool.lower() in ['true', 'yes', '1', 'y', 't'] else False
    cores = args.cores
    visualize = True if args.visualize.lower() in ['true', 'yes', '1', 'y', 't'] else False

    stats_file = args.stats
    gene_pool_file = args.gene_pool_file
    generation_to_show = args.generation
    best_only = True if args.best_only.lower() in ['true', 'yes', '1', 'y', 't'] else False

    if not visualize:

        print('Starting evolution...')

        if save_results:
            from datetime import datetime
            save_dir = os.getcwd()
            date_time = datetime.now().strftime("%m-%d-%Y-%H-%M-%S")
            save_dir += os.path.sep + 'src' + os.path.sep + 'results' + os.path.sep
            save_dir += 'all_gene_pools_{}gen_{}ind_{}dur_' + date_time + os.path.sep
            save_dir = save_dir.format(generations, individuals, duration_per_simulation_in_sec)
            if not os.path.isdir(save_dir):
                os.mkdir(save_dir)
        else:
            save_dir = 'src' + os.path.sep + 'results' + os.path.sep

        print('Individuals: {}'.format(individuals))
        print('Generations: {}'.format(generations))
        print('Duration per simulation: {}s'.format(duration_per_simulation_in_sec))
        print('FPS: {}'.format(fps))
        print('Number of cores utilized: {}'.format(cores))
        if save_results:
            print(('saving output to ' + save_dir).format(generations, individuals, duration_per_simulation_in_sec))
        print('')

        stats = []
        fitness_over_gen = []

        gene_pool = evo.new_gene_pool('random', num_inds=individuals)  # filename to load precomputed

        # make simulation IDs running on as mani servers as there are cores selected
        sim_ids = []
        for simulation in range(cores):
            sim_ids.append(make_sim_env('direct'))

        print('Connecting to physics server {}'.format(sim_ids))

        for generation in range(generations):
            start = time.time()
            fitness = simulate_multi_core(gene_pool,
                                          fps=fps,
                                          duration_in_sec=duration_per_simulation_in_sec,
                                          num_cores=cores,
                                          sim_ids=sim_ids)

            sorted_genome_ids = np.argsort(fitness)[::-1]
            selected = evo.selection(sorted_genome_ids)
            avg_dist = np.mean(fitness)

            best = sorted_genome_ids[0]

            if save_results:
                evo.save_gene_pool(gene_pool, filename=save_dir + 'gen_' + str(generation) + '.pkl')

            gene_pool = evo.crossing(selected, gene_pool, max_move_pattern=int(fps * duration_per_simulation_in_sec))

            # collect data on population
            stats.append([generation, avg_dist, best, fitness[best]])
            fitness_over_gen.append(fitness + [generation])

            print('generation {} | avg distance {} | duration {}s'.format(generation, avg_dist,
                                                                          round(time.time() - start)))

        st.save_stats(stats, filename=save_dir + 'stats.csv')
        st.save_stats(fitness_over_gen, filename=save_dir + 'fitness.csv')
        evo.save_gene_pool(gene_pool, filename=save_dir + 'gen_' + str(generations - 1) + '.pkl')

        print('done.')
        print('')

    else:
        # load stats file or use default
        if len(stats_file) < 1:
            stats = st.load_stats()
        else:
            stats = st.load_stats(stats_file)

        # load gene pool file or use default
        if len(gene_pool_file) < 1:
            gene_pool = evo.load_gene_pool()
        else:
            gene_pool = evo.load_gene_pool(gene_pool_file)

        # show only best individual, derived from stats
        if best_only:
            best = int(stats[generation_to_show, -2])
            gene_pool = [gene_pool[best]]
        else:
            ind_sel = np.random.random_integers(0, len(gene_pool) - 1, individuals)
            gene_pool = [gene_pool[ind] for ind in ind_sel]

        # show desired simulation
        pop, sim_id, tracker = simulate_pop(gene_pool,
                                            fps=240,
                                            duration_in_sec=duration_per_simulation_in_sec,
                                            track_individuals=True,
                                            direct=False)

        # show stats
        data2plot.show_stats(stats)

        # show tracked paths
        data2plot.show_path(tracker)


if __name__ == '__main__':
    main()
