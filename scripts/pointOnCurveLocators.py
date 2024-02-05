import maya.cmds as cmds

# Select the curve
curve = cmds.ls(sl=True)[0]

# Get the positions of all CVs on the curve
cv_positions = cmds.getAttr(curve+'.cv[*]')

# Create a locator at each CV position
locators = []
for pos in cv_positions:
    loc = cmds.spaceLocator()[0]
    cmds.move(pos[0], pos[1], pos[2], loc)
    locators.append(loc)

# Loop through each locator and connect its translate value to the corresponding parameter value
for i, loc in enumerate(locators):
    poc = cmds.createNode('pointOnCurveInfo', name='%s_poc' % loc)
    cmds.connectAttr(curve+'.worldSpace', poc+'.inputCurve')
    cmds.setAttr('%s.parameter' % poc, i)
    cmds.connectAttr('%s.position' % poc, '%s.translate' % loc)



