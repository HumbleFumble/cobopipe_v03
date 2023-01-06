import pprint

from RenderSubmit import logger

pp = pprint.PrettyPrinter(indent=4)

import os
from datetime import datetime
import sys
try:
    import maya.cmds as cmds
    from Maya_Functions.set_util_functions import FindObjectsFromSet
    from Maya_Functions.file_util_functions import saveJson, makeFolder, loadJson
    in_maya = True
except:
    in_maya =False



from getConfig import getConfigClass
CC = getConfigClass()
from Log.CoboLoggers import getLogger
logger = getLogger()

from runtimeEnv import getRuntimeEnvFromConfig
run_env = getRuntimeEnvFromConfig(config_class=CC)

import subprocess
######################################################################################
###### PRE-PUBLISH FUNCTIONS  ########################################################
######################################################################################


def CheckSetdressScene():
    ###  CHECK FOR GROUPS  ###
    if not cmds.objExists('Proxy'):
        logger.info('Setdress scene is missing Proxy group')
        return False
    if not cmds.objExists('Full'):
        logger.info('Setdress scene is missing Proxy group')
        return False

    if not cmds.listRelatives('Proxy', c=True):
        logger.info('Proxy Group is empty')
        return False
    if not cmds.listRelatives('Full', c=True):
        logger.info('Full Group is empty')
        return False
    return True


def CheckPublishSet(publish_set="PublishSet"):
    if not cmds.objExists(publish_set):
        logger.info("NO PublishSet! Nothing will be published without one!")
        return False
    if not cmds.sets(publish_set, q=True):
        logger.info("PublishSet EMPTY, please add what you would like to publish")
        return False
    return True

######################################################################################
###### ASSET PUBLISH REPORT   ########################################################
######################################################################################


def readyPublishReport(info_dict={}, current_dict={}, ref=True, texture=False, ids=False):
    logger.info("PublishReport Ready UP!")
    # logger.info("INFO/CURRENT DICT: %s || %s" %(info_dict,current_dict))
    if 'asset_name' in info_dict.keys():
        if ref:
            if info_dict["asset_output"] == "Proxy":
                full_list = getAllRefPathsInSet("Full_Set")
                current_dict["%s_ref_paths" % info_dict["asset_output"]] = full_list
            else:
                full_list = getAllRefPathsInSet("PublishSet")
                current_dict["%s_ref_paths" % info_dict["asset_output"]] = full_list

        if texture:
            current_dict["%s_texture_paths" % info_dict["asset_output"]] = getAllTexturePathsInScene()

        if ids:
            current_dict["%s_OIDs" % info_dict["asset_output"]] = getAllOIDsInScene()
            current_dict["%s_MIDs" % info_dict["asset_output"]] = getAllMIDsInScene()

    else:
        if ref:
            full_list = getRefs()
            current_dict["%s_ref_paths" % info_dict["publish_report_name"]] = full_list
        if texture:
            current_dict["%s_texture_paths" % info_dict["publish_report_name"]] = getAllTexturePathsInScene()


def savePublishReport(info_dict=None, content={}, filepath=None):
    """
    save a list of ref and textures used in the publish
    :param asset_info:
    :param content:
    :param filepath:
    :return:
    """
    if not "asset_publish_report_file" in CC.__dict__.keys():
        return False
    if not filepath and info_dict:
        if "asset_name" in info_dict:
            filepath = CC.get_asset_publish_report_file(**info_dict)
        if "shot_name" in info_dict:
            filepath = CC.get_shot_publish_report_file(**info_dict)
    from Maya_Functions.file_util_functions import saveJson, makeFolder,loadJson
    makeFolder(cur_path=filepath)
    old_content = loadJson(save_location=filepath)
    if not old_content:
        old_content = {}
    for cur_key in content.keys():
        old_content[cur_key] = content[cur_key]
    saveJson(save_location=filepath,save_info=old_content)


