import maya.cmds as cmds

newEdgeLoopTool = cmds.polySelectEditCtx(splitType=2, useEqualMultiplier=True, divisions=1, autoComplete=1, fixQuads=1, mode=1)
cmds.setToolTo(newEdgeLoopTool)
