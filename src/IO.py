import os
from datetime import datetime
import pickle
import numpy as np
from src.evolution import _make_random_gene_pool
from multiprocessing import cpu_count


def convert_some_args(args):
    # ensure arguments have certain formats and convert defaults into meaningful parameters

    # use all available CPU cores of -1
    if args.cores == -1:
        args.cores = cpu_count()

    # convert to bool
    args.save_gene_pool = True if args.save_gene_pool.lower() in ['true', 'yes', '1', 'y', 't'] else False
    args.show_stats = True if args.show_stats.lower() in ['true', 'yes', '1', 'y', 't'] else False
    args.visualize = True if args.visualize.lower() in ['true', 'yes', '1', 'y', 't'] else False
    args.best_only = True if args.best_only.lower() in ['true', 'yes', '1', 'y', 't'] else False
    args.overwrite = True if args.overwrite.lower() in ['true', 'yes', '1', 'y', 't'] else False

    # get parent directory for storing simulation data
    parent_dir = return_parent_path(args)

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
            try:
                args.generation = find_latest_gen(parent_dir)
                args.gene_pool_file = parent_dir + 'gen_' + str(args.generation) + '.pkl'
            except IndexError:
                args.gene_pool_file = None
                args.generation = 0
        # otherwise take generation specified
        else:
            args.gene_pool_file = parent_dir + 'gen_' + str(args.generation) + '.pkl'

    return args


def get_from_config(args):
    # get initial data from parsed arguments
    gene_pool = new_gene_pool(args.gene_pool_file, args.individuals)

    if args.overwrite:
        stats = []
        fitness = []
        tracker = []
    else:
        # if gene pool file was not defined create random gene pool
        try:
            stats = load_stats(args.stats)
            fitness = load_stats(args.fitness)
            tracker = load_tracker(args.tracker)
        except OSError:
            stats = []
            fitness = []
            tracker = []

    # load files specified or return defaults
    if args.visualize:
        if len(stats) < 1 or len(fitness) < 1 or len(tracker) < 1:
            print('evolution data not found in {}'.format(return_parent_path(args)))
            raise SystemExit

        if args.best_only:
            best = int(stats[args.generation][-2])
            gene_pool = [gene_pool[best]]
        else:
            ind_sel = np.random.random_integers(0, len(gene_pool) - 1, args.individuals)
            gene_pool = [gene_pool[ind] for ind in ind_sel]

    return gene_pool, stats, fitness, tracker, return_parent_path(args)


def new_gene_pool(gene_pool, num_inds):
    # create either random gene pool or load
    if not isinstance(gene_pool, str):
        return _make_random_gene_pool(num_inds=num_inds)
    if isinstance(gene_pool, str):
        if gene_pool.lower() == 'random':
            return _make_random_gene_pool(num_inds=num_inds)
        else:
            return load_gene_pool(gene_pool)


def return_parent_path(args):
    # create parent directory for simulation
    if len(args.evolution_dir) > 0:
        parent_dir = args.evolution_dir + os.path.sep
    else:
        parent_dir = os.getcwd() + os.path.sep
        if args.save_gene_pool:

            date_time = datetime.now().strftime("%m-%d-%Y-%H-%M-%S")
            parent_dir += 'all_gene_pools_{}gen_{}ind_{}dur_' + date_time + os.path.sep
            parent_dir = parent_dir.format(args.generations, args.individuals, args.duration)
        else:
            parent_dir += 'example' + os.path.sep

    if not os.path.isdir(parent_dir):
        os.mkdir(parent_dir)

    return parent_dir


def save_gene_pool(gene_pool, filename='gen_0.pkl'):
    output = open(filename, 'wb')
    pickle.dump(gene_pool, output)
    output.close()


def load_gene_pool(filename='gen_0.pkl'):
    pkl_file = open(filename, 'rb')
    gene_pool = pickle.load(pkl_file)
    pkl_file.close()
    return gene_pool


def save_stats(stats, filename='stats.csv'):
    np.savetxt(filename, stats, delimiter=',')


def load_stats(filename='stats.csv'):
    return np.loadtxt(filename, delimiter=',').tolist()


def save_tracker(tracker, filename='tracker.pkl'):
    output = open(filename, 'wb')
    pickle.dump(tracker, output)
    output.close()


def load_tracker(filename='tracker.pkl'):
    pkl_file = open(filename, 'rb')
    tracker = pickle.load(pkl_file)
    pkl_file.close()
    return tracker


def find_latest_gen(save_dir):
    generations = []
    for file in os.listdir(save_dir):
        if 'gen_' in file:
            generations.append(int(os.path.basename(file).split('gen_')[-1].split('.pkl')[0]))

    return sorted(generations)[-1]

