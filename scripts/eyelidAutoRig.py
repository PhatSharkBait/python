import math
from maya import cmds


def average_position(pos1, pos2):
    avgX = (pos1[0] + pos2[0]) / 2
    avgY = (pos1[1] + pos2[1]) / 2
    avgZ = (pos1[2] + pos2[2]) / 2
    return [avgX, avgY, avgZ]


def create_controls_from_list(joints):
    ctrl_radius = .1
    ctrl_axis = (0, 0, 1)

    ctrls = []
    for joint in joints:
        ctrl_name = joint.replace("jnt", "ctrl")
        ctrl_grp_name = joint.replace("jnt", "ctrl_grp")
        ctrl = cmds.circle(name=ctrl_name, radius=ctrl_radius, nr=ctrl_axis)[0]
        grp = cmds.group(ctrl, name=ctrl_grp_name)
        cmds.matchTransform(grp, joint)
        cmds.parentConstraint(ctrl, joint, maintainOffset=False)
        ctrls.append(ctrl)

    return ctrls


def create_single_lid_joints_curves(centerJoint, upObject, edges, upperLower):
    edgesToSelect = edges.split(',')
    name_base_parts = centerJoint.partition('eye')
    name_base = name_base_parts[0] + name_base_parts[1] + '_' + upperLower
    cmds.select(edgesToSelect, replace=True)
    cmds.polyToCurve(form=2, degree=1, conformToSmoothMeshPreview=0, name="%s.high_res_curve" % name_base)

    high_res_curve = cmds.ls(sl=True)[0]

    if upperLower == "lower":
        cmds.reverseCurve(high_res_curve, ch=True, rpo=True)

    cmds.delete(high_res_curve, ch=True)

    centerJoint = centerJoint
    centerJointPos = cmds.joint(centerJoint, query=True, position=True)

    lidBaseJoints = []
    lidTipJoints = []
    lidLocs = []

    for cv in (range(cmds.getAttr('%s.spans' % high_res_curve) + 1)):
        cvPos = cmds.xform('%s.cv[%i]' % (high_res_curve, cv), q=True, worldSpace=True, translation=True)
        cmds.select(clear=True)
        baseJoint = cmds.joint(name='%s.lid_base_jnt0' % name_base, position=cmds.joint(centerJoint, query=True, position=True))
        tipJoint = cmds.joint(name='%s.lid_tip_jnt0' % name_base, position=(cvPos[0], cvPos[1], cvPos[2]))

        loc = cmds.spaceLocator()[0]
        cmds.move(cvPos[0], cvPos[1], cvPos[2], loc)

        lidBaseJoints.append(baseJoint)
        lidTipJoints.append(tipJoint)
        lidLocs.append(loc)

    joints_grp = cmds.group(lidBaseJoints, name='%s.Lid_jnt_grp' % name_base)
    locs_grp = cmds.group(lidLocs, name='%s.Lid_Loc_grp' % name_base)

    # Loop through each locator and connect its translate value to the corresponding parameter value
    for i, loc in enumerate(lidLocs):
        pci = cmds.createNode('pointOnCurveInfo', name='%s_pci' % loc)
        cmds.connectAttr(high_res_curve+'.worldSpace', pci+'.inputCurve')
        cmds.setAttr('%s.parameter' % pci, i)
        cmds.connectAttr('%s.position' % pci, '%s.translate' % loc)
        cmds.aimConstraint(loc, lidBaseJoints[i], mo=True,
                           weight=1, aimVector=(1, 0, 0), upVector=(0, 1, 0),
                           worldUpType='object', worldUpObject=upObject)

    # Create low-res curve
    curveSpans = cmds.getAttr('%s.spans' % high_res_curve)
    firstCvPos = cmds.xform('%s.cv[%i]' % (high_res_curve, 0), q=True, worldSpace=True, translation=True)
    lastCvPos = cmds.xform('%s.cv[%i]' % (high_res_curve, curveSpans), q=True, worldSpace=True, translation=True)

    # if number of spans is even, the total number of cvs is odd
    if curveSpans % 2 == 0:
        cv = curveSpans / 2
        centerCvPos = cmds.xform('%s.cv[%i]' % (high_res_curve, cv), q=True, worldSpace=True, translation=True)

        if cv % 2 == 0:
            supportCv1 = cv / 2
            supportCvPos1 = cmds.xform('%s.cv[%i]' % (high_res_curve, supportCv1), q=True, worldSpace=True, translation=True)

            supportCv2 = (curveSpans + cv) / 2
            supportCvPos2 = cmds.xform('%s.cv[%i]' % (high_res_curve, supportCv2), q=True, worldSpace=True, translation=True)
        else:
            cv1 = math.floor(cv / 2)
            cv2 = cv1 + 1
            cv1Pos = cmds.xform('%s.cv[%i]' % (high_res_curve, cv1), q=True, worldSpace=True, translation=True)
            cv2Pos = cmds.xform('%s.cv[%i]' % (high_res_curve, cv2), q=True, worldSpace=True, translation=True)
            supportCvPos1 = average_position(cv1Pos, cv2Pos)

            cv1 = math.floor((curveSpans + cv)/2)
            cv2 = cv1 + 1
            cv1Pos = cmds.xform('%s.cv[%i]' % (high_res_curve, cv1), q=True, worldSpace=True, translation=True)
            cv2Pos = cmds.xform('%s.cv[%i]' % (high_res_curve, cv2), q=True, worldSpace=True, translation=True)
            supportCvPos2 = average_position(cv1Pos, cv2Pos)
    else:
        centerCv1 = math.floor(curveSpans / 2)
        centerCv2 = centerCv1 + 1
        cv1Pos = cmds.xform('%s.cv[%i]' % (high_res_curve, centerCv1), q=True, worldSpace=True, translation=True)
        cv2Pos = cmds.xform('%s.cv[%i]' % (high_res_curve, centerCv2), q=True, worldSpace=True, translation=True)
        centerCvPos = average_position(cv1Pos, cv2Pos)

        if centerCv1 % 2 == 0:
            supportCv1 = centerCv1 / 2
            supportCvPos1 = cmds.xform('%s.cv[%i]' % (high_res_curve, supportCv1), q=True, worldSpace=True, translation=True)

            supportCv2 = (curveSpans + centerCv2) / 2
            supportCvPos2 = cmds.xform('%s.cv[%i]' % (high_res_curve, supportCv2), q=True, worldSpace=True, translation=True)
        else:
            cv1 = math.floor(centerCv1 / 2)
            cv2 = cv1 + 1
            cv1Pos = cmds.xform('%s.cv[%i]' % (high_res_curve, cv1), q=True, worldSpace=True, translation=True)
            cv2Pos = cmds.xform('%s.cv[%i]' % (high_res_curve, cv2), q=True, worldSpace=True, translation=True)
            supportCvPos1 = average_position(cv1Pos, cv2Pos)

            cv1 = math.floor((curveSpans + centerCv2)/2)
            cv2 = cv1 + 1
            cv1Pos = cmds.xform('%s.cv[%i]' % (high_res_curve, cv1), q=True, worldSpace=True, translation=True)
            cv2Pos = cmds.xform('%s.cv[%i]' % (high_res_curve, cv2), q=True, worldSpace=True, translation=True)
            supportCvPos2 = average_position(cv1Pos, cv2Pos)

    lowResCvsPos = [firstCvPos, supportCvPos1, centerCvPos, supportCvPos2, lastCvPos]
    driver_joints = []

    low_res_curve = cmds.curve(name="%s.low_res_curve" % name_base, editPoint=lowResCvsPos, degree=3)

    for cvPos in lowResCvsPos:
        cmds.select(clear=True)
        joint = cmds.joint(name='%s.lid_driver_jnt' % name_base, position=(cvPos[0], cvPos[1], cvPos[2]))
        driver_joints.append(joint)

    driver_controls = create_controls_from_list(driver_joints)
    driver_group = cmds.group(driver_joints, name='%s.driver_jnt_grp' % name_base)

    high_res_low_res_wire = cmds.wire(high_res_curve, groupWithBase=False, envelope=1, crossingEffect=0,
              localInfluence=0, name="high_res_curve_wire", wire=low_res_curve)
    wire_group = cmds.group([low_res_curve, high_res_curve, '%s_low_res_curveBaseWire' % name_base],
                            name='%s.wire_grp' % name_base)

    cmds.skinCluster(driver_joints, low_res_curve, name="low_res_driver_skinCluster",
                     toSelectedBones=True, bindMethod=0, skinMethod=0, normalizeWeights=1)

    cmds.group([joints_grp, locs_grp, driver_group, wire_group], name='%s_grp' % name_base)

    return driver_controls, high_res_curve, low_res_curve


