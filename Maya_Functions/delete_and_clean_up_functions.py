try:
    import maya.cmds as cmds
    import maya.mel as mel
except Exception as e:
    print(e)

from getConfig import getConfigClass
CC = getConfigClass()

from Log.CoboLoggers import getLogger
logger = getLogger()


def DeleteEverythingBesidesPublishSet():
    cmds.sets(cmds.ls(assemblies=True, ud=True), n="everything")
    # if CheckPublishSet():
    delete_list = cmds.sets("PublishSet", sub="everything")
    logger.info("FULL DELETE LIST: %s" % delete_list)
    DeleteListAndChildren(delete_list)

def DeleteUnusedKeyframes():
    nodes_before = len(cmds.ls(dep=True))
    logger.info("Trying to delete unused keyframes; node amount before: %s" % nodes_before)

    mel.eval("cleanUpScene online")
    anim_curves = r'deleteUnusedCommon( "animCurve", 0,(uiRes("m_cleanUpScene.kDeletingUnusedAnimationCurves")));'
    group_id = r'deleteUnusedCommon( "groupId", 0,(uiRes("m_cleanUpScene.kDeletingUnusedGroupIDNodes")));'
    mel.eval(anim_curves)
    mel.eval(group_id)
    nodes_after = len(cmds.ls(dep=True))
    logger.info("Finished Remove keyframes, node amount after: %s" % nodes_after)

def DeleteKeyframes(time_start,time_end):
    try:
        anim_keys = cmds.ls(type=["animCurveTA", "animCurveTU", "animCurveTL"])
        cmds.cutKey(anim_keys, t=(time_start, time_end))
    except:
        logger.error("tryed to delete keyframes: %s-%s, but failed!" % (time_start,time_end))

def optimizeScene():
    import maya.mel as mel
    mel.eval('cleanUpScene(3)')

def DeleteListAndChildren(delete_list):  # a recursive function to delete the given list and all the children
    if delete_list:
        for c_obj in delete_list:
            if cmds.objExists(c_obj):
                logger.info("Deleting: %s" % c_obj)
                cmds.lockNode(c_obj, lock=False)
                cmds.delete(c_obj)
            # try:
            # 	cmds.delete(c_obj)
            # except:
            # 	print("CAN*T!")
            # 	DeleteListAndChildren(cmds.listRelatives(c_obj, c=True, f=True))
            # 	if cmds.objExists(c_obj):
            # 		cmds.delete(c_obj)
            if cmds.objExists(c_obj):
                DeleteListAndChildren(cmds.listRelatives(c_obj, c=True, f=True))
                if cmds.objExists(c_obj):
                    logger.info("Deleting: %s" % c_obj)
                    cmds.delete(c_obj)


def DeleteImagePlanes():  # Anim Publish, Deletes Imageplanes.
    for image_plane in cmds.ls(type="imagePlane"):
        cmds.delete(image_plane)


def DeleteOldAiExpressions():
    logger.info("Delete old aiPrevis expression")
    a_exp = cmds.ls("*aiPrevis_*", type="expression")
    cmds.delete(a_exp)

def deleteAllLights():
    logger.debug("Importing light_util")
    import Maya_Functions.light_util_functions as light_util
    logger.debug("Fetching all lights in scene")
    all_lights = light_util.getLights(dag=True, longName=True)
    logger.debug("Looping for light in all lights")
    for l in all_lights:
        logger.debug("If light exists")
        if not cmds.objExists(l):
            logger.debug("If light not referenced")
            if not cmds.referenceQuery(l, inr=True):
                logger.debug("Attempting to get light parent")
                p = cmds.listRelatives(l, parent=True, fullPath=True)
                logger.debug("If list of parents")
                if p:
                    logger.debug("List of parent = Parent[0]")
                    p = p[0]
                try:
                    logger.debug("Trying to delete light")
                    cmds.delete(l)
                    logger.debug("Trying to delete parent of light")
                    cmds.delete(p)
                except:
                    logger.debug("Can't delete: %s" % l)
    logger.debug("End of function")


def deleteSunAndSky():
    delete_list = []
    for sun in cmds.ls(type='VRayGeoSun'):
        sunTransform = cmds.listRelatives(sun, parent=True)[0]
        delete_list.append(sun)
        if sunTransform:
            delete_list.append(sunTransform)

    for sky in cmds.ls(type='VRaySky'):
        delete_list.append(sky)

    ref_issue_list = []
    for item in delete_list:
        if not cmds.referenceQuery(item, isNodeReferenced=True):
            if cmds.objExists(item):
                cmds.delete(item)
        else:
            ref_issue_list.append(cmds.referenceQuery(item, filename=True))

    for ref in ref_issue_list:
        logger.info('Reference contains VRaySun or VRaySky: ' + ref)


def DeleteDisplayLayers():  # Delete display layers
    cur_layers = cmds.ls(type="displayLayer")
    for lay in cur_layers:
        if "defaultLayer" in lay:
            continue
        try:
            find_members = cmds.editDisplayLayerMembers(lay, q=True, fn=True)
            logger.info("For %s - Found members: %s" % (lay, find_members))
            cmds.delete(lay)
            # clear_old_overrides
            SetDisplayOverride(obj_list=find_members)
        except:
            logger.info("Can't delete %s. Needs to be removed in Ref" % lay)

