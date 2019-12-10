from src.simulation import simulate_pop, reset_simulation
import src.evolution as evo
import src.stats as st

motion_pattern_duration = 2  # in seconds
fps = 240  # frames per second
move_steps = int(motion_pattern_duration * fps)

show_best = 0
duration_per_simulation_in_sec = 10
generations = 3
individuals = 20
stats = []
best = 0

all_gene_pools = []

gene_pool = evo.make_random_gene_pool(num_inds=individuals, move_steps=move_steps)

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
    reset_simulation(sim_id)

st.save_stats(stats)
evo.save_gene_pool(all_gene_pools, filename='src/results/latest_gene_pool_over_generations.pkl')
evo.save_gene_pool(gene_pool)

if show_best:
    # show best parent
    best = st.load_stats()[-1, -1]
    gene_pool = evo.load_gene_pool()
    simulate_pop([gene_pool[int(best)]], fps=fps, duration_in_sec=-1, direct=False)
