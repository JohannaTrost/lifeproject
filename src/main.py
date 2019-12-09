from src.simulation import simulate_pop
from src.evolution import make_random_pop, select, get_fitness

motion_pattern_duration = 2  # in seconds
fps = 240  # frames per second
move_steps = int(motion_pattern_duration * fps)

genomes = make_random_pop(num_inds=5, move_steps=move_steps)
pop = simulate_pop(genomes, fps=fps, duration_in_sec=2, direct=False)
best_performers = select(pop, get_fitness(pop))