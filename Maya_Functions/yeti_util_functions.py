
from getConfig import getConfigClass
CC = getConfigClass(set_env=False)

from Log.CoboLoggers import getLogger
logger = getLogger()

import os
import subprocess
import shutil

try:
    in_maya = True
    import maya.cmds as cmds
    import maya.mel as mel
    from Maya_Functions.asset_util_functions import GetAssetInfoFromRoot, GetAssetInfoFromFile
except:
    in_maya = False

# UF = UtilFunctions.PublishFunctions()

def setYetiPrePostRenderScripts():
    cmds.setAttr("defaultRenderGlobals.preMel", "catch(`pgYetiVRayPreRender`)", type="string")
    cmds.setAttr("defaultRenderGlobals.postMel", "catch(`pgYetiVRayPostRender`)", type="string")

def MayaPy_CacheShot(file_path="",only_selection=False,set_groom=True):
    selection = None
    if only_selection:
        selection = cmds.ls(sl=True)
    script_content = """import maya.standalone
maya.standalone.initialize('python')
import maya.cmds as cmds
import Maya_Functions.yeti_util_functions as YF
cmds.file('%s', open=True,f=True)
cmds.select(%s,r=True)
YF.CacheLightScene(only_selection=%s,set_groom=%s)
cmds.file(save=True)
cmds.quit(f=True)
""" % (file_path,selection,only_selection,set_groom)
    script_content = ";".join(script_content.split("\n"))
    base_command = 'mayapy.exe -c "%s"' % (script_content)
    logger.info(base_command)
    subprocess.Popen(base_command, shell=False, universal_newlines=True)


def CacheLightScene(only_selection=False, samples=2, set_groom=True):
    cur_scene = cmds.file(q=True,sn=True)
    info_dict = {}
    # info_dict = cfg_util.ComparePartOfPath(cur_scene,CC.get_shot_light_file(),info_dict)
    info_dict = CC.util.ComparePartOfPath(cur_scene,CC.get_shot_light_file(),**info_dict)
    cache_folder = CC.get_shot_yeti_cache_path(episode_name=info_dict["episode_name"],seq_name=info_dict["seq_name"],shot_name=info_dict["shot_name"])
    if not os.path.exists(cache_folder):
        os.mkdir(cache_folder)
    CacheYetiNode(selection=only_selection,cache_folder=cache_folder,samples=samples,set_groom=set_groom)


