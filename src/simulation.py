import pybullet as p
from src.individual import make_random_genome, move_individual
import time
import numpy as np
from matplotlib import cm

def get_random_color(colormap='viridis'):
    cmap = cm.get_cmap(colormap, 255)(np.linspace(0, 1, 255))
    return cmap[np.random.random_integers(0, 254, 1)].tolist()[0]


def simulate_pop(genomes, fps=240, duration_in_sec=-1, direct=False):
    if direct:
        sim_id = make_sim_env('direct')
    else:
        sim_id = make_sim_env('gui')

    pop = [genome2simulation(genome) for genome in genomes]
    disable_collision(pop)

    # simulate
    duration_steps = fps * duration_in_sec
    if duration_steps < 0:
        duration_steps = np.Inf

    step = 0
    while p.isConnected(sim_id) and step < duration_steps:
        p.stepSimulation()
        for indiv, genome in zip(pop, genomes):
            move_individual(indiv, genome, step)
        time.sleep(1. / fps)
        step += 1
    return pop, sim_id

def make_sim_env(gui_or_direct):

    if gui_or_direct.lower() == 'gui':
        sim_id = p.connect(p.GUI)
    else:
        sim_id = p.connect(p.DIRECT)

    p.setGravity(0, 0, -9.81)
    p.createMultiBody(0, p.createCollisionShape(p.GEOM_PLANE))
    return sim_id


def _make_mb_dict():
    return {'link_masses': [1] * 16,
            'link_col_shape_ids': [],
            'link_vis_shape_ids': [],
            'link_pos': [],
            'link_ori': [[0, 0, 0, 1], [1, 0, 0, 1], [-1, 0, 0, 1], [0, 0, 0, 1], [0, 0, 0, 1], [0, 0, 0, -1],
                         [1, 0, 0, 1],
                         [1, 0, 0, -1], [0, 0, 0, 1], [0, 0, 0, -1], [1, 0, 0, 1], [1, 0, 0, -1], [0, 0, 0, 1],
                         [0, 0, 0, 1],
                         [0, 0, 0, 1], [0, 0, 0, 1]],
            'link_iner_frame_pos': [[0, 0, 0]] * 16,
            'link_iner_frame_ori': [[0, 0, 0, 1]] * 16,
            'inds': [0, 1, 2, 3, 1, 1, 5, 6, 4, 4, 9, 10, 7, 8, 11, 12],
            'joint_types': [p.JOINT_FIXED, p.JOINT_REVOLUTE, p.JOINT_REVOLUTE, p.JOINT_FIXED, p.JOINT_REVOLUTE,
                            p.JOINT_REVOLUTE, p.JOINT_REVOLUTE, p.JOINT_REVOLUTE, p.JOINT_REVOLUTE, p.JOINT_REVOLUTE,
                            p.JOINT_REVOLUTE, p.JOINT_REVOLUTE, p.JOINT_FIXED, p.JOINT_FIXED, p.JOINT_FIXED,
                            p.JOINT_FIXED],
            'axis': [[0, 0, 1]] * 16}