def updatePublishReport_MayaPyCmd(info_dict=None,scene_path=None,report_name="AnimScene"):
    script_content = """import maya.standalone
    maya.standalone.initialize('python')
    import maya.cmds as cmds
    import Maya_Functions.publish_util_functions as pub_util
    cmds.file('{scene_path}', open=True,f=True)
    pub_util.updatePublishReport(info_dict={info_dict},report_name='{report_name}')
    cmds.quit(f=True)""".format(scene_path=scene_path,info_dict=info_dict,report_name=report_name)
    script_content = ";".join(script_content.split("\n"))
    base_command = 'mayapy.exe -c "%s"' % (script_content)
    print(base_command)
    # subprocess.call(base_command,shell=False,universal_newlines=True)

    p = subprocess.Popen(base_command, shell=True, universal_newlines=True,stdout=sys.stdout,stderr=sys.stderr,env=run_env)
    p.wait()

    # return base_command


def updatePublishReport(info_dict=None, report_name="AnimScene"):
    content_dict = {}
    if not info_dict:
        scene_path = cmds.file(q=True, sn=True)
        info_dict = CC.util.ComparePartOfPath(scene_path, CC.get_shot_anim_path())
    if info_dict:
        info_dict["publish_report_name"] = report_name
        readyPublishReport(info_dict=info_dict,current_dict=content_dict)
        savePublishReport(info_dict=info_dict,content=content_dict)
        print("FINISHED with publish report")
        return True
    else:
        return False


def gatherAssetsUsingRefReport(asset_info=None,filters=None):
    """
    function meant to give a back a list of all the places the asset is used.
    :param asset_info:
    :param filters:
    :return:
    """
    if not "asset_publish_report_file" in CC.__dict__.keys():
        return False
    asset_report_path = CC.get_shot_publish_report_file()
    film_report_path = CC.get_asset_publish_report_file()
    #TODO finish this


def gatherRefInReport(asset_info=None,filters=None):
    import os
    """
    use this to gather all the shots from either the whole episode or just the sequence.
    :param episode_name:
    :param seq_name:
    :return:
    """

    filepath = ""
    if not "asset_publish_report_file" in CC.__dict__.keys():
        return False
    if "episode_name" in asset_info:
            filepath = CC.get_shot_publish_report_file(**asset_info)
    if "asset_name" in asset_info:
        filepath = CC.get_asset_publish_report_file(**asset_info)
    if "<" in filepath:
        search_full_string = filepath.split("<")[0]
        search_path,search_string = os.path.split(search_full_string)
        cur_reports = os.listdir(search_path)
        report_dict = {}
        for cur_content in cur_reports:
            if search_string in cur_content:
                key_name = cur_content.split(".")[0]
                p_report = returnPublishReport(asset_info={}, filepath="%s/%s" % (search_path, cur_content), filters=filters)
                ref_list = recursiveReport(p_report)
                ref_count_dict = getRefCountForReport(ref_list)
                report_dict[key_name] = ref_count_dict
        #pp.pprint(report_dict)
        return report_dict
    else:
        p_report = returnPublishReport(asset_info, filters=filters)
        ref_list = recursiveReport(p_report)
        ref_count_dict = getRefCountForReport(ref_list)
        #pp.pprint(ref_count_dict)
        return ref_count_dict


def getRefCountForReport(final_list=None):
    return_dict = {}
    if final_list:
        for ref_dict in final_list:
            if ref_dict:
                for cur_key in ref_dict.keys():
                    ref_dict_value = ref_dict[cur_key]
                    for ref_path in ref_dict_value:
                        if ref_path in return_dict.keys():
                            return_dict[ref_path] = return_dict[ref_path] + 1
                        else:
                            return_dict[ref_path] = 1
    return return_dict


def reportFromRef(ref_path=None):
    import os
    ref_folder, ref_name = os.path.split(ref_path)
    asset_output = ref_name.split("_")[-1].split(".")[0]
    try:
        c_ref_dict = CC.util.ComparePartOfPath(scene_path=ref_folder, compare_path=CC.get_asset_ref_folder())
        # print("REF:%s - %s ->%s" % (ref_folder, asset_output, c_ref_dict))
        c_ref_report = returnPublishReport(asset_info=c_ref_dict, filters=["%s_ref_paths" %asset_output])
        # pp.pprint(c_ref_report)
        return c_ref_report
    except:
        return None


