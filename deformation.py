import maya.cmds as cmds
import globals
import math

def apply_stretch(joint, stretch_factor):
    if joint and cmds.objExists(joint):
        stretch_factor = max(0.01, stretch_factor)
        perpendicular_scale = 1.0 / math.sqrt(stretch_factor)

        cmds.setAttr(f"{joint}.scaleX", perpendicular_scale)
        cmds.setAttr(f"{joint}.scaleY", perpendicular_scale)
        cmds.setAttr(f"{joint}.scaleZ", stretch_factor)

def apply_joint_stretches(joints, stretches):
    if len(joints) != len(stretches):
        raise ValueError("Each joint must have one stretch factor")

    for joint, stretch in zip(joints, stretches):
        apply_stretch(joint, stretch)

def apply_stretch_factor(joints, stretch_factor):
    weights = calculate_joint_weights(len(joints))
    stretches = distribute_stretch(stretch_factor, weights)
    apply_joint_stretches(joints, stretches)

def get_stretch_factor(
    bend_angle,
    max_bend=math.radians(globals.DEFAULT_MAX_BEND),
    max_stretch=globals.DEFAULT_MAX_STRETCH,
    min_stretch=globals.DEFAULT_MIN_STRETCH):

    clamped_bend = max(0, min((bend_angle / max_bend), 1.0))
    stretch = max_stretch + (min_stretch - max_stretch) * clamped_bend

    return stretch

def distribute_stretch(stretch_factor, weights):
    # stretch factor for each joint
    stretch = []
    for i in range(len(weights)):
        stretch_i = 1 + (stretch_factor - 1) * weights[i]
        stretch.append(stretch_i)
    return stretch

def calculate_joint_weights(num_joints):
    weights = []
    if num_joints <= 0:
        return []
    if num_joints == 1:
        return [1.0]
    for i in range(num_joints):
        normalized_joint_pos = i / (num_joints-1)
        distance_to_center = abs(normalized_joint_pos - 0.5)
        weights.append(1 - 1.5 * distance_to_center)
    return weights

def calculate_joint_stretches(bend_angle, num_joints):
    stretch_factor = get_stretch_factor(bend_angle)
    weights = calculate_joint_weights(num_joints)
    stretches = distribute_stretch(stretch_factor, weights)
    return stretches