def CacheYetiNode(selection=True, start=None, end=None, samples=2, cache_folder=None, skip_caching=False, set_groom=True):
    yeti_node_list = GetYetiNodes(from_selection=selection, only_visible=False)  # Get selection yetinodes even if they are not visible
    #Seems to be nessessary. Add both paths to config?
    if yeti_node_list:
        logger.info("Found yetinodes: %s" % yeti_node_list)
        if not start:
            start = cmds.playbackOptions(q=True, minTime=True)
        if not end:
            end = cmds.playbackOptions(q=True, maxTime=True)
        start = start -1 #Get that frame before and after cached aswell
        end = end +1
        for yeti_node in yeti_node_list:
            # is_visible = cmds.ls(yeti_node, v=True)
            yeti_dict = {}
            cur_namespace = yeti_node.split(":")[-2] #Don't
            node_name = yeti_node  # Find node name:
            if "yetiNode_" in yeti_node:
                node_name = node_name.split("yetiNode_")[1]
            if "Shape" in yeti_node:
                node_name = node_name.split("Shape")[0]

            #Set yetinode to look at .GRM file for caching. Used for recaching.

            yeti_dict = GetAssetInfoFromRoot(yeti_node)

            yeti_dict["yeti_node"] = node_name
            yeti_node_groom = CC.get_YetiGroom(**yeti_dict)
            # print("This is the groom: %s" % yeti_node_groom)
            # yeti_node_groom = cfg_util.CreatePathFromDict(cfg.ref_paths["YetiGroom"], yeti_dict)
            logger.info(yeti_node_groom)
            if os.path.exists(yeti_node_groom) and set_groom:
                logger.info("setting groom input for %s" % yeti_node)
                cmds.setAttr("%s.fileMode" % yeti_node, 1)
                cmds.setAttr("%s.cacheFileName" % yeti_node, yeti_node_groom, type="string")
                cmds.setAttr("%s.overrideCacheWithInputs" % yeti_node,1)  # Set overwrite cache input to get new animation cached



            # Should use the config path to the shot to place the yeti cache. Should have its own path. Make dict with info and send it along to get path.
            if not cache_folder:
                cache_folder = "P:/930382_KiwiStrit2/Production/Temp/yeti_cache/"  # Temp folder for now. Should be place under shot/Publish/YetiCache/
            if not os.path.exists(cache_folder):
                os.mkdir(cache_folder)
            #add yeti_node folder:
            yeti_folder = "%s%s_%s/" % (cache_folder, cur_namespace,node_name)
            logger.info("Creating path for %s" % yeti_folder)
            if not os.path.exists(yeti_folder):
                os.mkdir(yeti_folder)
            yeti_filepath = "%s%s_%s_Cache_%s" % (yeti_folder,cur_namespace, node_name, "%04d.fur")  # ""Kiwi_Eyelids_Cache_0001.Fur"
            if not skip_caching:
                yeti_command = 'pgYetiCommand -writeCache "%s" -range %s %s -samples %s -updateViewport 0 -generatePreview 0 "%s"' % (
                yeti_filepath, start, end, samples,yeti_node)
                logger.info(yeti_command)
                logger.info("Caching yetinode: %s -> %s" % (yeti_node, yeti_filepath))
                mel.eval(yeti_command)
            else:
                logger.info("Skipping!")
                cache_path = "%s%s_%s_Cache_%s" % (yeti_folder, cur_namespace, node_name, "0001.fur")
                if not os.path.exists(cache_path):
                    logger.warning("can't find: %s" % cache_path)
                    return False
            logger.info("setting cache input for %s" % yeti_node)
            cmds.setAttr("%s.cacheFileName" % yeti_node, yeti_filepath, type="string")
            cmds.setAttr("%s.fileMode" % yeti_node, 1)
            cmds.setAttr("%s.overrideCacheWithInputs" % yeti_node, 0)

    else:
        logger.warning("Can't find yeti nodes! Stopped Caching")


def ExportAlembicSetup(samples=1, width=2, density=10,preview=False):
    temp_asset_info = GetAssetInfoFromFile()
    yeti_node_list = GetYetiNodes(True, True)
    for yeti_node in yeti_node_list:
        node_name = yeti_node
        #Clean up name:
        if "yetiNode_" in yeti_node:
            node_name = node_name.split("yetiNode_")[1]
        if "Shape" in yeti_node:
            node_name = node_name.split("Shape")[0]
        if preview:
            node_name = node_name + "_Preview"
            density = 1
        temp_asset_info["yeti_node"] = node_name
        # file_path = cfg_util.CreatePathFromDict(cfg.ref_paths["YetiAlembicCache"],temp_asset_info)
        file_path = CC.get_YetiAlembicCache(**temp_asset_info)
        #Make a save of the old cache just in case:
        f_folder,f_file = os.path.split(file_path)
        if not os.path.exists(f_folder):
            os.mkdir(f_folder)
        if os.path.exists(file_path):
            history_folder = "%s/_History" % f_folder
            if not os.path.exists(history_folder):
                os.mkdir(history_folder)
            v_num = 0
            for content in os.listdir(history_folder):
                if "%s_V" % f_file.split(".")[0] in content:
                    cur_num = int(content.split("%s_V" % f_file.split(".")[0])[1].split(".")[0])
                    if cur_num > v_num:
                        v_num = cur_num
            v_num = '%03d' % (v_num + 1)
            shutil.move(file_path,"%s/%s_V%s.grm" % (history_folder,f_file.split(".")[0],v_num))
        #Now do the new cache
        CacheToAlembic(yeti_filepath=file_path,yeti_node=yeti_node,samples=samples,alembic_width=width,alembic_density=density)
        #check if an alembic cache is already in scene
        if not cmds.objExists("yetiAlembic_%s" % node_name):
            ImportAlembicAsVrayProxy(yeti_filepath=file_path,node_name="yetiAlembic_%s" % node_name)


