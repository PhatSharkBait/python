import math
import maya.cmds as cmds
import maya.mel as mel


def create_curve_from_joints(joints, base_name):
    curve_name = joints[0].replace("jnt", base_name)

    point_positions = []
    for i, joint in enumerate(joints):
        point_positions.append(cmds.xform(joints[i], q=True, t=True, ws=True))

    return cmds.curve(name=curve_name, p=point_positions, d=3)


def create_ik_spline(joints, base_curve, base_name):
    ikSplineTool = cmds.ikSplineHandleCtx(rootOnCurve=False, parentCurve=False, createCurve=False, simplifyCurve=False,
                                          numSpans=1)
    cmds.setToolTo(ikSplineTool)
    cmds.select(joints[0], r=True)
    cmds.select(joints[-1], add=True)
    cmds.select(base_curve, add=True)
    cmds.setToolTo('selectSuperContext')
    ik_handle = cmds.ls(sl=True)[0]
    cmds.select(clear=True)
    ik_handle = cmds.rename(ik_handle, joints[0].replace('jnt', base_name))
    return ik_handle


def create_control_joints(joints, base_name):
    centerIndex = math.floor((len(joints) / 2))
    jointRadius = cmds.joint(joints[0], q=True, rad=True)[0] * 1.25
    base_ctrl_jnt = cmds.joint(position=cmds.xform(joints[0], q=True, t=True, ws=True),
                               orientation=cmds.xform(joints[0], q=True, ro=True, ws=True),
                               rad=jointRadius, n=joints[0].replace('jnt', ('base_' + base_name)))
    cmds.select(clear=True)
    mid_ctrl_jnt = cmds.joint(position=cmds.xform(joints[centerIndex], q=True, t=True, ws=True),
                              orientation=cmds.xform(joints[0], q=True, ro=True, ws=True),
                              rad=jointRadius, n=joints[0].replace('jnt', ('mid_' + base_name)))
    cmds.select(clear=True)
    tip_ctrl_jnt = cmds.joint(position=cmds.xform(joints[-1], q=True, t=True, ws=True),
                              orientation=cmds.xform(joints[0], q=True, ro=True, ws=True),
                              rad=jointRadius, n=joints[0].replace('jnt', ('tip_' + base_name)))
    cmds.select(clear=True)

    return [base_ctrl_jnt, mid_ctrl_jnt, tip_ctrl_jnt]


def bind_ik_curve_to_control_joints(control_joints, ik_curve):
    cmds.select(control_joints)
    cmds.skinCluster(control_joints[0], control_joints[1], control_joints[2], ik_curve,
                     tsb=True, n='ik_control_joints_skin_cluster')


def create_control_joint_controls(control_joints, base_name, scale, axis):
    midControl = create_control_grp_and_control(control_joints[1], base_name, scale, axis, replace_name='ctrl_jnt',
                                                shape='arrows')
    mid_control_grp = cmds.listRelatives(midControl, p=True)[0]
    tipControl = create_control_grp_and_control(control_joints[2], base_name, scale, axis, replace_name='ctrl_jnt',
                                                shape='arrows')
    tip_control_grp = cmds.listRelatives(tipControl, p=True)[0]

    parent_scale_constrain_joint_to_control([control_joints[1], control_joints[2]], [midControl, tipControl])
    connect_rotation_to_twist(tipControl, ik_spline_handle)

    ik_ctrl_grp = cmds.group([mid_control_grp, tip_control_grp], name='IK_ctrl_grp')

    return ik_ctrl_grp


