import maya.cmds as cmds
import maya.api.OpenMaya as om
import importlib
import sys

project_dir = cmds.workspace(query=True, rootDirectory=True)
scripts_dir = project_dir + "scripts/waterAnimator"
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

import globals
import curves
import animation


def cleanup_callbacks():
    if globals.ANIMATION_JOB is not None:
        print("cleaning up animation callback")
        try:
            om.MMessage.removeCallback(globals.ANIMATION_JOB)
        except RuntimeError:
            pass
        globals.ANIMATION_JOB = None

    if globals.NODE_REMOVED_JOB is not None:
        print("cleaning node removal callback")
        for callback_id in globals.NODE_REMOVED_JOB:
            try:
                om.MMessage.removeCallback(callback_id)
            except RuntimeError:
                pass
        globals.NODE_REMOVED_JOB = None

cleanup_callbacks()

importlib.reload(globals)
importlib.reload(curves)
importlib.reload(animation)

def get_mobject(node_name):
    selection = om.MSelectionList()
    selection.add(node_name)
    return selection.getDependNode(0)

def on_node_removed(node, modifier, client_data):
    cleanup_callbacks()

def generate_animation(speed):
    curve = curves.get_selected_curve()
    rig_group = curves.get_selected_rig()
    animated_rig = None
    joints = None

    if curve:
        if rig_group:
            animated_rig = cmds.duplicate(rig_group, 
                                        name="animatedRaindrop_RIG_GRP", 
                                        upstreamNodes=True
                                        )[0]
            joint_chain = curves.get_rig_joint_root(animated_rig)
            if joint_chain:
                ik_spline = curves.create_ik_spline_handle(curve, joint_chain)
                cmds.parent(ik_spline, animated_rig)
                ik_spline = curves.get_ik_spline(animated_rig)
                animation.create_ik_node(ik_spline)
                animation.set_ik_speed(ik_spline, speed)
                animation.drive_ik_offset(ik_spline)
                water = ik_spline
                joints = curves.get_rig_joints(joint_chain)
            else:
                water = curves.place_on_curve(curve, 1.0, animated_rig)
        else:
            water = curves.place_on_curve(curve, 1.0) # use the default sphere
        if water:
            curve_shape = (cmds.listRelatives(curve, shapes=True, noIntermediate=True, type="nurbsCurve") or [None])[0]
            # track node deletion for callback cleanup
            curve_obj = get_mobject(curve)
            curve_shape_obj = get_mobject(curve_shape)
            water_obj = get_mobject(water)
            
            globals.ANIMATION_JOB = om.MEventMessage.addEventCallback("timeChanged",
                                                                    lambda *args: animation.move_along_curve(
                                                                        curve,
                                                                        speed,
                                                                        water,
                                                                        joints))
            globals.NODE_REMOVED_JOB = [
                om.MNodeMessage.addNodeAboutToDeleteCallback(curve_obj, on_node_removed),
                om.MNodeMessage.addNodeAboutToDeleteCallback(curve_shape_obj, on_node_removed),
                om.MNodeMessage.addNodeAboutToDeleteCallback(water_obj, on_node_removed)
            ]
    return animated_rig