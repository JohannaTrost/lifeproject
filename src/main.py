from src.simulation import simulate_pop
from src.evolution import make_random_pop, selection
import pybullet as p

motion_pattern_duration = 2  # in seconds
fps = 240  # frames per second
move_steps = int(motion_pattern_duration * fps)
show_best = 1

genomes = make_random_pop(num_inds=10, move_steps=move_steps)
pop, sim_id = simulate_pop(genomes, fps=fps, duration_in_sec=10, direct=True)
new_parents = selection(pop)
p.resetSimulation(sim_id)
p.disconnect(sim_id)

if show_best:
    # show best parent
    simulate_pop([genomes[new_parents[1][0] - 1]],
                 fps=fps, duration_in_sec=-1, direct=False)