def CacheToAlembic(yeti_filepath=None, yeti_node=None, samples=1, alembic_width=2, alembic_density=10):
    # current_nodes =GetYetiNodes(True,True)
    # print("MAKING ALEMBIC OF : %s" % current_nodes)
    #pgYetiCommand -writeAlembic "P:/930382_KiwiStrit2/Production/Assets/3D_Assets/Set/Main/ForestClearing/02_Ref/YetiGroom/Alembic/yetiNode_Hill.abc" -range 1 1 -samples 1 -filePerFrame -updateViewport 0 -alembicWidth 2
    alembic_multi = cmds.getAttr("%s.renderWidth" % yeti_node)
    alembic_width = alembic_width*alembic_multi
    yeti_command = 'pgYetiCommand -writeAlembic "%s" -range 1 1 -samples %s -updateViewport 0 -filePerFrame -alembicWidth %s -alembicDensity %s "%s"' % (yeti_filepath, samples, alembic_width,alembic_density, yeti_node)
    mel.eval(yeti_command)
    mel.eval("vrayClearProxiesPreviewCache") #Clear vray proxies cache to update previous vray-proxy of alembic.


def ImportAlembicAsVrayProxy(yeti_filepath, node_name):
    # mel.eval("vrayClearProxiesPreviewCache")
    cmds.vrayCreateProxy(node=node_name, existing=True, dir="%s" % (yeti_filepath),createProxyNode=True,newProxyNode=True)


def ExportGroomSelection(yeti_node_list=None):
    temp_asset_info = GetAssetInfoFromFile()
    if not yeti_node_list:
        yeti_node_list = cmds.ls(sl=True)
    for yeti_node in yeti_node_list:
        if not cmds.nodeType(yeti_node)=="pgYetiMaya":
            find_yeti = cmds.listRelatives(yeti_node, type="pgYetiMaya")
            if not find_yeti:
                logger.info("%s not a yeti node! Skipping it" % yeti_node)
                continue
            else:
                yeti_node=find_yeti[0]
        node_name = yeti_node
        if "yetiNode_" in yeti_node:
            node_name = node_name.split("yetiNode_")[1]
        if "Shape" in yeti_node:
            node_name = node_name.split("Shape")[0]
        temp_asset_info["yeti_node"] = node_name
        file_path = CC.get_YetiGroom(**temp_asset_info)
        # file_path = cfg_util.CreatePathFromDict(cfg.ref_paths["YetiGroom"],temp_asset_info)
        f_folder,f_file = os.path.split(file_path)
        if not os.path.exists(f_folder):
            os.mkdir(f_folder)
        if os.path.exists(file_path):
            history_folder = "%s/_History" % f_folder
            if not os.path.exists(history_folder):
                os.mkdir(history_folder)
            v_num = 0
            for content in os.listdir(history_folder):
                if "%s_V" % f_file.split(".")[0] in content:
                    cur_num = int(content.split("%s_V" % f_file.split(".")[0])[1].split(".")[0])
                    if cur_num > v_num:
                        v_num = cur_num
            v_num = '%03d' % (v_num + 1)
            shutil.move(file_path,"%s/%s_V%s.grm" % (history_folder,f_file.split(".")[0],v_num))

        cmds.setAttr("%s.fileMode" % yeti_node, 0)
        ExportGrooms(yeti_node,file_path)
        cmds.setAttr("%s.cacheFileName" % yeti_node, file_path, type="string")
        cmds.setAttr("%s.fileMode" % yeti_node, 1)
        cmds.setAttr("%s.overrideCacheWithInputs" % yeti_node, 1)


