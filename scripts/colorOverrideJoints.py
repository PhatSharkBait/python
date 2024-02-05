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
        cmds.setAttr(selection + ".overrideEnabled", True)
        cmds.setAttr(selection + ".overrideRGBColors", True)
        cmds.setAttr(selection + ".overrideColorR", values[0])
        cmds.setAttr(selection + ".overrideColorG", values[1])
        cmds.setAttr(selection + ".overrideColorB", values[2])


if __name__ == '__main__':
    main()
