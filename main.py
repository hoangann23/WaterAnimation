import maya.cmds as cmds
import maya.api.OpenMaya as om
import importlib
import sys

project_dir = cmds.workspace(query=True, rootDirectory=True)
scripts_dir = project_dir + "scripts/waterAnimator"
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

import ui

importlib.reload(ui)

ui.show_ui()
