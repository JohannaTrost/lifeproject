import pybullet as p
import numpy as np


def get_dist(ind_id, sim_id):
    """Computes distance to starting position ([0, 0]).

    Parameters
    ----------
    ind_id : int
        Index pointing to the multi body of the respective simulation.
    sim_id : int
        Index pointing to the physics server of the respective simulation.

    Returns
    -------
    distance : float
        Distance to [0, 0]
    """
    x, y = _get_pos(ind_id, sim_id)
    return (x ** 2 + y ** 2) ** 0.5


def _compute_force(mass, evo_config):
    """Computes force for a given mass.

    With increasing size, mass increases as well. To boxes sizes cannot grow arbitrarily, the force per mass increases
    sigmoid to a certain ceiling. After passing this ceiling, increasing mass will not likewise lead to increased force
    and thus makes it harder for the individual to move.

    Minimum and maximum force are defined in the evolution configuration.

    Assumes a standard mass of 1. Scales the force sigmoid according to the box size. Scales roughly around
    force = mass * 150 centering around mass = 2, f(mass) = 300

    Parameters
    ----------
    mass : float
        Mass used to compute the force.
    evo_config : dict
        Configuration file for the current simulation.

    Returns
    -------
    force : float
        Force computed via a sigmoid function. With increasing mass force increases, but only until a ceiling is
        reached. This ceiling is defined by evo_config['individuals']['max_force']. When mass further increases, force
        will not increase anymore and thus act as a penalty for too high masses (i.e. too large sizes).
    """

    max_force = evo_config['individuals']['max_force']
    min_force = evo_config['individuals']['min_force']
    max_force = max_force - min_force
    return 1 / (1 / max_force + np.exp(-mass * 3)) + min_force


def _compute_mass(box_size, evo_config):
    """ Computes the mass given a certain box size.

    Mass will be scaled with the volume, normalized on the standard volume. The standard volume is the average volume
    obtained from: np.random.rand(3) / 2 + 0.4, which is the starting box size. Hence this box size will have a volume
    of (0.5 / 2 + 0.4)**3 and thus a normalized mass of (0.5 / 2 + 0.4)**3 / standard_volume = 1

    Parameters
    ----------
    box_size : list | np.array of length 3 (x, y, z)
        Size of the box for which to compute the mass. All three dimensions must be given in "half extend", which is
        half the size in each dimension.
    evo_config : dict
        Configuration file for the current simulation.

    Returns
    -------
    mass : float
        Normalized mass.
    """

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


def _get_pos(ind_id, sim_id):
    """Get current head position of individual.

    Parameters
    ----------
    ind_id : int
        Index pointing to the multi body of the respective simulation.
    sim_id : int
        Index pointing to the physics server of the respective simulation.

    Returns
    -------
    x : float
        X coordinate of the head.
    y : float
        Y coordinate of the head.
    """

    # get current position of 'head'
    x, y = p.getBasePositionAndOrientation(ind_id, physicsClientId=sim_id)[0][0:2]
    return x, y


def _make_limb_dict():
    """Create controller dictionary translating each limb id into human readable format.

    In order to control the individual, joint IDs are required. For easier code comprehension those are stored in human
    readable format as a dictionary.

    Returns
    -------
    limb_dict : dict
        Dictionary containing the joint IDs of the multi body.
    """
    return {'left_arm_y': 10, 'right_arm_y': 13,
            'left_arm_z': 11, 'right_arm_z': 14,
            'left_leg_y': 4, 'right_leg_y': 7,
            'left_leg_z': 5, 'right_leg_z': 8,
            'hip_y': 2, 'hip_x': 1}


def _move_individual(ind_id, genome, move_step, evo_config, sim_id):
    """Moves all limbs of a given individual by one step.

    Wrapper function to move all limbs of a given individual at once.

    Parameters
    ----------
    ind_id : int
        Index pointing to the multi body of the respective simulation.
    genome : dict
        Genome of the current individual.
    move_step : int
        Current step. Since each move pattern is a vector of steps, move_step selects the current step. A modulo
        operation is applied to ensure proper step selection, once all steps are used. This renders the move pattern
        being "circular".
    evo_config : dict
        Configuration file for the current simulation.
    sim_id : int
        Index pointing to the physics server of the respective simulation.
    """

    # move each limb of the individual one step
    limb_dict = _make_limb_dict()
    for key in limb_dict.keys():
        _move_limb(ind_id, limb_dict[key], genome[1][key][move_step % len(genome[1][key])], evo_config, sim_id)


def _move_limb(ind_id, limb, target_pos, evo_config, sim_id):
    """Moves a single limb of a given individual by one step.

    Parameters
    ----------
    ind_id : int
        Index pointing to the multi body of the respective simulation.
    limb : int
        Index pointing to the joint of the multi body.
    target_pos : float
        Target position of the joint motor in multiples of pi.
    evo_config : dict
        Configuration file for the current simulation.
    sim_id : int
        Index pointing to the physics server of the respective simulation.
    """

    # move specific limb motor to target position
    p.changeDynamics(ind_id, limb, lateralFriction=2, anisotropicFriction=[1, 1, 0.01], physicsClientId=sim_id)

    box_size = p.getCollisionShapeData(ind_id, limb,
                                       physicsClientId=sim_id)[0][3]

    if p.getCollisionShapeData(ind_id, limb, physicsClientId=sim_id)[0][2] == 2:
        box_size = box_size[0]

    p.setJointMotorControl2(ind_id,
                            limb,
                            p.POSITION_CONTROL,
                            targetPosition=target_pos,
                            force=_compute_force(_compute_mass(box_size, evo_config), evo_config),
                            physicsClientId=sim_id)


