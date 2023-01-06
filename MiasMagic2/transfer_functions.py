import os
import shutil
import subprocess

# from reloadModules import resetSession
# #resetSession()
# CIM.dropCachedImports("BasicTreeView_ThumbnailTesting","PublishMaster", "UtilFunctions", "AssetFunctions", "PublishSetdress","transferCustomAttributes", "UpdateTextures", "getConfig", "Configs.ConfigClass_MiasMagic2", "Configs.ConfigClass_MiasMagic", "Configs.Config_MiasMagic", "Configs.Config_MiasMagic2", "ConfigUtil")


from getConfig import getConfigClass

CC = getConfigClass()
from runtimeEnv import getRuntimeEnvFromConfig

cur_run = getRuntimeEnvFromConfig(CC, True)

import Maya_Functions.attr_util_functions as attr
import Maya_Functions.set_util_functions as set_util


#
#   Probably obsolete, delete when transferring is working
#
# def copyAsset(asset_info):
#     return_path = None
#     process = None
#     if asset_info['asset_type'] == 'Char':
#         new_asset_base_path = CC.get_asset_base_path(**asset_info)
#         old_asset_base_path = CC.old.asset_base_path(**asset_info)
#
#         new_base_path = CC.get_base_path()
#         old_base_path = CC.old.get_base_path()
#
#
#         if not os.path.exists(new_asset_base_path):
#             try:
#                 shutil.copytree(old_asset_base_path, new_asset_base_path, ignore=shutil.ignore_patterns('_History'))
#                 getMayaFiles(new_asset_base_path)
#
#             except shutil.Error as err:
#                 print(r'Copy error')
#                 shutil.errors.extend(err.args[0])
#
#             mayaFiles = getMayaFiles(new_asset_base_path)
#             for file_path in mayaFiles:
#                 if file_path[-3:] == '.ma':
#                     file_type = 'mayaAscii'
#                 elif file_path[-3:] == '.mb':
#                     file_type = 'mayaBinary'
#                 else:
#                     file_type = 'mayaAscii'
#                 cleanCharFiles(file_path, file_type, old_base_path, new_base_path)
#
#         else:
#             print('Folder already exists: ' + new_asset_base_path)
#
#
#     if asset_info['asset_type'] == 'Prop':
#         """Node info:"""
#         #asset_info.update(cfg.project_paths) #add new config paths to asset info
#         new_texture_folder = CC.get_asset_texture_folder(**asset_info)
#         asset_info["asset_step"] = "Base"
#         new_base_file = CC.get_asset_work_file(**asset_info)
#
#
#         asset_info["asset_output"] = "Render"
#         old_texture_folder = CC.old.get_asset_texture_folder(**asset_info)
#         render_ref = CC.get_Render(**asset_info)
#
#         new_base_path = CC.get_base_path()
#         old_base_path = CC.old.get_base_path()
#
#         try:
#             if os.path.exists(new_base_file):
#                 print('File already exists: ' + new_base_file)
#             else:
#                 asset_functions = AF.CreateAsset(asset_info)  # create new empty asset based on the new config and asset info.
#                 asset_functions.Run()  # if asset_functions.Run():
#
#                 # Loop through folders inside texture folder
#                 for folder in os.listdir(old_texture_folder):
#                     folderPath = os.path.join(old_texture_folder, folder).replace(os.sep, '/')
#
#                     # Loop through items inside the folders
#                     for item in os.listdir(folderPath):
#                         itemPath = os.path.join(old_texture_folder, folder, item).replace(os.sep, '/')
#                         destination = os.path.join(new_texture_folder, folder, item).replace(os.sep, '/')
#
#                         # If item is folder
#                         if os.path.isdir(itemPath):
#                             # Attempts to copy folder
#                             try:
#                                 shutil.copytree(itemPath, destination)
#                             except:
#                                 print('Failed to copy ' + itemPath + ' to ' + destination)
#                         else:
#                             # Attempts to copy file
#                             try:
#                                 shutil.copyfile(itemPath, destination)
#                             except:
#                                 print('Failed to copy ' + itemPath + ' to ' + destination)
#         except:
#             pass
#
#             return_path = new_base_file
#
#         # file_path = r"P:\_WFH_Projekter\930486_MiaMagicPlayground_S3-4\4_Production\Assets\3D_Assets\Prop\Assessory\Donut\01_Work\Maya\Donut_Base.ma".replace(
#         #     os.sep, '/')
#         file_type = "mayaAscii"
#         process = migrateProp(new_base_file, file_type, render_ref, old_base_path, new_base_path)
#
#
#     if asset_info['asset_type'].lower() == 'setdress':
#         if asset_info['name'] in ['BushE', 'FaceFlowerA', 'MushroomA', 'MushroomB', 'MushroomC', 'RockA', 'RockB', 'RockC',
#                               'RockY', 'StickA', 'StickB', 'TwigPileA', 'voleyballBall', 'voleyballScoreBoard',
#                               'WhirleyBallNetA', 'BabyCrystalA', 'SmallBluePlanet', 'SpaceBubbleA', 'BigTreeA',
#                               'BranchLongA', 'PineTreeU', 'ConePlantA', 'CoralPlantB', 'PlantB', 'StaggeredHills',
#                               'StaggeredHillsA', 'StaggeredHillsB', 'StaggeredHillsC', 'StarfishA', 'UWPlantB',
#                               'UWPlantBA', 'UWRockA', 'UWRockB', 'UWRockC', 'VineB']:
#             pass
#
#         else:
#             old_asset_info = asset_info.copy()
#             print(old_asset_info)
#             if asset_info['new_asset_category']:
#                 asset_info['asset_category'] = asset_info['new_asset_category']
#             asset_info['asset_type'] = 'Setdress'
#             # asset_info.update(cfg.project_paths) #add new config paths to asset info
#             new_texture_folder = CC.get_asset_texture_folder(**asset_info)
#             old_texture_folder = CC.old.get_asset_texture_folder(**old_asset_info)
#
#             asset_info["asset_step"] = "Base"
#             asset_info["asset_output"] = "Render"
#             old_asset_info["asset_step"] = "Base"
#             old_asset_info["asset_output"] = "Render"
#             new_base_file = CC.get_asset_work_file(**asset_info)
#             new_base_path = CC.get_base_path()
#             old_base_path = CC.old.get_base_path()
#             render_ref = CC.old.get_Render(**old_asset_info)
#             # new_base_file = cfg_util.CreatePathFromDict(cfg.project_paths["asset_work_file"], asset_info)
#             # new_base_path = cfg_util.CreatePathFromDict(cfg.project_paths["base_path"], asset_info)
#             # old_base_path = old_cfg_util.CreatePathFromDict(old_cfg.project_paths["base_path"], asset_info)
#             # render_ref = old_cfg_util.CreatePathFromDict(old_cfg.ref_paths["Render"], asset_info)
#
#             if os.path.exists(new_base_file):
#                 print('File already exists: ' + new_base_file)
#             else:
#                 asset_functions = AF.CreateAsset(asset_info)  # create new empty asset based on the new config and asset info.
#                 asset_functions.Run()  # if asset_functions.Run():
#
#                 # Loop through folders inside texture folder
#                 print(old_texture_folder)
#                 for folder in os.listdir(old_texture_folder):
#                     folderPath = os.path.join(old_texture_folder, folder).replace(os.sep, '/')
#                     if os.path.isdir(folderPath):
#
#                         # Loop through items inside the folders
#                         for item in os.listdir(folderPath):
#                             itemPath = os.path.join(old_texture_folder, folder, item).replace(os.sep, '/')
#                             destination = os.path.join(new_texture_folder, folder, item).replace(os.sep, '/')
#
#                         # If item is folder
#                             if os.path.isdir(itemPath):
#                                 # Attempts to copy folder
#                                 try:
#                                     shutil.copytree(itemPath, destination)
#                                 except:
#                                     print('Failed to copy ' + itemPath + ' to ' + destination)
#                             else:
#                                 # Attempts to copy file
#                                 try:
#                                     shutil.copyfile(itemPath, destination)
#                                 except:
#                                     print('Failed to copy ' + itemPath + ' to ' + destination)
#
#                     else:
#                         # Someone fucked up and there is a file where there should not be.
#                         # We will move it anyways
#                         try:
#                             shutil.copyfile(folderPath)
#                         except:
#                             print('Failed to copy ' + folderPath)
#
#
#                 file_type = "mayaAscii"
#                 print(new_base_file)
#                 print(new_base_path)
#                 print(old_base_path)
#                 print(render_ref)
#                 process = migrateSetdress(new_base_file, file_type, render_ref, old_base_path, new_base_path)
#                 print('Done migrating Setdress file: ' + asset_info['name'])
#                 return_path = new_base_file
#
#     return return_path, process


# def migrateProp(file_path, file_type, render_ref, old_base_path, new_base_path):
#     print(render_ref)
#     script_content = """import maya.standalone
# maya.standalone.initialize('python')
# import maya.cmds as cmds
# import sys
# sys.path.append('C:/Users/mmcb/PycharmProjects/bombay_base_production/')
# cmds.file('%s', open=True,f=True)
# cmds.file(type='%s')
# from assetTransfer import propAssetTransfer
# propAssetTransfer('%s')
# from UpdateTextures import update_textures
# update_textures('%s', '%s')
# cmds.file(save=True)
# cmds.quit(f=True)""" % (file_path, file_type, render_ref, old_base_path, new_base_path)
#     script_content = ";".join(script_content.split("\n"))
#     return script_content
#     # base_command = 'mayapy.exe -c "%s"' % (script_content)
#     # print(base_command)
#     # return subprocess.Popen(base_command, shell=False, universal_newlines=True)


