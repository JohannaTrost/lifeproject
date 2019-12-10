from src.simulation import simulate_pop, reset_simulation
from src.evolution import make_random_gene_pool, selection, crossing
from src.stats import avg_dist, pop_stats

motion_pattern_duration = 2  # in seconds
fps = 240  # frames per second
move_steps = int(motion_pattern_duration * fps)
show_best = 1
duration_per_simulation_in_sec = 10
generations = 10
individuals = 20
stats = []

gene_pool = make_random_gene_pool(num_inds=individuals, move_steps=move_steps)

for generation in range(generations):
    pop, sim_id = simulate_pop(gene_pool, fps=fps, duration_in_sec=duration_per_simulation_in_sec, direct=True)

    print('generation {} | avg distance {}'.format(generation, avg_dist(pop)))

    # collect data on population
    stats = pop_stats(stats, pop, generation)

    # evolute
    gene_pool = crossing(selection(pop), gene_pool)

    # reset simulation
    reset_simulation(sim_id)

if show_best:
    # show best parent
    simulate_pop([gene_pool[selection(pop)[1][0]]],
                 fps=fps, duration_in_sec=-1, direct=False)
