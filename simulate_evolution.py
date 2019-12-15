from src.simulation import simulate_multi_core, connect_to_servers
import src.evolution as evo
import src.visualize as vis
import src.IO as IO
import argparse
import numpy as np
import time


def main():
    # argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument('--individuals', '-i', default=None, type=int,
                        help='number of individuals - In case visualization mode was chosen, a random set of i '
                             'individuals will be chosen (default=40)')
    parser.add_argument('--generations', '-g', default=None, type=int,
                        help='number of generations (default=100)')
    parser.add_argument('--duration', '-d', default=None, type=int,
                        help='duration of each simulation in seconds (default=10)')
    parser.add_argument('--get_config', '-gc', default='False', type=str,
                        help='create config file and exit')
    parser.add_argument('--evolution_dir', '-e', default='', type=str,
                        help='directory for evolution to show (default=example)')
    parser.add_argument('--tracking', '-t', default='True', type=str,
                        help='whether the path of each individual is recorded (default=True)')
    parser.add_argument('--save_gene_pool', '-s', default='False', type=str,
                        help='Save all gene pools per generation to new folder - '
                             'If not set only last generation will be saved')
    parser.add_argument('--overwrite', '-o', default='False', type=str,
                        help='overwrite data (default=False)')
    parser.add_argument('--cores', '-c', default=-1, type=int,
                        help='number of CPU cores - Set to -1 for all cores (default=-1)')

    parser.add_argument('--visualize', '-v', default='False', type=str,
                        help='visualize result specified (default=False)')
    parser.add_argument('--generation', '-gen', default=-1, type=int,
                        help='generation selected for displaying - Set -1 for latest (default=-1)')
    parser.add_argument('--best_only', '-b', default='True', type=str,
                        help='whether to show only the best or multiple individuals (default=True)')
    parser.add_argument('--show_stats', '-ss', default='False', type=str,
                        help='whether to show statistics on the evolution - '
                             'If True only statistics and no rendered individuals are shown (default=False)')

    # convert certain arguments
    args, evo_config = IO.convert_some_args(parser.parse_args())

    # initialize simulation
    gene_pool, evo_config, stats, fitness_over_gen, tracker_over_gen, save_dir = IO.get_from_config(args, evo_config)

    IO.write_evo_config(evo_config, IO.return_parent_path(args) + 'evo_config.json')

    if args.get_config:
        raise SystemExit

    if not args.visualize:

        # print summary
        print('Starting evolution...')
        save_dir = IO.return_parent_path(args)

        print('Individuals: {}'.format(evo_config['simulation']['individuals']))
        print('Generations: {}'.format(evo_config['simulation']['generations']))
        print('Duration per simulation: {}s'.format(evo_config['simulation']['duration']))
        print('FPS: {}'.format(evo_config['simulation']['fps']))
        print('Number of cores utilized: {}'.format(args.cores))
        print('saving output to ' + save_dir)
        print('')

        # make simulation IDs running on as mani servers as there are cores selected
        sim_ids = connect_to_servers(args.cores)

        print('Connecting to physics server {}'.format(sim_ids))

        # iterate over generations
        for generation in range(args.generation, args.generations + args.generation):
            start = time.time()

            # obtain fitness for each individual in current generation
            fitness, tracker = simulate_multi_core(gene_pool, evo_config,
                                                   track_individuals=True,
                                                   num_cores=args.cores, sim_ids=sim_ids)

            # sort fitness descending
            sorted_genome_ids = np.argsort(fitness)[::-1]

            # select best performers and transform into parent pairs
            selected = evo.selection(sorted_genome_ids)

            # collect data on population
            avg_dist = np.mean(fitness)
            best = sorted_genome_ids[0]

            stats.append([generation, avg_dist, best, fitness[best]])
            fitness_over_gen.append(fitness + [generation])
            if args.tracking:
                tracker_over_gen.append(tracker)

            # if desired save state of current gene pool
            if args.save_gene_pool:
                IO.save_gene_pool(gene_pool, filename=save_dir + 'gen_' + str(generation) + '.pkl')

                # to make sure files are present even if the evolution was interrupted
                IO.save_stats(stats, filename=save_dir + 'stats.csv')
                IO.save_stats(fitness_over_gen, filename=save_dir + 'fitness.csv')
                if args.tracking:
                    IO.save_tracker(tracker_over_gen, filename=save_dir + 'tracker.pkl')

            # create new gene poll by pairing selected parents
            gene_pool = evo.crossing(selected, gene_pool, evo_config)

            # print status
            print('generation {} | avg distance {} | duration {}s'.format(generation, avg_dist,
                                                                          round(time.time() - start)))

        # save statistics, fitness and position data and gene pool
        IO.save_stats(stats, filename=save_dir + 'stats.csv')
        IO.save_stats(fitness_over_gen, filename=save_dir + 'fitness.csv')
        if args.tracking:
            IO.save_tracker(tracker_over_gen, filename=save_dir + 'tracker.pkl')
        IO.save_gene_pool(gene_pool, filename=save_dir + 'gen_' + str(args.generations +
                                                                      args.generation - 1) + '.pkl')

        print('done.')
        print('')

    else:

        if not args.show_stats:
            # show desired simulation
            pop, sim_id, tracker = vis.show_individual(gene_pool, evo_config)

            # show tracked paths
            vis.show_path(tracker)

        else:
            # show stats
            if args.tracking:
                # show tracked paths
                tracked_paths = IO.load_tracker(args.tracker)
                vis.show_path(tracked_paths[args.generation], title='paths of gen {}'.format(args.generation))

                vis.show_multiple_gen_paths(tracked_paths)
                
            vis.show_stats(IO.load_stats(args.stats))


if __name__ == '__main__':
    main()