#
#   Might be obsolete
#
# def migrateSetdress(file_path, file_type, render_ref, old_base_path, new_base_path, stdout=subprocess.PIPE):
#     script_content = """import maya.standalone
# maya.standalone.initialize('python')
# import maya.cmds as cmds
# cmds.file('%s', open=True,f=True)
# cmds.file(type='%s')
# from MiasMagic2.assetTransfer import setdressAssetTransfer
# setdressAssetTransfer('%s')
# from MiasMagic2.UpdateTextures import update_textures
# update_textures('%s', '%s')
# cmds.file(save=True)
# cmds.quit(f=True)""" % (file_path, file_type, render_ref, old_base_path, new_base_path)
#     script_content = ";".join(script_content.split("\n"))
#     # print(script_content)
#     return script_content
#     # Q.ProcRun()
#     #base_command = 'mayapy.exe -c "%s"' % (script_content)
#     #print(base_command)
#     #return subprocess.Popen(base_command, shell=False, universal_newlines=True, stdout=subprocess.PIPE)


# def cleanCharFiles(file_path, file_type, old_base_path, new_base_path):
#     script_content = """import maya.standalone
# maya.standalone.initialize('python')
# import maya.cmds as cmds
# cmds.file('%s', open=True,f=True)
# cmds.file(type='%s')
# from MiasMagic2.UpdateTextures import update_textures, updateRef, addPublishSet
# update_textures('%s', '%s')
# updateRef('%s', '%s')
# addPublishSet()
# cmds.file(save=True)
# cmds.quit(f=True)""" % (file_path, file_type, old_base_path, new_base_path, old_base_path, new_base_path)
#     script_content = ";".join(script_content.split("\n"))
#     base_command = 'mayapy.exe -c "%s"' % (script_content)
#     # return script_content
#     return subprocess.Popen(base_command, shell=False, universal_newlines=True, stdout=subprocess.PIPE)

def getMayaFiles(directory, list=[], ignore=[]):
    for item in os.listdir(directory):
        if item not in ignore:
            path = os.path.join(directory, item).replace(os.sep, '/')
            if os.path.isdir(path):
                getMayaFiles(path, list, ignore)
            else:
                if path[-3:] in ['.ma', '.mb']:
                    list.append(path)
    return list


def transferCharacter(asset_info):
    old_asset_base_path = CC.old.get_asset_base_path(**asset_info)
    new_asset_base_path = CC.get_asset_base_path(**asset_info)
    asset_work_folder = CC.get_asset_work_folder(**asset_info)

    if not os.path.exists(new_asset_base_path):
        transferFolderUntoFolder(old_asset_base_path, new_asset_base_path)
        transferTextureFolder(asset_info=asset_info, new_asset_info=asset_info)
        transferDesignFolder(asset_info=asset_info, new_asset_info=asset_info)
        mayaFiles = getMayaFiles(asset_work_folder, [], ignore=['_History'])
        processList = []
        import QThreads as Q
        for file in mayaFiles:
            asset_info = CC.util.ComparePartOfPath(file, CC.get_asset_work_file(), asset_info)
            process = """import maya.standalone
maya.standalone.initialize('python')
import maya.cmds as cmds
from MiasMagic2.transfer_functions import characterAssetFlow
characterAssetFlow(%s, '%s')""" % (asset_info, file)
            process = ";".join(process.split("\n"))
            processList.append(process)
        Q.CreateProcQueue(processList)
    else:
        print('Asset already exist: ' + new_asset_base_path)



def transferProp(old_asset_info):
    asset_info = old_asset_info.copy()
    from AssetFunctions import CreateAsset
    create_dict = asset_info.copy()
    new_asset = CreateAsset(create_dict)

    if new_asset.Run():
        # from MiasMagic2.transfer_functions import transferTextureFolder, transferDesignFolder
        transferTextureFolder(asset_info=old_asset_info, new_asset_info=asset_info)
        transferDesignFolder(asset_info=old_asset_info, new_asset_info=asset_info)
        import QThreads as Q
        process = """import maya.standalone
        maya.standalone.initialize('python')
        import maya.cmds as cmds
        from MiasMagic2.transfer_functions import propAssetFlow
        propAssetFlow(%s, %s)""" % (old_asset_info, asset_info)
        process = ";".join(process.split("\n"))
        Q.CreateProcQueue([process])
    else:
        print("Asset Already Exists!")

def transferSet(asset_info={}):
    import AssetFunctions as AF
    asset_info['asset_step'] = 'Base'
    old_asset_info = asset_info.copy()
    old_asset_info['asset_step'] = 'Model'
    print('CC: ' + str(CC.get_asset_work_file()))
    new_set_work_path = CC.get_asset_work_file(**asset_info)
    print(new_set_work_path)
    # TODO :BUG: Below here. The old kiwistrit2 'ConfigClass' does not have a 'get_asset_work_file()' this results in an AttributeError during runtime
    print('CC.old: ' + str(CC.old))
    old_set_work_path = CC.old.get_asset_work_file(**old_asset_info)
    old_set_work_path = old_set_work_path + '.ma'

    if os.path.exists(new_set_work_path):
        print('File already exists: ' + new_set_work_path)
    else:
        asset_functions = AF.CreateAsset(asset_info)  # create new empty asset based on the new config and asset info.
        if asset_functions.Run():
            transferTextureFolder(asset_info=asset_info)
            transferDesignFolder(asset_info=asset_info)

            import QThreads as Q
            process = """import maya.standalone
                    maya.standalone.initialize('python')
                    import maya.cmds as cmds
                    from MiasMagic2.transfer_functions import setAssetFlow
                    setAssetFlow('%s', '%s')""" % (new_set_work_path, old_set_work_path)
            process = ";".join(process.split("\n"))
            Q.CreateProcQueue([process])

    print('>> DONE <<')


def replaceOldSetdress():
    pass

# def transferTextureFolderDifferentAssets(old_asset_info={},new_asset_info={}):
#     old_texture_folder = CC.old.get_asset_texture_folder(**old_asset_info)
#     new_texture_folder = CC.get_asset_texture_folder(**new_asset_info)
#     print("Copying %s -> %s" % (old_texture_folder,new_texture_folder))
#     shutil.copytree(old_texture_folder,new_texture_folder,ignore=shutil.ignore_patterns("_History",))


def buildTextureUpdate(asset_info, new_asset_info):
    replace_list = []

    replace_list.append(('/Char/Module/EyeA/02_Ref/EyeA_Model_Ref.mb', '/RigModule/Eye/EyeA/02_Ref/EyeA_Rig_Ref.mb'))
    replace_list.append(('/Char/Module/EyeB/02_Ref/EyeB_Model_Ref.mb', '/RigModule/Eye/EyeB/02_Ref/EyeB_Rig_Ref.mb'))
    replace_list.append(('/Char/Module/EyeC/02_Ref/EyeC_Model_Ref.mb', '/RigModule/Eye/EyeC/02_Ref/EyeC_Rig_Ref.mb'))
    replace_list.append(('/Char/Module/EyeRainbowGuy/02_Ref/EyeRainbowGuy_Model_Ref.mb',
                         '/RigModule/Eye/EyeRainbowGuy/02_Ref/EyeRainbowGuy_Rig_Ref.mb'))
    replace_list.append(('/Char/Module/EyeSmallDragon/02_Ref/EyeSmallDragon_Model_Ref.mb',
                         '/RigModule/Eye/EyeSmallDragon/02_Ref/EyeSmallDragon_Rig_Ref.mb'))
    replace_list.append(
        ('/Char/Module/MouthA/02_Ref/MouthA_Model_Ref.mb', 'RigModule/Mouth/MouthA/02_Ref/MouthA_Model_Ref.mb'))

    replace_list.append((CC.old.get_base_path(), CC.get_base_path()))
    replace_list.append(("/%s/" % asset_info["asset_type"], "/%s/" % new_asset_info["asset_type"]))
    replace_list.append(("/%s/" % asset_info["asset_category"], "/%s/" % new_asset_info["asset_category"]))
    replace_list.append(("/%s/" % asset_info["asset_name"], "/%s/" % asset_info["asset_name"]))
    # for nkey in replace_dict.keys():
    #     new_path = new_path.replace(nkey, replace_dict[nkey])
    print("Updating: %s" % asset_info["asset_name"])

    print(replace_list)
    from Maya_Functions.update_functions import updateTextureAndRefPathsByTuple
    # place in subprocces:
    updateTextureAndRefPathsByTuple(replace_list)

