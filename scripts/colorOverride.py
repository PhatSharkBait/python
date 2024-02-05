import maya.cmds as cmds


def main():
    cmds.colorEditor()
    if cmds.colorEditor(query=True, result=True):
        values = cmds.colorEditor(query=True, rgb=True)
        change_colors(values)
    else:
        cmds.warning("color editor was dismissed")


def change_colors(values):
    sels = cmds.ls(selection=True)
    for selection in sels:
        selectionShape = cmds.listRelatives(selection, s=True)
        cmds.setAttr(selectionShape[0] + ".overrideEnabled", True)
        cmds.setAttr(selectionShape[0] + ".overrideRGBColors", True)
        cmds.setAttr(selectionShape[0] + ".overrideColorR", values[0])
        cmds.setAttr(selectionShape[0] + ".overrideColorG", values[1])
        cmds.setAttr(selectionShape[0] + ".overrideColorB", values[2])


if __name__ == '__main__':
    main()