def cleanProjectUniques(project_name=None,publish_step=None):
    if project_name == "MiasMagic2":
        if publish_step == "Anim":
            DeleteAttrs(["highlightVisibility","highlightOffset","highlightSize","highlightRadius", "highlightExtend"])
        if publish_step == "AnimPublish":
            DeleteKeyOnAttr(["highlightVisibility","highlightOffset","highlightSize","highlightRadius", "highlightExtend"])
            # import Maya_Functions.ref_util_functions as ref_util
            # ref_util.RemoveRefEdit(search_filter=["highlightVisibility","highlightOffset","highlightSize","highlightRadius"],attr_cmds=["setAttr"])

def DeleteAttrs(attr_list=None):
    if attr_list:
        for a in attr_list:
            cur_attrs = cmds.ls("::*.%s" % a, l=True)
            logger.debug("Looking for %s, Found: %s" % (a, cur_attrs))
            for cur_at in cur_attrs:
                logger.info("Removing Attrs: %s" % cur_at)
                cmds.deleteAttr(cur_at)


def DeleteKeyOnAttr(attr_list=[],obj=None,time_start_end=[]):
    # attr_list = ["highlightVisibility","highlightOffset","highlightSize","highlightRadius"]
    logger.info("Trying to cut keys on %s" % attr_list)
    for a in attr_list:
        if not obj:
            attr_plugs = cmds.ls("::*.%s" % a)
        else:
            attr_plugs = "%s.%s" % (obj,a)
        logger.debug("Found attrs to delete from")
        for p in attr_plugs:
            cur_obj, cur_a = p.split(".")
            logger.debug("Trying to Cut Key on %s" % p)
            if not time_start_end:
                cmds.cutKey(cur_obj, attribute=cur_a, option="keys")
            else:
                cmds.cutKey(cur_obj, attribute=cur_a, option="keys",t=(time_start_end[0], time_start_end[1]))

            # cur_cons = cmds.listConnections(p, s=True, d=False)
            # for con in cur_cons:
            #     if cmds.objectType(con) in ["animCurveTL", "animCurveTU", "animCurveTA", "animCurveTT"]:
            #         try:
            #             print("Trying to delete key: %s" % con)
            #             cmds.delete(con)
            #         except:
            #             print("Couldn't delete key %s" % con)


def SetDisplayOverride(obj_list=None, cur_value=0):
    for cur_obj in obj_list:
        logger.info("Trying to set display override off on: %s" % cur_obj)
        cmds.setAttr("%s.overrideEnabled" % cur_obj, cur_value)


def DeleteAnimLayers():  # Delete anim layers
    anim_layers = cmds.ls(type="animLayer")
    for cur_layer in anim_layers:
        if cmds.objExists(cur_layer):
            cmds.delete(cur_layer)

def DeleteGraphNodes():
    graph_nodes = cmds.ls(type="nodeGraphEditorInfo")
    for gn in graph_nodes:
        try:
            if not gn == 'MayaNodeEditorSavedTabsInfo':
                cmds.delete(gn)
        except:
            logger.debug("Couldn't delete: %s" % gn)

def DeleteUnknown(also_dag=True):  # Try to delete unknown nodes and plugins
    unknown = cmds.ls(type="unknown")
    if also_dag:
        unknown.extend(cmds.ls(type="unknownDag"))
    for un in unknown:
        if cmds.objExists(un):
            plg_orig = cmds.unknownNode(un, q=True, plugin=True)
            logger.info("Deleting %s as it is unknown. It came from: %s" % (un, plg_orig))
            cmds.delete(un)
    unplug = cmds.unknownPlugin(q=True, list=True)
    if unplug:
        for p in unplug:
            logger.info("Removing %s as it is unknown Plugin" % p)
            cmds.unknownPlugin(p, remove=True)


def DeleteUnusedNodes():  # Delete unused nodes. Same as "Delete Unused Nodes" in the hypershader
    logger.info("Trying to delete unused nodes!")
    mel.eval("MLdeleteUnused;")


def DeleteVrayRenderInfo():  # Delete Render settings added in scene, to avoid complications in Light Scene.
    logger.info("Trying to delete vray elements")
    res = cmds.ls(type="VRayRenderElement")
    for re in res:
        cmds.delete(re)
    if cmds.objExists("vrayEnvironmentPreviewTm"):
        cmds.delete("vrayEnvironmentPreviewTm")

def DeleteVraySettings():
    if cmds.objExists("vraySettings"):
        cmds.delete("vraySettings")


def CleanNamespaces(only_empty=True):  # Publish Set: Tries to remove empty namespaces to avoid clutter
    all_ns = cmds.namespaceInfo(listOnlyNamespaces=True, an=True, recurse=True)
    all_ns = list(reversed(sorted(all_ns)))
    for ns in all_ns:
        if not ns == ":shared" and not ns== ":UI":
            if only_empty:
                if not cmds.namespaceInfo(ns, ls=True) == None:
                    continue
                logger.info("Found empty namespace: %s" % ns)
            cmds.namespace(rm=ns, mnp=True)


