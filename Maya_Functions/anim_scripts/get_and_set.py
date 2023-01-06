import maya.cmds as cmds

attributes = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']

def getPosition():
    controller = cmds.ls(sl=True, long=True)[0]
    if controller == None:
        print('Nothing selected')
    else:
        position = cmds.xform(controller, ws=True, matrix=True, query=True)
        cmds.xform(controller, ws=True, matrix=position)
        for attribute in attributes:
            cmds.setKeyframe(controller, attribute=attribute)
        return position

def setPosition(position):
    controller = cmds.ls(sl=True, long=True)[0]
    if controller == None:
        print('Nothing selected')
    else:
        currentFrame = cmds.currentTime(query=True)
        cmds.currentTime(currentFrame+1, edit=True)
        cmds.xform(controller, ws=True, matrix=position)
        for attribute in attributes:
            cmds.setKeyframe(controller, attribute=attribute)