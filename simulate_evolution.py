from src.simulation import simulate_pop, reset_simulation
import src.evolution as evo
import src.stats as st
import argparse
import matplotlib.pylab as plt


def main():
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
    args = parser.parse_args()

    print('Individuals : {}'.format(args.individuals))
    print('Generations: {}'.format(args.generations))
    print('Duration per simulation: {}s'.format(args.duration))
    print('FPS: {}'.format(args.fps))
    print('Motion pattern duration: {}s'.format(args.pattern_duration))
    print('')

    motion_pattern_duration = args.pattern_duration
    fps = args.fps
    move_steps = int(motion_pattern_duration * fps)

    duration_per_simulation_in_sec = args.duration
    generations = args.generations
    individuals = args.individuals

    show_best = False

    stats = []
    all_gene_pools = []

    gene_pool = evo.new_gene_pool('random', num_inds=individuals, move_steps=move_steps)  # filename to load precomputed

    all_gene_pools.append(gene_pool)

    for generation in range(generations):
        pop, sim_id = simulate_pop(gene_pool, fps=fps, duration_in_sec=duration_per_simulation_in_sec, direct=True)

        avg_dist = st.avg_dist(pop)

        print('generation {} | avg distance {}'.format(generation, avg_dist))

        # evolute
        selected = evo.selection(pop)
        best = selected[0][0]
        gene_pool = evo.crossing(selected, gene_pool)

        all_gene_pools.append(gene_pool)
        # collect data on population
        stats.append([generations, avg_dist, best])

        # reset simulation
        reset_simulation(pop, sim_id)

    plt.figure()
    plt.plot(st.load_stats()[:, 1])
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