def characterAssetFlow(asset_info, file_path):
    import maya.cmds as cmds
    old_base_path = CC.old.get_base_path()
    new_base_path = CC.get_base_path()
    new_asset_info = asset_info.copy()

    if file_path[-3:] == '.ma':
        file_type = 'mayaAscii'
    elif file_path[-3] == '.mb':
        file_type = 'mayaBinary'

    cmds.file(file_path, open=True, f=True)
    cmds.file(type=file_type)
    from MiasMagic2.UpdateTextures import update_textures, updateRef, addPublishSet
    #update_textures(old_base_path, new_base_path)
    updateRef(old_base_path, new_base_path)
    buildTextureUpdate(asset_info, new_asset_info)
    addPublishSet()
    cmds.file(save=True)
    cmds.quit(f=True)


def riggedSetdressAssetFlow(asset_info, new_asset_info):
    import maya.cmds as cmds

    new_asset_info["asset_step"] = "Base"
    base_file = CC.get_asset_work_file(**new_asset_info)
    asset_info["asset_step"] = "Rig"
    rig_file = CC.old.get_asset_work_file(**asset_info)
    render_ref = CC.old.get_Render(**asset_info)

    cmds.file(base_file, open=True, f=True)
    cmds.file(type='mayaAscii')
    cmds.file(rig_file + '.ma', i=True, ignoreVersion=True, options="v:0;p=17;f=0", pr=True, importTimeRange="combine")
    # from Maya_Functions.update_functions import updateTextureAndRefPathsByTuple
    # updateTextureAndRefPathsByTuple(asset_info,new)
    # Reparent from Top_Group to Root_Group

    parentConstraintDict = None
    scaleConstraintDict = None
    orientConstraintDict = None

    parentConstraints = cmds.ls(type='parentConstraint')
    scaleConstraints = cmds.ls(type='scaleConstraint')
    orientConstraints = cmds.ls(type='orientConstraint')

    if parentConstraints:
        parentConstraintDict = {}
        for constraint in parentConstraints:
            parentConstraintDict[constraint] = getConstraintDict(constraint)
            parentConstraintDict[constraint] = reformatConstraintDict(parentConstraintDict[constraint])
            print(parentConstraintDict[constraint])

    if scaleConstraints:
        scaleConstraintDict = {}
        for constraint in scaleConstraints:
            scaleConstraintDict[constraint] = getConstraintDict(constraint)
            scaleConstraintDict[constraint] = reformatConstraintDict(scaleConstraintDict[constraint])
            print(scaleConstraintDict[constraint])

    if orientConstraints:
        orientConstraintDict = {}
        for constraint in orientConstraintDict:
            orientConstraintDict[constraint] = getConstraintDict(constraint)
            orientConstraintDict[constraint] = reformatConstraintDict(orientConstraintDict[constraint])
            print(orientConstraintDict[constraint])

    sourceNodes = ['Top_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl',
                   'Top_Group|Geo_Group',
                   'Top_Group|Rig_Group']

    targetNodes = ['Root_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl|Root_Ctrl_Group|Root_Ctrl',
                   'Root_Group|Geo_Group',
                   'Root_Group|Rig_Group']

    for i, node in enumerate(sourceNodes):
        if cmds.objExists(node):
            children = cmds.listRelatives(node, children=True, f=True)
            if children:
                for child in children:
                    if not cmds.ls(child, type="shape"):
                        if cmds.objExists(child) and cmds.objExists(targetNodes[i]):
                            cmds.parent(child, targetNodes[i])

    # Transfer attributes from old super-root to new super-root
    import Maya_Functions.attr_util_functions as attr
    attr.transferAttributes('Top_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl',
                            'Root_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl')

    # Remove :Model namespace
    refs = cmds.file(query=True, reference=True)
    for ref in refs:
        if cmds.referenceQuery(ref, namespace=True) == ':Model':
            cmds.file(ref, importReference=True)
            if cmds.namespace(exists=':Model'):
                cmds.namespace(removeNamespace=':Model', mergeNamespaceWithParent=True)

    buildTextureUpdate(asset_info, new_asset_info)

    refs = cmds.file(query=True, reference=True)
    for ref in refs:
        ns = cmds.referenceQuery(ref, namespace=True)
        if "Blendshape" in ns and "RigModule" in ref:
            asset_name = ref.split("/")[-1].split("_Rig_Ref.mb")[0]
            ref_node = cmds.referenceQuery(ref, rfn=True)
            cmds.namespace(rename=[ns, asset_name])
            cmds.lockNode(ref_node, lock=False)
            name = cmds.rename(ref_node, "%sRN" % asset_name)
            cmds.lockNode(name, lock=True)

    # Clear Full_Set
    cmds.sets(clear='Full_Set')

    # Put a duplicate of all unreferenced geoemtry under Geo_Group under Proxy
    nodes = cmds.listRelatives('Root_Group|Geo_Group', children=True, f=True)
    for node in nodes:
        if not cmds.referenceQuery(node, isNodeReferenced=True):
            # Add non-referenced geometry groups to Full_Set
            duplicate = cmds.duplicate(node)[0]
            cmds.sets(node, addElement='Full_Set')
            # cmds.parentConstraint('Root_Ctrl_Group|Root_Ctrl', node, mo=True, weight=1)
            # cmds.scaleConstraint('Root_Ctrl_Group|Root_Ctrl', node, offset=(1, 1, 1), weight=1)
            cmds.parent(duplicate, 'Proxy')
            cmds.rename(duplicate, node.split('|')[-1])

    # Delete remaining parts of Top_Group
    cmds.delete('Top_Group')

    # Import render_ref and transfer shaders
    cmds.file(render_ref, i=True, ignoreVersion=True, options="v:0;p=17;f=0", pr=True, importTimeRange="combine")
    from MiasMagic2.transfer_functions import transferShadersFromMatchingNames
    transferShadersFromMatchingNames()

    # Check for projection and place the nodes under Texture_Group
    proj_nodes = cmds.ls(type='projection')
    if proj_nodes:
        proj_grps = []
        for proj_node in proj_nodes:
            place_node = cmds.listConnections(proj_node, source=True, type='place3dTexture')
            place_parent = cmds.listRelatives(place_node, parent=True, fullPath=True)
            if place_parent not in proj_grps:
                proj_grps.append(place_parent)
        for grp in proj_grps:
            cmds.parent(grp, 'Root_Group|Texture_Group')

    # Transfer attributes from render super-root to rig super-root
    attr.transferAttributes('|Top_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl',
                            '|Root_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl')
    attr.transferAttributes('|Top_Group', '|Root_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl')

    vrayDisplacements = cmds.ls(type='VRayDisplacement')
    if vrayDisplacements:
        for node in vrayDisplacements:
            children = cmds.listConnections(node, source=True)
            if children:
                for child in children:
                    new_name = child.replace('Top_Group', 'Root_Group')
                    if cmds.objExists(new_name):
                        cmds.sets(new_name, addElement='Smooth_Set')
                        cmds.sets(new_name, addElement=node)
                # cmds.delete(node)

    # Delete remaining parts of Top_Group
    cmds.delete('|Top_Group')
    buildTextureUpdate(asset_info, new_asset_info)

    if parentConstraintDict:
        for key in parentConstraintDict.keys():
            rebuildConstraintsFromDict(parentConstraintDict[key])

    if scaleConstraintDict:
        for key in scaleConstraintDict.keys():
            rebuildConstraintsFromDict(scaleConstraintDict[key])

    if orientConstraintDict:
        for key in orientConstraintDict.keys():
            rebuildConstraintsFromDict(orientConstraintDict[key])

    cmds.file(save=True)

    cmds.quit(f=True)


def setAssetFlow(new_set_work_path, old_set_work_path):
    import maya.cmds as cmds
    cmds.file(new_set_work_path, open=True, f=True)
    if old_set_work_path[-3:] == '.ma':
        cmds.file(type='mayaAscii')
    elif old_set_work_path[-3:] == '.mb':
        cmds.file(type='mayaBinary')
    cmds.file(old_set_work_path, i=True, ignoreVersion=True, options="v:0;p=17;f=0", pr=True,
              importTimeRange="combine")
    imgPlanes = cmds.ls(type='imagePlane', long=True)

    # Delete all image planes. No exceptions.
    for imgPlane in imgPlanes:
        parent = cmds.listRelatives(imgPlane, parent=True, fullPath=True)
        cmds.delete(parent)

    cmds.file(save=True)

    # Update references
    #
    # from MiasMagic2.transfer_functions import updateReference
    # ref_paths = cmds.file(query=True, reference=True)
    # ref_nodes = []
    # for path in ref_paths:
    #     ref_node = cmds.referenceQuery(path, referenceNode=True)
    #     ref_nodes.append(ref_node)
    # updateReference(ref_nodes)

    # Instance proxies
    #
    # from Maya_Functions.ref_util_functions import instanceScene
    # instanceScene()


def getConstraintDict(constraint):
    import maya.cmds as cmds
    constraintType = cmds.nodeType(constraint).replace('Constraint', '')
    if constraintType == 'parent':
        source = cmds.parentConstraint(constraint, query=True, targetList=True)
    elif constraintType == 'scale':
        source = cmds.scaleConstraint(constraint, query=True, targetList=True)
    elif constraintType == 'orient':
        source = cmds.orientConstraint(constraint, query=True, targetList=True)
    for i, node in enumerate(source):
        source[i] = cmds.ls(node, long=True)[0]
    target = cmds.listRelatives(constraint, parent=True, fullPath=True)
    if constraintType == 'parent':
        weightList = cmds.parentConstraint(constraint, query=True, weightAliasList=True)
    elif constraintType == 'scale':
        weightList = cmds.scaleConstraint(constraint, query=True, weightAliasList=True)
    elif constraintType == 'orient':
        weightList = cmds.orientConstraint(constraint, query=True, weightAliasList=True)
    weights = []
    for attribute in weightList:
        weights.append(cmds.getAttr(constraint + '.' + attribute))
    dict = {'source': source, 'target': target, 'weights': weights, 'constraintType': constraintType}
    return dict


