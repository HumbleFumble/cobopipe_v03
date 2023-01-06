import maya.cmds as cmds
import random

def createAnimLayers():
    assets = cmds.ls('::Root_Group', assemblies=True)
    colors = [4, 6, 9, 13, 14, 17, 18, 19, 20, 22, 31]
    random.shuffle(colors)
    for i, asset in enumerate(assets):
        name = asset.split(':')[-2] + '_Ctrls'
        ctrl_groups = []
        children = cmds.listRelatives(asset, allDescendents=True, fullPath=True)
        for child in children:
            if child.endswith(':Ctrl_Group'):
                ctrl_groups.append(child)
        if ctrl_groups:
            if not cmds.objExists(name):
                layer = cmds.createDisplayLayer(ctrl_groups, name = name)
                while i > 10:
                    i = i - 11
                #cmds.setAttr(layer + '.color', 0)
                # Now animators DO like colors??
                cmds.setAttr(layer + '.color', colors[i])


