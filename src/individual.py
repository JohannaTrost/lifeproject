import pybullet as p
import numpy as np

move_steps = 240
limb_dict = {'left_arm_y': 10, 'right_arm_y': 13,
             'left_arm_z': 11, 'right_arm_z': 14,
             'left_leg_y': 4, 'right_leg_y': 7,
             'left_leg_z': 5, 'right_leg_z': 8,
             'hip_y': 2, 'hip_x': 1}

mb = {'link_masses': [1 for i in range(16)],
      'link_col_shape_ids': [],
      'link_vis_shape_ids': [],
      'link_pos': [],
      'link_ori': [[0, 0, 0, 1], [1, 0, 0, 1], [-1, 0, 0, 1], [0, 0, 0, 1], [0, 0, 0, 1], [0, 0, 0, -1], [1, 0, 0, 1],
                   [1, 0, 0, -1], [0, 0, 0, 1], [0, 0, 0, -1], [1, 0, 0, 1], [1, 0, 0, -1], [0, 0, 0, 1], [0, 0, 0, 1],
                   [0, 0, 0, 1], [0, 0, 0, 1]],
      'link_iner_frame_pos': [[0, 0, 0] for i in range(16)],
      'link_iner_frame_ori': [[0, 0, 0, 1] for i in range(16)],
      'inds': [0, 1, 2, 3, 1, 1, 5, 6, 4, 4, 9, 10, 7, 8, 11, 12],
      'joint_types': [p.JOINT_FIXED, p.JOINT_REVOLUTE, p.JOINT_REVOLUTE, p.JOINT_FIXED, p.JOINT_REVOLUTE,
                      p.JOINT_REVOLUTE, p.JOINT_REVOLUTE, p.JOINT_REVOLUTE, p.JOINT_REVOLUTE, p.JOINT_REVOLUTE,
                      p.JOINT_REVOLUTE, p.JOINT_REVOLUTE, p.JOINT_FIXED, p.JOINT_FIXED, p.JOINT_FIXED, p.JOINT_FIXED],
      'axis': [[0, 0, 1] for i in range(16)]
      }


def move_limb(ID, limb, target_pos, force=60):
    p.changeDynamics(ID, limb, lateralFriction=2, anisotropicFriction=[1, 0.01, 0.01])
    p.setJointMotorControl2(ID,
                            limb,
                            p.POSITION_CONTROL,
                            targetPosition=target_pos,
                            force=force)


def make_move_pattern(size_pattern, limb_dict):
    move_dict = {}
    for key in limb_dict.keys():
        move_dict[key] = np.random.random(size_pattern) * 2 * np.pi - np.pi
    return move_dict


def create_individual(genome=[]):
    if not genome:
        move_dict = make_move_pattern(move_steps, limb_dict)
        box_sizes = {'left_hand': np.random.rand(3) / 2 + 0.4,
                 'right_hand': np.random.rand(3) / 2 + 0.4,
                 'left_foot': np.random.rand(3) / 2 + 0.4,
                 'right_foot': np.random.rand(3) / 2 + 0.4,
                 'chest': np.random.rand(3) / 2 + 0.4,
                 'hip': np.random.rand(3) / 2 + 0.4,
                 }
        genome = [box_sizes, move_dict]

    col_box_ids = {}
    vis_box_ids = {}
    # generate visual/ collision shape ids for objects with 'new' sizes
    for limb in genome[0]:
        col_box_ids[limb] = p.createCollisionShape(p.GEOM_BOX, halfExtents=genome[0][limb])
        vis_box_ids[limb] = p.createVisualShape(p.GEOM_BOX, halfExtents=genome[0][limb], rgbaColor=[0.53, 0.41, 0.8, 255])

    # for all spheres connected to the chest take z value of chest box as radius
    vis_sphere_id_chest = p.createVisualShape(p.GEOM_SPHERE, radius=genome[0]['chest'][2], rgbaColor=[0.65, 0.55, 0.85, 1])
    col_sphere_id_chest = p.createCollisionShape(p.GEOM_SPHERE, radius=genome[0]['chest'][2])
    # analog for hip
    vis_sphere_id_hip = p.createVisualShape(p.GEOM_SPHERE, radius=genome[0]['hip'][2], rgbaColor=[0.65, 0.55, 0.85, 1])
    col_sphere_id_hip = p.createCollisionShape(p.GEOM_SPHERE, radius=genome[0]['hip'][2])

    # fill multi body parameter values
    mb['link_col_shape_ids'] = [col_box_ids['chest'], col_sphere_id_chest, col_sphere_id_chest, col_box_ids['hip']] + \
                               [col_sphere_id_chest for i in range(4)] + [col_sphere_id_hip for i in range(4)] + \
                               [col_box_ids[i] for i in list(col_box_ids)[0:4]]
    mb['link_vis_shape_ids'] = [vis_box_ids['chest'], vis_sphere_id_chest, vis_sphere_id_chest, vis_box_ids['hip']] + \
                               [vis_sphere_id_chest for i in range(4)] + [vis_sphere_id_hip for i in range(4)] + \
                               [vis_box_ids[i] for i in list(vis_box_ids)[0:4]]
    mb['link_pos'] = [[0, box_sizes['chest'][1] * 2, 0], [0, box_sizes['chest'][1] * 2, 0], [0, 0, 0],
                      [0, box_sizes['hip'][1] * 2, 0], [box_sizes['chest'][0] * 2, 0, 0],
                      [-box_sizes['chest'][0] * 2, 0, 0], [0, 0, 0], [0, 0, 0], [box_sizes['hip'][0] * 2, 0, 0],
                      [-box_sizes['hip'][0] * 2, 0, 0], [0, 0, 0], [0, 0, 0], [box_sizes['left_hand'][0] * 2, 0, 0],
                      [-box_sizes['right_hand'][0] * 2, 0, 0], [box_sizes['left_foot'][0] * 2, 0, 0],
                      [-box_sizes['right_foot'][0] * 2, 0, 0]]

    multiId = p.createMultiBody(1,
                      col_sphere_id_chest,
                      vis_sphere_id_chest,
                      [0, 0, 1],
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
                      useMaximalCoordinates=True)

    return multiId, genome


sim_time = 10  # s
dt = 1. / 240.
p.connect(p.GUI)  # p.GUI to display graphical output
p.createCollisionShape(p.GEOM_PLANE)
p.createMultiBody(0, 0)
p.setGravity(0, 0, -9.81)
assert (p.isConnected())

multiId, genome = create_individual()

while p.isConnected():
    for j in range(int(sim_time / dt)):
        p.stepSimulation()
        #for key in limb_dict.keys():
        #    for move in move_dict[key]:
        #        move_limb(multiId, limb_dict[key], move)


