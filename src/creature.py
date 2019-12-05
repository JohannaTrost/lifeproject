import pybullet as p
import numpy as np


def make_pop(num_inds, element_size, move_steps):
    ind_list = []

    for ind in range(num_inds):
        ind_list.append(list(make_crappy_multibody(element_size, move_steps)))

    return ind_list


def make_crappy_multibody(element_size, move_steps):
    col_box_id = p.createCollisionShape(p.GEOM_BOX,
                                        halfExtents=[element_size,
                                                     element_size,
                                                     element_size])

    vis_box_id = p.createVisualShape(p.GEOM_BOX,
                                     halfExtents=[element_size,
                                                     element_size,
                                                     element_size],
                                     rgbaColor=[0.53, 0.41, 0.8, 255])

    vis_sphere_id = p.createVisualShape(p.GEOM_SPHERE, radius=element_size,
                                        rgbaColor=[0.65, 0.55, 0.85, 1])

    col_sphere_id = p.createCollisionShape(
        p.GEOM_SPHERE, radius=element_size)

    limb_dict = {'left_arm_y':10, 'right_arm_y':13,
                 'left_arm_z':11, 'right_arm_z':14,
                 'left_leg_y':4, 'right_leg_y':7,
                 'left_leg_z':5, 'right_leg_z':8,
                 'hip_y':2, 'hip_x':1}

    link_masses = []
    link_col_shape_ids = []
    link_vis_shape_ids = []
    link_pos = []
    link_ori = []
    link_iner_frame_pos = []
    link_iner_frame_ori = []
    inds = []
    joint_types = []
    axis = []

    # head -> chest
    link_masses.append(1)
    link_col_shape_ids.append(col_box_id)
    link_vis_shape_ids.append(vis_box_id)
    link_pos.append([0, element_size * 2, 0])
    link_ori.append([0, 0, 0, 1])
    link_iner_frame_pos.append([0, 0, 0])
    link_iner_frame_ori.append([0, 0, 0, 1])
    inds.append(0)
    joint_types.append(p.JOINT_FIXED)
    axis.append([0, 0, 1])

    # chest -> taile
    link_masses.append(1)
    link_col_shape_ids.append(col_sphere_id)
    link_vis_shape_ids.append(vis_sphere_id)
    link_pos.append([0, element_size * 2, 0])
    link_ori.append([1, 0, 0, 1])
    link_iner_frame_pos.append([0, 0, 0])
    link_iner_frame_ori.append([0, 0, 0, 1])
    inds.append(1)
    joint_types.append(p.JOINT_REVOLUTE)
    axis.append([0, 0, 1])

    # taile -> taile
    link_masses.append(1)
    link_col_shape_ids.append(col_sphere_id)
    link_vis_shape_ids.append(vis_sphere_id)
    link_pos.append([0, 0, 0])
    link_ori.append([-1, 0, 0, 1])
    link_iner_frame_pos.append([0, 0, 0])
    link_iner_frame_ori.append([0, 0, 0, 1])
    inds.append(2)
    joint_types.append(p.JOINT_REVOLUTE)
    axis.append([0, 0, 1])

    # taile -> hip
    link_masses.append(1)
    link_col_shape_ids.append(col_box_id)
    link_vis_shape_ids.append(vis_box_id)
    link_pos.append([0, element_size * 2, 0])
    link_ori.append([0, 0, 0, 1])
    link_iner_frame_pos.append([0, 0, 0])
    link_iner_frame_ori.append([0, 0, 0, 1])
    inds.append(3)
    joint_types.append(p.JOINT_FIXED)
    axis.append([0, 0, 1])

    # chest -> left arm
    link_masses.append(1)
    link_col_shape_ids.append(col_sphere_id)
    link_vis_shape_ids.append(vis_sphere_id)
    link_pos.append([element_size * 2, 0, 0])
    link_ori.append([0, 0, 0, 1])
    link_iner_frame_pos.append([0, 0, 0])
    link_iner_frame_ori.append([0, 0, 0, 1])
    inds.append(1)
    joint_types.append(p.JOINT_REVOLUTE)
    axis.append([0, 0, 1])

    # chest -> right arm
    link_masses.append(1)
    link_col_shape_ids.append(col_sphere_id)
    link_vis_shape_ids.append(vis_sphere_id)
    link_pos.append([-element_size * 2, 0, 0])
    link_ori.append([0, 0, 0, -1])
    link_iner_frame_pos.append([0, 0, 0])
    link_iner_frame_ori.append([0, 0, 0, 1])
    inds.append(1)
    joint_types.append(p.JOINT_REVOLUTE)
    axis.append([0, 0, 1])

    # left arm -> left hand
    link_masses.append(1)
    link_col_shape_ids.append(col_sphere_id)
    link_vis_shape_ids.append(vis_sphere_id)
    link_pos.append([0, 0, 0])
    link_ori.append([1, 0, 0, 1])
    link_iner_frame_pos.append([0, 0, 0])
    link_iner_frame_ori.append([0, 0, 0, 1])
    inds.append(5)
    joint_types.append(p.JOINT_REVOLUTE)
    axis.append([0, 0, 1])

    # right arm -> right hand
    link_masses.append(1)
    link_col_shape_ids.append(col_sphere_id)
    link_vis_shape_ids.append(vis_sphere_id)
    link_pos.append([0, 0, 0])
    link_ori.append([1, 0, 0, -1])
    link_iner_frame_pos.append([0, 0, 0])
    link_iner_frame_ori.append([0, 0, 0, 1])
    inds.append(6)
    joint_types.append(p.JOINT_REVOLUTE)
    axis.append([0, 0, 1])

    # hip -> left leg
    link_masses.append(1)
    link_col_shape_ids.append(col_sphere_id)
    link_vis_shape_ids.append(vis_sphere_id)
    link_pos.append([element_size * 2, 0, 0])
    link_ori.append([0, 0, 0, 1])
    link_iner_frame_pos.append([0, 0, 0])
    link_iner_frame_ori.append([0, 0, 0, 1])
    inds.append(4)
    joint_types.append(p.JOINT_REVOLUTE)
    axis.append([0, 0, 1])

    # hip -> right leg
    link_masses.append(1)
    link_col_shape_ids.append(col_sphere_id)
    link_vis_shape_ids.append(vis_sphere_id)
    link_pos.append([-element_size * 2, 0, 0])
    link_ori.append([0, 0, 0, -1])
    link_iner_frame_pos.append([0, 0, 0])
    link_iner_frame_ori.append([0, 0, 0, 1])
    inds.append(4)
    joint_types.append(p.JOINT_REVOLUTE)
    axis.append([0, 0, 1])

    # left leg -> left foot
    link_masses.append(1)
    link_col_shape_ids.append(col_sphere_id)
    link_vis_shape_ids.append(vis_sphere_id)
    link_pos.append([0, 0, 0])
    link_ori.append([1, 0, 0, 1])
    link_iner_frame_pos.append([0, 0, 0])
    link_iner_frame_ori.append([0, 0, 0, 1])
    inds.append(9)
    joint_types.append(p.JOINT_REVOLUTE)
    axis.append([0, 0, 1])

    # right leg -> right foot
    link_masses.append(1)
    link_col_shape_ids.append(col_sphere_id)
    link_vis_shape_ids.append(vis_sphere_id)
    link_pos.append([0, 0, 0])
    link_ori.append([1, 0, 0, -1])
    link_iner_frame_pos.append([0, 0, 0])
    link_iner_frame_ori.append([0, 0, 0, 1])
    inds.append(10)
    joint_types.append(p.JOINT_REVOLUTE)
    axis.append([0, 0, 1])

    # left hand
    link_masses.append(1)
    link_col_shape_ids.append(col_box_id)
    link_vis_shape_ids.append(vis_box_id)
    link_pos.append([element_size * 2, 0, 0])
    link_ori.append([0, 0, 0, 1])
    link_iner_frame_pos.append([0, 0, 0])
    link_iner_frame_ori.append([0, 0, 0, 1])
    inds.append(7)
    joint_types.append(p.JOINT_FIXED)
    axis.append([0, 0, 1])

    # right hand
    link_masses.append(1)
    link_col_shape_ids.append(col_box_id)
    link_vis_shape_ids.append(vis_box_id)
    link_pos.append([-element_size * 2, 0, 0])
    link_ori.append([0, 0, 0, 1])
    link_iner_frame_pos.append([0, 0, 0])
    link_iner_frame_ori.append([0, 0, 0, 1])
    inds.append(8)
    joint_types.append(p.JOINT_FIXED)
    axis.append([0, 0, 1])

    # left foot
    link_masses.append(1)
    link_col_shape_ids.append(col_box_id)
    link_vis_shape_ids.append(vis_box_id)
    link_pos.append([element_size * 2, 0, 0])
    link_ori.append([0, 0, 0, 1])
    link_iner_frame_pos.append([0, 0, 0])
    link_iner_frame_ori.append([0, 0, 0, 1])
    inds.append(11)
    joint_types.append(p.JOINT_FIXED)
    axis.append([0, 0, 1])

    # right foot
    link_masses.append(1)
    link_col_shape_ids.append(col_box_id)
    link_vis_shape_ids.append(vis_box_id)
    link_pos.append([-element_size * 2, 0, 0])
    link_ori.append([0, 0, 0, 1])
    link_iner_frame_pos.append([0, 0, 0])
    link_iner_frame_ori.append([0, 0, 0, 1])
    inds.append(12)
    joint_types.append(p.JOINT_FIXED)
    axis.append([0, 0, 1])

    return p.createMultiBody(1,
                              col_sphere_id,
                              vis_sphere_id,
                              [0, 0, 1],
                              [0, 0, 0, 1],
                              linkMasses=link_masses,
                              linkCollisionShapeIndices=link_col_shape_ids,
                              linkVisualShapeIndices=link_vis_shape_ids,
                              linkPositions=link_pos,
                              linkOrientations=link_ori,
                              linkInertialFramePositions=link_iner_frame_pos,
                              linkInertialFrameOrientations=link_iner_frame_ori,
                              linkParentIndices=inds,
                              linkJointTypes=joint_types,
                              linkJointAxis=axis,
                              useMaximalCoordinates=True), limb_dict, make_move_pattern(move_steps, limb_dict)


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