def ExportGrooms(yeti_node=None,file_path=None):
    #Must be the shape node itself can't be transform
    if not yeti_node:
        yeti_node = cmds.ls(sl=True)[0]
    if cmds.nodeType(yeti_node)=="transform":
        yeti_node = cmds.listRelatives(yeti_node, type="pgYetiMaya")[0]

    cmds.pgYetiCommand(yeti_node,exportGroom=file_path) #".GRM" at the end I think


def SetYetiNodeToCache():
    yeti_nodes = cmds.ls(type="pgYetiMaya")
    for yeti_node in yeti_nodes:
        cmds.setAttr("%s.fileMode" % yeti_node, 1)
        cmds.setAttr("%s.overrideCacheWithInputs" % yeti_node, 1)

def refreshTextureCache():
    import maya.mel as mel
    mel.eval("pgYetiFlushDisplayCacheAllNodes")
    mel.eval("pgYetiFlushTextureCacheAllNodes")

def UpdateYetiNode(yeti_node=None, replace_list=[]): #Update texture paths from old season to new. Could also work for out-of-house path updates?
    if not yeti_node:
        yeti_node = cmds.ls(sl=True)
    if cmds.nodeType(yeti_node)=="transform":
        yeti_node = cmds.listRelatives(yeti_node, type="pgYetiMaya")[0]
    # my_yeti_node = "yetiNode_Grass1Shape"
    if yeti_node and cmds.nodeType(yeti_node)=="pgYetiMaya":
        cmds.setAttr("%s.fileMode" % yeti_node, 0)

        groom_path = cmds.getAttr("%s.cacheFileName" % yeti_node)
        if groom_path:
            groom_path = groom_path.replace("\\", "/")
            for pk,pv in replace_list:
                if pk in groom_path:
                    groom_path =groom_path.replace(pk,pv)
            cmds.setAttr("%s.cacheFileName" % yeti_node, groom_path, type="string")
        texture_nodes = cmds.pgYetiGraph(yeti_node, listNodes=True,type="texture")
        for cur_node in texture_nodes:
            cur_file = cmds.pgYetiGraph(yeti_node, node=cur_node, param="file_name", getParamValue=True)
            new_file = cur_file
            for k,v in replace_list:
                if k in new_file:
                    new_file = new_file.replace(k,v)
            if os.path.exists(new_file):
                logger.info("setting: %s -> %s" % (cur_file,new_file))
                cmds.pgYetiGraph(yeti_node, node=cur_node, param="file_name", setParamValueString=new_file)
            else:
                logger.warning("Can't find: %s->%s in %s" % (cur_file,new_file,yeti_node))
        """now also change the paths of the other-image search path on the yeti-node"""
        logger.info("yeti-node: %s" % yeti_node)
        # if cmds.attributeQuery("imageSearchPath", n=yeti_node, exists=True):
        yeti_paths = cmds.getAttr("%s.imageSearchPath" % yeti_node)
        if yeti_paths:
            yeti_paths = yeti_paths.replace("\\", "/")
            for pk,pv in replace_list:
                if pk in yeti_paths:
                    yeti_paths =yeti_paths.replace(pk,pv)
            cmds.setAttr("%s.imageSearchPath" % yeti_node,yeti_paths,type="string")


def GetYetiNodes(from_selection=True, only_visible=True):
    return_list = []
    if from_selection:
        yeti_node_list = cmds.ls(sl=True)
        for yeti_node in yeti_node_list:
            if not cmds.nodeType(yeti_node) == "pgYetiMaya":
                find_yeti = cmds.listRelatives(yeti_node, type="pgYetiMaya")
                if not find_yeti:
                    logger.warning("%s not a yeti node! Skipping it" % yeti_node)
                    continue
                else:
                    return_list.append(find_yeti[0])
            else:
                return_list.append(yeti_node)
    else:
        return_list = cmds.ls(type="pgYetiMaya")
    if only_visible and return_list:
        return_list = cmds.ls(return_list, v=True)
    return return_list