def reformatConstraintDict(dict):
    import maya.cmds as cmds
    output_list = []
    for item in dict['source']:
        # if item == '|Top_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl':
        #     item = '|Root_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl|Root_Ctrl_Group|Root_Ctrl'
        item = item.replace('Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl',
                            'Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl|Root_Ctrl_Group|Root_Ctrl')
        output_list.append(item.replace('Top_Group', 'Root_Group'))
    dict['source'] = output_list
    output_list = []
    if dict['target'][0] == '|Top_Group|Geo_Group':
        children = cmds.listRelatives(dict['target'], children=True, fullPath=True)
        if not children[0] == '|Root_Group|Geo_Group|Geo_Constraint_Group':
            group = cmds.group(*children)
            group = cmds.rename(group, 'Geo_Constraint_Group')
            cmds.xform(group, t=(0, 0, 0), ro=(0, 0, 0))
            dict['target'] = cmds.ls(group, long=True)
        else:
            dict['target'] = '|Root_Group|Geo_Group|Geo_Constraint_Group'
    if 'Model' in dict['target'][0]:
        dict['target'] = [dict['target'][0].replace('Model:', '')]
        print('target: ' + dict['target'][0])
    for item in dict['target']:
        output_list.append(item.replace('Top_Group', 'Root_Group'))
    dict['target'] = output_list
    return dict


def rebuildConstraintsFromDict(dict):
    import maya.cmds as cmds
    print(dict)
    for target in dict['target']:
        if dict['constraintType'] == 'parent':
            print(dict)
            nodeList = dict['source']
            nodeList.append(target)
            try:
                constraint = cmds.parentConstraint(*nodeList, mo=True)[0]
                attributes = cmds.parentConstraint(constraint, query=True, weightAliasList=True)
                for i, attribute in enumerate(attributes):
                    cmds.setAttr(constraint + '.' + attribute, dict['weights'][i])
            except:
                pass
        elif dict['constraintType'] == 'scale':
            nodeList = dict['source']
            nodeList.append(target)
            try:
                constraint = cmds.scaleConstraint(*nodeList, mo=True)[0]
                attributes = cmds.scaleConstraint(constraint, query=True, weightAliasList=True)
                for i, attribute in enumerate(attributes):
                    cmds.setAttr(constraint + '.' + attribute, dict['weights'][i])
            except:
                pass
        elif dict['constraintType'] == 'orient':
            nodeList = dict['source']
            nodeList.append(target)
            try:
                constraint = cmds.orientConstraint(*nodeList, mo=True)[0]
                attributes = cmds.orientConstraint(constraint, query=True, weightAliasList=True)
                for i, attribute in enumerate(attributes):
                    cmds.setAttr(constraint + '.' + attribute, dict['weights'][i])
            except:
                pass


def propAssetFlow(asset_info, new_asset_info):
    import maya.cmds as cmds

    new_asset_info["asset_step"] = "Base"
    base_file = CC.get_asset_work_file(**new_asset_info)
    asset_info["asset_step"] = "Rig"
    rig_file = CC.old.get_asset_work_file(**asset_info)
    render_ref = CC.old.get_Render(**asset_info)

    cmds.file(base_file, open=True, f=True)
    cmds.file(type='mayaAscii')
    cmds.file(rig_file + '.ma', i=True, ignoreVersion=True, options="v:0;p=17;f=0", pr=True, importTimeRange="combine")
    # from Maya_Functions.update_functions import updateTextureAndRefPathsByTuple
    # updateTextureAndRefPathsByTuple(asset_info,new)
    # Reparent from Top_Group to Root_Group

    parentConstraintDict = None
    scaleConstraintDict = None
    orientConstraintDict = None

    parentConstraints = cmds.ls(type='parentConstraint')
    scaleConstraints = cmds.ls(type='scaleConstraint')
    orientConstraints = cmds.ls(type='orientConstraint')

    if parentConstraints:
        parentConstraintDict = {}
        for constraint in parentConstraints:
            parentConstraintDict[constraint] = getConstraintDict(constraint)
            parentConstraintDict[constraint] = reformatConstraintDict(parentConstraintDict[constraint])
            print(parentConstraintDict[constraint])

    if scaleConstraints:
        scaleConstraintDict = {}
        for constraint in scaleConstraints:
            scaleConstraintDict[constraint] = getConstraintDict(constraint)
            scaleConstraintDict[constraint] = reformatConstraintDict(scaleConstraintDict[constraint])
            print(scaleConstraintDict[constraint])

    if orientConstraints:
        orientConstraintDict = {}
        for constraint in orientConstraintDict:
            orientConstraintDict[constraint] = getConstraintDict(constraint)
            orientConstraintDict[constraint] = reformatConstraintDict(orientConstraintDict[constraint])
            print(orientConstraintDict[constraint])

    sourceNodes = ['Top_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl|Root_Ctrl_Group|Root_Ctrl',
                   'Top_Group|Geo_Group',
                   'Top_Group|Rig_Group']

    targetNodes = ['Root_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl|Root_Ctrl_Group|Root_Ctrl',
                   'Root_Group|Geo_Group',
                   'Root_Group|Rig_Group']

    for i, node in enumerate(sourceNodes):
        if cmds.objExists(node):
            children = cmds.listRelatives(node, children=True, f=True)
            if children:
                for child in children:
                    if not cmds.ls(child, type="shape"):
                        if cmds.objExists(child) and cmds.objExists(targetNodes[i]):
                            cmds.parent(child, targetNodes[i])

    # Transfer attributes from old super-root to new super-root
    import Maya_Functions.attr_util_functions as attr
    attr.transferAttributes('Top_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl',
                            'Root_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl')

    # Remove :Model namespace
    refs = cmds.file(query=True, reference=True)
    for ref in refs:
        if cmds.referenceQuery(ref, namespace=True) == ':Model':
            cmds.file(ref, importReference=True)
            if cmds.namespace(exists=':Model'):
                cmds.namespace(removeNamespace=':Model', mergeNamespaceWithParent=True)

    buildTextureUpdate(asset_info, new_asset_info)

    refs = cmds.file(query=True, reference=True)
    for ref in refs:
        ns = cmds.referenceQuery(ref, namespace=True)
        if "Blendshape" in ns and "RigModule" in ref:
            asset_name = ref.split("/")[-1].split("_Rig_Ref.mb")[0]
            ref_node = cmds.referenceQuery(ref, rfn=True)
            cmds.namespace(rename=[ns, asset_name])
            cmds.lockNode(ref_node, lock=False)
            name = cmds.rename(ref_node, "%sRN" % asset_name)
            cmds.lockNode(name, lock=True)

    # Delete remaining parts of Top_Group
    cmds.delete('Top_Group')

    # Import render_ref and transfer shaders
    cmds.file(render_ref, i=True, ignoreVersion=True, options="v:0;p=17;f=0", pr=True, importTimeRange="combine")
    from MiasMagic2.transfer_functions import transferShadersFromMatchingNames
    transferShadersFromMatchingNames()

    # Check for projection and place the nodes under Texture_Group
    proj_nodes = cmds.ls(type='projection')
    if proj_nodes:
        proj_grps = []
        for proj_node in proj_nodes:
            place_node = cmds.listConnections(proj_node, source=True, type='place3dTexture')
            place_parent = cmds.listRelatives(place_node, parent=True)
            if place_parent not in proj_grps:
                proj_grps.append(place_parent)
        for grp in proj_grps:
            if grp:
                cmds.parent(grp, 'Root_Group|Texture_Group')

    # Transfer attributes from render super-root to rig super-root
    attr.transferAttributes('Top_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl',
                            'Root_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl')
    attr.transferAttributes('Top_Group', 'Root_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl')

    # vrayDisplacements = cmds.ls(type='VRayDisplacement')
    # if vrayDisplacements:
    #     for node in vrayDisplacements:
    #         children = cmds.listConnections(node, source=True)
    #         for child in children:
    #             cmds.sets(child.replace('Top_Group', 'Root_Group'), addElement='Smooth_Set')
    #             cmds.sets(child.replace('Top_Group', 'Root_Group'), addElement=node)
    #         # cmds.delete(node)

    # Delete remaining parts of Top_Group
    cmds.delete('Top_Group')
    buildTextureUpdate(asset_info, new_asset_info)

    if parentConstraintDict:
        for key in parentConstraintDict.keys():
            rebuildConstraintsFromDict(parentConstraintDict[key])

    if scaleConstraintDict:
        for key in scaleConstraintDict.keys():
            rebuildConstraintsFromDict(scaleConstraintDict[key])

    if orientConstraintDict:
        for key in orientConstraintDict.keys():
            rebuildConstraintsFromDict(orientConstraintDict[key])

    cmds.file(save=True)
    cmds.quit(f=True)