def RemoveNamespaceOfPreviousStep(cur_asset_dict=None):
    # Meant to remove the namespaces of the steps. ("Model" namespace in Rig file/"Rig" ns in Shading file)
    if cur_asset_dict:
        all_steps = CC.ref_order[cur_asset_dict["asset_type"]]
        cur_index = all_steps.index(cur_asset_dict["asset_step"])
        if cur_index > 0:
            remove_ns = all_steps[cur_index - 1]
            if cmds.namespace(ex=remove_ns):
                cmds.namespace(rm=remove_ns, mnr=True)


def RemoveArnold():  # Try to remove Arnold pluging from scene.
    is_arnold = cmds.pluginInfo("mtoa", q=True, loaded=True)
    logger.info("Arnold is loaded: %s" % is_arnold)
    if is_arnold:
        ai_path = cmds.pluginInfo("mtoa", q=True, path=True)
        cmds.pluginInfo(ai_path, e=True, writeRequires=False)

        arnold_nodes = cmds.pluginInfo("mtoa", q=True, dn=True)
        arnold_in_scene = cmds.ls(type=arnold_nodes)
        for an in arnold_in_scene:
            if cmds.objExists(an):
                logger.info("Deleting: %s " % an)
                cmds.delete(an)
    # cmds.unloadPlugin("mtoa", f=True) #force unload of arnold. Has a tendency to make maya a bit unstable
    DeleteUnknown()


def RemoveYetiPlugin():
    is_yeti = cmds.pluginInfo("pgYetiMaya", q=True, loaded=True)
    logger.info("Is Yeti Loaded: %s" % is_yeti)
    if is_yeti:
        yeti_path = cmds.pluginInfo("pgYetiMaya", q=True, path=True)
        cmds.pluginInfo(yeti_path, e=True, writeRequires=False)

        yeti_nodes = cmds.pluginInfo("pgYetiMaya", q=True, dn=True)
        yeti_in_scene = cmds.ls(type=yeti_nodes)
        if not yeti_in_scene:
            logger.info("No yeti nodes in scene, trying to unload plugin")
            cmds.unloadPlugin("pgYetiMaya")
            DeleteUnknown()
            cmds.setAttr("defaultRenderGlobals.preMel", "", type="string")
            cmds.setAttr("defaultRenderGlobals.postMel", "", type="string")


# if not "pgYetiMaya" in cmds.pluginInfo(q=True, pluginsInUse=True):
# 	cmds.setAttr("defaultRenderGlobals.preMel", "",type="string")
# 	cmds.setAttr("defaultRenderGlobals.postMel", "",type="string")


def DeleteRenderLayers():  # try to delete default render layer
    import maya.app.renderSetup.model.renderSetup as renderSetup
    rs = renderSetup.instance()
    rs.clearAll()

    cur_layers = cmds.ls(type="renderLayer")
    for lay in cur_layers:
        try:
            cmds.delete(lay)
        except:
            logger.info("Can't delete %s. Needs to be removed in Ref" % lay)


def DeleteAnimKeysOnCtrls():
    ctrl_objs = cmds.ls("*_Ctrl", type="transform")
    and_CTRL_objs = cmds.ls("*_CTRL",type="transform")
    ctrl_objs.extend(and_CTRL_objs)
    for ctrl in ctrl_objs:
        key_list = cmds.keyframe(ctrl, query=True, name=True)
        if key_list != None:
            for key in key_list:
                try:
                    cmds.delete(key)
                except:
                    pass


def DeleteManagerNodes():
    cmds.delete(cmds.ls(type="shapeEditorManager"))
    cmds.delete(cmds.ls(type="poseInterpolatorManager"))


def GeoGroup_Removing_Model():  # Asset Publish: Try to unparent children of geo_group and then delete it.
    if cmds.objExists("Geo_Group"):
        my_list = cmds.listRelatives("Geo_Group", type="transform", fullPath=True)
        if my_list:
            for cur in my_list:
                cmds.parent(cur, world=True)
        cmds.lockNode("Geo_Group", lock=False)
        cmds.delete("Geo_Group")

def hardcoreClean(clearHistory=False):
    # Delete non-deformer history
    if clearHistory:
        mel.eval("BakeAllNonDefHistory")

    # Delete LightStudioA
    target = cmds.ls('LightStudioA:*', long=True)
    for node in target:
        try:
            cmds.delete(node)
        except:
            pass

    DeleteUnknown()

    DeleteUnusedNodes()

    optimizeScene()

    # Delete garbage nodes
    for nodeType in ['sequencer', 'shapeEditorManager', 'poseInterpolatorManager', 'trackInfoManager',
                     'gameFbxExporter']:
        for node in cmds.ls(type=nodeType, long=True):
            if ':' in node:
                try:
                    cmds.delete(node)
                except:
                    pass