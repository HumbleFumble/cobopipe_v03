import maya.cmds as cmds
from getConfig import getConfigClass

CC = getConfigClass()
from Log.CoboLoggers import getLogger

logger = getLogger()

def createSpaceSwitch(master_list=[],name_obj=None,name_list=[],target=None, attributeName=None):
    space_con = cmds.parentConstraint(master_list[0],target,mo=True)[0]
    for t in master_list[1:]:
        cmds.parentConstraint(t,target,mo=True)
    enum_string = ":".join(name_list)
    if not attributeName:
        attributeName = 'spaceSwitch'
    if not cmds.attributeQuery(attributeName, node=name_obj, exists=True):
        cmds.addAttr(name_obj, ln=attributeName, attributeType='enum', enumName=enum_string)
    for x in range(len(master_list)):
        cur_obj = master_list[x]
        c_node = cmds.shadingNode("condition",name="%s_%s" %(name_obj,name_list[x]),asUtility=True)
        cmds.setAttr("%s.secondTerm" % c_node,x)
        cmds.setAttr("%s.colorIfTrueR" % c_node, 1)
        cmds.setAttr("%s.colorIfFalseR" % c_node, 0)
        cmds.connectAttr("%s.%s" % (name_obj, attributeName),"%s.firstTerm" % c_node, force=True)
        cmds.connectAttr("%s.outColorR" % c_node,"%s.%sW%s" % (space_con, cur_obj.split(':')[-1], x), force=True)
        #Connect enum to condition #cmds.connectAttr()
        #connect condition to pcon weight