def GetGeoOfGPUCache(): #TODO Make import of geo here
    pass
    #selection = cmds.ls(sl=True)
    #gp_sel = cmds.listRelatives(selection,type="GPUCache")
    # for sel in gp_sel:
    #
    #     cur_path = cmds.getAttr("%s.gpu_path")
        #AbcImport -mode import "P:/930382_KiwiStrit2/Production/Assets/3D_Assets/Setdress/Stone/StoneG/02_Ref/StoneG_GPU.abc";


def ReadyForBakeTexture(size=50, cur_samples=0, map_size=1024):
    ext_type = "png"
    selection = cmds.ls(sl=True)
    if selection:
        target_mesh = selection[0]
    else:
        logger.info("Please select your target mesh!")
        return False
    if len(selection)>1:
        painter_objects = selection[1:]
    else:
        painter_group = "Grass_Painter_Group"
        if cmds.objExists(painter_group):
            painter_objects = cmds.listRelatives(painter_group, type="transform")  # get all transform children of group.
        else:
            logger.info("Can't find Grass_Painter_Group to use for selection of painter objects!")
            return False
    cur_asset_dict = GetAssetInfoFromRoot()
    if cur_asset_dict:
        file_path = "%s/03_Texture/PNG/Grass_Exclude_Texture" % CC.get_asset_base_path(**cur_asset_dict)
        if not os.path.exists(os.path.split(file_path)[0]):
            os.mkdir(os.path.split(file_path)[0])
    else:
        scene_name = cmds.file(q=True, sn=True,shn=True)
        if scene_name:
            scene_name = scene_name.split(".")[0]
        else:
            logger.warning("Please save scene to continue")
            return False
        file_path = "%s/images/Grass_Exclude_%s" % (CC.get_base_path(),scene_name)
        logger.warning("Doesn't recognise current scene as an asset! Can't create correct output path\nSaving here instead: %s" % file_path)
    logger.info("Trying to bake texture!")
    BakeTextureFromObjectCollision(target_mesh=target_mesh,painter_objects=painter_objects,save_path=file_path,cur_size=size,map_size=map_size,samples=cur_samples)
    if os.path.exists("%s.%s" %(file_path,ext_type)):
        lam_node = "Bake_Test_Lambert"
        tex_node = "Bake_Test_Texture"
        if not cmds.objExists(lam_node):
            cmds.shadingNode("lambert", asShader=True,name=lam_node)
        if not cmds.objExists(tex_node):
            cmds.shadingNode("file", asTexture=True,isColorManaged=True,name=tex_node)
            cmds.connectAttr("%s.outColor" % tex_node,"%s.color" % lam_node,f=True)
        cmds.setAttr("%s.fileTextureName" % tex_node, "%s.%s" % (file_path,ext_type),type="string")


def ImportStyledGroomsFromSelection(groom_type="Uncut", also_cache=False):
    cur_selection = cmds.ls(sl=True)
    to_cache = []
    for sel in cur_selection:

        if ":" in sel:
            yeti_dict = GetAssetInfoFromRoot(sel)
            if "Anim:" in sel:
                cur_namespace = ":".join(sel.split(":")[0:2])
                #cur_asset = sel.split(":")[1]
            else:
                cur_namespace = sel.split(":")[0]
                #cur_asset = cur_namespace
            cur_asset = yeti_dict["asset_name"]
        logger.info("Trying to import using %s:%s" % (cur_namespace,cur_asset))
        if groom_type =="Styled":

            style_nodes = ImportStyledGrooms(cur_namespace,cur_asset)
            to_cache.extend(style_nodes)
        unique_nodes = SetUniqueGroom(cur_asset,groom_type,cur_namespace)
        to_cache.extend(unique_nodes)
        cmds.select(to_cache,r=True)
        logger.info(to_cache)
        if also_cache:
            CacheLightScene(only_selection=True,set_groom=False)




