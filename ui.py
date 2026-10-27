import maya.cmds as cmds
import globals
import waterGenerator
import deformation
import curves
import animation
import importlib

importlib.reload(waterGenerator)
importlib.reload(globals)
importlib.reload(deformation)
importlib.reload(curves)
importlib.reload(animation)

rig = None
joints = None
ik_handle = None

def get_all_curves():
    curve_shapes = cmds.ls(type="nurbsCurve")
    if curve_shapes:
        curve_transforms = cmds.listRelatives(curve_shapes, parent=True, fullPath=True)
        return curve_transforms
    return None

def get_all_joints():
    joints = cmds.ls(type="joint")
    return joints

def get_all_ik_handles():
    ik_handles = cmds.ls(type="ikHandle")
    return ik_handles

def toggle_visibility(objects):
    current_visibility = cmds.getAttr(f"{objects[0]}.visibility")
    for transform in objects:
        cmds.setAttr(f"{transform}.visibility", not current_visibility)


def show_ui():
    window_name = "waterAnimationWindow"

    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)

    window = cmds.window(window_name, title="Water Animation Parameters", sizeable=True, widthHeight=(300, 180))
    cmds.columnLayout(adjustableColumn=True, rowSpacing=8, columnAttach=("both", 10))

    def on_stretch_change(*args):
            global rig
            global joints
            if not rig or not cmds.objExists(rig):
                rig = curves.get_selected_rig()
            if rig and cmds.objExists(rig): # prioritize most recently generated animation
                cmds.select(rig)
                root_joint= curves.get_rig_joint_root(rig)
                if root_joint:
                    joints = curves.get_rig_joints(root_joint)
                    stretch_factor = cmds.floatSliderGrp(stretch_slider, query=True, value=True)
                    deformation.apply_stretch_factor(joints, stretch_factor)

    def on_speed_change(*args):
        global rig
        global joints
        global ik_handle
        if not rig or not cmds.objExists(rig):
            rig = curves.get_selected_rig()
        if rig and cmds.objExists(rig): # prioritize most recently generated animation
            cmds.select(rig)
            root_joint= curves.get_rig_joint_root(rig)
            if root_joint:
                joints = curves.get_rig_joints(root_joint)
                ik_handle = curves.get_ik_spline(rig)
                speed = cmds.floatSliderGrp(speed_slider, query=True, value=True)
                animation.set_ik_speed(ik_handle, speed)
    
    speed_slider = cmds.floatSliderGrp(label="Speed", field=True, 
                                       minValue = 0, maxValue=5, 
                                       value=globals.DEFAULT_SPEED, precision=2,
                                       dragCommand=on_speed_change, changeCommand=on_speed_change)
    stretch_slider = cmds.floatSliderGrp(label="Stretch", field=True, 
                                         minValue = 0.01, maxValue=5, 
                                         value=globals.DEFAULT_MAX_STRETCH, precision=2,
                                         dragCommand=on_stretch_change, changeCommand=on_stretch_change)
    def on_click(*args):
        global rig
        global joints
        global ik_handle
        speed = cmds.floatSliderGrp(speed_slider, query=True, value=True)
        rig = waterGenerator.generate_animation(speed)
        root_joint = curves.get_rig_joint_root(rig)
        joints = curves.get_rig_joints(root_joint)
        ik_handle = curves.get_ik_spline(rig)
        cmds.select(rig)

    
    def toggle_curve_visibility(*args):
        curves = get_all_curves()
        toggle_visibility(curves)

    def toggle_joint_visibility(*args):
        joints = get_all_joints()
        toggle_visibility(joints)

    def toggle_ik_visibility(*args):
        iks = get_all_ik_handles()
        toggle_visibility(iks)

    cmds.button(label="Toggle Curve Visibility", command=toggle_curve_visibility)
    cmds.button(label="Toggle Joint Visibility", command=toggle_joint_visibility)
    cmds.button(label="Toggle IK Visibility", command=toggle_ik_visibility)

    def set_joint_keyframe(*args):
        global joints
        if joints and cmds.objExists(joints[0]):
            for joint in joints:
                cmds.setKeyframe(
                    joint,
                    attribute=["scaleX", "scaleY", "scaleZ",
                               "translateX", "translateY", "translateZ"]
                )

    
    def set_speed_keyframe(*args):
        global ik_handle

        if ik_handle and cmds.objExists(ik_handle):
            animation.set_ik_speed_keyframe(ik_handle)
    
    cmds.button(label="Set Joint Keyframe", command=set_joint_keyframe)
    cmds.button(label="Set Speed Keyframe", command=set_speed_keyframe)
                
    cmds.button(label="Generate", command=on_click)
    cmds.showWindow(window)
