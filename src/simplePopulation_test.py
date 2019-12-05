import pybullet as p
import time
import numpy as np
import random


def distance(x1, x2, y1, y2):
    return ((x2 - x1)**2 + (y2 - y1)**2)**0.5


def generate_rand_genome(num_objects, mutation_factor=1):
    genome = []
    for obj in range(num_objects):
        # genomechoose size power and velocity for current box randomly
        sizeX, sizeY, sizeZ = np.random.rand(3) / 2 * mutation_factor + 0.4
        # number of power/ velocity has to correspond to number of links (num_objects-1)
        velocity_z, velocity_y = ((np.random.rand() * 2 - 1) * mutation_factor) * 10, ((np.random.rand() * 2 - 1) * mutation_factor) * 10
        power_z, power_y = np.random.rand() * 5 * mutation_factor + 5, np.random.rand() * 5 * mutation_factor + 5
        # genome[0] corresponds to first box etc.
        sphere_radius = sizeZ / 2
        genome.append([sizeX, sizeY, sizeZ, sphere_radius, velocity_z, power_z, velocity_y, power_y])
    return genome


def generate_visual_body(num_objs, genome):
    # declaration/init of parameters for multibody
    mass = 1
    visualShapeId = -1
    basePosition = [0, 0, 4]
    link_Masses = []                            # [1, 1]
    linkCollisionShapeIndices = []              # [colBoxId2, colBoxId3]
    linkVisualShapeIndices = []                 # [-1, -1]
    # set positions to connect objects
    linkPositions = []                          # [[0, 0, genome['sizes'][0]['sZ'] + genome['sizes'][1]['sZ']],
                                                # [0, 0, genome['sizes'][1]['sZ'] + genome['sizes'][2]['sZ']]]
    linkOrientations = []                       # [[0, 0, 0, 1], [0, 0, 0, 1]]
    linkInertialFramePositions = []             # [[0, 0, 0], [0, 0, 0]]
    linkInertialFrameOrientations = []          # [[0, 0, 0, 1], [0, 0, 0, 1]]
    indices = []                                # [0, 1]
    jointTypes = []                             # [p.JOINT_REVOLUTE, p.JOINT_REVOLUTE]
    axis = []                                   # [[0, 0, 1], [0, 0, 1]]

    box_ids = []
    for obj in range(num_objs):
        assert [gene for gene in genome[obj]]
        # create collision shapes for the objects
        box_ids.append(p.createCollisionShape(p.GEOM_BOX,
                                              halfExtents=[genome[obj][0], genome[obj][1], genome[obj][2]]))  # [sizeX, sizeY, sizeZ]
        if(obj < num_obj-1)

        # set link and joint parameters for box (no link/joint for the first box)
        if (obj > 0):
            # set links for joint on z axis
            link_Masses.append(1)                                                   # [1, 1]
            linkCollisionShapeIndices.append(box_ids[obj])                          # [colBoxId2, colBoxId3]
            linkVisualShapeIndices.append(-1)                                       # [-1, -1]
            # set positions to connect objects
            linkPositions.append([0, 0, genome[obj - 1][2] + genome[obj][2]])       # [[0, 0, sizeZ of 1. box + sizeZ of 2. box], [0, 0, sizeZ of 2. box + sizeZ of 3. box ]]
            linkOrientations.append([0, 0, 0, 1])                                   # [[0, 0, 0, 1], [0, 0, 0, 1]]
            linkInertialFramePositions.append([0, 0, 0])                            # [[0, 0, 0], [0, 0, 0]]
            linkInertialFrameOrientations.append([0, 0, 0, 1])                      # [[0, 0, 0, 1], [0, 0, 0, 1]]
            indices.append(obj - 1)                                                 # [0, 1]
            jointTypes.append(p.JOINT_REVOLUTE)                                     # [p.JOINT_REVOLUTE, p.JOINT_REVOLUTE]
            axis.append([0, 0, 1])

    # link obj 2 to obj 1 and obj 3 to obj 2
    # create creature
    boxID = p.createMultiBody(mass,
                              box_ids[0],
                              visualShapeId,
                              basePosition,
                              baseOrientation=[0, 1, 0, 1],
                              linkMasses=link_Masses,
                              linkCollisionShapeIndices=linkCollisionShapeIndices,
                              linkVisualShapeIndices=linkVisualShapeIndices,
                              linkPositions=linkPositions,
                              linkOrientations=linkOrientations,
                              linkInertialFramePositions=linkInertialFramePositions,
                              linkInertialFrameOrientations=linkInertialFrameOrientations,
                              linkParentIndices=indices,
                              linkJointTypes=jointTypes,
                              linkJointAxis=axis)

    p.changeDynamics(boxID,
                     -1,
                     spinningFriction=0.001,
                     rollingFriction=0.001,
                     linearDamping=0.0)

    for joint in range(int(p.getNumJoints(boxID)/2)):
        p.setJointMotorControl2(boxID,
                                joint,
                                p.VELOCITY_CONTROL,
                                targetVelocity=genome[joint][3],
                                force=genome[joint][4])

    return boxID, basePosition


