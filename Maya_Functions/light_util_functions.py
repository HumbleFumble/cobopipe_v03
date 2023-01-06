import maya.cmds as cmds


# Returns all nodes affected by a given light
def affectedByLight(light):
    nodes = cmds.lightlink(light=light, query=True, shapes=False)
    return nodes

# Returns all lights affecting object
def affectingObject(object):
    lights = cmds.lightlink(object=object, query=True, shapes=False)
    return lights


# Links object to a light
def addLightLink(light, object):
    cmds.lightlink(light=light, object=object, m=True)
    return True


# Removes link between object and light
def removeLightLink(light, object):
    cmds.lightlink(light=light, object=object, b=True)
    return True


# Toggles link between object and light
def toggleLightLink(light, object):
    if object in affectedByLight(light):
        removeLightLink(light, object)
    else:
        addLightLink(light, object)
    return True


# Clears all light links from given light
def clearLightLinks(light):
    affectedNodes = affectedByLight(light)
    nodeList = []
    for node in affectedNodes:
        if cmds.objectType(node) in ['transform', 'shadingEngine']:
            nodeList.append(node)
    removeLightLink(light, nodeList)
    return True


# Clear all light links to given object
def clearLightLinksToObject(object):
    lights = affectingObject(object)
    removeLightLink(lights, object)
    return True


# Links light to everything
def affectAll(light):
    transformNodes = cmds.ls(type='transform', long=True)
    shadingEngineNodes = cmds.ls(type='shadingEngine', long=True)
    addLightLink(light, transformNodes)
    addLightLink(light, shadingEngineNodes)
    return True


# Links given object to every light
def allAffect(object):
    addLightLink(getLights(), object)
    return True


# Reset light links in scene
def resetSceneLightLinks():
    affectAll(getLights())
    return True


# Unlinks all lights from everything
def removeAllLightLinks():
    clearLightLinks(getLights())
    return True


# Removes all light links from light and reestablishing to given objects
def lightOnlyAffects(light, object):
    clearLightLinks(light)
    addLightLink(light, object)
    return True



# Code by BigRoyNL
# Copied from https://forums.cgsociety.org/t/maya-python-get-all-lights-in-the-scene/1616306
def getLights(dag=True, longName=False):
    """
        Returns a list of node types that classify as 'light'

        :param dag: If dag is True then returned types will only be dag/shape types
        :type  dag: bool

        :rtype: list
        :return: List of available light shape types.
    """
    return cmds.ls(type=["light"] + cmds.listNodeTypes("light"), dag=dag, long=longName)


def getLightTypes(dag=True):
    """
        Returns a list of node types that classify as 'light'

        :param dag: If dag is True then returned types will only be dag/shape types
        :type  dag: bool

        :rtype: list
        :return: List of available light shape types.
    """
    if dag:
        return list(set(cmds.nodeType("shape", derived=True, isTypeName=True)).intersection(cmds.listNodeTypes("light")))
    else:
        return cmds.listNodeTypes("light")

def createNewVFXScene():
    """
    run this in an open ligth scene, for easily create extra light-scenes for extra render stuff.
    :return:
    """
    import os
    cur_scene = cmds.file(q=True,sn=True)
    get_new_name = None
    from PySide2 import QtWidgets
    text, ok = QtWidgets.QInputDialog().getText(QtWidgets.QInputDialog(),"Save VFX As:", "example: VFX",
                                                QtWidgets.QLineEdit.Normal, "")
    if ok and text and not text == "" and not text == "":
        get_new_name = text
    else:
        return False
    if get_new_name:
        scene_name = "%s_%s_Light.ma" %(cur_scene.split("_Light.ma")[0],get_new_name)
        if os.path.exists(scene_name):
            cmds.warning("FILE ALREADY EXISTS! ABORTING!")
            return False
        else:
            import Maya_Functions.file_util_functions as file_util
            file_util.PrepareForSave(scene_name,True)
            cmds.file(save=True)


def checkForSunAndSkyRefs():
    delete_list = []
    for sun in cmds.ls(type='VRayGeoSun', long=True):
        sunTransform = cmds.listRelatives(sun, parent=True, fullPath=True)[0]
        delete_list.append(sun)
        if sunTransform:
            delete_list.append(sunTransform)

    for sky in cmds.ls(type='VRaySky', long=True):
        delete_list.append(sky)

    ref_issue_list = []
    for item in delete_list:
        if cmds.referenceQuery(item, isNodeReferenced=True):
            ref_issue_list.append(cmds.referenceQuery(item, filename=True))

    for node in ref_issue_list:
        print(node)


def selectAllLightInScene():
    import Maya_Functions.light_util_functions as luf
    lights = luf.getLights()
    selectGroup = []
    for light in lights:
        selectGroup.append(cmds.listRelatives(light, parent=True)[0])
    for sky in cmds.ls(type='VRaySky'):
        selectGroup.append(sky)
    cmds.select(selectGroup)


# def addYetiShaders(object):
#     nodes = []
#     shaders = []
#     if type(object) == type(''):
#         nodes.append(object)
#     else:
#         for item in object:
#             nodes.append(item)
#
#     if nodes:
#         for node in nodes:
#             yetiNodes = cmds.listRelatives(node, allDescendents=True, type='pgYetiMaya', fullPath=True)
#             if yetiNodes:
#                 for yetiNode in yetiNodes:
#                     shadingNodes = cmds.listConnections(yetiNode, type='shadingEngine')
#                     if shadingNodes:
#                         for shadingNode in shadingNodes:
#                             shaders.append(shadingNode)
#
#     return nodes + shaders