def recursiveReport(report_dict=None):
    """
    gather a list of refs used recursively, so that we go like shot->set->setdress.
    get a report dict back, add list of refs individually to main-dict with ref as a key and counter as a value ( +1 for each of the same refs)
    :param ref_path:
    :return:
    """
    final_list = []
    if report_dict:
        final_list.append(report_dict)
        for p_key in report_dict.keys():
            # print("Current key: ", p_key)
            if "ref_paths" in p_key: #hardcoded to refs at the moment
                ref_list = report_dict[p_key]
                for p_ref in ref_list:
                    ref_report = reportFromRef(ref_path=p_ref)
                    #option 1:
                    if ref_report:
                        # final_list.append(ref_report)
                        recursive_list = recursiveReport(ref_report)
                        if recursive_list:
                            final_list.extend(recursive_list)
                print("Done with %s\n\n" % p_key)
        return final_list
    else:
        return None


def returnPublishReport(asset_info=None,filepath=None,filters=None):
    from Maya_Functions.file_util_functions import saveJson, makeFolder, loadJson
    return_dict = {}
    if not "asset_publish_report_file" in CC.__dict__.keys():
        return False
    if "asset_name" in asset_info and not filepath:
        filepath = CC.get_asset_publish_report_file(**asset_info)
    if "episode_name" in asset_info and not filepath:
        filepath = CC.get_shot_publish_report_file(**asset_info)
    if filepath:
        old_content = loadJson(save_location=filepath)
        if filters and old_content:
            for cur_key in old_content.keys():
                for cur_filter in filters:
                    if cur_filter in cur_key:
                        return_dict[cur_key] = old_content[cur_key]
        else:
            return old_content
    return return_dict


def getDependency(asset_info=None,filter_key=None):
    """
    get asset dict from file or as arg
    get publish report from CC.asset_publish_report_file(**asset_info)
    return_dict = loadJson(save_location="")
    ref_paths = []
    texture_paths = []
    filter_key = None
    for cur_key in return_dict.keys():
        if filter_key and filter_key in cur_key:
            ref_paths.extend(return_dict[cur_key]
        elif ref_path in cur_key:
            ref_paths.extend(return_dict[cur_key]
        if texture in cur_key:
            texture_paths.extend(return_dict[cur_key]

    :return:
    """
    pass


def getRefs():
    ref_list = []
    refs = cmds.file(q=True,reference=True)
    for ref_file in refs:
        if "{" in ref_file:
            ref_file = ref_file.split("{")[0]
        ref_list.append(ref_file)
    return ref_list


def getAllRefPathsInSet(set_name=None):
    logger.debug("Getting all ref paths for %s" % set_name)
    check_list = cmds.sets(set_name, q=True)
    if set_name:
        ls_list = cmds.ls(check_list, dag=True)
    else:
        ls_list = cmds.ls(dag=True)
    node_check = []
    ref_list = []
    for check in sorted(ls_list):
        if cmds.referenceQuery(check, inr=True):
            ref_node = cmds.referenceQuery(check, rfn=True)
            if not ref_node in node_check:
                node_check.append(ref_node)
                ref_file = cmds.referenceQuery(check, filename=True)
                if "{" in ref_file:
                    ref_file = ref_file.split("{")[0]
                ref_list.append(ref_file)
    return ref_list


def getAllTexturePathsInScene():
    texture_list = []
    file_nodes = cmds.ls(type='file')
    for cur_node in file_nodes:
        tex_path = cmds.getAttr('%s.fileTextureName' % (cur_node))
        texture_list.append(tex_path)
    return sorted(texture_list)

def getAllOIDsInScene():
    OID_list = {}
    OIDs = cmds.ls("::*.vrayObjectID")
    for OID in OIDs:
        nodeName = cmds.ls(OID.split('.')[0], long=True)[0]
        value = int(cmds.getAttr(OID))
        if value and nodeName:
            if value not in OID_list.keys():
                OID_list[value] = [nodeName]
            elif nodeName not in OID_list[value]:

                OID_list[value].append(nodeName)
    return OID_list

def getAllMIDsInScene():
    MID_list = {}
    MIDs = cmds.ls("::*.vrayMaterialId")
    for MID in MIDs:
        shaderName = MID.replace('.vrayMaterialId', '')
        value = int(cmds.getAttr(MID))
        if value not in MID_list.keys():
            MID_list[value] = [shaderName]
        elif shaderName not in MID_list[value]:
            MID_list[value].append(shaderName)
    return MID_list