def create_individual(num_objects=3, genome=[]):
    if not genome:
        # select size and power for each obj randomly
        genome = generate_rand_genome(num_objects)
    # create physical body of individual and get its ID and start position in world
    individual_id, base_position = generate_visual_body(num_objects, genome)

    return individual_id, genome, base_position


def disable_collision(pop):
    for idx, individual in enumerate(pop[:-1]): # from first to second last
        for other_individual in pop[idx + 1:]: # from next (relative to above) to end

            # pair all link indices and disable collision (num of joints = num of links)
            for joint in range(-1, p.getNumJoints(individual[0])): # all joints to ...
                for other_joint in range(-1, p.getNumJoints(other_individual[0])): # ... all other joints
                    p.setCollisionFilterPair(individual[0], other_individual[0], joint, other_joint, enableCollision=0)


# sort population along with distances
def sort(pop, dist):
    # list of indices of sorted distances
    indices_sorted = np.argsort(dist)[::-1] #[:len(dist)]
    # sort population and distances with help of indices_sorted
    pop_sorted = [pop[i] for i in indices_sorted]
    dist_sorted = [dist[i] for i in indices_sorted]

    return pop_sorted, dist_sorted


def selection(pop):
    # want to keep 50% of the pop
    num_survivors = int(0.5 * len(pop))
    # calcul of select and k and value of coeff
    # from "Concepts fondamentaux des algorithmes évolutionnistes"
    # by Jean-Baptiste Mouret
    coeff = 1.1
    k = coeff ** (num_survivors + 1) - 1
    survivor_ids = list(np.round(num_survivors - (num_survivors / np.log(k + 1)) *
                            np.log(k * np.random.rand(num_survivors) + 1)))

    survivor_ids += survivor_ids # to ensure population length

    parents = []
    for this_survivor_id in survivor_ids:
        # pair each survivor with one randomly chosen survivor from the difference-set
        # between the selected survivor and the others
        not_this_survivor_ids = np.setdiff1d(survivor_ids, this_survivor_id)
        not_this_survivor_id = int(random.choice(not_this_survivor_ids))
        parents.append((pop[int(this_survivor_id)], pop[not_this_survivor_id]))

    return parents


# define limit function
def limit(mid, diff, a):
    limit_1 = np.asarray(mid) + np.asarray(diff) / 2 + a * np.asarray(diff)
    limit_2 = np.asarray(mid) - np.asarray(diff) / 2 - a * np.asarray(diff)
    # determine upper and lower bound
    limits_sorted = np.sort([limit_1, limit_2], axis=0)
    lower_bounds = np.array(limits_sorted[0])
    higher_bounds = np.array(limits_sorted[1])

    lower_bounds[lower_bounds < 0] = 0

    return lower_bounds, higher_bounds


def randoms_between(lows, highs):
    lows = np.array(lows)
    highs = np.array(highs)
    # abs difference to shift random distribution that is natively between 0 and 1
    # you modify the range of values by multiplying and shift the lowest values by adding
    # Example: if you want random values between 1 and 3 you say: rand * 2 + 1, etc

    # array of random values between 0 and 1
    rand_values = np.random.rand(len(highs))  # len(high) == len(low)
    differences = highs - lows
    # random values between lower bound of limits and bound of limits + abs_difference
    rand_in_limits = (rand_values * differences) + lows

    return rand_in_limits


