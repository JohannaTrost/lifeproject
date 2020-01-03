import os
from datetime import datetime
import pickle
import numpy as np
from src.evolution import _make_random_gene_pool
from psutil import cpu_count
import json


def convert_some_args(args):
    # ensure arguments have certain formats and convert defaults into meaningful parameters

    # use all available CPU cores of -1
    if args.cores == -1:
        args.cores = cpu_count(logical=False)

    # check whether generation and duration was parsed - this is necessary to forward updated values to the evolution
    # configuration
    gen_was_none, dur_was_none = False, False

    # default values have to be created this way because in visualization mode duration should be passed without
    # overwriting the config and in case the user wants to continue evolving for some generations, the argument needs
    # to be passed to the config
    if args.generations is None:
        args.generations = 10
        gen_was_none = True

    if args.duration is None:
        args.duration = 10
        dur_was_none = True

    # get parent directory for storing simulation data
    parent_dir = return_parent_path(args)

    # try to load existing evolution file - if it does not exist or cannot be read make default
    try:
        evo_config = read_evo_config(parent_dir + 'evo_config.json')
        print('Using precomputed evolution configuration: {}'.format(parent_dir + 'evo_config.json'))

        # pass updated arguments to evolution configuration
        if not gen_was_none and not args.visualize:
            evo_config['simulation']['generations'] = args.generations
        else:
            args.generations = evo_config['simulation']['generations']

        if not dur_was_none and not args.visualize:
            evo_config['simulation']['duration'] = args.duration
        elif dur_was_none:
            args.duration = evo_config['simulation']['duration']

    except OSError:
        print('No configuration found. Creating new default evolution.')
        evo_config = make_default_evo_config()

        # pass arguments to evolution configuration
        evo_config['simulation']['generations'] = args.generations
        evo_config['simulation']['individuals'] = args.individuals
        evo_config['simulation']['duration'] = args.duration

    # define result paths
    args.stats = parent_dir + 'stats.csv'
    args.fitness = parent_dir + 'fitness.csv'
    args.tracker = parent_dir + 'tracker.pkl'

    # if parent dir empty or overwrite initialize new evolution
    if len(os.listdir(parent_dir)) == 0 or args.overwrite:
        args.gene_pool_file = None
        args.generation = 0
    else:

        # if desired find last generation
        if args.generation == -1:
            # if no generation file present initialize new evolution
            if any(['gen_' in f for f in os.listdir(parent_dir)]):
                args.generation = find_latest_gen(parent_dir)
                args.gene_pool_file = parent_dir + 'gen_' + str(args.generation) + '.pkl'
            else:
                args.gene_pool_file = None
                args.generation = 0

        # otherwise take generation specified
        else:
            args.gene_pool_file = parent_dir + 'gen_' + str(args.generation) + '.pkl'

    # make sure evolution continues at correct generation
    if args.generation > 0 and not args.visualize:
        args.generation += 1
        evo_config['simulation']['generations'] = args.generation + args.generations

    return args, evo_config


def get_from_config(args, evo_config):
    # get initial data from parsed arguments
    gene_pool = new_gene_pool(args.gene_pool_file, evo_config)

    # in case a previous gene pool was loaded, we have to assure proper number of individuals parsing
    evo_config['simulation']['individuals'] = len(gene_pool)

    if args.overwrite:
        stats = []
        fitness = []
        tracker = []
    else:
        # if gene pool file was not defined create random gene pool
        try:
            stats = load_stats(args.stats)
            fitness = load_stats(args.fitness)
            if not args.no_tracking and args.show_stats:
                tracker = load_tracker(args.tracker)
            else:
                tracker = []
        except OSError:
            stats = []
            fitness = []
            tracker = []

    # if not results to display were found warn and exit program
    if args.visualize:
        if args.show_stats and (len(stats) < 1 or len(fitness) < 1 or (len(tracker) < 1 and not args.no_tracking)):
            print('evolution data not found in {}'.format(return_parent_path(args)))
            raise SystemExit

        # select the best or i random individuals to display
        if not args.not_only_best:
            best = int(stats[args.generation][-2])
            gene_pool = [gene_pool[best]]
        else:
            ind_sel = np.random.random_integers(0, len(gene_pool) - 1, args.individuals)
            gene_pool = [gene_pool[ind] for ind in ind_sel]

    return gene_pool, evo_config, stats, fitness, tracker, return_parent_path(args)