def setdressAssetFlow(asset_info, new_asset_info):
    import maya.cmds as cmds

    new_asset_info["asset_step"] = "Base"
    base_file = CC.get_asset_work_file(**new_asset_info)
    render_ref = CC.old.get_Render(**asset_info)

    cmds.file(base_file, open=True, f=True)
    cmds.file(type='mayaAscii')

    cmds.file(render_ref, i=True)
    superRoot = 'Top_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl'
    if not cmds.objExists('Top_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl'):
        nodes = cmds.ls(type='transform', long=True)
        for node in nodes:
            if node.split('|')[-1] == 'SuperRoot_Ctrl':
                superRoot = node
    #cmds.select(superRoot)

    #cmds.file(save=True)

    attr.transferAttributes(superRoot, 'Root_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl')
    geo_group = 'Root_Group|Geo_Group'

    set_util.RemoveFromSet(set_name="Full_Set", selection=[geo_group])

    parentConstraintDict = None
    scaleConstraintDict = None
    orientConstraintDict = None

    parentConstraints = cmds.ls(type='parentConstraint')
    scaleConstraints = cmds.ls(type='scaleConstraint')
    orientConstraints = cmds.ls(type='orientConstraint')

    if parentConstraints:
        parentConstraintDict = {}
        for constraint in parentConstraints:
            parentConstraintDict[constraint] = getConstraintDict(constraint)
            parentConstraintDict[constraint] = reformatConstraintDict(parentConstraintDict[constraint])
            print(parentConstraintDict[constraint])

    if scaleConstraints:
        scaleConstraintDict = {}
        for constraint in scaleConstraints:
            scaleConstraintDict[constraint] = getConstraintDict(constraint)
            scaleConstraintDict[constraint] = reformatConstraintDict(scaleConstraintDict[constraint])
            print(scaleConstraintDict[constraint])

    if orientConstraints:
        orientConstraintDict = {}
        for constraint in orientConstraintDict:
            orientConstraintDict[constraint] = getConstraintDict(constraint)
            orientConstraintDict[constraint] = reformatConstraintDict(orientConstraintDict[constraint])
            print(orientConstraintDict[constraint])

    if cmds.objExists('Top_Group|Geo_Group'):
        old_geo_group = 'Top_Group|Geo_Group'
    else:
        for node in cmds.ls(type='transform', long=True):
            if node.split('|')[-1] == 'Geo_Group':
                if node != '|Root_Group|Geo_Group':
                    old_geo_group = node
    print('old_geo_group: ' + old_geo_group)

    geoChildren = cmds.listRelatives(old_geo_group, children=True, fullPath=True)
    if geoChildren:
        for geoChild in geoChildren:
            if not cmds.nodeType(geoChild)[-10:] == 'Constraint':
                cmds.parent(geoChild, geo_group)
    new_name = cmds.duplicate(geo_group, rc=True)[0]
    cmds.lockNode('Proxy', lock=False)
    cmds.parent(new_name, 'Proxy')
    # cmds.rename(new_name, geo_group.split('|')[-1])
    set_util.AddToSet(set_name="Full_Set", selection=[geo_group])

    cmds.lockNode('Proxy', lock=True)
    nodes = cmds.ls(dagObjects=True, sets=True)
    topLevelNodes = []
    if nodes:
        for node in nodes:
            if cmds.listRelatives(node, parent=True) == None:
                topLevelNodes.append(node)

    # Looping through all nodes in the scene without parents
    # and if they don't fit on the pre-approved list, delete the node
    for node in topLevelNodes:
        if node not in ['persp', 'top', 'front', 'side', 'Root_Group', 'defaultLightSet', 'initialParticleSE',
                        'initialShadingGroup', 'defaultObjectSet', 'Full_Set', 'Proxy_Set', 'PublishSet', 'Smooth_Set',
                        'Full', 'Proxy']:
            cmds.lockNode(node, lock=False)
            cmds.delete(node)

    # Check if asset_type attribute exists, then check if it's SetDress and change it to Setdress
    if cmds.attributeQuery('asset_type', node='Root_Group', exists=True):
        if cmds.getAttr("Root_Group.asset_type") == "SetDress":
            cmds.setAttr("Root_Group.asset_type", "Setdress", type="string")

    # Check if asset_category attribute exists,
    # then check if it is either Ground, Bush or Tree and if so replace with Forest
    if cmds.attributeQuery('assetCategory', node='Root_Group', exists=True):
        if cmds.getAttr("Root_Group.asset_category") in ['Ground', 'Bush', 'Tree']:
            cmds.setAttr("Root_Group.asset_category", "Forest", type="string")

    if parentConstraintDict:
        for key in parentConstraintDict.keys():
            rebuildConstraintsFromDict(parentConstraintDict[key])

    if scaleConstraintDict:
        for key in scaleConstraintDict.keys():
            rebuildConstraintsFromDict(scaleConstraintDict[key])

    if orientConstraintDict:
        for key in orientConstraintDict.keys():
            rebuildConstraintsFromDict(orientConstraintDict[key])

    cmds.file(save=True)
    cmds.quit(f=True)


def transferFolderUntoFolder(from_folder, to_folder):
    if os.path.exists(from_folder):
        for name in os.listdir(from_folder):
            if name not in ['.mayaSwatches']:
                source_path = os.path.join(from_folder, name).replace(os.sep, '/')
                target_path = os.path.join(to_folder, name).replace(os.sep, '/')
                if os.path.exists(source_path):
                    if not os.path.exists(target_path):
                        if os.path.isdir(source_path):
                            try:
                                shutil.copytree(source_path, target_path)
                            except shutil.Error as err:
                                print(err)
                        elif os.path.isfile(source_path):
                            try:
                                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                            except OSError:
                                pass
                            try:
                                shutil.copyfile(source_path, target_path)
                            except shutil.Error as err:
                                print(err)
                        else:
                            print('This should not ever print..? Time to panic!?')
                    else:
                        print('Path already exist: ' + target_path)
                else:
                    print('Path does not exist: ' + source_path)
            else:
                print('Path does not exist: ' + from_folder)
    # for folder in os.listdir(from_folder):
    #     folderPath = os.path.join(from_folder, folder).replace(os.sep, '/')
    #     print('folderPath: ' + folderPath)
    #     if os.path.isdir(folderPath):
    #
    #         # Loop through items inside the folders
    #         for item in os.listdir(folderPath):
    #             itemPath = os.path.join(from_folder, folder, item).replace(os.sep, '/')
    #             destination = os.path.join(to_folder, folder, item).replace(os.sep, '/')
    #
    #             # If item is folder
    #             if os.path.isdir(itemPath):
    #                 # Attempts to copy folder
    #                 try:
    #                     shutil.copytree(itemPath, destination)
    #                 except:
    #                     print('Failed to copy ' + itemPath + ' to ' + destination)
    #             else:
    #                 # Attempts to copy file
    #                 try:
    #                     shutil.copyfile(itemPath, destination)
    #                 except Exception as e:
    #                     print('Failed to copy ' + itemPath + ' to ' + destination + " : %s" % e)
    #     else:
    #         # Someone fucked up and there is a file where there should not be.
    #         # We will move it anyways
    #         try:
    #             shutil.copyfile(folderPath)
    #         except:
    #             print('Failed to copy ' + folderPath)


def transferShadersFromMatchingNames():
    target = "|Root_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl"
    source = "|Top_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl"
    import MiasMagic2.transferCustomAttributes as tca
    import maya.cmds as cmds
    # attributes = tca.getAttributes(source)
    # tca.transferAttributes(source, target, attributes)

    orig_root_list = cmds.listRelatives("|Root_Group", f=True, ad=True, type="transform")
    top_list = cmds.listRelatives("|Top_Group", f=True, ad=True, type="transform")
    root_list = []
    for ro in orig_root_list:
        if cmds.listRelatives(ro, s=True):
            root_list.append(ro)


    for cur_xform in root_list:
        compare_name = cur_xform.split("|Geo_Group|")[-1]
        if ":" in compare_name:
            name = compare_name.split(":")[-1]
            compare_name = compare_name.split("|")[0:-1]
            compare_name.append(name)
            compare_name = "|".join(compare_name)
        for top_xform in top_list:
            if compare_name in top_xform:
                if cmds.listRelatives(top_xform, s=True):
                    print("Found ", top_xform, " -> ", cur_xform, " compared: ", compare_name)
                    # target = "Root_Group|Geo_Group|PineTreeU|Trunk"
                    # source = "Top_Group|Geo_Group|PineTreeU|Trunk"
                    if ":" in top_xform or cur_xform:
                        print(cur_xform.split(":"))
                    try:

                        cmds.transferShadingSets(top_xform, cur_xform, sampleSpace=1)
                    except Exception as e:
                        print(
                            "Can't transfer shading set from %s to %s.Assuming it already is connected correctly.\n Exception: %s" % (
                                cur_xform, top_xform, e))


def transferDesignFolder(asset_info={}, new_asset_info={}):
    if not new_asset_info:
        new_asset_info = asset_info
    old_design_folder = CC.old.get_asset_design_folder(**asset_info)
    new_design_folder = CC.get_asset_design_folder(**new_asset_info)
    transferFolderUntoFolder(old_design_folder, new_design_folder)


