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