def new_gene_pool(gene_pool_file, evo_config):
    # create either random gene pool or load
    if not isinstance(gene_pool_file, str):
        return _make_random_gene_pool(evo_config)
    if isinstance(gene_pool_file, str):
        if gene_pool_file.lower() == 'random':
            return _make_random_gene_pool(evo_config)
        else:
            return load_gene_pool(gene_pool_file)


def return_parent_path(args):
    # returns parent folder to save data in it

    # create parent directory for simulation
    if len(args.evolution_dir) > 0:
        parent_dir = args.evolution_dir + os.path.sep
    else:
        parent_dir = os.getcwd() + os.path.sep
        if args.save_gene_pool:

            # make unique folder name
            date_time = datetime.now().strftime("%m-%d-%Y-%H-%M-%S")
            parent_dir += 'all_gene_pools_{}gen_{}ind_{}dur_' + date_time + os.path.sep
            parent_dir = parent_dir.format(args.generations, args.individuals, args.duration)
        else:
            parent_dir += 'example' + os.path.sep

    if not os.path.isdir(parent_dir):
        os.mkdir(parent_dir)

    return parent_dir


def save_gene_pool(gene_pool, filename='gen_0.pkl'):
    with open(filename, 'wb') as pkl_file:
        pickle.dump(gene_pool, pkl_file)


def load_gene_pool(filename='gen_0.pkl'):
    with open(filename, 'rb') as pkl_file:
        return pickle.load(pkl_file)


def save_stats(stats, filename='stats.csv'):
    np.savetxt(filename, stats, delimiter=',')


def load_stats(filename='stats.csv'):
    return np.loadtxt(filename, delimiter=',').tolist()


def save_tracker(tracker, filename='tracker.pkl'):
    with open(filename, 'wb') as pkl_file:
        pickle.dump(tracker, pkl_file)


def load_tracker(filename='tracker.pkl'):
    with open(filename, 'rb') as pkl_file:
        return pickle.load(pkl_file)


def find_latest_gen(save_folder_dir):
    latest_gen = 0
    for file in os.listdir(save_folder_dir):
        if 'gen_' in file:
            curr_gen = int(str(os.path.basename(file).split('gen_')[-1]).split('.pkl')[0])
            if curr_gen > latest_gen:
                latest_gen = curr_gen

    return latest_gen


def read_evo_config(filename='evo_config.json'):
    with open(filename) as json_file:
        return json.load(json_file)


def write_evo_config(evo_config, filename='evo_config.json'):
    with open(filename, 'w') as outfile:
        json.dump(evo_config, outfile)


def make_default_evo_config():
    evo_config = {'individuals': {
                                'min_box_size': 0.3,
                                'max_box_size': 1.0,
                                'random_box_size': True,
                                'symmetric': False,
                                'min_force': 100,
                                'max_force': 500,
                                'start_move_pattern_size': 240,
                                'max_move_pattern_size': None,
                                'vary_pattern_length': True,
                                'normalize_move_pattern': False
                                },
                  'simulation': {
                                'fps': 240,
                                'colormap': 'viridis'
                                },
                  'evolution':  {
                                'mutation_prob_ind': 0.05,
                                'mutation_prob_gene': 0.05,
                                'mutation_prob_feature': 0.05,
                                'alpha_limits': 0.5
                                }
                  }

    evo_config['individuals']['standard_volume'] = (evo_config['individuals']['min_box_size'] +
                                                    evo_config['individuals']['max_box_size'])**3

    return evo_config