def transferTextureFolder(asset_info={}, new_asset_info={}):
    if not new_asset_info:
        new_asset_info = asset_info
    old_texture_folder = CC.old.get_asset_texture_folder(**asset_info)
    new_texture_folder = CC.get_asset_texture_folder(**new_asset_info)
    transferFolderUntoFolder(old_texture_folder, new_texture_folder)


def updateReference(ref_nodes):
    import maya.cmds as cmds
    import shutil
    import QThreads as Q

    ref_node_check = []
    for ref_node in ref_nodes:
        print('\n>> Now attempting to update ' + ref_node + '\n')
        ref_node = cmds.referenceQuery(ref_node, rfn=True)
        if ref_node in ref_node_check:
            continue
        else:
            ref_node_check.append(ref_node)
        print("Starting on ", ref_node)
        path = cmds.referenceQuery(ref_node, filename=True)
        if CC.get_base_path() in path:
            print(ref_node + ' is already up to date')
            continue
        old_asset_info = CC.util.ComparePartOfPath(path, CC.old.get_Render())
        old_asset_info['is_proxy'] = False
        if old_asset_info['asset_name'][-8:] == '_ReProxy': # Apparently some are named ReProxy and it messes with ComparePartOfPath()
            old_asset_info['asset_name'] = old_asset_info['asset_name'][:-8]
            old_asset_info['is_proxy'] = True
        old_asset_info["asset_step"] = "Base"
        asset_info = old_asset_info.copy()
        if asset_info['asset_name'] == 'PineTreeU':
            asset_info['asset_name'] = 'PineTreeT'
        if old_asset_info['asset_type'] == 'SetDress':
            asset_info['asset_type'] = 'Setdress'
        if old_asset_info['asset_category'] in ['Bushs', 'Grounds', 'Trees']:
            asset_info['asset_category'] = 'Forest'
        asset_info['asset_step'] = 'Base'
        new_path = CC.get_asset_work_file(**asset_info)
        asset_info = getReferenceInfo(ref_node, asset_info)
        if os.path.exists(new_path):
            print(asset_info['asset_name'] + ' already exists at ' + new_path)
        else:
            asset_info = getReferenceInfo(ref_node, asset_info)
            print('Transferring ' + asset_info['asset_name'])
            if asset_info['asset_type'] == 'Setdress':
                if asset_info['asset_name'] in ['BushE', 'FaceFlowerA', 'MushroomA', 'MushroomB', 'MushroomC', 'RockA',
                                                'RockB', 'RockC',
                                                'RockY', 'StickA', 'StickB', 'TwigPileA', 'voleyballBall',
                                                'voleyballScoreBoard',
                                                'WhirleyBallNetA', 'BabyCrystalA', 'SmallBluePlanet', 'SpaceBubbleA',
                                                'BigTreeA',
                                                'BranchLongA', 'PineTreeU', 'ConePlantA', 'CoralPlantB', 'PlantB',
                                                'StaggeredHills',
                                                'StaggeredHillsA', 'StaggeredHillsB', 'StaggeredHillsC', 'StarfishA',
                                                'UWPlantB',
                                                'UWPlantBA', 'UWRockA', 'UWRockB', 'UWRockC', 'VineB']:
                    print('\n>> Now attempting to transfer ' + ref_node + ' as a rigged setdress asset\n')
                    transferRiggedSetdress(asset_info, old_asset_info)
                else:
                    print('\n>> Now attempting to transfer ' + ref_node + ' as a non-rigged setdress asset\n')
                    transferSetdress(asset_info, old_asset_info)
        if not os.path.exists(CC.get_Proxy(**asset_info)) or not os.path.exists(CC.get_Ingest(**asset_info)):
            print('\n>> Now attempting to publish ' + ref_node + '\n')
            from PublishAssets.PublishMaster import ReadyPublish
            pc = ReadyPublish(asset_info)
            pc.StartPublishInMayaPy()
        if 'customAttributes' in asset_info.keys():
            print(asset_info['customAttributes'])
            if 'eyesMouthVisibility' in asset_info['customAttributes'].keys():
                if asset_info['customAttributes']['eyesMouthVisibility'] == 0:
                    asset_info['is_proxy'] = True
                else:
                    asset_info['is_proxy'] = False
        if 'superRoot' in asset_info.keys():
            if cmds.objExists(asset_info['superRoot']):
                if not cmds.listRelatives(asset_info['superRoot'], children=True, type='transform'):
                    asset_info['is_proxy'] = True

        #now replace and postion
        if asset_info['is_proxy']:
            print('\n>> Now attempting to import ' + ref_node + ' as a proxy\n')
            cmds.file(path, removeReference=True)
            publish_path = CC.get_Proxy(**asset_info)
            if os.path.exists(publish_path):
                new_ref_path = cmds.file(publish_path, reference=True, ns=asset_info['namespace'])
                new_ref_node = cmds.referenceQuery(new_ref_path, referenceNode=True)
                referencedNodes = cmds.referenceQuery(new_ref_node, nodes=True)
                for node in referencedNodes:
                    if node.split(':')[0] == cmds.referenceQuery(new_ref_node, namespace=True, shortName=True):
                        if node.split(':')[-1] == 'Proxy':
                            cmds.xform(node, matrix=asset_info['xform'])
                            if 'customAttributes' in asset_info.keys():
                                for attribute in asset_info['customAttributes']:
                                    if attribute != '__________':
                                        cmds.setAttr(node + '.' + attribute, asset_info['customAttributes'][attribute])
                            if 'parent' in asset_info.keys():
                                if asset_info['parent'] != None:
                                    try:
                                        cmds.parent(node, asset_info['parent'])
                                    except:
                                        pass
                if asset_info['loaded'] == False:
                    cmds.file(unloadReference=node)
                isLocked = cmds.lockNode(new_ref_node, query=True, lock=True)[0]
                if isLocked:
                    cmds.lockNode(new_ref_node, lock=False)
                new_name = cmds.referenceQuery(new_ref_node, namespace=True).replace(':', '')
                new_name = new_name.replace(asset_info['asset_name'], asset_info['asset_name'] + 'RN')
                new_ref_node = cmds.rename(new_ref_node, new_name)
                if isLocked:
                    cmds.lockNode(new_ref_node, lock=True)
        else:
            print('\n>> Now attempting to import ' + ref_node + ' as an ingest\n')
            cmds.file(path, removeReference=True, unresolvedName=False)
            publish_path = CC.get_Ingest(**asset_info)
            if os.path.exists(publish_path):
                new_ref_path = cmds.file(publish_path, reference=True, ns=asset_info['namespace'])
                new_ref_node = cmds.referenceQuery(new_ref_path, referenceNode=True)
                referencedNodes = cmds.referenceQuery(new_ref_node, nodes=True)
                for node in referencedNodes:
                    if node.split(':')[0] == cmds.referenceQuery(new_ref_node, namespace=True, shortName=True):
                        if node.split(':')[-1] == 'SuperRoot_Ctrl':
                            cmds.xform(node, matrix=asset_info['xform'])
                            if 'customAttributes' in asset_info.keys():
                                for attribute in asset_info['customAttributes']:
                                    if attribute != '__________':
                                        cmds.setAttr(node + '.' + attribute, asset_info['customAttributes'][attribute])
                        elif node.split(':')[-1] == 'Geo_Group':
                            try:
                                cmds.parent(node, asset_info['parent'])
                            except:
                                pass
                        elif node.split(':')[-1] == 'Ctrl_Group':
                            if cmds.listRelatives(node, parent=True, fullPath=True) != '|Root_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl|Root_Ctrl_Group|Root_Ctrl':
                                cmds.parent(node, '|Root_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl|Root_Ctrl_Group|Root_Ctrl')
                        elif node.split(':')[-1] == 'Rig_Group':
                            cmds.parent(node, '|Root_Group|Rig_Group')
                        elif node.split(':')[-1] == 'Texture_Group':
                            cmds.parent(node, '|Root_Group|Texture_Group')
                    if asset_info['loaded'] == False:
                        cmds.file(unloadReference=new_ref_node)
                isLocked = cmds.lockNode(new_ref_node, query=True, lock=True)[0]
                if isLocked:
                    cmds.lockNode(new_ref_node, lock=False)
                print('asset_info: ' + str(asset_info['asset_name']))
                new_name = cmds.referenceQuery(new_ref_node, namespace=True).replace(':', '')
                new_name = new_name.replace(asset_info['asset_name'], asset_info['asset_name'] + 'RN')
                new_ref_node = cmds.rename(new_ref_node, new_name)
                if isLocked:
                    cmds.lockNode(new_ref_node, lock=True)

        print('\n>> Finished updating ' + ref_node)

        # DONE - if is_re_proxy:
        # DONE -     ref proxy version in. place gpu node in place of super_root. take scale/size from super_root. apply attributes.
        # DONE -     and parent under previous parent
        # DONE - else:
        #   ref ingest version in. super-root -> super-root.
        #   parent ctrl_group under super_root. |Under |Root_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl|Root_Ctrl_Group|Root_Ctrl ??
        #   parent geo_group under previous parent
        #   parent rig -> rig and so on.



    # assets = []
    # processes = []
    # for ref_node in ref_nodes:
    #     if ref_node != '':
    #         print(ref_node)
    #         asset, process = copyReferencedAsset(ref_node)
    #         assets.append(asset)
    #         if process != None:
    #             if os.path.exists(asset['new_path']):
    #                 processes.append(process)
    # Q.CreateProcQueue(processes)
    # processes = []
    # for asset in assets:
    #     riggedAsset = []
    #     if asset['name'] in ['BushE', 'FaceFlowerA', 'MushroomA', 'MushroomB', 'MushroomC', 'RockA', 'RockB', 'RockC',
    #                          'RockY', 'StickA', 'StickB', 'TwigPileA', 'voleyballBall', 'voleyballScoreBoard',
    #                          'WhirleyBallNetA', 'BabyCrystalA', 'SmallBluePlanet', 'SpaceBubbleA', 'BigTreeA',
    #                          'BranchLongA', 'PineTreeU', 'ConePlantA', 'CoralPlantB', 'PlantB', 'StaggeredHills',
    #                          'StaggeredHillsA', 'StaggeredHillsB', 'StaggeredHillsC', 'StarfishA', 'UWPlantB',
    #                          'UWPlantBA', 'UWRockA', 'UWRockB', 'UWRockC', 'VineB']:
    #         riggedAsset.append(asset)
    #     else:
    #         updated_asset, process = publishCopiedAsset(asset)
    #         if process != None:
    #             if os.path.exists(updated_asset['publish_path']):
    #                 processes.append(process)
    # Q.CreateProcQueue(processes)


