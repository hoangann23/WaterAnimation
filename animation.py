import maya.cmds as cmds
import curves
import deformation
import importlib

importlib.reload(curves)
importlib.reload(deformation)

def move_along_curve(curve, speed, object=None, joints=None):
    if not curve or not cmds.objExists(curve):
        return

    time = cmds.getAttr("time1.outTime")
    distance = speed * time

    if object and cmds.objExists(object):
        if cmds.nodeType(object) != "ikHandle":
            curves.place_on_curve(curve, distance, object)

    if joints:
        update_deformation(curve, joints, distance)
        

def update_deformation(curve, joints, distance):
    if not joints:
        return

    bend_angle = curves.get_curve_bend(curve, distance)
    if bend_angle is None:
        return

    num_joints = len(joints)
    stretches = deformation.calculate_joint_stretches(
        bend_angle, num_joints
    )
    deformation.apply_joint_stretches(joints, stretches)

def get_node_name(handle):
    node_name = handle
    if handle[0] == '|':
        node_name = handle[1:]
        node_name = node_name.replace('|', '_')
    return f"{node_name}" 

def create_speed_node(ik_handle):
    node_name = get_node_name(ik_handle)
    ik_node = cmds.createNode('network', name=f'{node_name}_node')
    cmds.addAttr(ik_node, longName='speed', shortName='spd', attributeType='float', defaultValue=1.0, keyable=True)

def create_distance_offset_node(ik_handle):
    node_name = get_node_name(ik_handle)
    distance_node = cmds.createNode('network', name=f'{node_name}_distance_node')
    cmds.addAttr(distance_node, longName='offset', shortName='os', attributeType='float', defaultValue=0.0, keyable=True)
    cmds.addAttr(distance_node, longName='currentDistance', shortName='dist', attributeType='float', defaultValue=0.0, keyable=True)

def get_distance_offset_node(ik_handle):
    node_name = get_node_name(ik_handle)
    return f"{node_name}_distance_node" 

def set_distance_offset(ik_handle):
    distance_node = get_distance_offset_node(ik_handle)
    speed_node = get_speed_node(ik_handle)
    current_dist = cmds.getAttr(f"{distance_node}.currentDistance")
    current_time = cmds.getAttr('time1.outTime')
    speed = cmds.getAttr(f"{speed_node}.speed")
    offset = current_dist - (current_time * speed)
    cmds.setAttr(f'{distance_node}.offset', offset)

def get_speed_node(ik_handle):
    node_name = get_node_name(ik_handle)
    return f"{node_name}_node" 

def set_ik_speed(ik_handle, speed, initialGeneration=False):
    speed_node = get_speed_node(ik_handle)
    distance_node = get_distance_offset_node(ik_handle)
    if cmds.objExists(speed_node) and cmds.objExists(distance_node):
        current_dist = cmds.getAttr(f"{distance_node}.currentDistance")
        current_time = cmds.getAttr('time1.outTime')
        cmds.setAttr(f"{speed_node}.speed", speed)
        if not initialGeneration:
            offset = current_dist - (current_time * speed)
            cmds.setAttr(f'{distance_node}.offset', offset)

def drive_ik_offset(ik_handle):
    ik_node = get_speed_node(ik_handle)
    distance_node = get_distance_offset_node(ik_handle)

    multiply_node = cmds.createNode(
        "multiplyDivide",
        name="raindropOffset_MD"
    )

    add_node = cmds.createNode(
        "sum",
        name="sumNode"
    )

    cmds.connectAttr(
        'time1.outTime',
        multiply_node + ".input1X",
        force=True
    )

    cmds.connectAttr(
        ik_node + ".speed",
        multiply_node + ".input2X",
        force=True
    )

    cmds.connectAttr(
        multiply_node + ".outputX",
        add_node + ".input[0]",
        force=True
    )

    cmds.connectAttr(
        distance_node + ".offset",
        add_node + ".input[1]",
        force=True
    )

    cmds.connectAttr(
        add_node + ".output", #multiply_node + ".outputX",
        ik_handle + ".offset",
        force=True
    )

    cmds.connectAttr(
        add_node + ".output", #multiply_node + ".outputX",
        distance_node + ".currentDistance",
        force=True
    )

def set_ik_speed_keyframe(ik_handle, speed):
    ik_node = get_speed_node(ik_handle)
    distance_node = get_distance_offset_node(ik_handle)

    if not cmds.objExists(ik_node) or not cmds.objExists(distance_node):
        cmds.warning("Speed or distance node doesn't exist")
        return

    # Capture the current position before changing the speed.
    current_time = cmds.currentTime(query=True)
    current_dist = cmds.getAttr(f"{distance_node}.currentDistance")

    # Calculate the offset needed to preserve that position.
    offset = current_dist - (current_time * speed)

    # Key both values at the current frame.
    cmds.setKeyframe(
        ik_node,
        attribute="speed",
        time=(current_time, current_time),
        value=speed
    )

    cmds.setKeyframe(
        distance_node,
        attribute="offset",
        time=(current_time, current_time),
        value=offset
    )