def _move_pattern_size(evo_config):
    """Initialize the size of the movement pattern obtained from the evolution configuration.

    If specified in the evolution configuration, the size can vary by ± 50% randomly.

    Parameters
    ----------
    evo_config : dict
        Configuration file for the current simulation.

    Returns
    -------
    pattern_length : int
        Defines the length of the movement pattern.
    """

    pattern_length = evo_config['individuals']['start_move_pattern_size']
    vary_pattern_length = evo_config['individuals']['vary_pattern_length']

    # compute size of movement pattern (jitter of ± 50%)
    if vary_pattern_length:
        return int(pattern_length * (1.5 - np.random.rand()))
    else:
        return pattern_length


def _make_move_pattern(limb_dict, evo_config):
    """Initializes a random start movement pattern.

    Randomly initializes a movement pattern by selecting values between ± pi. If specified the movement pattern can be
    normalized. In case so, it will be ensured, that the absolute values of all steps within the pattern sum up to 2 pi.

    Parameters
    ----------
    limb_dict : dict
        Dictionary containing the joint IDs of the multi body.
    evo_config : dict
        Configuration file for the current simulation.

    Returns
    -------
    move_dict : dict
        Dictionary containing the movement pattern for all limbs.
    """

    # create random movement pattern
    move_dict = {key: None for key in limb_dict.keys()}

    for key in limb_dict.keys():
        move_dict[key] = np.random.random(_move_pattern_size(evo_config)) * 2 * np.pi - np.pi

        # rescale step sizes to make the absolute values summing up to 2 pi
        if evo_config['individuals']['normalize_move_pattern']:
            move_dict[key] = _normalize_move_pattern(move_dict[key])
    return move_dict


def _normalize_move_pattern(move_pattern, max_val=2 * np.pi):
    """Normalizes movement patterns to ensure all absolute values of all steps sum up to a maximum value.

    Parameters
    ----------
    move_pattern : list | np.array
        Vector containing all movement steps in multiples of pi.
    max_val : float
        Maximum value to which all absolute values will sum up to.

    Returns
    -------
    move_pattern : np.array
        Normalized movement pattern.
    """

    return move_pattern / np.sum(np.abs(move_pattern)) * max_val


def _interpolate_move_pattern(move_pattern, new_size, min_size=10, max_size=1000):
    """Interpolates movement pattern to fit a given size.

    Linearly interpolates all values in move_pattern to fit a certain vector length.

    If move pattern is longer than new_size, it cannot be interpolated in the classical sense (i.e. it has to be
    extrapolated). We have to find a common multiple to extent the size, in order to reslice it properly later.
    However, in order to ensure that we keep the first and last value in the vector untouched, we have to add 1 and
    subtract len(move_pattern). Doing as described will yield a new vector of size new_size, with the first and last
    value in move_pattern untouched, whereas values in between are interpolated according to the standard procedure.

    Parameters
    ----------
    move_pattern : list | np.array
        Vector containing all movement steps in multiples of pi.
    new_size : int
        New length of the vector move_pattern.
    min_size : int
        Minimum length of the vector move_pattern.
    max_size : int
        Maximum length of the vector move_pattern.

    Returns
    -------
    interpolated_move_pattern : np.array
        Interpolated movement pattern.
    """

    # interpolate movement pattern to fit a certain size by linear interpolation
    if new_size < min_size:
        new_size = min_size
    elif new_size > max_size:
        new_size = max_size

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
    """Create box size dictionary translating each limb size into human readable format.

    Box sizes are initialized random within a range defined in the evolution configuration. Furthermore, if selected,
    sizes of limbs can be symmetric. If no random selection was defined, a fixed box size is computed (i.e. the average
    between the minimum and maximum value defined in the evolution configuration).

    Parameters
    ----------
    evo_config : dict
        Configuration file for the current simulation.

    Returns
    -------
    size_dict : dict
        Dictionary storing all sizes of all boxes of a given individual.
    """

    # get default variables from config
    min_size = evo_config['individuals']['min_box_size']
    max_size = evo_config['individuals']['max_box_size']
    is_random = evo_config['individuals']['random_box_size']
    symmetric = evo_config['individuals']['symmetric']

    # make random sizes for each box
    size_dict = {key: None for key in ['left_hand', 'right_hand', 'left_foot', 'right_foot', 'chest', 'hip']}

    for size_key in size_dict.keys():

        # if symmetric, we can skip the computation for the other limb
        if symmetric and 'right_' in size_key and size_dict['left_' + size_key.split('right_')[1]] is not None:
            size_dict[size_key] = size_dict['left_' + size_key.split('right_')[1]]
            continue

        elif symmetric and 'left_' in size_key and size_dict['right_' + size_key.split('left_')[1]] is not None:
            size_dict[size_key] = size_dict['right_' + size_key.split('left_')[1]]
            continue

        # make 3 values according to the selected policy
        if is_random:
            limb_size = np.random.rand(3) * (max_size - min_size) + min_size
        else:
            limb_size = np.asarray([(max_size + min_size) / 2] * 3)

        size_dict[size_key] = limb_size

    return size_dict


def _make_random_genome(evo_config):
    """Creates a random genome

    A genome consists of genes for sizes and movement patterns as well as the evolution configuration. Thus this
    function is a wrapper to return the aforementioned.

    Parameters
    ----------
    evo_config : dict
        Configuration file for the current simulation.

    Returns
    -------
    size_dict : dict
        Dictionary storing all sizes of all boxes of a given individual.
    move_dict : dict
        Dictionary containing the movement pattern for all limbs.
    evo_config : dict
        Configuration file for the current simulation.
    """

    # create random genome by creating chromosomes for box size and movement
    return _make_size_dict(evo_config), _make_move_pattern(_make_limb_dict(), evo_config)
