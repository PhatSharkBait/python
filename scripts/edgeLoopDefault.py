import maya.cmds as cmds

newEdgeLoopTool = cmds.polySelectEditCtx(splitType=1, mode=1)
cmds.setToolTo(newEdgeLoopTool)
