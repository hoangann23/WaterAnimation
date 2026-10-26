# # Procedural Water Animation Tool

A procedural animation tool built with Python in Autodesk Maya. The tool deforms a raindrop mesh along a user-defined NURBS curve using spline IK and provides controls for squash-and-stretch animation.



https://github.com/user-attachments/assets/be5034c7-8e10-49da-af67-0c7f4374d2e7


<img width="1259" height="737" alt="image" src="https://github.com/user-attachments/assets/7198b1f3-b622-4e73-9c76-1b3fef98a6e2" />



## Features

- **Curve-based animation:** Animates a raindrop rig along a user-selected NURBS curve using spline IK.
- **Procedural rig setup:** Duplicates the selected rig and creates a spline IK system to drive its motion along the curve.
- **Interactive scale controls:** Adjusts the animated rig's scale through a custom UI.
- **Squash and stretch:** Supports shaping the raindrop by adjusting joint scales to create dynamic-looking deformation.
- **Keyframe animation:** Allows scale changes to be keyed at different timeline frames to create a complete animation.
- **Node-based motion:** Uses Maya dependency graph connections to drive the spline IK offset based on time and speed.

## Technical Implementation

The project uses Maya's Python environment, `maya.cmds`, and `maya.api.OpenMaya` to create and manage the rig and animation.

Key techniques include:

- Creating spline IK handles from a NURBS curve and a joint chain.
- Connecting Maya utility nodes to drive animation parameters.
- Duplicating rigs to preserve the original setup.
- Modifying joint scales to create squash-and-stretch effects.
- Setting keyframes programmatically to animate scale changes.
- Using Maya event callbacks to manage timeline updates and animation behavior.

## Requirements

- Autodesk Maya
- Maya Python environment with `maya.cmds` and `maya.api.OpenMaya`

## Usage

1. Open a Maya scene containing a NURBS curve and a rigged raindrop mesh.
2. Select the curve and rig using the tool's expected selection workflow.
3. Generate the animated rig using the tool UI.
4. Adjust the raindrop's scale at different timeline frames.
5. Set keyframes to animate squash-and-stretch poses.
6. Play the timeline to preview the resulting animation.


