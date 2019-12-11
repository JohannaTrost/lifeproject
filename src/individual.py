import pybullet as p
import numpy as np


def get_dist(id_ind, sim_id):
    x = p.getBasePositionAndOrientation(id_ind, physicsClientId=sim_id)[0][0]
    y = p.getBasePositionAndOrientation(id_ind, physicsClientId=sim_id)[0][0]
    return (x ** 2 + y ** 2) ** 0.5


def _make_limb_dict():
    return {'left_arm_y': 10, 'right_arm_y': 13,
            'left_arm_z': 11, 'right_arm_z': 14,
            'left_leg_y': 4, 'right_leg_y': 7,
            'left_leg_z': 5, 'right_leg_z': 8,
            'hip_y': 2, 'hip_x': 1}


def _move_individual(obj_id, genome, move_step, sim_id):
    limb_dict = _make_limb_dict()
    for key in limb_dict.keys():
        _move_limb(obj_id, limb_dict[key], genome[1][key][move_step % genome[2]], sim_id)


def _move_limb(obj_id, limb, target_pos, sim_id, force=120):
    p.changeDynamics(obj_id, limb, lateralFriction=2, anisotropicFriction=[1, 1, 0.01], physicsClientId=sim_id)
    p.setJointMotorControl2(obj_id,
                            limb,
                            p.POSITION_CONTROL,
                            targetPosition=target_pos,
                            force=force,
                            physicsClientId=sim_id)


def _make_move_pattern(size_pattern, limb_dict):
    move_dict = {}
    for key in limb_dict.keys():
        move_dict[key] = np.random.random(size_pattern) * 2 * np.pi - np.pi
    return move_dict


def _make_size_dict():
    return {'left_hand': np.random.rand(3) / 2 + 0.4,
            'right_hand': np.random.rand(3) / 2 + 0.4,
            'left_foot': np.random.rand(3) / 2 + 0.4,
            'right_foot': np.random.rand(3) / 2 + 0.4,
            'chest': np.random.rand(3) / 2 + 0.4,
            'hip': np.random.rand(3) / 2 + 0.4,
            }


def _make_random_genome(move_steps=240):
    return _make_size_dict(), _make_move_pattern(move_steps, _make_limb_dict()), move_steps