def ImportStyledGrooms(cur_namespace, cur_asset):
    # cur_namespace = "Anim:ForestCreatureC"
    # cur_asset = "ForestCreatureC"

    file_dict = {
        "ForestCreatureA": ["P:/930382_KiwiStrit2/Production/Assets/3D_Assets/Char/Secondary/ForestCreatureA/02_Ref/YetiGroom/FurTrimmingDay_Style_Import.ma","Body_GeoShape","yetiNode_FurTrimmingDay_HairShape"],
        "ForestCreatureC": ["P:/930382_KiwiStrit2/Production/Assets/3D_Assets/Char/Secondary/ForestCreatureC/02_Ref/YetiGroom/FurTrimming_Style_Import.ma","Body_GeoShape", "yetiNode_FurTrimmingDay_HairShape"],
        "ForestCreatureF": ["P:/930382_KiwiStrit2/Production/Assets/3D_Assets/Char/Secondary/ForestCreatureF/02_Ref/YetiGroom/FurTrimming_Style_Import.ma","Body_GeoShape", "yetiNode_FurTrimmingDay_HairShape"],
    }
    return_list = []
    if cur_asset in file_dict.keys():
        cmds.file(file_dict[cur_asset][0],type="mayaAscii", i=True, namespace=cur_namespace, mergeNamespacesOnClash=True)

        cur_string = "pgYetiAddGeometry \"%s:%s\" \"%s:%s\"" % (cur_namespace,file_dict[cur_asset][1],cur_namespace,file_dict[cur_asset][2])
        import maya.mel as mel
        mel.eval(cur_string)
        return_list.append("%s:%s" % (cur_namespace,file_dict[cur_asset][2]))
    return return_list


