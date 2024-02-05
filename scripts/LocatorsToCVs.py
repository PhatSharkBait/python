import maya.cmds as cmds

curveName = "curveShape1"

selection = cmds.ls(sl=True)

for eachItem in selection:
    #get position of locator
    pos = cmds.xform(eachItem, q=True, ws=True, t=True)

    #get parameter U on curve from locator
    u = getUParam(pos, curveName)

    #create point on curve info node
    nodeName = eachItem.replace('_loc', '_pci')
    pci = cmds.createNode('pointOnCurveInfo', name=nodeName)

    #connect curve to the pointOnCurveInfo node
    cmds.connectAttr(curveName+'.worldSpace', pci+'.inputCurve')

    #set parameter to U value
    cmds.setAttr(pci+'.parameter', u)

    #connect PCI to locator
    cmds.connectAttr(pci+'.position', eachItem+'.translate')
