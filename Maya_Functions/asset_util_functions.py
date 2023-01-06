# import Config_KiwiStrit3 as cfg
# import ConfigUtil
# cfg_util = ConfigUtil.ConfigUtilClass(cfg)
# import ConfigClass_KiwiStrit3
import maya.cmds as cmds
from Maya_Functions.general_util_functions import CheckAttribute, SetStringAttribute
from Log.CoboLoggers import getLogger
logger = getLogger()
from getConfig import getConfigClass
CC = getConfigClass()


def UpdateVrayScene():
    # !!! Remember to enable autosave in vray 'VFB-Settings' !!!
    # STEP 1-------------------------------------------------------------------------------
    if cmds.colorManagementPrefs(q=True, cme=True):
        answer = cmds.confirmDialog( title='Migrate', message='This scene was already migrated\nWould you like to proceed?', button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No')
        if answer == "No":
            cmds.warning("UpdateVrayScene: SCENE WAS ALREADY MIGRATED, CALL CANCELLED.")
            return

    # STEP 2-------------------------------------------------------------------------------
    if not any([i for i in cmds.file(q=True, r=True) if "Day_Render.mb" in i]):
        cmds.file("P:/930383_KiwiStrit3/Production/Assets/3D_Assets/Set/SkyDome/Day/02_Ref/Day_Render.mb", r=True, namespace="Day")

    import maya.mel as mel
    import maya.app.renderSetup.views.renderSetupPreferences as prefs
    prefs.loadUserPreset("KS_FastBrute_Linear")

    import Maya_Functions.yeti_util_functions as YF
    YF.setYetiPrePostRenderScripts()
    # if "vraySettings" in cmds.ls():
    #     cmds.delete("vraySettings")
    cmds.vrend()

    # STEP 3-------------------------------------------------------------------------------
    cmds.colorManagementPrefs(e=True, cme=True)
    cmds.colorManagementPrefs(cma=True)

    import vray.vray_migrate_script as vmig
    vmig.migratePortals()
    vmig.migrateLinearWorkflow()
    cmds.vrend()


def SetAssetAttrsBasedOnFile():  # Meant to gather the correct asset info to set on the root_group of an old asset
    cur_scene = cmds.file(q=True, sn=True)
    compare_path = CC.get_asset_work_file  # cfg_util.CreatePathFromDict(cfg.project_paths["asset_work_file"])
    attr_dict = CC.util.ComparePartOfPath(cur_scene, compare_path)
    return attr_dict

def CleanRootAttributes(scene_info={}):  # Deletes old attributes and set new ones based on the filepath
    from_file = SetAssetAttrsBasedOnFile()
    if cmds.objExists("Root_Group"):  # Rename root to top??
        DeleteOldRootAttributes()
        for key in scene_info.keys():
            cur_value = CheckAttribute("Root_Group", key)
            if not cur_value == from_file[key]:
                SetStringAttribute("Root_Group", key, from_file[key])


def RemoveVisibilityKeys():
    all_tops = cmds.ls("Anim:*:Root_Group")
    for top in all_tops:
        if cmds.attributeQuery("asset_type", n=top, ex=True):
            cmds.cutKey(top, attribute='visibility', option="keys")
            cmds.setAttr("%s.visibility" % top, 1)


def UnlockAndHideRigGroup():
    c_obj = "|Root_Group|Rig_Group"
    try:
        cmds.setAttr("%s.visibility" % c_obj, cb=True, l=False, k=True)
        cmds.setAttr("%s.visibility" % c_obj, 0)
    except:
        logger.warning("Couldn't hide Rig_Group")


def DeleteOldRootAttributes():  # meant to delete all Afilm attributes on root_groups from kiwiOgStrit1
    c_obj = "Root_Group"
    if cmds.objExists(c_obj):
        # unlock visibility so we can remove the aiVisibility attribute
        cmds.setAttr("%s.visibility" % c_obj, cb=True, l=False, k=True)
        u_attrs = cmds.listAttr(c_obj, ud=True)  # get all attributes that are user generated
        if u_attrs:
            for c_a in u_attrs:  # check for ai attribute
                if c_a.startswith("ai"):
                    cmds.deleteAttr(c_obj, at=c_a)  # delete it if possible

def countRefNodes():
    myrefs = cmds.file(q=True, r=True)
    count = 0
    for r in myrefs:
        ref_node = cmds.referenceQuery(r, rfn=True)
        if cmds.referenceQuery(r, il=True):
            namespace_r = cmds.referenceQuery(r, ns=True)
            # namespace_r = ref_node.split("RN")[0] + ref_node.split("RN")[-1]
            # print(":%s:*" % namespace_r)
            r_len = len(cmds.ls(":%s:*" % namespace_r, dep=True))
            print("%s \t\t %s" % (r_len, namespace_r))
            count = count + r_len
    print(count)

def freezeIngestGeo(set_name="FreezeGeo_Set"):
    if cmds.objExists(set_name):
        node_number = len(cmds.ls(dep=True))
        logger.info("FREEZING GEO: Nodes: %s" % node_number)
        objs = cmds.sets(set_name, q=True)
        for obj in objs:
            obj_namespace = ":".join(obj.split(":")[0:-1])
            cmds.duplicate(obj)
            delete_list = ["Ctrl_Group", "Rig_Group"]
            for d in delete_list:
                if cmds.objExists("%s:%s" % (obj_namespace, d)):
                    cmds.delete("%s:%s" % (obj_namespace, d))
            cmds.delete(obj)
        node_number = len(cmds.ls(dep=True))
        logger.info("FINISHED FREEZING GEO: Nodes: %s" % node_number)


def CleanRootGroup(cur_asset_info):
    c_obj = "|Root_Group"
    attr_order = ["asset_type", "asset_category", "asset_name"]

    c_root = "|Root_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl|Root_Ctrl_Group|Root_Ctrl"
    c_obj_super = "|Root_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl"

    for c_at in ["scaleX", "scaleY", "scaleZ"]:
        if cmds.objExists(c_root):
            cmds.setAttr("%s.%s" % (c_root, c_at), e=True, k=True, l=False)
        if cmds.objExists(c_obj_super):
            cmds.setAttr("%s.%s" % (c_obj_super, c_at), e=True, k=True, l=False)

    if cmds.objExists(c_root):
        cmds.deleteAttr(c_root, at="smooth")

    if cmds.objExists(c_obj):  # Clean up Root_Group
        DeleteOldRootAttributes()
        for my_attr in attr_order:
            SetStringAttribute(c_obj, my_attr, cur_asset_info[my_attr])


def RemoveOldSetsAndAddNew():
    # Add and remove sets:
    unlock_and_remove = ["Anim_Set", "Model_Set", "Render_Set", "Rig_Set"]
    add_and_lock = ['Anim_Delete_Set', "Rig_Delete_Set", 'PublishSet']
    add_to_publish_set = ["Root_Group"]
    for r_set in unlock_and_remove:
        if cmds.objExists(r_set):
            cmds.lockNode(r_set, lock=False)
            cmds.delete(r_set)
    for c_set in add_and_lock:
        if not cmds.objExists(c_set):
            cmds.sets(n=c_set, empty=True)
        cmds.lockNode(c_set, lock=True)
    cmds.sets(add_to_publish_set, add="PublishSet")


def GetAssetInfoFromRoot(selection=None):
    asset_dict = {}
    if selection:
        root_group = cmds.ls("*%s:Root_Group" % ":".join(selection.split(":")[0:-1]))
        root_group = root_group[0]
    else:
        root_group = cmds.ls("*::Root_Group*", sl=True)
        if root_group:
            root_group = root_group[0]
        else:
            root_group = "Root_Group"
    if cmds.objExists(root_group):
        attr_dict = {"asset_type": ["asset_type","assetType"],"asset_category":["asset_category","assetCategory"],"asset_name":["asset_name","assetName"]}
        # attribute_list = ["asset_type", "asset_category", "asset_name"]
        for key in attr_dict.keys():
            attribute_list = attr_dict[key]
            found=False
            for cur_a in attribute_list:
                c_return = CheckAttribute(root_group, cur_a)
                if c_return:
                    asset_dict[cur_a] = c_return
                    found =True
                else:
                    logger.warning("can't find: %s on %s" % (cur_a, root_group))
            if not found:
                return False
        return asset_dict
    return False

def replaceSnowOnCliff(replace_asset="SnowyRockA"): #TODO Finish this.
    #find all objects that needs to be changed
    cliff_list = cmds.ls("::*%s:Proxy*" % replace_asset,type="transform")
    snow_export = "P:/930383_KiwiStrit3/Production/Temp/%s_Snow_Export.ma" % replace_asset
    for c in cliff_list:
        new_nodes = cmds.file(snow_export, i=True, options="v=0;",rnn=True)
        import_geo = cmds.ls(new_nodes, type="transform")[0]
        y_differ = 46.301
        t = cmds.parentConstraint(c,import_geo,mo=False)
        cmds.delete(t)
        cmds.move(y_differ, import_geo, y=True, os=True, relative=True)


        #import snow and rename to fit namespace?
        #align
        #add difference

def GetAssetInfoFromFile():  # TODO Make this more efficient. Right now it always checks with file, because it asset_step is not included on root.
    import maya.cmds as cmds
    scene_info = {"asset_type": "", "asset_category": "", "asset_name": "", "asset_step": ""}
    cur_scene_path = cmds.file(q=True, sn=True)  # the current scenepath
    # get_from_scene = False  # a boolean to decide if we need to use the scene path to gather asset info

    # Check if the base asset path is in the scene path.
    # if cfg_util.CreatePathFromDict(cfg.project_paths["asset_top_path"]) in cur_scene_path:
    #     check_path = CC.get_asset_work_file()
    # #      .project_paths["asset_work_file"]
    # else:
    #     # print("CAN'T PUBLISH A FILE OUT OF THE STRUCTURE!")
    #     return False
    if cur_scene_path == "":
        # CollectDumpInfo("GetAssetInfoFromFile", "File not saved. Can't get info from here")

        return False
    # if cmds.objExists("Root_Group"):
    # 	for key in scene_info.keys():
    # 		cur_value = CheckAttribute("Root_Group", key)
    # 		if cur_value and not cur_value == "":
    # 			scene_info[key] = cur_value
    # 		# else:
    # 			# print("Missing info: Can't proceed without: %s" % key)
    # 			# CollectDumpInfo("GetAssetInfoFromFile", "Missing info: Can't proceed without: %s" % key)
    # else:
    # 	CollectDumpInfo("GetAssetInfoFromFile",
    # 							"Can't find Root_Group to check for attributes. Will try to extrapolate from scene path out from scene path")

    # collect_dict = cfg.project_paths.copy()
    # collect_dict.update(scene_info)  # use the info already collected from root

    compare_path = CC.get_asset_work_file()
    collect_dict = CC.util.ComparePartOfPath(cur_scene_path, compare_path)
    if collect_dict:
        scene_info.update(collect_dict)
    else:
        return False
    # if not collect_dict:  # If file works out:
    # 	print("Not the correct type of file to publish!")
    # 	return False

    # for key in scene_info.keys():
    # 	if key in collect_dict:
    # 		scene_info[key] = collect_dict[key]
    # 	else:
    # 		return False
    if "" in scene_info.values():
        logger.warning("Missing: INFO: %s" % scene_info)
        return False
    return scene_info



def FindAssetTypeInScene(asset_type="Prop"):
    all_tops = cmds.ls("Anim:*:Root_Group")
    return_list = []
    for top in all_tops:
        if cmds.attributeQuery("asset_type", n=top, ex=True):
            c_type = cmds.getAttr("%s.asset_type" % top)
            if c_type == asset_type:
                logger.info("Found %s -> %s" % (asset_type, top))
                return_list.append(top)
    return return_list

def checkForProxy(parent_obj=None):
    to_return = []
    if cmds.objExists(parent_obj):
        all_children = cmds.listRelatives(parent_obj,ad=True,shapes=False,pa=True)
        all_xforms = cmds.ls(all_children,type="transform",long=True)
        for cur_xform in all_xforms:
            if cmds.listRelatives(cur_xform,type="VRayMeshPreview",pa=True):
                to_return.append(cur_xform)
    return to_return


#TODO If vray proxy creation fails. Stop publish! When proxy is in use/rendering, then we can't overwrite it, and the publish fails and saves an empty Render ref.
def CreateSetdressProxySetup(asset_info):  # change to asset_info?
    from Maya_Functions.set_util_functions import AddToSet
    from Maya_Functions.vray_util_functions import setVrayProxyDisplay, createVrayProxy
    from Maya_Functions.attr_util_functions import copyAttribs, copyOID
    base_path = CC.get_asset_base_path(**asset_info)
    gpu_path = CC.get_GPU(**asset_info)
    vray_path = CC.get_VrayProxy(**asset_info)
    # gpu_path = cfg_util.CreatePathFromDict(cfg.ref_paths["GPU"], asset_info)
    # gpu_path = '%sCache/Gpu' % (base_asset_path)

    # vray_path = cfg_util.CreatePathFromDict(cfg.ref_paths["VrayProxy"], asset_info)
    # vray_path = '%sVrMesh' % (asset_base_path)

    gpu_node = createGpuCache(gpu_path, 'Proxy', replace=True)
    if cmds.objExists('|Root_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl'):
        copyAttribs('|Root_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl', 'Proxy')
        copyOID('|Root_Group', 'Proxy')
    #Check if there is any vray proxy nodes in the Full group. That would usually be for yeti cached as alembic or such.
    proxies_in_full = checkForProxy("Full")
    if proxies_in_full:
        print("Found existing proxies in full group: %s" % proxies_in_full)
        full_proxy_group = cmds.group(proxies_in_full, name="ToParentUnderProxy", w=True)

    vray_node = createVrayProxy(vray_path, mesh_group='Full', previewFaces=1000, crtProxy=True,newProxyNode=False)
    if not vray_node:
        return False
    # ApplyVraySubDiv([vray_node])
    cmds.parent(vray_node, gpu_node)
    if proxies_in_full:
        cmds.parent(cmds.listRelatives(full_proxy_group,type="transform"),gpu_node)
    AddToSet("PublishSet", cmds.listRelatives(gpu_node, p=True))
    setVrayProxyDisplay(cmds.listRelatives(cmds.listRelatives(gpu_node, p=True)[0], type="transform"))
    return True


def createGpuCache(out_path, mesh_group, replace=False):
    import os
    cmds.loadPlugin('AbcExport')
    cmds.loadPlugin('gpuCache')
    if cmds.objExists(mesh_group):
        # zero translations
        # cmds.makeIdentity(mesh_group, apply=True, s=True) # Is this needed??
        cmds.setAttr("%s.visibility" % mesh_group, 1)  # Try to make sure the visibilty is turned on
        # set directory
        # export_dir = '%sCache/Gpu' % (base_asset_path)

        out_folder_path, out_file = os.path.split(out_path)
        out_file = os.path.splitext(out_file)[0]

        # Create directory
        if not os.path.exists(out_folder_path):
            os.makedirs(out_folder_path)

        logger.info('mesh_group: ' + mesh_group)
        logger.info('out_folder_path: ' + out_folder_path)
        logger.info('out_file: ' + out_file)

        # EXPORT GPU
        return_path = cmds.gpuCache(mesh_group, startTime=1, endTime=1, writeMaterials=True, directory=out_folder_path,
                                    fileName=out_file)

        logger.info("GPU-Cahced: %s" % return_path)
        # ABC export options. We can do this with gpu cache instead and get lambert colors.
        # String mesh elements
        # gpu_sel = ''
        # for m in cmds.listRelatives(mesh_group,f=True, c=True):
        #     gpu_sel = '%s -root %s' % (gpu_sel, m)
        # print('GPU ITEMS : ', gpu_sel)
        # command = "-frameRange 1 1 -uvWrite %s -file %s" % (gpu_sel, out_path)  # missing size and color
        # print("CREATE PROXY COMMAND: %s" % command)
        # a = cmds.AbcExport(j=command)
        # print('abc result', a)

        if replace:
            cmds.lockNode(mesh_group, lock=False)
            cmds.delete(mesh_group)
            cache_node = cmds.createNode("gpuCache", name=mesh_group + "Shape")
            logger.info("GPU Shape: " + cache_node)
            cmds.setAttr(cache_node + ".cacheFileName", out_path, type="string")

            return cache_node

        return (out_path)

    else:
        logger.warning('NO '+mesh_group+' IN SCENE')
        return False


def LockGeoGroup(lock=True, obj_namespace=""):  # Locks the geo group before publishing
    logger.info("Trying to lock/unlock Geo_Group")
    cur_obj = "|Root_Group|Geo_Group"
    if cmds.objExists(cur_obj):
        if lock:
            cmds.setAttr("%s.overrideEnabled" % cur_obj, 1)
            cmds.setAttr("%s.overrideDisplayType" % cur_obj, 2)
        else:
            cmds.setAttr("%s.overrideEnabled" % cur_obj, 0)


def SelectCtrlsFromNamespace(super_root=False, only_super=False):
    selection_objects = cmds.ls(sl=True)
    final_selection = []
    namespace_check = []
    for obj in selection_objects:
        cur_namespace = ":".join(obj.split(":")[:-1])
        if cur_namespace in namespace_check:
            continue
        else:
            namespace_check.append(cur_namespace)
        logger.info("adding ctrls from %s" % cur_namespace)

        new_selection = cmds.ls("%s::*_Ctrl" % cur_namespace, type="transform")
        super_root_obj = "%s:SuperRoot_Ctrl" % cur_namespace
        if super_root_obj in new_selection:
            if not super_root and not only_super:
                new_selection.remove(super_root_obj)
            elif only_super:
                final_selection += [super_root_obj]
            else:
                final_selection += new_selection
        else:
            if not only_super:
                final_selection += new_selection
    if final_selection:
        cmds.select(final_selection, r=True)


def FindRootByName(name_list=[]):
    return_list = []
    for c_name in name_list:
        cur_objs = cmds.ls("::%s*:Root_Group" % c_name)
        return_list.extend(cur_objs)
    return_list = list(set(return_list))
    return return_list


def CreateOnlyBGExceptionSet(object_list=None):
    from set_util_functions import AddToSet
    AddToSet("OnlyBG_Exception", object_list)

def buildEyeHighlightConnections():
    """
    addAttr -ln "highlightVisibility"  -at "enum" -en "Off:On:"  |L_Eye_Group|L_Eye_Scale_Group|L_Eye_Highlight_Group|L_Eye_Highlight_Offset_Group;
    setAttr -e-keyable true |L_Eye_Group|L_Eye_Scale_Group|L_Eye_Highlight_Group|L_Eye_Highlight_Offset_Group.highlightVisibility;
    addAttr -ln "highlightVisibility"  -at "enum" -en "Off:On:"  |R_Eye_Group;
    setAttr -e-keyable true |R_Eye_Group.highlightVisibility;
    addAttr -ln "highlightOffset"  -at double  -dv 0 |R_Eye_Group;
    setAttr -e-keyable true |R_Eye_Group.highlightOffset;
    addAttr -ln "highlightSize"  -at double  -min 0 -dv 0.78 |R_Eye_Group;
    setAttr -e-keyable true |R_Eye_Group.highlightSize;
    addAttr -ln "highlightRadius"  -at double  -min 0 -dv 9 |R_Eye_Group;
    setAttr -e-keyable true |R_Eye_Group.highlightRadius;

    shadingNode -asUtility multiplyDivide;
    connectAttr -f R_Eye_Group.highlightRadius R_radius_invert.input1X;

    connectAttr -f R_Eye_Group.highlightSize R_Eye_Highlight_Ref_Geo.scaleX;
    connectAttr -f R_Eye_Group.highlightSize R_Eye_Highlight_Ref_Geo.scaleY;

    connectAttr -f R_Eye_Group.highlightOffset R_Highlight_Offset_Group.rotateZ;
    connectAttr -f R_radius_invert.outputX R_Eye_Highlight_Ref_Geo.rotateX;
    """
    pass

def buildHighlightOnEyeCtrl(source=None,target=None):
    selection = cmds.ls(sl=True)
    if not source and not target:
        selection = cmds.ls(sl=True)
        if selection:
            if len(selection)==2:
                source = selection[0]
                target = selection[1]
        else:
            return False
    # source = "EyeA:L_Eye_Group"
    # target = "L_Eye_Ctrl"
    attribute_list = ["highlightVisibility","highlightOffset","highlightSize","highlightRadius"]
    import Maya_Functions.attr_util_functions as auf
    auf.transferAttributes(source,target,attribute_list,True)
    for l in attribute_list:
        cmds.connectAttr("%s.%s" % (target,l),"%s.%s" % (source,l),f=True)

def buildEyeDConnections(build_on_source=False,source=None,target=None):
    import Maya_Functions.attr_util_functions as auf
    #"Also build lattice connections with script.
    if not source and not target:
        selection = cmds.ls(sl=True)
        if selection:
            if len(selection)==2:
                source = selection[0]
                target = selection[1]
        else:
            return False
    bs_list = ["Iris_blink_L", "Iris_blink_R", "Eye_button_L", "Eye_button_R", "Eye_happy_L", "Eye_happy_R",
               "Eye_sad_L", "Eye_sad_R"]
    if build_on_source:
        auf.transferAttributes(source, target, bs_list, True)
    for bs in bs_list:
        if cmds.attributeQuery(bs,node=source,exists=True) and cmds.attributeQuery(bs,node=target,exists=True):
            cmds.connectAttr("%s.%s" % (target, bs), "%s.%s" % (source, bs), f=True)

def connectEyeDSetup():
    """
    select in order - eye_ctrl_group -> eye_ctrl -> eye_ctrl_aim_constraint -> Eye Geo Top group
    :return:
    """

    sel = cmds.ls(sl=True)
    e_ctrl_grp = sel[0]
    e_ctrl = sel[1]
    aim_c = sel[2]
    e_group = sel[3]
    e_look = sel[4]

    #Get info and delete aim constraint
    target = cmds.aimConstraint(aim_c, q=True, targetList=True)
    up_obj = cmds.aimConstraint(aim_c, q=True, wuo=True)
    source = cmds.listConnections("%s.constraintRotate.constraintRotateX" % aim_c, d=True, s=False)
    weight_con = cmds.listConnections("%s.%s" % (aim_c, cmds.aimConstraint(aim_c, q=True, wal=True)[0]), d=True,
                                      s=True, plugs=True)
    cmds.delete(aim_c)

    #Find the orient con and the joint
    orient_con = cmds.listConnections(e_ctrl, d=True, s=False)[0]
    jnt = cmds.listConnections(orient_con, source=False, d=True)[0]

    #delete orient cont
    cmds.delete(orient_con)

    tp = cmds.parentConstraint(e_group,jnt,mo=False)
    cmds.delete(tp)
    cmds.makeIdentity(jnt, apply=True, r=True)
    # cmds.setAttr("%s.translateX" % e_ctrl,l=False)
    # cmds.setAttr("%s.translateY" % e_ctrl, l=False)
    cmds.setAttr("%s.translateZ" % e_ctrl, l=False)
    cmds.setAttr("%s.translateZ" % e_ctrl, 0.2)
    cmds.setAttr("%s.translateZ" % e_ctrl, l=True)
    tp = cmds.parentConstraint(e_group,e_ctrl_grp,mo=False)
    cmds.delete(tp)

    #make orient cnt
    cmds.orientConstraint(e_ctrl, jnt, mo=True)
    cmds.parentConstraint(jnt,e_look,mo=True)

    new_ac = cmds.aimConstraint(target, source, wuo=up_obj[0], worldUpType="object", mo=True)
    cmds.connectAttr(weight_con[1], "%s.%s" % (new_ac[0], cmds.aimConstraint(new_ac, q=True, wal=True)[0]), f=True)

    buildHighlightOnEyeCtrl(e_group,e_ctrl)


#
# #Select LATTICE and Eye_Group
# selection = cmds.ls(sl=True)
# lat = selection[0]
# eye_group = selection[1]
# cmds.lattice(lat,e=True,g=eye_group)
# #select in order - eye_ctrl_group -> eye_ctrl -> eye_ctrl_aim_constraint -> Eye Geo Top group -> Eye Geo Look Group
# import Maya_Functions.asset_util_functions as auf
# reload(auf)
# auf.connectEyeDSetup()
# #Select Blink_Eye_Ctrl and Eye_Group
# import Maya_Functions.asset_util_functions as auf
# reload(auf)
# auf.buildEyeDConnections()

def setCopycatRenderSettings(copycat=False):
    if not copycat:
        #main
        cmds.setAttr('Anim:CopycatMirror:SuperRoot_Ctrl.mirror', 1)
        try:
            cmds.setAttr('Anim:RainbowGuy:NoCastShadow.ignore', 0)
            cmds.setAttr('Anim:RainbowGuy:ReflectionExclude.ignore', 0)
        except:
            pass
        cmds.setAttr('hide.ignore', 0)
        cmds.setAttr('matte.ignore', 1)

    else:
        cmds.setAttr('Anim:CopycatMirror:SuperRoot_Ctrl.mirror', 0)
        try:
            cmds.setAttr('Anim:RainbowGuy:NoCastShadow.ignore', 1)
            cmds.setAttr('Anim:RainbowGuy:ReflectionExclude.ignore', 1)
        except:
            pass
        cmds.setAttr('hide.ignore', 1)
        cmds.setAttr('matte.ignore', 0)