######################################################################################
###### ASSET PUBLISH FUNCTIONS ########################################################
######################################################################################


def SetFrameRate():
    cmds.currentUnit(time="pal", ua=False)



def LockModuleAttrs():  # Use this if we need to lock attributes on rig module in publish
    attr_list = ["moduleSize", "armSize", ]
    for cur_attr in attr_list:
        cur_obj = cmds.ls("*.%s" % cur_attr, o=True, ln=True)
    pass


def removeRootGroup():
    root_groups = cmds.listRelatives("Root_Group", children=True)
    for rg in root_groups:
        cmds.parent(rg, world=True)
        if not cmds.listRelatives(rg):
            cmds.delete(rg)
    cmds.delete("Root_Group")


def SetDressImport():
    logger.info("Trying to avoid more geo and top groups")
    geo_groups = cmds.ls("Geo_Group", l=True)
    for gg in geo_groups:
        if not gg == "|Geo_Group":
            cmds.rename(gg, "SetDress_Geo_Group")
    top_groups = cmds.ls("Top_Group", l=True)
    for tg in top_groups:
        cmds.rename(tg, "SetDress_Top_Group")


def ignoreColorspaceRule(nodes=None):
    if not nodes:
        nodes = cmds.ls(type="file")
    for cur_node in nodes:
        if not cmds.referenceQuery(cur_node, inr=True):
            print("Found %s and removing" % cur_node)
            cmds.setAttr("%s.ignoreColorSpaceFileRules" % cur_node, 1)


def FindAndGroupFullAndProxyGroup():
    from Maya_Functions.set_util_functions import FindObjectsFromSet,AddToSet
    full = FindObjectsFromSet("Full_Set")
    proxy = FindObjectsFromSet("Proxy_Set")
    logger.info("FULL: %s" % full)
    logger.info("PROXY: %s" % proxy)
    if not proxy and not cmds.objExists("Proxy"):
        raise ValueError("Can't find proxy group and/or sets!")

    if not full:
        if cmds.objExists("Full"):
            AddToSet(set_name="Full_Set",selection="Full")
        else:
            raise ValueError("Can't find full/proxy group and/or sets!")
    else:
        if not cmds.objExists("Full"):
            full_group = cmds.group(empty=True,name="Full")
        for cur_obj in full:
            try:
                cmds.parent(cur_obj,"Full")
            except:
                logger.warning("Skipping parenting to Full: %s" % cur_obj)
        if not cmds.objExists("Proxy"):
            proxy_group = cmds.group(empty=True,name="Proxy")
        if proxy:
            for cur_obj in proxy:
                try:
                    cmds.parent(cur_obj,"Proxy")
                except:
                    logger.warning("Skipping parenting to proxy %s" % cur_obj)


######################################################################################
####### ANIM SCENE PUBLISH FUNCTIONS #################################################
######################################################################################


def DeleteLightDirection():  # Animation Publish: Deletes the Light Direction group meant for pre-setting light in previz
    if cmds.objExists("LD_directionalLight"):
        cmds.delete("LD_directionalLight")


def SetKeyOnPublish( key_dict):
    for key in key_dict.keys():
        refs = cmds.ls("%s*:Root_Group" % key)
        for ref in refs:
            ref = ref.split(":")[0]
            for obj in key_dict[key].keys():
                if cmds.objExists("%s:%s" % (ref, obj)):
                    SetKeyOnAttribute(c_ns=ref, c_object=obj, c_attr=key_dict[key][obj])

def SetKeyOnAttribute(c_ref=None, c_object=None, c_attr=None, c_ns=None):  # Animation Publish: Set key on attribute. Special case.
    if not c_ns:
        c_ns = cmds.referenceQuery(c_ref, ns=True)
    if cmds.objExists("%s:%s" % (c_ns, c_object)):
        logger.info("Trying to set a key on %s:%s.%s" % (c_ns, c_object, c_attr))
        if c_attr:
            cmds.setKeyframe("%s:%s" % (c_ns, c_object), attribute=c_attr, t=1)
        else:
            cmds.setKeyframe("%s:%s" % (c_ns, c_object), t=1)