def transferRiggedSetdress(asset_info, old_asset_info):
    from AssetFunctions import CreateAsset

    new_asset = CreateAsset(asset_info)
    new_asset.Run()
    from MiasMagic2.transfer_functions import transferTextureFolder, transferDesignFolder

    transferTextureFolder(asset_info=old_asset_info, new_asset_info=asset_info)
    transferDesignFolder(asset_info=old_asset_info, new_asset_info=asset_info)
    import QThreads as Q

    process = """import maya.standalone
        maya.standalone.initialize('python')
        import maya.cmds as cmds
        from MiasMagic2.transfer_functions import riggedSetdressAssetFlow
        riggedSetdressAssetFlow(%s, %s)""" % (old_asset_info, asset_info)
    process = ";".join(process.split("\n"))
    Q.CreateProcQueue([process])


def transferSetdress(asset_info, old_asset_info):
    from AssetFunctions import CreateAsset
    create_dict = asset_info.copy()
    new_asset = CreateAsset(create_dict)

    if new_asset.Run():

        # from MiasMagic2.transfer_functions import transferTextureFolder, transferDesignFolder
        transferTextureFolder(asset_info=old_asset_info, new_asset_info=asset_info)
        transferDesignFolder(asset_info=old_asset_info, new_asset_info=asset_info)
        import QThreads as Q
        process = """import maya.standalone
        maya.standalone.initialize('python')
        import maya.cmds as cmds
        from MiasMagic2.transfer_functions import setdressAssetFlow
        setdressAssetFlow(%s, %s)""" % (old_asset_info, asset_info)
        process = ";".join(process.split("\n"))
        Q.CreateProcQueue([process])
    else:
        print("Asset Already Exists!")


def getReferenceInfo(ref_node, asset_info):
    import maya.cmds as cmds
    asset_info['longName'] = ref_node
    asset_info['namespace'] = cmds.referenceQuery(ref_node, namespace=True)
    asset_info['loaded'] = cmds.referenceQuery(ref_node, isLoaded=True)
    referencedNodes = cmds.referenceQuery(ref_node, nodes=True, dagPath=True)
    for node in referencedNodes:
        if node.split(':')[-1] == 'Top_Group':
            asset_info['top_group'] = node
            parent = cmds.listRelatives(node, parent=True, fullPath=True)
            if parent:
                asset_info['parent'] = parent[0]
            else:
                asset_info['parent'] = None
    nodes = cmds.referenceQuery(asset_info['longName'], nodes=True)
    superRoot = None
    if nodes:
        for node in nodes:
            print(node)
            if node[-14:] == 'SuperRoot_Ctrl':
                asset_info['superRoot'] = node
                asset_info['xform'] = cmds.xform(asset_info['superRoot'], query=True, ws=True, matrix=True)
                attributes = cmds.listAttr(asset_info['superRoot'], userDefined=True)
                dict = {}
                if attributes != None:
                    for attribute in attributes:
                        dict[attribute] = cmds.getAttr(asset_info['superRoot'] + '.' + attribute)
                    asset_info['customAttributes'] = dict
    #if 'top_group' in asset_info.keys():
    #    asset_info['top_group_xform'] = cmds.xform(asset_info['top_group'], query=True, matrix=True)

    #Check if rigged! To determine if we should use Proxy or Render.
    return asset_info

#
#   Obsolete
#   TODO: Delete when transferring set works
#
# def copyReferencedAsset(ref_node):
#     import maya.cmds as cmds
#     asset = {}
#     asset['path'] = cmds.referenceQuery(ref_node, filename=True)
#     if asset['path'][-1] == '}':
#         asset['path'] = asset['path'].split('{')[0]
#     dict = CC.util.ComparePartOfPath(asset['path'], CC.old.get_Render())
#     asset['name'] = dict['asset_name']
#     asset['asset_name'] = asset['name']
#     asset['asset_type'] = dict['asset_type']
#
#     if dict['asset_category'] in ['Grounds', 'Bushes', 'Trees']:
#         asset['asset_category'] = dict['asset_category']
#         asset['new_asset_category'] = 'Forest'
#     else:
#         asset['asset_category'] = dict['asset_category']
#     asset['longName'] = ref_node
#     asset['loaded'] = cmds.referenceQuery(ref_node, isLoaded=True)
#
#     referencedNodes = cmds.referenceQuery(ref_node, nodes=True)
#     for node in referencedNodes:
#         if node.split(':')[-1] == 'Top_Group':
#             parent = cmds.listRelatives(node, parent=True, fullPath=True)
#             if parent != None:
#                 asset['parent'] = parent[0]
#             else:
#                 asset['parent'] = None
#
#     print(asset)
#     process = None
#     print(asset['path'])
#     if asset['asset_type'].lower() == 'setdress':
#         if os.path.exists(asset['path']):
#             print('Transferring ' + asset['path'])
#             asset['new_path'], process = copyAsset(asset)
#             print("Transferring process: %s" % process)
#
#     return asset, process


def publishSetdress(asset_info, old_asset_info):
    import QThreads as Q
    asset_info['asset_step'] = 'Base'
    new_path = CC.get_asset_work_file(**asset_info)

    if os.path.exists(new_path):
        print('\n\n>>>>> PATH EXISTS!!\n\n')
        print(new_path)
        asset_info['asset_step'] = CC.ref_order[asset_info['asset_type']][0]
        asset_info['asset_output'] = CC.ref_steps[asset_info['asset_type']][asset_info['asset_step']][0]
        script_content = '''import maya.standalone
maya.standalone.initialize('python')
import maya.cmds as cmds
from MiasMagic2.transfer_functions import QuickPublish
cmds.loadPlugin('AbcExport')
cmds.loadPlugin('gpuCache')
cmds.file('%s', open=True, f=True)
QuickPublish(%s)
cmds.quit(f=True)''' % (new_path, asset_info)
        process = ";".join(script_content.split("\n"))
        Q.CreateProcQueue([process])
    else:
        print('Path does not exist! OH NO! ' + new_path)