def create_control_grp_and_control(joint, base_name, scale, axis, replace_name='jnt', shape='circle'):
    control = ''
    if shape == 'circle':
        control = cmds.circle(name=joint.replace(replace_name, base_name), radius=scale, nr=axis)[0]
    elif shape == 'square':
        control = cmds.nurbsSquare(name=joint.replace(replace_name, base_name),
                                   nr=axis, d=2, c=(0, 0, 0), sl1=(scale * 2), sl2=(scale * 2))[0]
        cmds.select(cmds.listRelatives(control, children=True), r=True)
        cmds.pickWalk(d='down')
        cmds.select(control, add=True)
        cmds.parent(r=True, s=True, nc=True)
    elif shape == 'arrows':
        points = [[0, 0, -6], [-2, 0, -4], [-1, 0, -4], [-2, 0, -2], [-4, 0, -1], [-4, 0, -2], [-6, 0, 0], [-4, 0, 2],
                  [-4, 0, 1], [-2, 0, 2], [-1, 0, 4], [-2, 0, 4], [0, 0, 6], [2, 0, 4], [1, 0, 4], [2, 0, 2], [4, 0, 1],
                  [4, 0, 2], [6, 0, 0], [4, 0, -2], [4, 0, -1], [2, 0, -2], [1, 0, -4], [2, 0, -4], [0, 0, -6]]
        scaled_points = []
        for point in points:
            scaled_point = []
            for value in point:
                # .17 sets the control to about the same size as a default nurbs circle
                scaled_point.append((value * scale * 0.17))
            scaled_points.append(scaled_point)
        control = cmds.curve(name=joint.replace(replace_name, base_name), d=1, p=scaled_points)
        cmds.rotate(90, control, rotateZ=True)
        cmds.makeIdentity(control, r=True, a=True)

    control_grp = cmds.group(control, name=(control + '_grp'))
    cmds.matchTransform(control_grp, joint, position=True, rotation=True, pivots=True)

    return control


def parent_scale_constrain_joint_to_control(joints, controls):
    for i in range(len(joints)):
        cmds.parentConstraint(controls[i], joints[i], maintainOffset=True, weight=1)
        cmds.scaleConstraint(controls[i], joints[i], maintainOffset=True, weight=1)


def connect_rotation_to_twist(tip_control, spline_handle):
    cmds.connectAttr('%s.rotateX' % tip_control, '%s.twist' % spline_handle, force=True)


def create_ik_stretch_system(curve, joints):
    curve_shape = cmds.listRelatives(curve, s=True)[0]
    curve_info = cmds.shadingNode('curveInfo', n=(curve_shape + '_info'), asUtility=True)
    scale_factor_MD = cmds.shadingNode('multiplyDivide', n=(curve_shape + '_scaleFactor_MD'), asUtility=True)
    stretch_volume_Rev = cmds.shadingNode('reverse', n=(curve_shape + '_stretchVolume_rev'), asUtility=True)
    stretch_volume_MD = cmds.shadingNode('multiplyDivide', n=(curve_shape + '_stretchVolume_MD'), asUtility=True)
    stretch_volume_PMA = cmds.shadingNode('plusMinusAverage', n=(curve_shape + '_stretchVolume_PMA'), asUtility=True)

    cmds.setAttr("%s.operation" % scale_factor_MD, 2)

    cmds.connectAttr("%s.worldSpace" % curve_shape, "%s.inputCurve" % curve_info, force=True)

    default_arc_length = cmds.getAttr("%s.arcLength" % curve_info)
    cmds.connectAttr("%s.arcLength" % curve_info, "%s.input1.input1X" % scale_factor_MD, force=True)
    cmds.setAttr("%s.input2.input2X" % scale_factor_MD, default_arc_length)

    cmds.connectAttr("%s.output.outputX" % scale_factor_MD, '%s.input.inputX' % stretch_volume_Rev, force=True)
    cmds.connectAttr("%s.output.outputX" % stretch_volume_Rev, "%s.input1.input1X" % stretch_volume_MD, force=True)
    cmds.setAttr('%s.input2.input2X' % stretch_volume_MD, .5)

    cmds.connectAttr("%s.output.outputX" % stretch_volume_MD, '%s.input1D[0]' % stretch_volume_PMA, force=True)
    cmds.setAttr('%s.input1D[1]' % stretch_volume_PMA, 1)

    for i in range((len(joints) - 1)):
        cmds.connectAttr("%s.output.outputX" % scale_factor_MD, '%s.scaleX' % joints[i], force=True)
        cmds.connectAttr("%s.output1D" % stretch_volume_PMA, '%s.scaleY' % joints[i], force=True)
        cmds.connectAttr("%s.output1D" % stretch_volume_PMA, '%s.scaleZ' % joints[i], force=True)


