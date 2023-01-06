import maya.cmds as cmds
import Maya_Functions.light_util_functions as lightUtil

from Log.CoboLoggers import getLogger
logger = getLogger()


def lightUniqueToAssetButton():
    selection = cmds.ls(sl=True, long=True)
    light = selection[0]
    if cmds.listRelatives(light, shapes=True)[0] in lightUtil.getLights():
        asset_names = []
        assets = getAssets()
        for node in selection[1:]:
            asset_name = node.split('|')[-1].split(':')[-2]
            if asset_name in assets.keys() and asset_name not in asset_names:
                asset_names.append(asset_name)
        if light and asset_names:
            # Print
            _string = str(light.split('|')[-1]) + ' now only affects '
            for i, asset_name in enumerate(asset_names):
                if i == (len(asset_names) - 1):
                    _string = _string + str(asset_name)
                elif i == (len(asset_names) - 2):
                    _string = _string + str(asset_name)  + ' and '
                else:
                    _string = _string + str(asset_name) + ', '
            print(_string)
        # Action
        makeLightUniqueToAssets(light, asset_names)
    else:
        print('ERROR: Not a valid light as first selection')



def function():
    return "Hello World"

def lightUniqueToSelectionButton():
    selection = cmds.ls(sl=True, long=True)
    light = selection[0]

    # Action
    makeLightUniqueToSelection(light, selection[1:])

def resetLightButton():
    selection = cmds.ls(sl=True, long=True)
    light = selection[0]
    if cmds.listRelatives(light, shapes=True)[0] in lightUtil.getLights():
        resetLight(light)
    else:
        print('ERROR: Not a valid light as first selection')

###################################################
# Functions for light linking based on namespaces
def getAssets():
    assets = {}
    for node in cmds.ls('::*.asset_name', long=True):
        assets[node.split('|')[-1].split(':')[-2]] = node.replace('.asset_name', '')
    for node in cmds.ls('::*.assetName', long=True):
        assets[node.split('|')[-1].split(':')[-2]] = node.replace('.assetName', '')
    return assets


def makeLightUniqueToAssets(light, asset_names):
    if cmds.objExists(light):
        light = cmds.ls(light, long=True)[0]
        assets = getAssets()
        nodes = []
        shadingNodes = []
        for asset_name in asset_names:
            nodes.append(assets[asset_name])

            try:
                yetiShapes = cmds.listRelatives(assets[asset_name], allDescendents=True, fullPath=True, type='pgYetiMaya')
            except:
                yetiShapes = None

            if yetiShapes:
                for yetiShape in yetiShapes:
                    yetiNode = cmds.listRelatives(yetiShape, parent=True, fullPath=True)[0]
                    nodes.append(yetiNode)

            for cur_node in cmds.listRelatives(assets[asset_name], allDescendents=True, fullPath=True, type='transform'):
                shape = cmds.listRelatives(cur_node, shapes=True, fullPath=True)
                if shape:
                    shadingEngineNodes = cmds.listConnections(shape, type='shadingEngine')
                    if shadingEngineNodes:
                        shadingNodes = shadingNodes + shadingEngineNodes


        setName = name = 'objectSet_' + str(light.split('|')[-1].split(':')[-1])
        if not cmds.objExists(setName):
            cmds.sets(name=setName, empty=True)
            nodesFromSet = cmds.sets(setName, query=True)
            if nodesFromSet:
                for nodeFromSet in nodesFromSet:
                    cmds.sets(nodeFromSet, remove=setName)
        for node in nodes + shadingNodes:
            cmds.sets(node, addElement=setName)


        lightUtil.clearLightLinks(light)
        targetList = [setName] + nodes + shadingNodes
        lightUtil.addLightLink(light, targetList)
        # lightUtil.addLightLink(light, setName)
        # lightUtil.addLightLink(light, nodes)
        # lightUtil.addLightLink(light, shadingNodes)


def makeLightUniqueToSelection(light, objects):
    if cmds.objExists(light):
        light = cmds.ls(light, long=True)[0]
        nodes = []
        shadingNodes = []
        for object in objects:
            nodes.append(object)
            yetiShapes = cmds.listRelatives(object, allDescendents=True, fullPath=True, type='pgYetiMaya')
            if yetiShapes:
                for yetiShape in yetiShapes:
                    yetiNode = cmds.listRelatives(yetiShape, parent=True, fullPath=True)[0]
                    nodes.append(yetiNode)

            transNodes = cmds.listRelatives(object, allDescendents=True, fullPath=True, type='transform')
            if transNodes:
                for cur_node in transNodes:
                    shape = cmds.listRelatives(cur_node, shapes=True, fullPath=True)
                    if shape:
                        shadingEngineNodes = cmds.listConnections(shape, type='shadingEngine')
                        if shadingEngineNodes:
                            shadingNodes = shadingNodes + shadingEngineNodes


        setName = name = 'objectSet_' + str(light.split('|')[-1].split(':')[-1])
        if not cmds.objExists(setName):
            cmds.sets(name=setName, empty=True)
            nodesFromSet = cmds.sets(setName, query=True)
            if nodesFromSet:
                for nodeFromSet in nodesFromSet:
                    cmds.sets(nodeFromSet, remove=setName)
        for node in nodes + shadingNodes:
            cmds.sets(node, addElement=setName)

        lightUtil.clearLightLinks(light)
        targetList = [setName] + nodes + shadingNodes
        lightUtil.addLightLink(light, targetList)
        # lightUtil.addLightLink(light, setName)
        # lightUtil.addLightLink(light, nodes)
        # lightUtil.addLightLink(light, shadingNodes)


def resetLight(light):
    if cmds.objExists(light):
        setName = name = 'objectSet_' + str(light.split('|')[-1].split(':')[-1])
        if cmds.objExists(setName):
            nodesFromSet = cmds.sets(setName, query=True)
            if nodesFromSet:
                for nodeFromSet in nodesFromSet:
                    cmds.sets(nodeFromSet, remove=setName)
            cmds.delete(setName)

        lightUtil.affectAll(light)