####### INPUT #######
# p1, p2 each is list of lists: [box1, box2,..., boxn]
# where each box consists of [x, y, z, velocity, power]
# a is alpha = 0.5
####### OUTPUT #######
# genome for individual [[x1, y1, z1, velo1, pow1][x2, y2, z2, velo2, pow2]...]
def generate_child_genome(p1, p2, a, mutation_prob):
    child = []
    for obj_p1, obj_p2 in zip(p1, p2):
        # get o (average of parents)and d (distance between parents)
        o = np.mean([obj_p1, obj_p2], axis=0)
        d = np.asarray(obj_p1) - np.asarray(obj_p2)
        # compute limits in both directions
        # (calcul from p.39 of "Concepts fondamentaux des algorithmes évolutionnistes" by Jean-Baptiste Mouret)
        low_bounds, high_bounds = limit(o, d, a)
        child.append(randoms_between(low_bounds, high_bounds))
    # mutate genes with a chance of e.g. 2% -> replace certain gene with a new random value

    child = np.asarray(child)
    mutate = np.random.random(child.shape) < mutation_prob
    if np.any(mutate):
        rands = np.asarray(generate_rand_genome(len(child)))
        child[mutate] = rands[mutate]
    child = list(child)
    return child


def crossing(parents, mutation_prob):
    next_generation = []
    # save parent couple (only ids) for each individual
    all_parents = []
    alpha = 0.5
    num_limbs = len(parents[0][0][1])
    for couple in parents:
        genome_child = generate_child_genome(couple[0][1], couple[1][1], alpha, mutation_prob=mutation_prob)
        next_generation.append(create_individual(num_objects=num_limbs, genome=genome_child))
        # contains [id, genome, basePosisiton]
        all_parents.append((couple[0][0], couple[1][0]))
    return next_generation, all_parents


def input_manually():
    # USER INPUT
    try:
        num_generations = int(input('How many generations?'))
        pop_size = int(input('How many individuals shall a population contain?'))
        limbs_num = int(input('How many limbs(boxes) shall an individual have?'))
        if pop_size % 2 == 1:
            pop_size += 1
    except ValueError:
        print("Not a number")


def simulate_evolution(num_generations, pop_size, mutation_prob, limbs_num=3):
    # inits for simulation
    sim_time = 10 #s
    dt = 1. / 240.
    p.connect(p.DIRECT) # p.GUI to display graphical output
    p.createCollisionShape(p.GEOM_PLANE)
    p.createMultiBody(0, 0)
    p.setGravity(0, 0, -9.81)
    assert(p.isConnected())

    initial_population = [create_individual(limbs_num) for i in range(pop_size)]
    assert(len(initial_population) == pop_size and all(ind is not None for ind in initial_population))
    disable_collision(initial_population)

    # first generation
    generations = []
    generations.append(initial_population)

    curr_population = initial_population
    all_parent_ids = []
    # first generation has no parents
    all_parent_ids.append([])
    all_distances = []
    for i in range(num_generations):
        #simulation
        for j in range(int(sim_time / dt)):
            p.stepSimulation()
            #time.sleep(dt)

        # figure out the fitness for each individual
        distances = []
        print('generation {}'.format(i))
        for individual in curr_population:
            endPos = p.getBasePositionAndOrientation(individual[0])[0]
            basePosition = individual[2]
            distances.append(distance(endPos[0], basePosition[0], endPos[1], basePosition[1])) # distance(x1, x2, y1, y2)
        curr_population, distances = sort(curr_population, distances)
        all_distances.append(distances)

        # don't do selection and crossing for the last generation
        if i < num_generations - 1:
            parents_selected = selection(curr_population)

            # removing visual bodies of pop from simulation
            [p.removeBody(ind[0]) for ind in curr_population]

            curr_population, parent_ids = crossing(parents_selected, mutation_prob=mutation_prob)
            all_parent_ids.append(parent_ids)
            disable_collision(curr_population)

            generations.append(curr_population)
    return generations, all_parent_ids, all_distances