def GetRotationAxisDict(ref_path):  # Rotation Axis Dict?? Please explain, Rune :D
    ctrl_rot_order = {}
    ref_node = cmds.referenceQuery(ref_path, referenceNode=True)
    name_space = cmds.referenceQuery(ref_node, ns=True)
    ctrls = cmds.ls('%s:*_Ctrl' % (name_space))
    for i in ctrls:
        if not cmds.listConnections('%s.rotateOrder' % (i), s=1, d=0):
            ctrl_rot_order[i] = cmds.getAttr('%s.rotateOrder' % (i))

    return ctrl_rot_order


def DeleteKeyAndChangeCenter(cur_shotname):  # Anim Publish: Sets center of interest distance to camera, has to be above 25 or it will affect the light in render!
    my_cam = "%s_Cam" % (cur_shotname)  # TODO need current shot as input
    if len(cmds.ls(my_cam)) > 1:
        raise NameError('More than one node named: ' + my_cam)
    my_cam_shape = cmds.listRelatives(my_cam, shapes=True)[0]
    cmds.camera(my_cam_shape, e=True, lt=False)
    cmds.cutKey(my_cam, cl=True, at="coi")
    cmds.setAttr("%s.centerOfInterest" % my_cam_shape, 50)


def setVelocityEndKeys():  # Anim Publish: Make animation overshoot after shot ends so motion blur doesn't get bungled
    # get anim curves
    curves = cmds.ls(typ=("animCurveTL", "animCurveTU", "animCurveTA", "animCurveTT"))

    # find anim shot end
    cTime = cmds.currentTime(q=True)
    shotEnd = cmds.getAttr('%s.endFrame' % (cmds.sequenceManager(lsh=True)[0]))

    # get active curves that are float type
    active_attrs = []
    for crv in curves:
        # filter referenced curves
        if cmds.referenceQuery(crv, isNodeReferenced=True):
            continue

        endKeyTime = cmds.keyframe(crv, q=True)
        if endKeyTime:
            endKeyTime = endKeyTime[-1]
            if endKeyTime >= shotEnd:
                attr = cmds.listConnections('%s.output' % (crv), d=True, p=True, scn=True)

                # filter curves without a destination
                if attr:
                    if "." in attr[0]:
                        if cmds.objectType(attr[0].split(".")[0]) in ["parentConstraint","orientConstraint","pointConstraint"]:
                            continue
                    # filter curves that are not float values
                    if isinstance(cmds.getAttr(attr[0]), float):
                        active_attrs.append(attr[0])

    # Set animation keys and tangent
    # print(active_attrs)
    for attr in active_attrs:
        # print attr
        valA = cmds.getAttr(attr, time=shotEnd - 1)
        valB = cmds.getAttr(attr, time=shotEnd)
        newVal = valB + valB - valA
        # print(attr, newVal, shotEnd + 1)
        cmds.setKeyframe(attr.split('.')[0], attribute=attr.split('.')[1], t=shotEnd, insert=True)
        cmds.setKeyframe(attr.split('.')[0], attribute=attr.split('.')[1], t=shotEnd + 1, v=newVal)
        cmds.keyTangent(attr.split('.')[0], attribute=attr.split('.')[1], inTangentType='linear',
                        time=(shotEnd + 1, shotEnd + 1))


# def SmoothSmoothSet(input_list=[]):
#     my_objs = []
#     if not input_list:
#         my_objs = FindObjectsFromSet("Smooth_Set")
#     else:
#         my_objs = input_list
#     if my_objs:
#         _list = []
#         _list = getSmoothTarget(my_objs, [])
#         # print("Smooth geo list: %s" % _list)
#         for node in _list:
#             # print("Smoothing: %s" % node)
#             try:
#                 cmds.delete(node, ch=True)
#                 cmds.polySmooth(node, mth=0, sdt=2, ovb=1, ofb=3, ofc=0, ost=0, ocr=0, dv=2, bnr=1, c=1, kb=1,
#                                         ksb=1,
#                                         khe=0, kt=1, kmb=1, suv=1, peh=0, sl=1, dpe=1, ps=0.1, ro=1, ch=0)
#             except:
#                 print("Missed smoothing on %s" % node)
#
#
#
# def getSmoothTarget(_list, output=[]):
#     return_list = []
#     for obj in _list:
#         if cmds.objExists(cmds.ls(obj, long=True)[0]):
#             if cmds.listRelatives(obj, s=True, fullPath=True):
#                 if cmds.ls(obj, long=True)[0] not in output:
#                     output.append(obj)
#                     return_list.append(obj)
#             children = cmds.listRelatives(obj, children=True, type="transform", f=True)
#             if children:
#                 return_list.extend(getSmoothTarget(children, output))
#     return return_list


