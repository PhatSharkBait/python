import maya.cmds as cmds

ctrl_radius = .75
ctrl_axis = (1, 0, 0)

sels = cmds.ls(sl=True)

for sel in sels:
    ctrl_name = sel.replace("jnt", "ctrl")
    ctrl_grp_name = sel.replace("jnt", "ctrl_grp")
    ctrl = cmds.circle(name=ctrl_name, radius=ctrl_radius, nr=ctrl_axis)
    grp = cmds.group(ctrl, name=ctrl_grp_name)
    cmds.matchTransform(grp, sel)
