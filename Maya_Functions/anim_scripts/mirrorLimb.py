import maya.cmds as cmds


def mirrorLimb():
    selected = cmds.ls(sl=True, long=True)
    source = selected[0]
    target = selected[1]
    mirrorAxis = [-1, 1, 1]
    translateValues = cmds.xform(source, query=True, t=True)
    rotateValues = cmds.xform(source, query=True, ro=True)
    for i, axis in enumerate(mirrorAxis):
        if 'Foot' not in source.split('|')[-1] and 'Foot' not in target.split('|')[-1]:
            translateValues[i] = translateValues[i] * axis
            rotateValues[i] = rotateValues[i] * axis * -1

    cmds.xform(target, t=translateValues)
    cmds.xform(target, ro=rotateValues)