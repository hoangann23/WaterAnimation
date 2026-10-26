import maya.cmds as cmds
import maya.api.OpenMaya as om
import math

def get_selected_objects():
    selected = cmds.ls(selection=True, type="transform") or []
    curve = None
    rig_group = None

    for obj in selected:
        descendants = cmds.listRelatives(
            obj,
            allDescendents=True,
            type="transform",
        ) or []

        transforms = [obj] + descendants
        for transform in transforms:
            shapes = cmds.listRelatives(
                transform,
                shapes=True,
                noIntermediate=True) or []
            for shape in shapes:
                shape_type = cmds.nodeType(shape)
                if shape_type == "mesh" and cmds.nodeType(transform) == "joint" and rig_group is None:
                    rig_group = obj
                elif shape_type == "nurbsCurve" and curve is None:
                    curve = transform
    if not curve:
        cmds.warning("Please select a NURBS curve.")
    if not rig_group:
        cmds.warning("Please select a rig")

    return curve, rig_group

def get_selected_rig():
    selected = cmds.ls(selection=True, type="transform") or []
    rig_group = None
    for obj in selected:
        descendants = cmds.listRelatives(
            obj,
            allDescendents=True,
            type="transform",
            fullPath=True
        ) or []

        transforms = [obj] + descendants
        for transform in transforms:
            shapes = cmds.listRelatives(
                transform,
                shapes=True,
                noIntermediate=True,
                fullPath=True) or []
            if any(cmds.nodeType(shape) == "mesh" for shape in shapes) and rig_group is None:
                rig_group = obj
    return rig_group

def get_rig_joint_root(rig_group):
    descendants = cmds.listRelatives(
        rig_group,
        fullPath=True
    ) or []
    for transform in descendants:
        if cmds.nodeType(transform) == "joint":
            return transform
    cmds.warning("No joints found")
    return None

def get_rig_joints(root_joint):
    descendants = cmds.listRelatives(
        root_joint,
        allDescendents=True,
        type="joint",
        fullPath=True
    ) or []
    joints = descendants + [root_joint]
    joints.reverse()
    return joints

def create_ik_spline_handle(curve, joint_chain):
    root = joint_chain
    end = None
    joints = cmds.listRelatives(joint_chain, allDescendents=True, type="joint", fullPath=True) or []
    if joints:
        end = joints[0]
    if not end:
        cmds.warning("Please select a valid rig")
        return None
    ik_spline  = cmds.ikHandle(name="spline_IK#",
                               startJoint=root,
                               endEffector=end,
                               solver="ikSplineSolver",
                               createCurve=False,
                               curve=curve,
                               rootOnCurve=True
    )
    cmds.parent(curve, world=True)
    return ik_spline[0]

def drive_ik_offset(ik_handle, speed):
    time_node = "time1"

    multiply_node = cmds.createNode(
        "multiplyDivide",
        name="raindropOffset_MD"
    )

    cmds.connectAttr(
        time_node + ".outTime",
        multiply_node + ".input1X",
        force=True
    )

    cmds.setAttr(multiply_node + ".input2X", speed)

    cmds.connectAttr(
        multiply_node + ".outputX",
        ik_handle + ".offset",
        force=True
    )
    

def get_spline_ik_curve(rig_group):
    descendants = cmds.listRelatives(
        rig_group,
        allDescendents=True,
        fullPath=True
    ) or []
    for obj in descendants:
        if cmds.nodeType(obj) != "ikHandle":
            continue
        curve_shapes = cmds.listConnections(
            obj + ".inCurve",
            source=True,
            destination=False,
            shapes=True
        ) or []
        if curve_shapes:
            parents = cmds.listRelatives(
                curve_shapes[0],
                parent=True,
                fullPath=True
            ) or []
            if parents:
                return parents[0]
    cmds.warning("No spline IK curve found in the rig group")
    return None

def get_selected_curve():
    selected = cmds.ls(selection=True, objectsOnly=True) or []
    if not selected:
        cmds.warning("Please select one NURBs curve.")
        return None
    curve = None
    for obj in selected:
        shapes = cmds.listRelatives(obj, shapes=True, noIntermediate=True) or []
        is_curve = any(cmds.nodeType(shape) == "nurbsCurve" for shape in shapes)
        if is_curve:
            curve = obj

    if not curve:
        cmds.warning("NURBs curve not found")
    return curve

