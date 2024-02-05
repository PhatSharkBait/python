import maya.cmds as cmds


def set_object(text_field, *args):
    sels = cmds.ls(sl=True)
    text_field_text = ','.join(sels)
    cmds.textField(text_field, edit=True, text=text_field_text)


def create_window():
    window = 'copyNodeAttributes'

    windowUIkwargs = {"backgroundColor": (0.04, 0.11, 0.32)}
    buttonUIkwargs = {"backgroundColor": (0.50, 0.50, 0.50),
                      "highlightColor": (1.00, 0.81, 0.34),
                      "width": 150}
    textFieldUIkwargs = {"aie": True,
                         "backgroundColor": (0.30, 0.55, 0.75)}

    if cmds.window(window, exists=True):
        cmds.deleteUI(window)

    window = cmds.window(window, title="Copy Node Attributes", widthHeight=[400, 100], resizeToFitChildren=1,
                         **windowUIkwargs)

    main_column = cmds.columnLayout(parent=window, adjustableColumn=1)

    fields_column = cmds.columnLayout(parent=main_column, adjustableColumn=1)

    to_copy_label = cmds.text(parent=fields_column, label='Attributes to copy')
    to_copy_field = cmds.textField(to_copy_label, **textFieldUIkwargs)
    sel_to_copy_button = cmds.button("Node to copy = Selection",
                                     command=lambda *args: set_object(to_copy_field), **buttonUIkwargs)

    copy_to_label = cmds.text(parent=fields_column, label='Node to copy to')
    copy_to_field = cmds.textField(copy_to_label, **textFieldUIkwargs)
    sel_to_copy_to_button = cmds.button("Receiving Node = Selection",
                                        command=lambda *args: set_object(copy_to_field), **buttonUIkwargs)

    cmds.rowLayout(parent=main_column, numberOfColumns=2, columnWidth2=(100, 100),
                   columnAttach=[(1, 'both', 0), (2, 'both', 0)])
    run_button = cmds.button("Send it", command=lambda *args: copy_attributes([to_copy_field, copy_to_field]), **buttonUIkwargs)
    close_button = cmds.button("Close", command=lambda *args: close_window(window), **buttonUIkwargs)

    cmds.showWindow(window)
    return [[to_copy_field, copy_to_field]]


def close_window(window, *args):
    cmds.deleteUI(window)


def copy_attributes(input_fields):
    node_to_copy = cmds.textField(input_fields[0], q=True, text=True)
    node_to_copy_to = cmds.textField(input_fields[1], q=True, text=True)
    to_copy_attributes = cmds.listAttr(node_to_copy, sa=True, multi=True, nn=True, ca=True, o=True)
    node_to_copy_to_attributes = cmds.listAttr(node_to_copy_to, sa=True, multi=True, nn=True, ca=True, o=True)
    for i, attr in enumerate(to_copy_attributes):
        if not cmds.listConnections(attr, s=True, d=False):
            value = cmds.getAttr(attr)
            cmds.setAttr(attr.replace(node_to_copy, node_to_copy_to), value)


if __name__ == '__main__':
    create_window()
