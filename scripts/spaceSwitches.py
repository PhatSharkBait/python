import maya.cmds as cmds

sels = cmds.ls(sl=True)

ctrl = ""
constraints = []
targets_per_constraint = []
constraint_targets = []
constraint_targets_format = ""
attrName = 'Follow'

for sel in sels:
    selNodeType = cmds.nodeType(sel)
    if selNodeType == 'transform':
        ctrl = sel
    elif selNodeType == 'parentConstraint':
        constraints.append(sel)
        targets_per_constraint.append(cmds.parentConstraint(sel, q=True, tl=True))
    elif selNodeType == 'scaleConstraint':
        constraints.append(sel)
        targets_per_constraint.append(cmds.scaleConstraint(sel, q=True, tl=True))

[constraint_targets.append(targets) for targets in targets_per_constraint if targets not in constraint_targets]
if len(constraint_targets) == 1:
    constraint_targets = constraint_targets[0]
    for target in constraint_targets:
        constraint_targets_format += target + ':'

if cmds.attributeQuery('%s' % attrName, n='%s' % ctrl, exists=True):
    cmds.deleteAttr('%s.%s' % (ctrl, attrName))
    for constraint in constraints:
        cmds.cutKey([constraint], shape=1, clear=True)

cmds.addAttr(ctrl, ln=attrName, at='enum', en=constraint_targets_format)
cmds.setAttr('%s.%s' % (ctrl, attrName), edit=True, keyable=True)

constraint_weights_all = []
switch = '%s.%s' % (ctrl, attrName)

for constraint in constraints:
    constraint_weights_current = []
    for i in range(len(constraint_targets)):
        constraint_weights_current.append('%s.%sW%i' % (constraint, constraint_targets[i], i))
    constraint_weights_all.append(constraint_weights_current)

for i in range((int(cmds.attributeQuery('Follow', node=ctrl, range=True)[1]) + 1)):
    cmds.setAttr(switch, i)
    for constraint_weights_current in constraint_weights_all:
        for j in range(len(constraint_weights_current)):
            cmds.setAttr(constraint_weights_current[j], 0)
            if int(constraint_weights_current[j][-1:]) == i:
                cmds.setAttr(constraint_weights_current[j], 1)
            cmds.setDrivenKeyframe(constraint_weights_current[j], cd=switch)

for constraint_weights in constraint_weights_all:
    for constraint_weight in constraint_weights:
        cmds.setDrivenKeyframe(constraint_weight, cd=switch)