def get_selected_mesh():
    selected = cmds.ls(selection=True, type="transform") or []
    if not selected:
        cmds.warning("Please select a mesh")
        return None
    for transform in selected:
        shapes = cmds.listRelatives(transform, shapes=True, noIntermediate=True) or []
        has_mesh = any(cmds.nodeType(shape) == "mesh" for shape in shapes)
        if not has_mesh:
            cmds.warning("Please select a polygon mesh")
            continue
        return transform
    return None

def get_curve_point(curve_transform, distance):
    if not cmds.objExists(curve_transform):
        cmds.warning("The source curve no longer exists")
        return None

    shapes = cmds.listRelatives(curve_transform, shapes=True, noIntermediate=True) or []
    selection = om.MSelectionList()
    for shape in shapes:
        if cmds.nodeType(shape) == "nurbsCurve":
            selection.add(shape)
            break
    else:
        cmds.warning("The source curve was not found")
        return None
    dag_path = selection.getDagPath(0)

    curve_fn = om.MFnNurbsCurve(dag_path)
    length = curve_fn.length()
    if not math.isfinite(length) or length <= 1e-6:
        cmds.warning("The source curve must have a non-zero length.")
        return None

    if distance > length:
        distance = length
    parameter = curve_fn.findParamFromLength(distance)
    point = curve_fn.getPointAtParam(parameter, om.MSpace.kWorld)
    default_tangent = om.MVector(0, 0, 1)
    tangent = curve_fn.tangent(parameter, om.MSpace.kWorld)
    if tangent.length() > 1e-6:
        tangent.normalize()
    else:
        tangent = default_tangent
    return point, tangent

def place_on_curve(curve_transform, distance, object=None):
    point, tangent = get_curve_point(curve_transform, distance)
    if point:
        if object:
            sphere = object
        else:
            sphere = cmds.polySphere(name="sphere")[0]

        world_up = om.MVector(0,1,0)
        side = tangent ^ world_up
        if side.length() <= 1e-6:
            side = tangent ^ om.MVector(1,0,0)
        side.normalize()
        forward = -tangent 
        if forward.length() > 1e-6:
            forward.normalize()
        else:
            forward = om.MVector(0,0,1)
        up = side ^ forward
        up.normalize()

        matrix = om.MMatrix(
            [side.x, side.y, side.z, 0,
             up.x, up.y, up.z, 0,
             forward.x, forward.y, forward.z, 0,
             point.x, point.y, point.z, 1])

        transform_matrix = om.MTransformationMatrix(matrix)

        # extract rotation as an MEulerRotation object
        euler_rot = transform_matrix.rotation()

        # convert radians, cmds.rotate requires degrees
        rx = math.degrees(euler_rot.x)
        ry = math.degrees(euler_rot.y)
        rz = math.degrees(euler_rot.z)

        cmds.xform(sphere, worldSpace=True, translation=(point.x, point.y, point.z))

        cmds.rotate(rx, ry, rz, sphere, worldSpace=True)
        cmds.refresh(force=True)
        return sphere
    return None

def get_curve_bend(curve_transform, distance, sample_distance=0.5):
    curve_length = get_curve_length(curve_transform)
    if curve_length is None:
        return None

    distance = max(0.0, min(distance, curve_length))
    before_distance = max(0.0, distance - sample_distance)
    after_distance = min(curve_length, distance + sample_distance)

    before = get_curve_point(curve_transform, before_distance)
    after = get_curve_point(curve_transform, after_distance)

    if before is None or after is None:
        return None

    tangent_before = before[1]
    tangent_after = after[1]

    dot = tangent_before * tangent_after
    dot = max(-1.0, min(1.0, dot))

    return math.acos(dot) #bend in radians

def get_curve_length(curve_transform):
    shapes = cmds.listRelatives(
        curve_transform,
        shapes=True,
        noIntermediate=True,
        type="nurbsCurve"
    ) or []

    if not shapes:
        return None

    selection = om.MSelectionList()
    selection.add(shapes[0])
    curve_fn = om.MFnNurbsCurve(selection.getDagPath(0))

    return curve_fn.length()