def create_low_res_blend_shape(curves):
    bs_curve = cmds.duplicate(curves[0], name='low_res_blink_bs_curve')[0]
    cmds.select([curves[0], curves[1], bs_curve], r=True)
    bs = cmds.blendShape(n="low_res_blend_shape")[0]

    return bs_curve, bs


def create_high_res_blink_curves(curves):
    upper_blink_curve = cmds.duplicate(curves[0], name="upper_high_res_blink_curve")[0]
    lower_blink_curve = cmds.duplicate(curves[1], name="lower_high_res_blink_curve")[0]

    return [upper_blink_curve, lower_blink_curve]


def create_blink_attrs(control):
    cmds.addAttr(control, ln='Blink', at="double", min=0, max=1, dv=0)
    cmds.setAttr("%s.Blink" % control, e=True, keyable=True)
    cmds.addAttr(control, ln='Blink_Height', at="double", min=0, max=1, dv=0)
    cmds.setAttr("%s.Blink_Height" % control, e=True, keyable=True)
    cmds.setAttr("%s.Blink_Height" % control, .2)
    return ["%s.Blink" % control, "%s.Blink_Height" % control]


def create_blink_wire_deformers(bs_curve_and_bs_node, high_res_blink_curves, low_res_curves):
    cmds.setAttr("%s.%s" % (bs_curve_and_bs_node[1], low_res_curves[0]), 1)
    cmds.setAttr("%s.%s" % (bs_curve_and_bs_node[1], low_res_curves[1]), 0)
    upper_wire_name = low_res_curves[0].replace('low_res_curve', 'high_res_blink_curve_wire')
    upper_high_res_wire = cmds.wire(high_res_blink_curves[0], groupWithBase=False, envelope=1, crossingEffect=0,
              localInfluence=0, name=upper_wire_name, wire=bs_curve_and_bs_node[0])[0]

    cmds.setAttr("%s.%s" % (bs_curve_and_bs_node[1], low_res_curves[0]), 0)
    cmds.setAttr("%s.%s" % (bs_curve_and_bs_node[1], low_res_curves[1]), 1)
    lower_wire_name = low_res_curves[1].replace('low_res_curve', 'high_res_blink_curve_wire')
    lower_high_res_wire = cmds.wire(high_res_blink_curves[1], groupWithBase=False, envelope=1, crossingEffect=0,
              localInfluence=0, name=lower_wire_name, wire=bs_curve_and_bs_node[0])[0]

    return [upper_high_res_wire, lower_high_res_wire]


