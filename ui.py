import maya.cmds as cmds
import globals
import waterGenerator
import importlib

importlib.reload(waterGenerator)
importlib.reload(globals)

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

    speed_slider = cmds.floatSliderGrp(label="Speed", field=True, minValue = 0, maxValue=1, value=globals.DEFAULT_SPEED, precision=2)

    def on_click(*args):
        speed = cmds.floatSliderGrp(speed_slider, query=True, value=True)
        waterGenerator.generate_animation(speed)

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

    cmds.button(label="Generate", command=on_click)
    cmds.showWindow(window)