def transferDirtyAsset():
    import maya.cmds as cmds
    from getConfig import getConfigClass
    CC = getConfigClass()
    import MiasMagic2.transfer_functions as tf
    import os

    assets = []
    selection = cmds.ls(sl=1, long=True)
    nodes = cmds.listRelatives(allDescendents=True, fullPath=True)
    for node in nodes:
        if node.split('|')[-1] == 'SuperRoot_Ctrl' or node.split(':')[-1] == 'SuperRoot_Ctrl':
            asset_info = {}
            asset_info['superRoot'] = node
            assets.append(asset_info)
    for asset_info in assets:
        parent_1 = cmds.listRelatives(asset_info['superRoot'], parent=True, fullPath=True)
        parent_2 = cmds.listRelatives(parent_1, parent=True, fullPath=True)
        parent_3 = cmds.listRelatives(parent_2, parent=True, fullPath=True)
        if parent_2[0].split('|')[-1] == 'Top_Group' or parent_2[0].split(':')[-1] == 'Top_Group':
            asset_info['top_group'] = parent_2[0]
        elif parent_3[0].split('|')[-1] == 'Top_Group' or parent_3[0].split(':')[-1] == 'Top_Group':
            asset_info['top_group'] = parent_3[0]
        else:
            parent_4 = cmds.listRelatives(parent_3, parent=True, fullPath=True)
            if parent_4[0].split('|')[-1] == 'Top_Group' or parent_4[0].split(':')[-1] == 'Top_Group':
                asset_info['top_group'] = parent_4[0]

    for asset_info in assets:
        if 'top_group' in asset_info.keys():
            asset_info['asset_name'] = cmds.getAttr(asset_info['top_group'] + '.assetName')
        asset_info['asset_category'] = cmds.getAttr(asset_info['top_group'] + '.assetCategory')
        asset_info['asset_type'] = cmds.getAttr(asset_info['top_group'] + '.assetType')
        asset_info['xform'] = cmds.xform(asset_info['superRoot'], query=True, ws=True, matrix=True)
        asset_info['loaded'] = False
        if cmds.listRelatives(asset_info['top_group'], parent=True, fullPath=True):
            asset_info['parent'] = cmds.listRelatives(asset_info['top_group'], parent=True, fullPath=True)[0]
        else:
            asset_info['parent'] = None
        #asset_info['namespace'] = cmds.namespace(asset_info['top_group'], query=True)
        attributes = cmds.listAttr(asset_info['superRoot'], userDefined=True)
        dict = {}
        if attributes != None:
            for attribute in attributes:
                dict[attribute] = cmds.getAttr(asset_info['superRoot'] + '.' + attribute)
            asset_info['customAttributes'] = dict

    for asset_info in assets:
        old_asset_info = asset_info.copy()
        old_asset_info['is_proxy'] = False
        if old_asset_info['asset_name'][
           -8:] == '_ReProxy':  # Apparently some are named ReProxy and it messes with ComparePartOfPath()
            old_asset_info['asset_name'] = old_asset_info['asset_name'][:-8]
            old_asset_info['is_proxy'] = True
        old_asset_info["asset_step"] = "Base"
        asset_info = old_asset_info.copy()
        if asset_info['asset_name'] == 'PineTreeU':
            asset_info['asset_name'] = 'PineTreeT'
        if old_asset_info['asset_type'] == 'SetDress':
            asset_info['asset_type'] = 'Setdress'
        if old_asset_info['asset_category'] in ['Bushs', 'Grounds', 'Trees']:
            asset_info['asset_category'] = 'Forest'
        asset_info['asset_step'] = 'Base'
        new_path = CC.get_asset_work_file(**asset_info)
        # asset_info = getReferenceInfo(ref_node, asset_info)
        if os.path.exists(new_path):
            print(asset_info['asset_name'] + ' already exists at ' + new_path)
        else:
            print('Transferring ' + asset_info['asset_name'])
            if asset_info['asset_type'] == 'Setdress':
                if asset_info['asset_name'] in ['BushE', 'FaceFlowerA', 'MushroomA', 'MushroomB', 'MushroomC', 'RockA',
                                                'RockB', 'RockC',
                                                'RockY', 'StickA', 'StickB', 'TwigPileA', 'voleyballBall',
                                                'voleyballScoreBoard',
                                                'WhirleyBallNetA', 'BabyCrystalA', 'SmallBluePlanet', 'SpaceBubbleA',
                                                'BigTreeA',
                                                'BranchLongA', 'PineTreeU', 'ConePlantA', 'CoralPlantB', 'PlantB',
                                                'StaggeredHills',
                                                'StaggeredHillsA', 'StaggeredHillsB', 'StaggeredHillsC', 'StarfishA',
                                                'UWPlantB',
                                                'UWPlantBA', 'UWRockA', 'UWRockB', 'UWRockC', 'VineB']:
                    print('\n>> Now attempting to transfer ' + asset_info['top_group'] + ' as a rigged setdress asset\n')
                    tf.transferRiggedSetdress(asset_info, old_asset_info)
                else:
                    print(
                        '\n>> Now attempting to transfer ' + asset_info['top_group'] + ' as a non-rigged setdress asset\n')
                    tf.transferSetdress(asset_info, old_asset_info)
        if not os.path.exists(CC.get_Proxy(**asset_info)) or not os.path.exists(CC.get_Ingest(**asset_info)):
            print('\n>> Now attempting to publish ' + asset_info['top_group'] + '\n')
            from PublishMaster import ReadyPublish

            pc = ReadyPublish(asset_info)
            pc.StartPublishInMayaPy()
        if 'customAttributes' in asset_info.keys():
            print(asset_info['customAttributes'])
            if 'eyesMouthVisibility' in asset_info['customAttributes'].keys():
                if asset_info['customAttributes']['eyesMouthVisibility'] == 0:
                    asset_info['is_proxy'] = True
                else:
                    asset_info['is_proxy'] = False
        if cmds.objExists(asset_info['superRoot']):
            if not cmds.listRelatives(asset_info['superRoot'], children=True, type='transform'):
                asset_info['is_proxy'] = True

        # now replace and postion
        if not asset_info['is_proxy']:
            print('\n>> Now attempting to import ' + asset_info['top_group'] + ' as an ingest\n')
            if cmds.objExists(asset_info['top_group']):
                if cmds.referenceQuery(asset_info['top_group'], isNodeReferenced=True):
                    ref_path = cmds.referenceQuery(asset_info['top_group'], filename=True)
                    cmds.file(ref_path, removeReference=True)
                else:
                    cmds.delete(asset_info['top_group'])
            publish_path = CC.get_Ingest(**asset_info)
            print(publish_path)
            if os.path.exists(publish_path):
                new_ref_path = cmds.file(publish_path, reference=True, ns=asset_info['asset_name'])
                new_ref_node = cmds.referenceQuery(new_ref_path, referenceNode=True)
                referencedNodes = cmds.referenceQuery(new_ref_node, nodes=True)
                for node in referencedNodes:
                    print('node: ' + node)
                    if node.split(':')[0] == cmds.referenceQuery(new_ref_node, namespace=True, shortName=True):
                        if node.split(':')[-1] == 'SuperRoot_Ctrl':
                            cmds.xform(node, matrix=asset_info['xform'])
                            if 'customAttributes' in asset_info.keys():
                                for attribute in asset_info['customAttributes']:
                                    if attribute != '__________':
                                        cmds.setAttr(node + '.' + attribute, asset_info['customAttributes'][attribute])
                        elif node.split(':')[-1] == 'Geo_Group':
                            try:
                                cmds.parent(node, asset_info['parent'])
                            except:
                                pass
                        elif node.split(':')[-1] == 'Ctrl_Group':
                            if cmds.listRelatives(node, parent=True,
                                                  fullPath=True) != '|Root_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl|Root_Ctrl_Group|Root_Ctrl':
                                cmds.parent(node, '|Root_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl|Root_Ctrl_Group|Root_Ctrl')
                        elif node.split(':')[-1] == 'Rig_Group':
                            cmds.parent(node, '|Root_Group|Rig_Group')
                        elif node.split(':')[-1] == 'Texture_Group':
                            cmds.parent(node, '|Root_Group|Texture_Group')
                isLocked = cmds.lockNode(new_ref_node, query=True, lock=True)[0]
                if isLocked:
                    cmds.lockNode(new_ref_node, lock=False)
                print('asset_info: ' + str(asset_info['asset_name']))
                new_name = cmds.referenceQuery(new_ref_node, namespace=True).replace(':', '')
                new_name = new_name.replace(asset_info['asset_name'], asset_info['asset_name'] + 'RN')
                new_ref_node = cmds.rename(new_ref_node, new_name)
                if isLocked:
                    cmds.lockNode(new_ref_node, lock=True)
        if asset_info['is_proxy']:
            print('\n>> Now attempting to import ' + asset_info['top_group'] + ' as a proxy\n')
            if cmds.referenceQuery(asset_info['top_group'], isNodeReferenced=True):
                ref_path = cmds.referenceQuery(asset_info['top_group'], filename=True)
                cmds.file(ref_path, removeReference=True)
            else:
                cmds.delete(asset_info['top_group'])
            publish_path = CC.get_Proxy(**asset_info)
            if os.path.exists(publish_path):
                new_ref_path = cmds.file(publish_path, reference=True, ns=asset_info['asset_name'])
                new_ref_node = cmds.referenceQuery(new_ref_path, referenceNode=True)
                referencedNodes = cmds.referenceQuery(new_ref_node, nodes=True)
                for node in referencedNodes:
                    if node.split(':')[0] == cmds.referenceQuery(new_ref_node, namespace=True, shortName=True):
                        if node.split(':')[-1] == 'Proxy':
                            cmds.xform(node, matrix=asset_info['xform'])
                            if 'customAttributes' in asset_info.keys():
                                for attribute in asset_info['customAttributes']:
                                    if attribute != '__________':
                                        try:
                                            cmds.setAttr(node + '.' + attribute, asset_info['customAttributes'][attribute])
                                        except:
                                            pass
                            if asset_info['parent'] != None:
                                cmds.parent(node, asset_info['parent'])
                isLocked = cmds.lockNode(new_ref_node, query=True, lock=True)[0]
                if isLocked:
                    cmds.lockNode(new_ref_node, lock=False)
                new_name = cmds.referenceQuery(new_ref_node, namespace=True).replace(':', '')
                new_name = new_name.replace(asset_info['asset_name'], asset_info['asset_name'] + 'RN')
                new_ref_node = cmds.rename(new_ref_node, new_name)
                if isLocked:
                    cmds.lockNode(new_ref_node, lock=True)

                print('\n>> Finished updating ' + asset_info['top_group'])


def QuickPublish(asset_info={}):
    from PublishAssets import PublishMaster
    print("quick publish")
    PubClass = PublishMaster.ReadyPublish(asset_info=asset_info)
    PubClass.StartPublish()

if __name__ == '__main__':
    pass


# import maya.cmds as cmds
# from MiasMagic2.transfer_functions import updateReference
# ref_paths = cmds.file(query=True, reference=True)
# ref_nodes = []
# for path in ref_paths:
#     ref_node = cmds.referenceQuery(path, referenceNode=True)
#     ref_nodes.append(ref_node)
# updateReference(ref_nodes)