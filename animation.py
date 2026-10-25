import maya.cmds as cmds
import curves

def move_along_curve(curve, speed, object=None):
    if not curve or not cmds.objExists(curve):
        return

    if not object or not cmds.objExists(object):
        return

    if cmds.nodeType(object) != "ikHandle":
        time = cmds.getAttr("time1.outTime")
        distance = speed * time

        curves.place_on_curve(curve, distance, object)
    