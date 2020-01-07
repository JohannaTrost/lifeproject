from src.simulation import simulate_multi_core
import src.evolution as evo
import src.visualize as vis
import src.IO as IO
import argparse
import numpy as np
import time


def main():
    """Main function to run the program.

    The function can be run from the command line, via

    ``python simulate_evolution.py <args>``

    .. note:: There are two different modes: `simulation` and `visualization` mode.
              You can obtain an overview of all the command line arguments by typing:

              ``python simulate_evolution.py -h``

              .. code-block:: bash

                usage: simulate_evolution.py [-h] [-i INDIVIDUALS] [-g GENERATIONS]
                                     [-d DURATION] [-gc] [-e EVOLUTION_DIR]
                                     [-gen GENERATION] [-nt] [-s] [-o] [-c CORES] [-v]
                                     [-f] [-sd SLOW_DOWN_FACTOR] [-nb] [-ss]

                optional arguments:
                  -h, --help            show this help message and exit
                  -i INDIVIDUALS, --individuals INDIVIDUALS
                                        number of individuals per generation - In case
                                        visualization mode was chosen, a random set of i
                                        individuals will be chosen for displaying (default=10)
                  -g GENERATIONS, --generations GENERATIONS
                                        number of generations to be evolved (default=10)
                  -d DURATION, --duration DURATION
                                        duration of each simulation in seconds - Final fitness
                                        is obtained after that time (default=10)
                  -gc, --get_config     only create default config file and exit
                  -e EVOLUTION_DIR, --evolution_dir EVOLUTION_DIR
                                        parent directory for the evolution to be stored or
                                        loaded from (default=example)
                  -gen GENERATION, --generation GENERATION
                                        generation on which to continue evolution or
                                        generation to display if visualization mode was chosen
                                        - Set -1 for latest (default=-1)
                  -nt, --no_tracking    disable tracker for individuals
                  -s, --save_gene_pool  Save all gene pools per generation to new folder
                  -o, --overwrite       overwrite existing data
                  -c CORES, --cores CORES
                                        number of CPU cores for simulating one generation -
                                        Set to -1 for all cores (default=-1)
                  -v, --visualize       visualize results - specify evolution directory with
                                        the help of -e
                  -f, --follow_target   whether to follow the target with the GUI camera
                  -sd SLOW_DOWN_FACTOR, --slow_down_factor SLOW_DOWN_FACTOR
                                        divide GUI update speed by this value
                  -nb, --not_only_best  do not show result of best, but rather -i random
                                        individuals
                  -ss, --show_stats     whether to show statistics on the evolution - If set,
                                        statistics and not rendered individuals are shown

    `Simulation` mode refers to simulating an evolution without displaying actual individuals, whereas `visualization`
    mode renders a selected set of individuals in a GUI window for the user to inspect.
    """

    # argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--individuals', default=10, type=int,
                        help='number of individuals per generation - In case visualization mode was chosen, a random '
                             'set of i individuals will be chosen for displaying (default=10)')

    parser.add_argument('-g', '--generations', default=None, type=int,
                        help='number of generations to be evolved (default=10)')

    parser.add_argument('-d', '--duration', default=None, type=int,
                        help='duration of each simulation in seconds - Final fitness is obtained after that time '
                             '(default=10)')

    parser.add_argument('-gc', '--get_config', action='store_true',
                        help='only create default config file and exit')

    parser.add_argument('-e', '--evolution_dir', default='', type=str,
                        help='parent directory for the evolution to be stored or loaded from (default=example)')

    parser.add_argument('-gen', '--generation', default=-1, type=int,
                        help='generation on which to continue evolution or generation to display if visualization '
                             'mode was chosen - Set -1 for latest (default=-1)')

    parser.add_argument('-nt', '--no_tracking', action='store_true',
                        help='disable tracker for individuals')

    parser.add_argument('-s', '--save_gene_pool', action='store_true',
                        help='Save all gene pools per generation to new folder')

    parser.add_argument('-o', '--overwrite', action='store_true',
                        help='overwrite existing data')

    parser.add_argument('-c', '--cores', default=-1, type=int,
                        help='number of CPU cores for simulating one generation - Set to -1 for all cores (default=-1)')

    parser.add_argument('-v', '--visualize', action='store_true',
                        help='visualize results - specify evolution directory with the help of -e')

    parser.add_argument('-f', '--follow_target', action='store_true',
                        help='whether to follow the target with the GUI camera')

    parser.add_argument('-sd', '--slow_down_factor', default=1., type=float,
                        help='divide GUI update speed by this value')

    parser.add_argument('-nb', '--not_only_best', action='store_true',
                        help='do not show result of best, but rather -i random individuals ')

    parser.add_argument('-ss', '--show_stats', action='store_true',
                        help='whether to show statistics on the evolution - '
                             'If set, statistics and not rendered individuals are shown')

    # convert certain arguments
    args, evo_config = IO.convert_some_args(parser.parse_args())

    # initialize simulation
    gene_pool, evo_config, stats, fitness_over_gen, tracker_over_gen, parent_dir = IO.get_from_config(args, evo_config)

    IO.write_evo_config(evo_config, IO.return_parent_path(args) + 'evo_config.json')

    # only default config file created before exit
    if args.get_config:
        raise SystemExit

    if not args.visualize:

        # print summary
        print('Starting evolution...')
        parent_dir = IO.return_parent_path(args)

        print('Individuals: {}'.format(evo_config['simulation']['individuals']))
        print('Generations: {}'.format(evo_config['simulation']['generations']))
        print('Duration per simulation: {}s'.format(evo_config['simulation']['duration']))
        print('FPS: {}'.format(evo_config['simulation']['fps']))
        print('Number of cores utilized: {}'.format(args.cores))
        print('saving output to ' + parent_dir)
        print('')

        # iterate over generations
        for generation in range(args.generation, args.generations + args.generation):
            start = time.time()

            # obtain fitness for each individual in current generation
            fitness, tracker = simulate_multi_core(gene_pool,
                                                   evo_config,
                                                   track_individuals=(not args.no_tracking),
                                                   num_cores=args.cores)

            # sort fitness descending
            sorted_genome_ids = np.argsort(fitness)[::-1]  # from:to:instepsof
            # select best performers and transform into parent pairs
            selected = evo.selection(sorted_genome_ids)

            # collect data on population
            avg_dist = np.mean(fitness)
            best = sorted_genome_ids[0]

            stats.append([generation, avg_dist, best, fitness[best]])
            fitness_over_gen.append(fitness + [generation])
            if not args.no_tracking:
                tracker_over_gen.append(tracker)

            # if desired save state of current gene pool
            if args.save_gene_pool:
                IO.save_gene_pool(gene_pool, filename=parent_dir + 'gen_' + str(generation) + '.pkl')

                # to make sure files are present even if the evolution was interrupted
                IO.save_stats(stats, filename=parent_dir + 'stats.csv')
                IO.save_stats(fitness_over_gen, filename=parent_dir + 'fitness.csv')
                if not args.no_tracking:
                    IO.save_tracker(tracker_over_gen, filename=parent_dir + 'tracker.pkl')

            # create new gene pool by pairing selected parents
            gene_pool = evo.crossing(selected, gene_pool, evo_config)

            # print status
            print('individuals {} | generation {} | avg distance {} | duration {}s'.format(len(gene_pool), generation,
                                                                                           avg_dist,
                                                                                           round(time.time() - start)))

        # save statistics, fitness and position data and gene pool
        IO.save_stats(stats, filename=parent_dir + 'stats.csv')
        IO.save_stats(fitness_over_gen, filename=parent_dir + 'fitness.csv')
        if not args.no_tracking:
            IO.save_tracker(tracker_over_gen, filename=parent_dir + 'tracker.pkl')
        IO.save_gene_pool(gene_pool, filename=parent_dir + 'gen_' + str(
            args.generations + args.generation - 1) + '.pkl')

        print('done.')
        print('')

    else:

        if not args.show_stats:
            # show desired simulation
            pop, sim_id, tracker = vis.show_individual(gene_pool, evo_config, args)

            # show tracked paths
            vis.show_path(tracker)

        else:
            # show stats
            if not args.no_tracking:
                # show tracked paths
                tracked_paths = IO.load_tracker(args.tracker)
                vis.show_path(tracked_paths[args.generation], title='paths of gen {}'.format(args.generation))

                vis.show_multiple_gen_paths(tracked_paths)

            vis.show_stats(IO.load_stats(args.stats))


if __name__ == '__main__':
    main()
