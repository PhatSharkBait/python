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
        for shape in selectionShape:
            cmds.setAttr(selection + "|" + shape + ".overrideEnabled", True)
            cmds.setAttr(selection + "|" + shape + ".overrideRGBColors", True)
            cmds.setAttr(selection + "|" + shape + ".overrideColorR", values[0])
            cmds.setAttr(selection + "|" + shape + ".overrideColorG", values[1])
            cmds.setAttr(selection + "|" + shape + ".overrideColorB", values[2])


if __name__ == '__main__':
    main()