def _genome2multi_body_data(genome=({}, {})):
    if not bool(genome[0]):
        genome = make_random_genome()

    col_box_ids = {}
    vis_box_ids = {}
    box_color = get_random_color()
    sphere_color = [sphere_color * 0.5 for sphere_color in box_color[:-1]] + [1]
    # generate visual/ collision shape ids for objects with 'new' sizes
    for limb in genome[0].keys():
        col_box_ids[limb] = p.createCollisionShape(p.GEOM_BOX, halfExtents=genome[0][limb])
        vis_box_ids[limb] = p.createVisualShape(p.GEOM_BOX, halfExtents=genome[0][limb],
                                                rgbaColor=box_color)

    # for all spheres connected to the chest take z value of chest box as radius
    vis_sphere_id_chest = p.createVisualShape(p.GEOM_SPHERE, radius=genome[0]['chest'][2],
                                              rgbaColor=sphere_color)
    col_sphere_id_chest = p.createCollisionShape(p.GEOM_SPHERE, radius=genome[0]['chest'][2])
    # analog for hip
    vis_sphere_id_hip = p.createVisualShape(p.GEOM_SPHERE, radius=genome[0]['hip'][2], rgbaColor=sphere_color)
    col_sphere_id_hip = p.createCollisionShape(p.GEOM_SPHERE, radius=genome[0]['hip'][2])

    # fill multi body parameter values
    mb = _make_mb_dict()
    mb['link_col_shape_ids'] = [col_box_ids['chest'],
                                col_sphere_id_chest,
                                col_sphere_id_chest,
                                col_box_ids['hip']] + \
                               [col_sphere_id_chest] * 4 + \
                               [col_sphere_id_hip] * 4 + \
                               [col_box_ids['left_hand'],
                                col_box_ids['right_hand'],
                                col_box_ids['left_foot'],
                                col_box_ids['right_foot']]

    mb['link_vis_shape_ids'] = [vis_box_ids['chest'],
                                vis_sphere_id_chest,
                                vis_sphere_id_chest,
                                vis_box_ids['hip']] + \
                               [vis_sphere_id_chest] * 4 + \
                               [vis_sphere_id_hip] * 4 + \
                               [vis_box_ids['left_hand'],
                                vis_box_ids['right_hand'],
                                vis_box_ids['left_foot'],
                                vis_box_ids['right_foot']]

    mb['link_pos'] = [[0, genome[0]['chest'][1] + genome[0]['chest'][2], 0],
                      [0, genome[0]['chest'][1] + genome[0]['chest'][2], 0],
                      [0, 0, 0],
                      [0, genome[0]['chest'][2] + genome[0]['hip'][1], 0],
                      [-genome[0]['chest'][0] - genome[0]['chest'][2], 0, 0],
                      [genome[0]['chest'][0] + genome[0]['chest'][2], 0, 0],
                      [0, 0, 0],
                      [0, 0, 0],
                      [-genome[0]['hip'][0] - genome[0]['hip'][2], 0, 0],
                      [genome[0]['hip'][0] + genome[0]['hip'][2], 0, 0],
                      [0, 0, 0],
                      [0, 0, 0],
                      [-genome[0]['left_hand'][0] - genome[0]['chest'][2], 0, 0],
                      [genome[0]['right_hand'][0] + genome[0]['chest'][2], 0, 0],
                      [-genome[0]['left_foot'][0] - genome[0]['hip'][2], 0, 0],
                      [genome[0]['right_foot'][0] + genome[0]['hip'][2], 0, 0],
                      ]

    return mb, col_sphere_id_chest, vis_sphere_id_chest


def genome2simulation(genome=({}, {})):
    if not bool(genome[0]):
        mb_data = _genome2multi_body_data()
    else:
        mb_data = _genome2multi_body_data(genome)

    mb = mb_data[0]

    return p.createMultiBody(1,
                             mb_data[1],
                             mb_data[2],
                             [0, 0, 2],
                             [0, 0, 0, 1],
                             linkMasses=mb['link_masses'],
                             linkCollisionShapeIndices=mb['link_col_shape_ids'],
                             linkVisualShapeIndices=mb['link_vis_shape_ids'],
                             linkPositions=mb['link_pos'],
                             linkOrientations=mb['link_ori'],
                             linkInertialFramePositions=mb['link_iner_frame_pos'],
                             linkInertialFrameOrientations=mb['link_iner_frame_ori'],
                             linkParentIndices=mb['inds'],
                             linkJointTypes=mb['joint_types'],
                             linkJointAxis=mb['axis'],
                             useMaximalCoordinates=False)


def disable_collision(pop):
    for idx, individual in enumerate(pop[:-1]): # from first to second last
        for other_individual in pop[idx + 1:]: # from next (relative to above) to end

            # pair all link indices and disable collision (num of joints = num of links)
            for joint in range(-1, p.getNumJoints(individual)): # all joints to ...
                for other_joint in range(-1, p.getNumJoints(other_individual)): # ... all other joints
                    p.setCollisionFilterPair(individual, other_individual, joint, other_joint, 0)
