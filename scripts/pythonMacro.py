#This makes snakes
import random
import maya.cmds as cmds

cube = cmds.polyCube(d=2, h=2, w=2)
cmds.move(1, cube, moveY=True)

curveMult = 8
curvePosX = curveMult * random.random()
curvePosZ = -3 * random.random()-2
curveNegX = -curveMult * random.random()
curveNegZ = (-5 * random.random())-5

curve = cmds.curve(p=[(0, 1, -1), (curvePosX, 1, curvePosZ), (curveNegX, 1, curveNegZ), (0, 1, -15)])
cmds.polyExtrudeFacet(cube[0]+'.f[2]', keepFacesTogether=1, pvx=0, pvy=1, pvz=1, divisions=30, smoothingAngle=30, inputCurve=curve, taper=0.3)
cmds.move(0, 0, .75, cube[0] + '.f[0:1]', cube[0] + '.f[3:5]', r=True)
cmds.select(cube[0] + '.f[0]', cube[0]+'.f[2]', cube[0]+'.f[4:5]', cube[0]+'.f[36:65]', cube[0]+'.f[96:125]')
cmds.polyBevel3(fraction=1)

cmds.move(-.75, 2, 1.5, cmds.polySphere(radius=0.5)[0], r=True)
cmds.move(.75, 2, 1.5, cmds.polySphere(radius=0.5)[0], r=True)