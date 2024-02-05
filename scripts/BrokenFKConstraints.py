import maya.cmds as cmds

# make viewport selections, parent control then child control
# get selection, define parent control and child control
# get parent group of child control
# create constraints
# create attributes on child control
# connect attributes from child control to constraint weights

sels = cmds.ls(sl=True)
parentCtrl = sels[0]
childCtrl = sels[1]
childCtrlGrp = cmds.listRelatives(childCtrl, parent=True)[0]

pConstraint1 = \
    cmds.parentConstraint(parentCtrl, childCtrlGrp, maintainOffset=True, skipRotate=['x','y','z'], weight=1)[0]
pConstraint2 = \
    cmds.parentConstraint(parentCtrl, childCtrlGrp, maintainOffset=True, skipTranslate=['x','y','z'], weight=1)[0]
cmds.scaleConstraint(parentCtrl, childCtrlGrp, weight=1)

if not cmds.attributeQuery('FollowTranslate', node=childCtrl, exists=True):
    cmds.addAttr(childCtrl, ln='FollowTranslate', at='double', min=0, max=1, dv=1)
    cmds.setAttr('%s.FollowTranslate' % childCtrl, e=True, keyable=True)
if not cmds.attributeQuery('FollowRotate', node=childCtrl, exists=True):
    cmds.addAttr(childCtrl, ln='FollowRotate', at='double', min=0, max=1, dv=1)
    cmds.setAttr('%s.FollowRotate' % childCtrl, e=True, keyable=True)

cmds.connectAttr('%s.FollowTranslate' % childCtrl, '%s.w0' % pConstraint1, f=True)
cmds.connectAttr('%s.FollowRotate' % childCtrl, '%s.w0' % pConstraint2, f=True)
