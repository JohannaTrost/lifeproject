import numpy as np
import math


# azimuth -> angle of first joint
# inclination -> angle of second joint
# radius -> radius of second joint
def spheric2cart(radius, inclination, azimuth):
    x = radius * math.sin(azimuth) * math.cos(inclination)
    y = radius * math.sin(azimuth) * math.sin(inclination)
    z = radius * math.cos(azimuth)
    return [x, y, z]


def get_rotation_axis(curr_point, target_point):
    curr_point = np.asarray(curr_point)
    target_point = np.asarray(target_point)
    curr_point_norm = curr_point * (1 / np.linalg.norm(curr_point))
    target_point_norm = target_point * (1 / np.linalg.norm(target_point))
    return np.cross(curr_point_norm, target_point_norm)


def get_rotation_angle(curr_point, target_point):
    curr_point = np.asarray(curr_point)
    target_point = np.asarray(target_point)
    return np.arccos(np.dot(curr_point, target_point) / (np.linalg.norm(curr_point) * np.linalg.norm(target_point)))


def mod_angle2range(angle_in_rad):
    """
	Transforms any angle (in radians) into an angle between pi and -pi.
	First we need to mod the angle between 0 and pi and then apply some corrections for angles greater than pi,
	smaller than -pi and equal -pi so that the result has the correct value and direction.
	:param angle_in_rad: numpy array or list of angles
	:return:
	"""
    angle_in_rad = np.asarray(angle_in_rad)  # convert to numpy array (e.g. if input is list)
    unit_angle = angle_in_rad % (2 * np.pi)  # shift between 0 and 2pi

    more_than_pi = (unit_angle > np.pi) + 0  # correct for bigger pi (+ 0 to convert from bool to int)
    less_than_minus_pi = (unit_angle < -np.pi) + 0  # correct for smaller -pi (+ 0 to convert from bool to int)
    equal_minus_pi = (angle_in_rad == -np.pi) + 0  # correct for equals -pi (+ 0 to convert from bool to int)

    mod_angle = unit_angle + 2 * np.pi * (less_than_minus_pi - more_than_pi - equal_minus_pi)

    return mod_angle


def average_angles(angle_a, angle_b):
    """
	Computes the average angle between angle_a and angle_b. Note that simple arithmetic averaging does not work
	for angles. Thus the angles need to be transformed into the range between pi and -pi first in order to obtain
	correct results.
	:param angle_a: numpy array or list of angles in radians
	:param angle_b: numpy array or list of angles in radians
	:return:
	"""
    return (mod_angle2range(angle_a) + mod_angle2range(angle_b)) / 2.
