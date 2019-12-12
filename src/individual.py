import pybullet as p
import numpy as np


def get_dist(id_ind, sim_id):
    x, y = _get_pos(id_ind, sim_id)
    return (x ** 2 + y ** 2) ** 0.5


def _compute_force(mass, num_joints, max_force=600):
    # assumes a standard mass of 1
    # scales the force according to the box size, but caps at 600

    scaled_mass = mass * max_force / (num_joints + 1) / 3

    y = 1 / ((1 / max_force) + np.exp(-scaled_mass)) - 1 / max_force
    return y


def _compute_mass(box_size, standard_volume=2.197):
    # Mass will be scaled with the volume, normalized on the standard volume.
    # The standard volume is the average volume obtained from:
    # np.random.rand(3) / 2 + 0.4, which is the starting box size. Hence this
    # box size will have a volume of (0.5 / 2 + 0.4)**3 and thus a normalized
    # mass of (0.5 / 2 + 0.4)**3 / standard_volume = 1
    if np.isscalar(box_size):  # sphere
        return 4 / 3 * np.pi * box_size**3 / standard_volume
    else:  # box
        if np.ndim(box_size) == 1:
            return np.prod(box_size * 2) / standard_volume
        else:
            return np.prod(box_size * 2, axis=1) / standard_volume


def _get_pos(id_ind, sim_id):
    x, y = p.getBasePositionAndOrientation(id_ind, physicsClientId=sim_id)[0][0:2]
    return x, y


def _make_limb_dict():
    return {'left_arm_y': 10, 'right_arm_y': 13,
            'left_arm_z': 11, 'right_arm_z': 14,
            'left_leg_y': 4, 'right_leg_y': 7,
            'left_leg_z': 5, 'right_leg_z': 8,
            'hip_y': 2, 'hip_x': 1}


def _move_individual(obj_id, genome, move_step, num_joints, sim_id):
    limb_dict = _make_limb_dict()
    for key in limb_dict.keys():
        _move_limb(obj_id, limb_dict[key], genome[1][key][move_step % genome[2]], num_joints, sim_id)


def _move_limb(obj_id, limb, target_pos, num_joints, sim_id):
    p.changeDynamics(obj_id, limb, lateralFriction=2, anisotropicFriction=[1, 1, 0.01], physicsClientId=sim_id)

    box_size = p.getCollisionShapeData(obj_id, limb,
                                       physicsClientId=sim_id)[0][3]

    if p.getCollisionShapeData(obj_id, limb, physicsClientId=sim_id)[0][2] == 2:
        box_size = box_size[0]

    p.setJointMotorControl2(obj_id,
                            limb,
                            p.POSITION_CONTROL,
                            targetPosition=target_pos,
                            force=_compute_force(_compute_mass(box_size), num_joints),
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
