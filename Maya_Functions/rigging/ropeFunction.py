import maya.cmds as cmds

def rope(numberOfJoints, spaceBetween, alongAxis, controllersRadius, step):
    index = 0
    jointList = []
    for i in range(numberOfJoints):
        if alongAxis is 'x':
            jointList.append(cmds.joint(name='joint_' + str(i + 1) + '_jnt', position=[index, 0, 0]))
        elif alongAxis is 'y':
            jointList.append(cmds.joint(name='joint_' + str(i + 1) + '_jnt', position=[0, index, 0]))
        elif alongAxis is 'z':
            jointList.append(cmds.joint(name='joint_' + str(i + 1) + '_jnt', position=[0, 0, index]))
        index += spaceBetween

    jointPositions = []
    jointStep = []
    for i in range(0, len(jointList) - 1, step):
        jointPositions.append(cmds.xform(jointList[i], query=True, worldSpace=True, rotatePivot=True))
        jointStep.append(jointList[i])

    ctrlList = []
    for i, j in zip(jointStep, jointPositions):  # Create controllers, rename and position them on the joints
        cmds.xform(cmds.circle(name=i[:-4] + '_ctrl', radius=controllersRadius), translation=j)
        ctrlList.append(i[:-4] + '_ctrl')
    for i in ctrlList:
        if alongAxis is 'x':
            cmds.circle(i, edit=True, normal=[1, 0,
                                              0])  # Set normal orientation for the controllers based on primary axis orientation
        elif alongAxis is 'y':
            cmds.circle(i, edit=True, normal=[0, 1, 0])
        elif alongAxis is 'z':
            cmds.circle(i, edit=True, normal=[0, 0, 1])

    offsetList = []
    for i, j in zip(ctrlList, jointStep):
        offsetList.append(cmds.group(i, name=i[:-4] + 'offset'))  # Group each controller and add the name to a list

    for i, j, o in zip(ctrlList, jointStep, offsetList):
        cmds.matchTransform(o, j)
        cmds.makeIdentity(o, apply=True, translate=True)  # Freeze transformations
        cmds.makeIdentity(i, apply=True)  # Freeze transformations
        cmds.delete(i, constructionHistory=True)  # Delete construction history
        cmds.parentConstraint(i, j, maintainOffset=True)  # Constrain joints to controls

    for i, j in zip(ctrlList[:-1], offsetList[:-1]):  #
        offset = offsetList[offsetList.index(j) + 1]
        ctrl = ctrlList[ctrlList.index(i)]
        cmds.parent(offset, ctrl)  # Parent controls under each other

    for i in ctrlList:
        for j in jointList:
            if i[:-4] in j:
                for each in range(step):
                    cmds.connectAttr(i + '.rotate', jointList[jointList.index(j) + each] + '.rotate', force=True)

    for i, j in zip(jointStep[1:], offsetList[1:]):
        if i in jointList:
            cmds.parentConstraint(jointList[jointList.index(i) - 1], j, mo=True, w=1)