def SetUniqueGroom(cur_asset, groom_type, cur_namespace):
    """
    :param cur_asset: the asset name "ForestCow"
    :param cur_namespace: the full path to the yeti_node "Anim:ForestCow:yetiNode_BodyShape"
    :param groom_type: the groom type to change to. namedbased.
    """
    #TODO FINISH THIS CONVERTING TO USING CC
    to_return = []
    groom_dict = {
        "Strit":{
            "Uncut": {'asset_name':'Strit','asset_type':'Char','asset_category':'Main','groom_name':'Strit_FurTrimmingDay_Groom.grm','target_yeti_node':'yetiNode_BodyShape'},
            "Styled": {'asset_name':'Strit','asset_type':'Char','asset_category':'Main','groom_name':'Strit_FurTrimmingStyle_Groom.grm','target_yeti_node':'yetiNode_BodyShape'}},
        "Kiwi": {"Uncut": {'asset_name':'Kiwi','asset_type':'Char','asset_category':'Main','groom_name':'Kiwi_FurTrimmingDay_Hair_Groom.grm','target_yeti_node':'yetiNode_BodyShape'}},
        "ForestCow":{"Uncut":{'asset_name':'ForestCow','asset_type':'Char','asset_category':'Secondary','groom_name':'ForestCow_FurTrimmingDay_Body_Groom.grm','target_yeti_node':'yetiNode_BodyShape'},
                     "Styled":{'asset_name':'ForestCow','asset_type':'Char','asset_category':'Secondary','groom_name':'ForestCow_FurTrimmingDay_Hair_Groom.grm','target_yeti_node':'yetiNode_BodyShape'}},
        "ForestCreatureA":{"Uncut":{'asset_name':'ForestCreatureA','asset_type':'Char','asset_category':'Secondary','groom_name':'ForestCreatureA_FurTrimmingDay_Body_Groom.grm','target_yeti_node':'yetiNode_BodyShape'}},
        "ForestCreatureC": {"Uncut":{'asset_name':'ForestCreatureC','asset_type':'Char','asset_category':'Secondary','groom_name':'ForestCreatureC_FurTrimmingDay_Body_Groom.grm','target_yeti_node':'yetiNode_BodyShape'}},
        "ForestCreatureD": {"StyleA":{'asset_name':'ForestCreatureD','asset_type':'Char','asset_category':'Secondary','groom_name':'StyleA_ForestCreatureD_Body_Groom.grm','target_yeti_node':'yetiNode_BodyShape'}},
        "ForestCreatureF": {"Uncut":{'asset_name':'ForestCreatureF','asset_type':'Char','asset_category':'Secondary','groom_name':'ForestCreatureF_FurTrimmingDay_Body_Groom.grm','target_yeti_node':'yetiNode_BodyShape'}}
    }

    if cur_asset in groom_dict:
        if groom_type in groom_dict[cur_asset]:
            logger.info("Found %s for %s" % (groom_type,cur_asset))
            cur_groom_dict = groom_dict[cur_asset][groom_type]
            yeti_groom_path = "%s/YetiGroom/%s" % (CC.get_asset_ref_folder(**cur_groom_dict),cur_groom_dict["groom_name"]) #groom_dict[cur_asset][groom_type][0]
            yeti_groom_node = "%s:%s" % (cur_namespace,cur_groom_dict["target_yeti_node"])
            if os.path.exists(yeti_groom_path):
                logger.info("Path found")
                if cmds.objExists(yeti_groom_node):
                    logger.info("Found")
                    cmds.setAttr("%s.fileMode" % yeti_groom_node, 1)
                    cmds.setAttr("%s.cacheFileName" % yeti_groom_node, yeti_groom_path, type="string")
                    cmds.setAttr("%s.overrideCacheWithInputs" % yeti_groom_node, 1)  # Set overwrite cache input to get new animation cached
                to_return.append(yeti_groom_node)
    return to_return


def changeHairStyleOnList(asset_name="",shot_dict_list=[],style_name=""):
    from Multiplicity import ThreadPool
    cur_threadpoll = ThreadPool.ThreadPool(max_threads=5)
    thread_list = []
    print(shot_dict_list)
    for shot in shot_dict_list:
        print(shot)
        shot_path = CC.get_shot_light_file(**shot)
        print(shot_path)
        thread_list.append(ThreadPool.Worker(func=runSetUniqueGroomInMayaPy,file_path=shot_path,asset_name=asset_name,style_name=style_name))
    cur_threadpoll.startBatch(thread_list,use_amount=5)