def isGeometryNode(node):

    shapes = cmds.listRelatives(node, shapes=True, fullPath=True)
    if shapes:
        _list = []
        for shape in shapes:
            if shape:
                if cmds.objExists(shape):
                    if cmds.objectType(shape) == 'mesh':
                        _list.append(True)
        if all(_list):
            return True
    return False



def getGeometryNodes(node):
    geometryNodes = []
    if isGeometryNode(node):
        if node not in geometryNodes:
            geometryNodes.append(node)
    else:
        children = cmds.listRelatives(node, allDescendents=True, fullPath=True)
        if children:
            for child in children:
                cmds.ls(node, long=True)[0]
                output = getGeometryNodes(child)
                for item in output:
                    if item not in geometryNodes:
                        geometryNodes.append(child)
    return geometryNodes

def makeCleanFileForPublishContent(output_file=None):
    """
    this is meant to export the publishSet and then reimport it into a clean new file, to avoid having a lot of useless nodes following us around.
    :param asset_info:
    :return:
    """
    placeUsedVraySetsIntoPublish()
    cmds.select(cmds.sets("PublishSet", q=True), r=True,ne=True)
    cmds.file(output_file, force=True, options="v=0;", typ="mayaBinary", pr=True, es=True, ch=True, exp=True)
    cmds.file(output_file,open=True, f=True)
    # cmds.file(export_path, i=True, typ="mayaBinary", ignoreVersion=True, options="v=0;", pr=True)

def placeUsedVraySetsIntoPublish():
    """
    Add vray sets to the publish set, if there are elements intersecting (used in both).
    :return:
    """
    my_ls = cmds.ls(type=["VRayDisplacement", "VRayObjectProperties","VRayFur"])
    full_list = []
    for p in cmds.sets("PublishSet", q=True):
        temp_list = cmds.listRelatives(p, ad=True, f=True)
        if temp_list:
            full_list.extend(temp_list)
    for l in my_ls:
        compare_list = cmds.listRelatives(l, ad=True, f=True)
        if compare_list:
            intersection_set = set.intersection(set(full_list), set(compare_list))
            if intersection_set:
                cmds.sets(l, add="PublishSet")

def SmoothSmoothSet(input_list=[]):
    test_list = []
    if not test_list:
        smoothSet = cmds.sets('Smooth_Set', query=True)
        smooth_full_name = cmds.ls(smoothSet, long=True)
        print("In Smooth_Set: %s " % smooth_full_name)
        mesh_list = []
        for node in smooth_full_name:
            # print("orig: %s" % node)
            # new_node = cmds.ls(node, long=True)[0]
            node_child_list = cmds.listRelatives(node,ad=True,children=True,type="mesh",f=True)
            if node_child_list:
                mesh_list.extend(node_child_list)
        # smooth_list = []
        for mesh_node in set(mesh_list):
            # print(cmds.listRelatives(mesh_node,f=True,p=True))
            test_list.extend(cmds.listRelatives(mesh_node,f=True,p=True))
        test_list = list(set(test_list))
        # for t in sorted(test_list):
        #     print(t)
        # print(test_list)
        # cmds.select(set(test_list),r=True)

        # for node in smoothSet:
        #     # print("orig: %s" % node)
        #     node = cmds.ls(node, long=True)[0]
        #     # print("LS node: %s" % node)
        #     if isGeometryNode(node):
        #         if node not in input_list:
        #             input_list.append(node)
        #     else:
        #         output = getGeometryNodes(node)
        #         for item in output:
        #             item = cmds.ls(item, long=True)[0]
        #             if item not in input_list:
        #                 input_list.append(item)
    if test_list:
        for target in test_list:
            # print(target)
            try:
                cmds.delete(target, ch=True)
                cmds.polySmooth(target, mth=0, sdt=2, ovb=1, ofb=3, ofc=0, ost=0, ocr=0, dv=2, bnr=1, c=1, kb=1, ksb=1,
                                khe=0, kt=1, kmb=1, suv=1, peh=0, sl=1, dpe=1, ps=0.1, ro=1, ch=0)
            except Exception as e:
                print("Missed smoothing on %s -> %s" % (target.split('+')[-1], e))

