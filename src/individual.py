import pybullet as p
import numpy as np


def make_limb_dict():
    return {'left_arm_y': 10, 'right_arm_y': 13,
                 'left_arm_z': 11, 'right_arm_z': 14,
                 'left_leg_y': 4, 'right_leg_y': 7,
                 'left_leg_z': 5, 'right_leg_z': 8,
                 'hip_y': 2, 'hip_x': 1}


def move_individual(id, genome, move_step):
    limb_dict = make_limb_dict()
    for key in limb_dict.keys():
        move_limb(id, limb_dict[key], genome[1][key][move_step % genome[2]], force=60)


def move_limb(id, limb, target_pos, force=60):
    p.changeDynamics(id, limb, lateralFriction=2, anisotropicFriction=[1, 0.01, 0.01])
    p.setJointMotorControl2(id,
                            limb,
                            p.POSITION_CONTROL,
                            targetPosition=target_pos,
                            force=force)


def _make_move_pattern(size_pattern, limb_dict):
    move_dict = {}
    for key in limb_dict.keys():
        move_dict[key] = np.random.random(size_pattern) * 2 * np.pi - np.pi
    return move_dict


def make_random_genome(move_steps=240):
    move_dict = _make_move_pattern(move_steps, make_limb_dict())
    box_sizes = {'left_hand': np.random.rand(3) / 2 + 0.4,
                 'right_hand': np.random.rand(3) / 2 + 0.4,
                 'left_foot': np.random.rand(3) / 2 + 0.4,
                 'right_foot': np.random.rand(3) / 2 + 0.4,
                 'chest': np.random.rand(3) / 2 + 0.4,
                 'hip': np.random.rand(3) / 2 + 0.4,
                 }
    return box_sizes, move_dict, move_steps