def create_high_res_blend_shapes(high_res_curves, high_res_blink_curves):
    high_res_blink_bs_nodes = []
    for i in range(len(high_res_curves)):
        cmds.select([high_res_blink_curves[i], high_res_curves[i]], r=True)
        high_res_blink_bs_nodes.append(cmds.blendShape(n='%s_blink_bs' % high_res_curves[i], before=True)[0])
        
    return high_res_blink_bs_nodes


def connect_attributes(blink_attrs, bs, upper_high_res_blink_bs_node, lower_high_res_blink_bs_node):
    # connectAttr -f upper_lid_driver_ctrl2.Blink high_res_curve_wire.envelope;
    upper_target = cmds.blendShape(upper_high_res_blink_bs_node, q=True, t=True)[0]
    lower_target = cmds.blendShape(lower_high_res_blink_bs_node, q=True, t=True)[0]
    cmds.connectAttr(blink_attrs[0], '%s.%s' % (upper_high_res_blink_bs_node, upper_target), force=True)
    cmds.connectAttr(blink_attrs[0], '%s.%s' % (lower_high_res_blink_bs_node, lower_target), force=True)

    # connectAttr -f upper_lid_driver_ctrl2.Blink_Height low_res_blend_shape.upper_low_res_curve;
    # // Result: Connected upper_lid_driver_ctrl2.Blink_Height to low_res_blend_shape.weight.
    # shadingNode -asUtility reverse;
    # // Result: reverse1
    # connectAttr -f upper_lid_driver_ctrl2.Blink_Height reverse1.inputX;
    # // Result: Connected upper_lid_driver_ctrl2.Blink_Height to reverse1.input.inputX.
    # connectAttr -f reverse1.outputX low_res_blend_shape.lower_low_res_curve;
    # // Result: Connected reverse1.output.outputX to low_res_blend_shape.weight.
    bs_weights = cmds.listAttr('%s.w' % bs, multi=True)
    bs_rev_node = cmds.shadingNode('reverse', n='blink_bs_rev', asUtility=True)

    cmds.connectAttr(blink_attrs[1], "%s.%s" % (bs, bs_weights[0]), force=True)
    cmds.connectAttr(blink_attrs[1], "%s.input.inputX" % bs_rev_node, force=True)
    cmds.connectAttr("%s.output.outputX" % bs_rev_node, "%s.%s" % (bs, bs_weights[1]), force=True)