# Obsolete func. Would smooth same object multiple times if it's parent groups where in SmoothSet
#
# def SmoothSmoothSet(input_list=[]):
#     if not input_list:
#         my_objs = FindObjectsFromSet("Smooth_Set")
#     else:
#         my_objs = input_list
#     if my_objs:
#         for obj in my_objs:
#             if cmds.objExists(obj):
#                 if cmds.listRelatives(obj, s=True):
#                     cmds.delete(obj, ch=True)
#                     cmds.polySmooth(obj, mth=0, sdt=2, ovb=1, ofb=3, ofc=0, ost=0, ocr=0, dv=2, bnr=1, c=1, kb=1,
#                                     ksb=1,
#                                     khe=0, kt=1, kmb=1, suv=1, peh=0, sl=1, dpe=1, ps=0.1, ro=1, ch=0)
#                 children = cmds.listRelatives(obj, children=True, type="transform", f=True)
#                 if children:
#                     SmoothSmoothSet(children)


######################################################################################
####### RENDER SUBMIT PUBLISH FUNCTIONS ##############################################
######################################################################################


def OnlyBG():  # Submit Render Scene
    # Hide all assets except Set and SetDress
    cmds.setAttr("vraySettings.cam_environmentVolumeOn", 0)  # turning off sphere render
    all_tops = cmds.ls("Anim:*:Root_Group")
    if cmds.objExists("OnlyBG_Exception"):
        except_list = FindObjectsFromSet("OnlyBG_Exception")
        all_tops = [x for x in all_tops if x not in except_list]
    if cmds.objExists("Bubble_VFX_Set"):
        cmds.setAttr("Bubble_VFX_Set.ignore", 1)
    for top in all_tops:
        c_type = None
        if cmds.attributeQuery("asset_type", n=top, ex=True):
            c_type = cmds.getAttr("%s.asset_type" % top)
        elif cmds.attributeQuery("assetType", n=top, ex=True):
            c_type = cmds.getAttr("%s.assetType" % top)
        if c_type:
            c_vis = cmds.getAttr("%s.visibility" % top)
            cmds.cutKey(top, attribute='visibility', option="keys")
            # TODO Change this so it doens't set set /setdress to 1, but sets everyhting else to 0 in visibility
            if c_type == "Set" or c_type == "SetDress":
                cmds.setAttr("%s.visibility" % top, c_vis)
            # cmds.setAttr("%s.visibility" % top, 1)
            else:
                cmds.setAttr("%s.visibility" % top, 0)

    if cmds.objExists("OnlyBG_Hide"):
        hide_list = FindObjectsFromSet("OnlyBG_Hide")
        for cur_obj in hide_list:
            if cmds.objExists(cur_obj):
                try:
                    cmds.cutKey(cur_obj, attribute='visibility', option="keys")
                    cmds.setAttr("%s.visibility" % cur_obj, 0)
                except:
                    logger.info("Can't work visibilty for %s" % cur_obj)

def exportPurpleCloudAlembicCache():
    import os
    startFrame = cmds.playbackOptions(query=True, minTime=True)
    cmds.currentTime(startFrame)
    purpleTintList = cmds.ls('::*.purpleTint')
    target = None
    for tint in purpleTintList:
        if not target:
            target = tint
        else:
            if cmds.getAttr(tint) > cmds.getAttr(target):
                target = tint
    target = target.replace(target.split(':')[-1], 'Cloud_Model_Ref:cloud_v004:Cloud_new')
    endFrame = cmds.playbackOptions(query=True, maxTime=True)
    root = "-root " + target
    save_name = os.path.abspath(os.path.join(cmds.file(query=True, sceneName=True), '../../04_Publish/cloudAlembic.abc')).replace(os.sep, '/')
    command = "-frameRange " + str(int(startFrame)) + " " + str(int(endFrame)) +" -uvWrite -worldSpace " + root + " -file " + save_name
    cmds.AbcExport(j=command)


