import pybullet as p
import time
from src.creature import make_pop, move_limb
from src.simplePopulation_test import disable_collision

p.connect(p.GUI)
p.createMultiBody(0, p.createCollisionShape(p.GEOM_PLANE))

p.setGravity(0, 0, -9.81)
p.setRealTimeSimulation(0)
size_pattern = 240

num_individuals = 1

pop = make_pop(num_individuals, 0.25, size_pattern)
disable_collision(pop)
dt = 1. / 240.

# pos = 0.
# pos_diff = 0.1

pattern_counter = 0

while p.isConnected(0):
    p.stepSimulation()

    time.sleep(dt)
    # pos += pos_diff

    # if pos > np.pi or pos < -np.pi:
    #     pos_diff *= -1

    for ind in pop:
        move_limb(ind[0], ind[1]['left_leg_y'], ind[2]['left_leg_y'][pattern_counter], force=60)
        move_limb(ind[0], ind[1]['left_leg_z'], ind[2]['left_leg_z'][pattern_counter], force=60)

        move_limb(ind[0], ind[1]['right_leg_y'], ind[2]['right_leg_y'][pattern_counter], force=60)
        move_limb(ind[0], ind[1]['right_leg_z'], ind[2]['right_leg_z'][pattern_counter], force=60)

        move_limb(ind[0], ind[1]['left_arm_y'], ind[2]['left_arm_y'][pattern_counter], force=60)
        move_limb(ind[0], ind[1]['left_arm_z'], ind[2]['left_arm_z'][pattern_counter], force=60)

        move_limb(ind[0], ind[1]['right_arm_y'], ind[2]['right_arm_y'][pattern_counter], force=60)
        move_limb(ind[0], ind[1]['right_arm_z'], ind[2]['right_arm_z'][pattern_counter], force=60)

        move_limb(ind[0], ind[1]['hip_y'], ind[2]['hip_y'][pattern_counter], force=60)
        move_limb(ind[0], ind[1]['hip_x'], ind[2]['hip_x'][pattern_counter], force=60)

    pattern_counter += 1

    if pattern_counter >= size_pattern:
        pattern_counter = 0