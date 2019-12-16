import pybullet as p
import numpy as np


def get_dist(id_ind, sim_id):
    # get distance to starting position ([0, 0])
    x, y = _get_pos(id_ind, sim_id)
    return (x ** 2 + y ** 2) ** 0.5


def _compute_force(mass, evo_config):
    # assumes a standard mass of 1
    # scales the force sigmoid according to the box size.
    # scales roughly around force = mass * 150 centering around mass = 2, f(mass) = 300
    max_force = evo_config['individuals']['max_force']
    min_force = evo_config['individuals']['min_force']
    max_force = max_force - min_force
    return 1 / (1 / max_force + np.exp(-mass * 3)) + min_force


def _compute_mass(box_size, evo_config):
    # Mass will be scaled with the volume, normalized on the standard volume.
    # The standard volume is the average volume obtained from:
    # np.random.rand(3) / 2 + 0.4, which is the starting box size. Hence this
    # box size will have a volume of (0.5 / 2 + 0.4)**3 and thus a normalized
    # mass of (0.5 / 2 + 0.4)**3 / standard_volume = 1

    # ensure format
    standard_volume = evo_config['individuals']['standard_volume']
    if isinstance(box_size, list):
        if len(box_size) == 1:
            box_size = box_size[0]
    box_size = np.asarray(box_size)

    if np.prod(box_size.shape) < 2:  # sphere
        return 4 / 3 * np.pi * box_size**3 / standard_volume
    else:  # box
        if np.ndim(box_size) == 1:
            return np.prod(box_size * 2) / standard_volume
        else:
            return np.prod(box_size * 2, axis=1) / standard_volume


def _get_pos(id_ind, sim_id):
    # get current position of 'head'
    x, y = p.getBasePositionAndOrientation(id_ind, physicsClientId=sim_id)[0][0:2]
    return x, y


def _make_limb_dict():
    # create controller dictionary translating each limb id into human readable format
    return {'left_arm_y': 10, 'right_arm_y': 13,
            'left_arm_z': 11, 'right_arm_z': 14,
            'left_leg_y': 4, 'right_leg_y': 7,
            'left_leg_z': 5, 'right_leg_z': 8,
            'hip_y': 2, 'hip_x': 1}


def _move_individual(obj_id, genome, move_step, evo_config, sim_id):
    # move each limb of the individual one step
    limb_dict = _make_limb_dict()
    for key in limb_dict.keys():
        _move_limb(obj_id, limb_dict[key], genome[1][key][move_step % len(genome[1][key])], evo_config, sim_id)


def _move_limb(obj_id, limb, target_pos, evo_config, sim_id):
    # move specific limb motor to target position
    p.changeDynamics(obj_id, limb, lateralFriction=2, anisotropicFriction=[1, 1, 0.01], physicsClientId=sim_id)

    box_size = p.getCollisionShapeData(obj_id, limb,
                                       physicsClientId=sim_id)[0][3]

    if p.getCollisionShapeData(obj_id, limb, physicsClientId=sim_id)[0][2] == 2:
        box_size = box_size[0]

    p.setJointMotorControl2(obj_id,
                            limb,
                            p.POSITION_CONTROL,
                            targetPosition=target_pos,
                            force=_compute_force(_compute_mass(box_size, evo_config), evo_config),
                            physicsClientId=sim_id)


def _move_pattern_size(evo_config):
    default = evo_config['individuals']['start_move_pattern_size']
    vary_pattern_length = evo_config['individuals']['vary_pattern_length']
    # compute size of movement pattern (jitter of ± 50%)
    if vary_pattern_length:
        return int(default * (1.5 - np.random.rand()))
    else:
        return default


def _make_move_pattern(limb_dict, evo_config):
    # create random movement pattern
    move_dict = {}
    for key in limb_dict.keys():
        move_dict[key] = np.random.random(_move_pattern_size(evo_config)) * 2 * np.pi - np.pi
    return move_dict


def _interpolate_move_pattern(move_pattern, new_size, min_size=10, max_size=1000):
    # interpolate movement pattern to fit a certain size by linear interpolation
    if new_size < min_size:
        new_size = min_size
    elif new_size > max_size:
        new_size = max_size

    # if move pattern is longer than new_size, it cannot be interpolated in the classical sense. We have to find a
    # common multiple to extent the size to, in order to reslice it properly later. However in order to ensure that we
    # keep the first and last value in the vector untouched, we have to add 1 and subtract len(move_pattern). Doing as
    # described will yield a new vector of size new_size, with the first and last value in move_pattern untouched,
    # whereas values in between are interpolated according to the standard procedure (below).
    if len(move_pattern) > new_size:
        int_size = new_size * len(move_pattern) - len(move_pattern) + 1
    else:
        int_size = new_size

    # linear interpolation
    x = np.linspace(0, len(move_pattern), len(move_pattern))
    new_x = np.linspace(0, len(move_pattern), int_size)
    interpolated_move_pattern = np.interp(new_x, x, move_pattern)

    # in the above described case, we have to reslice the enlarged vector.
    if len(move_pattern) > new_size:
        return interpolated_move_pattern[::len(move_pattern)]
    else:
        return interpolated_move_pattern


def _make_size_dict(evo_config):
    # get default variables from config
    min_size = evo_config['individuals']['min_box_size']
    max_size = evo_config['individuals']['max_box_size']
    is_random = evo_config['individuals']['random_box_size']
    symmetric = evo_config['individuals']['symmetric']

    # make random sizes for each box
    move_dict = {}
    limb_keys = ['left_hand', 'right_hand', 'left_foot', 'right_foot', 'chest', 'hip']
    for limb_key in limb_keys:

        # if symmetric, we can skip the computation for the other limb
        if symmetric and 'right_' in limb_key:
            move_dict[limb_key] = move_dict['left_' + limb_key.split('right_')[1]]
            continue

        # make 3 values according to the selected policy
        if is_random:
            limb_size = np.random.rand(3) * (max_size - min_size) + min_size
        else:
            limb_size = np.asarray([(max_size + min_size) / 2] * 3)

        move_dict[limb_key] = limb_size

    return move_dict


def _make_random_genome(evo_config):
    # create random genome by creating chromosomes for box size and movement
    return _make_size_dict(evo_config), _make_move_pattern(_make_limb_dict(), evo_config)