def exportCopycatMirrorAlembicCache():
    import os
    startFrame = cmds.playbackOptions(query=True, minTime=True)
    cmds.currentTime(startFrame)
    target = cmds.ls('::CopycatMirror:Matte')[0]
    endFrame = cmds.playbackOptions(query=True, maxTime=True)
    root = "-root " + target
    save_name = os.path.abspath(os.path.join(cmds.file(query=True, sceneName=True), '../../04_Publish/copycatMirrorAlembic.abc')).replace(os.sep, '/')
    command = "-frameRange " + str(int(startFrame)) + " " + str(int(endFrame)) +" -uvWrite -worldSpace " + root + " -file " + save_name
    cmds.AbcExport(j=command)


def createRenderSubDivSet():
    import maya.mel as mel
    assetName = cmds.getAttr('|Root_Group.asset_name')
    setName = str(assetName).replace(' ', '_') + '_SubDivSet'
    subDivSet = cmds.ls(setName)
    if subDivSet:
        subDivSet = subDivSet[0]
    else:
        smoothTargets = cmds.sets('Smooth_Set', query=True)
        subDivSet = cmds.createNode('VRayDisplacement', n=setName)
        print(subDivSet)
        melCommand = "vray addAttributesFromGroup " + subDivSet + " vray_subdivision 1"
        mel.eval(melCommand)
        cmds.sets(smoothTargets, add=subDivSet)
    return subDivSet

def deleteRenderSubDivSet():
    assetName = cmds.getAttr('Root_Group.asset_name')
    setName = assetName.replace(' ', '_') + '_SubDivSet'
    subDivSet = cmds.ls(setName)
    if subDivSet:
        subDivSet = subDivSet[0]
        cmds.delete(subDivSet)
    #test for other subdiv sets
    vd_list = cmds.ls(type="VRayDisplacement",l=True)
    for vd in vd_list:
        #check if it has a displamcent map, else delete it.
        if not cmds.getAttr("%s.displacement" % vd):
            cmds.delete(vd)



def ExportBakedCamera(shot, shot_path, ep_seq_shot):
    #TODO Paths are hardcoded a bit, we could pull some of this out and use the config class instead
    if shot != "" and shot_path:
        camera_name = "%s_Cam" % shot
        if not cmds.objExists(camera_name):
            camera_name = "Anim:%s_Cam" % shot
        camera_path = "%s/04_Publish/%s_CameraPublish.ma" % (shot_path, ep_seq_shot)
    else:
        logger.warning("Can't export cam - couldn't find it or the path")
        return False
    # duplicate original camera transform, ic=True and un=True gets keys
    scene_camera_duplicate = (cmds.duplicate(camera_name, n="%s_Baked" % camera_name))[0]
    cmds.camera(scene_camera_duplicate, e=True, lt=False)

    cmds.setAttr("%s.renderable" % scene_camera_duplicate, 0)
    if cmds.listRelatives(scene_camera_duplicate, parent=True):
        cmds.parent(scene_camera_duplicate, world=True)

    # parent duplicated camera transform to original camera transform
    cmds.parentConstraint(camera_name, scene_camera_duplicate, mo=False, n="%s_pCon" % scene_camera_duplicate)
    start = cmds.playbackOptions(q=True, min=True)
    end = cmds.playbackOptions(q=True, max=True)
    # bake keys
    cmds.bakeResults('%s' % scene_camera_duplicate, simulation=True, time=(start, end), sampleBy=1,
                     oversamplingRate=1, disableImplicitControl=True, preserveOutsideKeys=False,
                     sparseAnimCurveBake=False, removeBakedAttributeFromLayer=False, removeBakedAnimFromLayer=True,
                     bakeOnOverrideLayer=False, minimizeRotation=True, controlPoints=False, shape=True)

    # delete parent constraint
    cmds.delete("%s_pCon" % scene_camera_duplicate)

    # export camera
    if cmds.objExists(scene_camera_duplicate):
        logger.info("EXPORTING CAMERA")
        cmds.select(scene_camera_duplicate, r=True)
        cmds.file(camera_path, f=True, type="mayaAscii", es=True, chn=True, exp=False, con=True,
                  preserveReferences=False)
    cmds.delete(scene_camera_duplicate)