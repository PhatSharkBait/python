import maya.cmds as cmds


def main():
    template = input("joint name template in \"leg_##_jnt\" format\n")
    count = template.count('#')
    if is_valid_string(template, count):
        rename(template, count)


def rename(template, count):
    sels = cmds.ls(sl=True)
    if len(sels) <= 0:
        cmds.warning("No selection found")
    template_parts = template.partition('#' * count) #  leg_##_jnt  ("leg_", "##", "_jnt")
    for i in range(1, len(sels) + 1):
        new_name = template_parts[0] + str(i).zfill(count) + template_parts[2]
        cmds.rename((sels[i - 1]), new_name)


def is_valid_string(template, count):
    if count <= 0 or template.find('#' * count) <= 0:
        cmds.error("invalid format")
    return True


if __name__ == '__main__':
    main()