def runSetUniqueGroomInMayaPy(file_path=None,asset_name=None,style_name=None):
    import sys
    print("STARTING ON %s" % file_path)
    script_content = """import maya.standalone
    maya.standalone.initialize('python')
    import maya.cmds as cmds
    import Maya_Functions.yeti_util_functions as yeti_util
    cmds.file('{file_path}', open=True,f=True)
    yeti_util.setGroomBasedOnAssetName(asset_name='{asset_name}',style_name='{style_name}')
    cmds.quit(f=True)""".format(file_path=file_path, asset_name=asset_name, style_name=style_name)
    script_content = ";".join(script_content.split("\n"))
    base_command = 'mayapy.exe -c "%s"' % (script_content)
    print(base_command)
    # subprocess.call(base_command,shell=False,universal_newlines=True)
    p = subprocess.Popen(base_command, shell=False, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    st,se = p.communicate()
    print("ERRORS:\n%s" % se)
    print("OUTPUT:\n%s" % st)




def setGroomBasedOnAssetName(asset_name="",style_name=""):
    import maya.cmds as cmds
    asset_yeti = cmds.ls("*::%s*:Root_Group" % asset_name)
    yeti_nodes = []
    for cur_asset in asset_yeti:
        cur_namespace = cur_asset.split(":Root_Group")[0]
        yn = SetUniqueGroom(cur_asset=asset_name,groom_type=style_name,cur_namespace=cur_namespace)
        if yn:
            yeti_nodes.extend(yn)
    if yeti_nodes:
        print("SELECTION: %s" % yeti_nodes)
        cmds.select(yeti_nodes,r=True)
        CacheLightScene(only_selection=True, set_groom=False)
    else:
        CacheLightScene(only_selection=False, set_groom=False)


def BakeTextureFromObjectCollision(target_mesh="", painter_objects=[], save_path="", cur_size=80, map_size=1024, samples=0): #NOT USED -Experimental
    #To invert 1 to 0 in yeti: "original_length_multiplier" * ("texture_attribute" > 0?0:1)
    # baking a texture from objects:
    # #Creating collision objects to be excluded from the texture
    # my_loc = "locator1"
    # my_painters = []
    # cur_target = "pPlaneShape1"
    # for x in range(1, 11):
    #     print(x)
    #     cmds.currentTime(x, update=True)
    #     temp = cmds.polySphere(n="%s_%s_Collision" % (my_loc, x))
    #     cmds.matchTransform(temp, my_loc)
    #     my_painters.append(temp)

    # file_path = "C:/Users/chris/OneDrive/Documents/maya/projects/930382_Kiwi&Strit_2/Production/images/sampledDiffuseColor"
    my_source = ""
    for painter_obj in painter_objects:
        paint_shape = cmds.listRelatives(painter_obj,s=True)[0]
        my_source = '%s -source %s'%(my_source, paint_shape)
    #map_output = "diffuseRGB"
    map_output = "alpha"
    # my_command = 'surfaceSampler -target %s -uvSet map1 -searchOffset %s\
    # -maxSearchDistance %s -searchCage "" %s -mapOutput diffuseRGB -mapWidth 1024 -mapHeight 1024 -max 1 -mapSpace tangent\
    #  -mapMaterials 1 -shadows 1 -filename "%s" -fileFormat "png" -superSampling 0 -filterType 2 -filterSize 1\
    #   -overscan 1 -searchMethod 1 -useGeometryNormals 1 -ignoreMirroredFaces 0 -flipU 0 -flipV 0' % (target_mesh,cur_size,cur_size,my_source,save_path)
    my_command = 'surfaceSampler -target {target_mesh} -uvSet map1 -searchOffset {cur_size}\
    -maxSearchDistance {cur_size} -searchCage "" {my_source} -mapOutput {map_output} -mapWidth {map_size} -mapHeight {map_size} -max 1 -mapSpace tangent\
     -mapMaterials 1 -shadows 1 -filename "{save_path}" -fileFormat "png" -superSampling {samples} -filterType 2 -filterSize 1\
      -overscan 1 -searchMethod 1 -useGeometryNormals 1 -ignoreMirroredFaces 0 -flipU 0 -flipV 0'.format(target_mesh=target_mesh,cur_size=cur_size,map_size=map_size,map_output=map_output,samples=samples,my_source=my_source,save_path=save_path)
    mel.eval(my_command)

if __name__ == '__main__':
    from PublishReport import PublishReport
    pr = PublishReport()
    pr.getData("E08")
    shot_list = pr.getShotsUsingAsset(identity="ForestCreatureD",scope="E08_SQ010_SH010")
    shot_dict_list = []
    for shot in shot_list:
        shot_info = pr.data[shot].getInfoDict()
        shot_dict_list.append(shot_info)
    # import Maya_Functions.yeti_util_functions as yeti_util
    # reload(yeti_util)
    # yeti_util.setGroomBasedOnAssetName(asset_name="ForestCreatureD", style_name="StyleA")
    # changeHairStyleOnList(asset_name="ForestCreatureD",style_name="StyleA",shot_dict_list=shot_dict_list)