def create_ik_stretch_system_no_volume_preserve(curve, joints):
    curve_shape = cmds.listRelatives(curve, s=True)[0]
    curve_info = cmds.shadingNode('curveInfo', n=(curve_shape + '_info'), asUtility=True)
    scale_factor_MD = cmds.shadingNode('multiplyDivide', n=(curve_shape + '_scaleFactor_MD'), asUtility=True)

    cmds.setAttr("%s.operation" % scale_factor_MD, 2)

    cmds.connectAttr("%s.worldSpace" % curve_shape, "%s.inputCurve" % curve_info, force=True)

    default_arc_length = cmds.getAttr("%s.arcLength" % curve_info)
    cmds.connectAttr("%s.arcLength" % curve_info, "%s.input1.input1X" % scale_factor_MD, force=True)
    cmds.setAttr("%s.input2.input2X" % scale_factor_MD, default_arc_length)

    for i in range((len(joints) - 1)):
        cmds.connectAttr("%s.output.outputX" % scale_factor_MD, '%s.scaleX' % joints[i], force=True)


def create_hair_system(dynamic_curve, dynamic_curve_base_name):
    cmds.select(dynamic_curve, r=True)
    mel.eval('makeCurvesDynamic 2 { "0", "0", "1", "1", "0"}')

    # there's gotta be a better way to do select each of these elements, I just don't know what it is.
    cmds.pickWalk(d='up')
    hair_system = cmds.ls(sl=True)[0]
    cmds.pickWalk(d='right')

    nucleus = ''
    hair_follicles_grp = ''
    hair_output_curves_grp = ''
    if cmds.nodeType(cmds.ls(sl=True)[0]) == 'nucleus':
        nucleus = cmds.ls(sl=True)[0]
        cmds.pickWalk(d='right')
        hair_follicles_grp = cmds.ls(sl=True)[0]
        cmds.pickWalk(d='right')
        hair_output_curves_grp = cmds.ls(sl=True)[0]
        nucleus = cmds.rename(nucleus, "dynamics_nucleus")
    else:
        hair_follicles_grp = cmds.ls(sl=True)[0]
        cmds.pickWalk(d='right')
        hair_output_curves_grp = cmds.ls(sl=True)[0]
        nucleus = cmds.ls(type='nucleus')

    follicle = cmds.listRelatives(hair_follicles_grp, c=True)[0]
    output_curve = cmds.listRelatives(hair_output_curves_grp, c=True)[0]

    cmds.select(dynamic_curve, follicle, output_curve, r=True)
    cmds.parent(world=True)
    cmds.delete([hair_follicles_grp, hair_output_curves_grp])

    hair_system = cmds.rename(hair_system, dynamic_curve.replace(dynamic_curve_base_name, "hair_system"))
    follicle = cmds.rename(follicle, dynamic_curve.replace(dynamic_curve_base_name, "follicle"))
    output_curve = cmds.rename(output_curve, dynamic_curve.replace(dynamic_curve_base_name, "dynamics_curve"))

    return [hair_system, nucleus, follicle, output_curve]


def create_ik_dyn_blend_shape(ik_curve, dyn_curve, ik_base_name, base_name):
    return cmds.blendShape(dyn_curve, ik_curve, name=ik_curve.replace(ik_base_name, base_name))[0]


def create_dynamics_controls(joints, dynamics_curve, base_name, scale, axis):
    controls = []
    for joint in joints:
        controls.append(create_control_grp_and_control(joint, base_name, scale, axis))

    # control hierarchy
    for i in range(len(controls[:-1])):
        control_parent = cmds.listRelatives(controls[i + 1], parent=True)[0]
        cmds.parent(control_parent, controls[i])

    # create clusters and introduce into hierarchy
    for i, control in enumerate(controls):
        cluster_handle = cmds.cluster("%s.cv[%i]" % (dynamics_curve, i))[1]
        cmds.parent(cluster_handle, control)

    dynamics_control_group = cmds.group(cmds.listRelatives(controls[0], p=True), name='DYN_ctrl_grp')

    return dynamics_control_group


def create_switch_control(base_joint, base_name, scale, axis):
    return create_control_grp_and_control(base_joint, base_name, scale, axis, shape='square')