def create_eyelid_rig(fields):
    field_values = []
    for field in fields:
        field_values.append(cmds.textField(field, q=True, text=True))

    #upper lid
    upper_lid_joints_curves = create_single_lid_joints_curves(field_values[0], field_values[1], field_values[2], "upper")

    #lower lid
    lower_lid_joints_curves = create_single_lid_joints_curves(field_values[0], field_values[1], field_values[3], "lower")

    bs_curve_and_bs_node = create_low_res_blend_shape([upper_lid_joints_curves[2], lower_lid_joints_curves[2]])
    upper_high_res_curve = upper_lid_joints_curves[1]
    lower_high_res_curve = lower_lid_joints_curves[1]
    high_res_blink_curves = create_high_res_blink_curves([upper_high_res_curve, lower_high_res_curve])
    blink_attrs = create_blink_attrs(upper_lid_joints_curves[0][2])
    wire_deformer_nodes = create_blink_wire_deformers(bs_curve_and_bs_node, high_res_blink_curves,
                                                      [upper_lid_joints_curves[2], lower_lid_joints_curves[2]])
    high_res_blink_bs_nodes = create_high_res_blend_shapes([upper_high_res_curve, lower_high_res_curve], high_res_blink_curves)
    connect_attributes(blink_attrs, bs_curve_and_bs_node[1], high_res_blink_bs_nodes[0], high_res_blink_bs_nodes[1])


def set_object(textField, *args):
    sels = cmds.ls(sl=True)
    textFieldtext = ','.join(sels)
    cmds.textField(textField, edit=True, text=textFieldtext)


def create_window():
    window = 'EyelidAutoRig'

    windowUIkwargs = {"backgroundColor": (0.04, 0.11, 0.32)}
    buttonUIkwargs = {"backgroundColor": (0.50, 0.50, 0.50),
                      "highlightColor": (1.00, 0.81, 0.34),
                      "width": 150}
    textFieldUIkwargs = {"aie": True,
                         "backgroundColor": (0.30, 0.55, 0.75)}

    if cmds.window(window, exists=True):
        cmds.deleteUI(window)

    window = cmds.window(window, title="Eyelid Auto Rig", widthHeight=[300, 400], resizeToFitChildren=1,
                         **windowUIkwargs)

    main_column = cmds.columnLayout(parent=window, adjustableColumn=1)

    fields_column = cmds.columnLayout(parent=main_column, adjustableColumn=1)

    center_joint_label = cmds.text(parent=fields_column, label='Center Joint')
    center_joint_field = cmds.textField(center_joint_label, **textFieldUIkwargs)
    sel_to_center_joint_button = cmds.button("Center Joint = Selection",
                                             command=lambda *args: set_object(center_joint_field), **buttonUIkwargs)

    up_object_label = cmds.text(parent=fields_column, label='Up Object')
    up_object_field = cmds.textField(up_object_label, **textFieldUIkwargs)
    sel_to_up_object_button = cmds.button("Up Object = Selection",
                                          command=lambda *args: set_object(up_object_field), **buttonUIkwargs)

    upper_lid_label = cmds.text(parent=fields_column, label='Upper Eyelid Edge')
    upper_lid_field = cmds.textField(upper_lid_label, **textFieldUIkwargs)
    sel_to_upper_lip_button = cmds.button("Upper Lid = Selection",
                                          command=lambda *args: set_object(upper_lid_field), **buttonUIkwargs)

    lower_lid_label = cmds.text(parent=fields_column, label='Lower Eyelid Edge')
    lower_lid_field = cmds.textField(lower_lid_label, **textFieldUIkwargs)
    sel_to_lower_lip_button = cmds.button("Lower Lid = Selection",
                                          command=lambda *args: set_object(lower_lid_field), **buttonUIkwargs)

    cmds.rowLayout(parent=main_column, numberOfColumns=2, columnWidth2=(100, 100),
                   columnAttach=[(1, 'both', 0), (2, 'both', 0)])
    run_button = cmds.button("Send it", **buttonUIkwargs)
    close_button = cmds.button("Close", command=lambda *args: close_window(window), **buttonUIkwargs)

    cmds.showWindow(window)
    return [[center_joint_field, up_object_field, upper_lid_field, lower_lid_field], run_button]


def close_window(window, *args):
    cmds.deleteUI(window)


def get_text_fields():
    params = create_window()

    run_button = params[1]
    cmds.button(run_button, edit=True, command=lambda *args: create_eyelid_rig(params[0]))


if __name__ == '__main__':
    get_text_fields()

