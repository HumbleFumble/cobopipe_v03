try:
    import maya.cmds as cmds
except:
    pass
from Log.CoboLoggers import getLogger
logger = getLogger()


def CreateOnlyBGExceptionSet(object_list=None):
    AddToSet("OnlyBG_Exception" ,object_list)


def DeleteAllInSet(cur_set):
    s_objs = FindObjectsFromSet(cur_set)
    if s_objs:
        for obj in s_objs:
            if cmds.objExists(obj):
                # print("Deleting: %s" % obj)
                cmds.delete(obj)


def DeleteSets():  # Used to clean away publish set and other work sets
    my_sets = cmds.ls(exactType="objectSet")
    logger.info("All sets: %s " % my_sets)
    exclude_list = []
    for obj in my_sets:  # go through and try to determine if the set is used behind the scenes (clusters and so on)
        if cmds.listConnections(obj, type="groupId"):
            logger.info("Excluding because of groupID: %s " % obj)
            if not "_Weight" in obj:
                exclude_list.append(obj)
        else:
            if "yetiGroom" in obj or "Guide_Set" in obj:
                logger.warning("Removed object: ", obj)
                exclude_list.append(obj)

    my_sets = [i for i in my_sets if i not in exclude_list]
    if my_sets:
        logger.info("Deleting sets: %s " % my_sets)
        cmds.lockNode(my_sets, lock=False)
        cmds.delete(my_sets)


def AddToSet(set_name, selection=None):
    if not selection:
        selection = cmds.ls(sl=True)
    if not cmds.objExists(set_name):
        cmds.sets(n=set_name, empty=True)
    cmds.sets(selection, add=set_name)


def RemoveFromSet(set_name,selection=None):
    if cmds.objExists(set_name):
        if not selection:
            selection = cmds.ls(sl=True)
        cmds.sets(selection, rm=set_name)


def FindObjectsFromSet(set_name):
    import maya.cmds as cmds
    if cmds.objExists(set_name):
        set_objs = cmds.sets(set_name, q=True)
        logger.info("Found in set %s : %s" % (set_name,set_objs))
        return set_objs
    else:
        return None


def CreateOIDSet(object_list=None, object_type=None, set_name=None, OID=None, use_force=True):
    from Maya_Functions.asset_util_functions import FindAssetTypeInScene
    from Maya_Functions.vray_util_functions import CreateVrayObjectSet,SetOIDonObjectSet
    selection = False
    if object_type:
        select_all = FindAssetTypeInScene(object_type)
    elif object_list:
        select_all = object_list
    else:
        select_all = None
        selection = True
    # if not cmds.objExists(set_name):
    #delete old set:

    CreateVrayObjectSet(set_name=set_name, obj_list=select_all, selection=selection, use_force=use_force)
    SetOIDonObjectSet(set_name, OID)