def create_switch_attributes(switch):
    cmds.addAttr(switch, ln='Simulation', at='double', min=0, max=1, dv=0)
    sim_attr = '%s.Simulation' % switch
    cmds.setAttr(sim_attr, e=True, keyable=True)
    cmds.addAttr(switch, ln='FollowPose', at='double', min=0, max=3, dv=0)
    follow_attr = '%s.FollowPose' % switch
    cmds.setAttr(follow_attr, e=True, keyable=True)
    drag_attr = '%s.Drag' % switch
    cmds.addAttr(switch, ln='Drag', at='double', min=0, max=1, dv=0)
    cmds.setAttr(drag_attr, e=True, keyable=True)
    turbulence_attr = '%s.Turbulence' % switch
    cmds.addAttr(switch, ln='Turbulence', at='double', min=0, max=1, dv=0)
    cmds.setAttr(turbulence_attr, e=True, keyable=True)

    return [sim_attr, follow_attr, drag_attr, turbulence_attr]


def connect_attributes(attributes, ik_grp, dyn_grp, blend_shape, blend_shape_target, hair_system):
    cmds.select(hair_system, r=True)
    cmds.pickWalk(d='down')
    hair_system_shape = cmds.ls(sl=True)[0]

    # hide controls
    cmds.connectAttr(attributes[0], '%s.visibility' % dyn_grp, force=True)
    control_vis_rev = cmds.shadingNode('reverse', n='control_visibility_rev', asUtility=True)
    cmds.connectAttr(attributes[0], '%s.input.inputX' % control_vis_rev, force=True)
    cmds.connectAttr('%s.output.outputX' % control_vis_rev, '%s.visibility' % ik_grp, force=True)

    # control blend shape
    cmds.connectAttr(attributes[0], '%s.%s' % (blend_shape, blend_shape_target), force=True)

    # follow base curve
    cmds.connectAttr(attributes[1], '%s.startCurveAttract' % hair_system_shape, force=True)

    # drag
    cmds.connectAttr(attributes[2], '%s.drag' % hair_system_shape, force=True)

    # turbulence
    cmds.connectAttr(attributes[3], '%s.turbulenceStrength' % hair_system_shape, force=True)


if __name__ == '__main__':
    base_curve_base_name = "ik_curve"
    base_dynamics_curve_base_name = "base_dynamics_curve"
    ik_spline_base_name = "spline_handle"
    control_joint_base_name = "ctrl_jnt"
    ik_control_base_name = "IK_ctrl"
    blend_shape_base_name = "bShape"
    dynamic_control_base_name = "DYN_ctrl"
    dynamic_switch_base_name = "switch_ctrl"
    control_scale = .25
    control_axis = (1, 0, 0)

    joint_chain = cmds.ls(sl=True)

    ik_curve = create_curve_from_joints(joint_chain, base_curve_base_name)
    base_dynamics_curve = \
        cmds.duplicate(ik_curve, n=ik_curve.replace(base_curve_base_name, base_dynamics_curve_base_name), rr=True)[0]
    ik_spline_handle = create_ik_spline(joint_chain, ik_curve, ik_spline_base_name)
    control_joints = create_control_joints(joint_chain, control_joint_base_name)

    bind_ik_curve_to_control_joints(control_joints, ik_curve)
    ik_control_grp = create_control_joint_controls(control_joints, ik_control_base_name, control_scale, control_axis)

    create_ik_stretch_system(ik_curve, joint_chain)
    hair_system_objects = create_hair_system(base_dynamics_curve, base_dynamics_curve_base_name)

    ik_dyn_blend_shape = create_ik_dyn_blend_shape(ik_curve, hair_system_objects[3], base_curve_base_name,
                                                   blend_shape_base_name)

    dynamic_control_grp = create_dynamics_controls(joint_chain, base_dynamics_curve, dynamic_control_base_name,
                                                   control_scale, control_axis)

    switch_control = create_switch_control(joint_chain[0], dynamic_switch_base_name, control_scale, control_axis)

    switch_attributes = create_switch_attributes(switch_control)

    connect_attributes(switch_attributes, ik_control_grp, dynamic_control_grp, ik_dyn_blend_shape,
                       hair_system_objects[3], hair_system_objects[0])
