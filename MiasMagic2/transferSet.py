# from reloadModules import resetSession
# #resetSession()
#
import os
import sys

# import shutil
# import maya.cmds as cmds
#import ClearImportedModules as CIM
# import subprocess
# import QThreads as Q
# sys.path.append(os.path.abspath(os.path.join(__file__, '../..')))

from getConfig import getConfigClass
CC = getConfigClass()
#
# CIM.dropCachedImports("BasicTreeView_ThumbnailTesting","PublishMaster", "UtilFunctions", "AssetFunctions", "PublishSetdress","transferCustomAttributes", "UpdateTextures", "getConfig", "Configs.ConfigClass_MiasMagic2", "Configs.ConfigClass_MiasMagic", "Configs.Config_MiasMagic", "Configs.Config_MiasMagic2", "ConfigUtil")
#
# import AssetFunctions as AF
# import PublishMaster
#
# #sys.path.append(os.path.join(__file__, '../..'))
# #from Configs.getConfig import getConfigClass
#
# from BasicTreeView_ThumbnailTesting import copyAsset, createTreeNodes



def transferSet(set_path):
    import maya.cmds as cmds
    import AssetFunctions as AF
    dict = CC.util.ComparePartOfPath(set_path, CC.old.get_asset_work_file())
    dict['asset_step'] = 'Base'
    new_set_work_path = CC.get_asset_work_file(**dict)

    for key in dict:
        print(key + ': ' + dict[key])

    print('new_set_work_path: ' + new_set_work_path)
    print('set_path: ' + set_path)

    if os.path.exists(new_set_work_path):
        print('File already exists: ' + new_set_work_path)
    else:
        asset_functions = AF.CreateAsset(dict)  # create new empty asset based on the new config and asset info.
        asset_functions.Run()

        cmds.file(new_set_work_path, open=True, f=True)
        if set_path[-3:] == '.ma':
            cmds.file(type='mayaAscii')
        elif set_path[-3:] == '.mb':
            cmds.file(type='mayaBinary')
        cmds.file(set_path, i=True, ignoreVersion=True, options="v:0;p=17;f=0", pr=True, importTimeRange="combine")
    #     cmds.file(save=True)

def updateReference(ref_nodes):
    import shutil
    import QThreads as Q

    try:
        shutil.rmtree('P:/_WFH_Projekter/930486_MiaMagicPlayground_S3-4/05_Production_Testing/Assets/3D_Assets/Setdress/Forest/HillD')
    except:
        pass

    assets = []
    processes = []
    for ref_node in ref_nodes:
        if ref_node != '':
            print(ref_node)
            asset, process = copyReferencedAsset(ref_node)
            assets.append(asset)
            if process != None:
                if os.path.exists(asset['new_path']):
                    processes.append(process)
    Q.CreateProcQueue(processes)
    processes = []
    for asset in assets:
        riggedAsset = []
        if asset['name'] in ['BushE', 'FaceFlowerA', 'MushroomA', 'MushroomB', 'MushroomC', 'RockA', 'RockB', 'RockC',
                             'RockY', 'StickA', 'StickB', 'TwigPileA', 'voleyballBall', 'voleyballScoreBoard',
                             'WhirleyBallNetA', 'BabyCrystalA', 'SmallBluePlanet', 'SpaceBubbleA', 'BigTreeA',
                             'BranchLongA', 'PineTreeU', 'ConePlantA', 'CoralPlantB', 'PlantB', 'StaggeredHills',
                             'StaggeredHillsA', 'StaggeredHillsB', 'StaggeredHillsC', 'StarfishA', 'UWPlantB',
                             'UWPlantBA', 'UWRockA', 'UWRockB', 'UWRockC', 'VineB']:
            riggedAsset.append(asset)
        else:
            updated_asset, process = publishCopiedAsset(asset)
            if process != None:
                if os.path.exists(updated_asset['publish_path']):
                    processes.append(process)
    Q.CreateProcQueue(processes)

def copyReferencedAsset(ref_node):
    import maya.cmds as cmds
    from MiasMagic2.transfer_functions import copyAsset
    asset = {}
    asset['path'] = cmds.referenceQuery(ref_node, filename=True)
    if asset['path'][-1] == '}':
        asset['path'] = asset['path'].split('{')[0]
    dict = CC.util.ComparePartOfPath(asset['path'], CC.old.get_Render())
    asset['name'] = dict['asset_name']
    asset['asset_name'] = asset['name']
    asset['asset_type'] = dict['asset_type']

    if dict['asset_category'] in ['Grounds', 'Bushes', 'Trees']:
        asset['asset_category'] = dict['asset_category']
        asset['new_asset_category'] = 'Forest'
    else:
        asset['asset_category'] = dict['asset_category']
    asset['longName'] = ref_node
    asset['loaded'] = cmds.referenceQuery(ref_node, isLoaded=True)

    referencedNodes = cmds.referenceQuery(ref_node, nodes=True)
    for node in referencedNodes:
        if node.split(':')[-1] == 'Top_Group':
            parent = cmds.listRelatives(node, parent=True, fullPath=True)
            if parent != None:
                asset['parent'] = parent[0]
            else:
                asset['parent'] = None

    print(asset)
    process = None
    print(asset['path'])
    if asset['asset_type'].lower() == 'setdress':
        if os.path.exists(asset['path']):
            print('Transferring ' + asset['path'])
            asset['new_path'], process = copyAsset(asset)
            print("Transferring process: %s" % process)

    return asset, process


def publishCopiedAsset(asset):
    import maya.cmds as cmds
    nodes = cmds.referenceQuery(asset['longName'], nodes=True)
    superRoot = None
    if nodes != None:
        for node in nodes:
            if node[-14:] == 'SuperRoot_Ctrl':
                asset['superRoot'] = node
                asset['xform'] = cmds.xform(asset['superRoot'], query=True, matrix=True)
                attributes = cmds.listAttr(asset['superRoot'], userDefined=True)
                dict = {}
                if attributes != None:
                    for attribute in attributes:
                        dict[attribute] = cmds.getAttr(asset['superRoot'] + '.' + attribute)
                    asset['customAttributes'] = dict

    process = None
    if asset['asset_type'].lower() == 'setdress':
        asset['new_path'] = CC.get_asset_work_file(**asset)
        if os.path.exists(asset['new_path']):
            # if dict['asset_category'] in ['Grounds', 'Bushes', 'Trees']:
            #     dict['asset_category'] = 'Forest'
            asset['asset_step'] = CC.ref_order[asset['asset_type']][0]
            asset['asset_output'] = CC.ref_steps[asset['asset_type']][asset['asset_step']][0]
            script_content = '''import maya.standalone
maya.standalone.initialize('python')
import maya.cmds as cmds
import sys
sys.path.append('C:/Users/mmcb/PycharmProjects/bombay_base_production/')
import MiasMagic2.BasicTreeView_ThumbnailTesting
cmds.loadPlugin('AbcExport')
cmds.loadPlugin('gpuCache')
MiasMagic2.BasicTreeView_ThumbnailTesting.QuickPublish('%s', '%s', '%s', '%s')
cmds.quit(f=True)''' % (asset['asset_name'], asset['asset_step'], asset['asset_type'], asset['asset_category'])
            script_content = ";".join(script_content.split("\n"))
            # process = 'mayapy.exe -c "%s"' % (script_content)
            process = script_content
            print("Publishing process: %s" % process)
            # publishProcess = subprocess.Popen(base_command, shell=False, universal_newlines=True, stdout=subprocess.PIPE)
            # publishProcess.communicate()
            # publishProcesses.append(publishProcess)
            # publishProcess.communicate(input=subprocess.PIPE)

            asset['publish_path'] = CC.get_Render(**asset)

    return asset, process




def QuickPublish(asset_info={}):
    print("quick publish")
    PubClass = PublishMaster.ReadyPublish(asset_info=asset_info)
    PubClass.StartPublish()


def run():
    import maya.cmds as cmds
    import shutil

    # try:
    #     shutil.rmtree('P:/_WFH_Projekter/930486_MiaMagicPlayground_S3-4/05_Production_Testing/Assets/3D_Assets/Set/Forest/BigTreeSetB')
    # except:
    #     pass
    transferSet('P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Assets/3D_Assets/Set/Forest/WhatWouldMiaDoForestClearing/01_Work/Maya/WhatWouldMiaDoForestClearing_Model.ma')

    # selectedNodes = cmds.ls(sl=True)
    # updateReference(selectedNodes)


if __name__ == '__main__':
    run()

    #print(str(getConfigClass.__file__))
    #transferSet('P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Assets/3D_Assets/Set/Forest/BigTreeSetB/01_Work/Maya/BigTreeSetB_Model.ma')
    #updateReference('FaceFlowerARN')

    # try:
    #     shutil.rmtree('P:/_WFH_Projekter/930486_MiaMagicPlayground_S3-4/4_Production/Assets/3D_Assets/Set')
    # except:
    #     pass
    # try:
    #     shutil.rmtree('P:/_WFH_Projekter/930486_MiaMagicPlayground_S3-4/4_Production/Assets/3D_Assets/Setdress')
    # except:
    #     pass
    # transferSet('P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Assets/3D_Assets/Set/Forest/BigTreeSetB/01_Work/Maya/BigTreeSetB_Model.ma')
    #dress_dict = {'asset_name': 'HillB', 'asset_step': 'Base', 'asset_type': 'Setdress', 'asset_category': 'Forest'}
    #QuickPublish(dress_dict)



    #transferSet('P:/_WFH_Projekter/930486_MiaMagicPlayground_S3-4/4_Production/_Temp/Set_Test_HillB.ma')

    # def __init__(self, name=None,url=None,parent=None, type=None, assetType=None):
    #dict = cfg_util.CreateDictFromAssetPath('P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film/E09/E09_SQ040/E09_SQ040_SH040/02_Light/E09_SQ040_SH040_Light.ma', old_cfg)


# print(str(assets) + '\n') * 20
#     # riggedSetdress = []
#     # for asset in assets:
#     #     if asset['name'] in ['BushE', 'FaceFlowerA', 'MushroomA', 'MushroomB', 'MushroomC', 'RockA', 'RockB', 'RockC',
#     #                       'RockY', 'StickA', 'StickB', 'TwigPileA', 'voleyballBall', 'voleyballScoreBoard',
#     #                       'WhirleyBallNetA', 'BabyCrystalA', 'SmallBluePlanet', 'SpaceBubbleA', 'BigTreeA',
#     #                       'BranchLongA', 'PineTreeU', 'ConePlantA', 'CoralPlantB', 'PlantB', 'StaggeredHills',
#     #                       'StaggeredHillsA', 'StaggeredHillsB', 'StaggeredHillsC', 'StarfishA', 'UWPlantB',
#     #                       'UWPlantBA', 'UWRockA', 'UWRockB', 'UWRockC', 'VineB']:
#     #         riggedSetdress.append(asset)
#
#     assets = [i for i in assets if not (i['name'] in ['BushE', 'FaceFlowerA', 'MushroomA', 'MushroomB', 'MushroomC',
#                                                       'RockA', 'RockB', 'RockC', 'RockY', 'StickA', 'StickB',
#                                                       'TwigPileA', 'voleyballBall', 'voleyballScoreBoard',
#                                                       'WhirleyBallNetA', 'BabyCrystalA', 'SmallBluePlanet',
#                                                       'SpaceBubbleA', 'BigTreeA', 'BranchLongA', 'PineTreeU',
#                                                       'ConePlantA', 'CoralPlantB', 'PlantB', 'StaggeredHills',
#                                                       'StaggeredHillsA', 'StaggeredHillsB', 'StaggeredHillsC',
#                                                       'StarfishA', 'UWPlantB', 'UWPlantBA', 'UWRockA', 'UWRockB',
#                                                       'UWRockC', 'VineB'])]
#
#     for asset in assets:
#         nodes = cmds.referenceQuery(asset['longName'], nodes=True)
#         superRoot = None
#         if nodes != None:
#             for node in nodes:
#                 if node[-14:] == 'SuperRoot_Ctrl':
#                     asset['superRoot'] = node
#                     asset['xform'] = cmds.xform(asset['superRoot'], query=True, matrix=True)
#                     attributes = cmds.listAttr(asset['superRoot'], userDefined=True)
#                     dict = {}
#                     if attributes != None:
#                         for attribute in attributes:
#                             dict[attribute] = cmds.getAttr(asset['superRoot'] + '.' + attribute)
#                         asset['customAttributes'] = dict
#
#     print('2222222222222222222\n') * 10
#
#     # for process in processes:
#     #     if process != None:
#     #         if not process.poll():
#     #             print('Waiting for assets being transferred')
#     #             process.wait()
#     #             print('Assets has finished transferring')
#     #         else:
#     #             print('Assets has been transferred')
#
#     commands = []
#     # publishProcesses = []
#     for uniqueAsset in uniqueAssets:
#         if uniqueAsset.getAssetType().lower() == 'setdress':
#             if os.path.exists(uniqueAsset.getUrl()):
#                 dict = uniqueAsset.generate_info_dict()
#                 dict['asset_step'] = 'Base'
#                 if dict['asset_category'] in ['Grounds', 'Bushes', 'Trees']:
#                     dict['asset_category'] = 'Forest'
#                 print('\nPublishing ' + str(dict))
#                 script_content = '''import maya.standalone
#     maya.standalone.initialize('python')
#     import maya.cmds as cmds
#     import BasicTreeView_ThumbnailTesting
#     cmds.loadPlugin('AbcExport')
#     cmds.loadPlugin('gpuCache')
#     BasicTreeView_ThumbnailTesting.QuickPublish('%s', '%s', '%s', '%s')
#     cmds.quit(f=True)''' % (dict['asset_name'], dict['asset_step'], dict['asset_type'], dict['asset_category'])
#                 script_content = ";".join(script_content.split("\n"))
#                 # base_command = 'mayapy.exe -c "%s"' % (script_content)
#                 commands.append(script_content)
#                 # publishProcess = subprocess.Popen(base_command, shell=False, universal_newlines=True, stdout=subprocess.PIPE)
#                 # publishProcess.communicate()
#                 # publishProcesses.append(publishProcess)
#                 # publishProcess.communicate(input=subprocess.PIPE)
#                 dict["asset_output"] = cfg.ref_steps[dict["asset_type"]][dict["asset_step"]][0]
#                 new_path = cfg_util.CreatePathFromDict(cfg.ref_paths[dict["asset_output"]], dict)
#                 for asset in assets:
#                     if asset['uniqueAsset'].getName() == uniqueAsset.getName():
#                         asset['uniqueAsset_new_path'] = new_path
#
#             else:
#                 print('I am' + uniqueAsset.getName() + ' and my path does not exist! Eww!')
#                 print('Here is the fake path: ' + uniqueAsset.getUrl())
#         else:
#             print('I am' + uniqueAsset.getName() + ' and I am not a setdress element. I suck!')
#
#     Q.CreateProcQueue(commands)
#
#     # for publishProcess in publishProcesses:
#     #     if publishProcess != None:
#     #         if not publishProcess.poll():
#     #             print('Waiting for assets being published')
#     #             publishProcess.wait()
#     #             print('Assets has finished published')
#     #         else:
#     #             print('Assets has been published')
#
#     print('333333333333333333\n') * 10
#
#     for asset in assets:
#         if 'uniqueAsset_new_path' in asset:
#             for string in ['Trees', 'Bushes', 'Grounds']:
#                 if '/Setdress/' + string in asset['uniqueAsset_new_path']:
#                     asset['uniqueAsset_new_path'] = asset['uniqueAsset_new_path'].replace('/Setdress/' + string,
#                                                                                           '/Setdress/Forest')
#             if os.path.exists(asset['uniqueAsset_new_path']):
#                 cmds.lockNode(asset['longName'], lock=False)
#                 old_ref_path = cmds.referenceQuery(asset['longName'], filename=True)
#                 namespace = cmds.referenceQuery(asset['longName'], ns=True)
#                 cmds.file(old_ref_path, rr=True)
#                 reference = cmds.file(asset['uniqueAsset_new_path'], reference=True, namespace=namespace,
#                                       type="mayaBinary", loadReferenceDepth='all', mergeNamespacesOnClash=False,
#                                       options='v=0')
#                 referencedNodes = cmds.referenceQuery(reference, nodes=True)
#                 for node in referencedNodes:
#                     if node.split(':')[-1] == 'Proxy':
#                         cmds.xform(node, matrix=asset['xform'])
#                         if 'customAttributes' in assets:
#                             for attribute in asset['customAttributes']:
#                                 cmds.setAttr(node + '.' + attribute, asset['customAttributes'][attribute])
#                         else:
#                             print('I am ' + node + ' and I do not have a customAttributes key')
#                         if asset['parent'] != None:
#                             print('Attempting to parent ' + node + ' to ' + asset['parent'])
#                             cmds.parent(node, asset['parent'])
#                         else:
#                             print('I am ' + node + ' and I do not have a parent, sue me')
#                         if asset['loaded'] == False:
#                             print('I am ' + asset['longName'] + ' and I should not be loaded')
#                             cmds.file(unloadReference=node)
#
#             else:
#                 print('I am ' + asset['name'] + ' and my uniqueAsset_new_path does not exist, I am a fraud!!')
#                 print('Here is the fake path: ' + asset['uniqueAsset_new_path'])
#         else:
#             print('I am ' + asset['name'] + ' and I do not have a uniqueAsset_new_path, I am a failure!')



#
# def updateAllReferences():
#     # from ConfigClass_MiaMagic2 import ConfigClass
#     # CC = ConfigClass()
#     # from ConfigClass_MiaMagic import ConfigClass
#     # oldCC = ConfigClass()
#     import Config_MiaMagic2 as cfg
#     import Config_MiaMagic as old_cfg
#     from ConfigUtil import ConfigUtilClass
#
#     set_path = cmds.file(query=True, sceneName=True)
#     old_set_info = cfg_util.CreateDictFromAssetPath(set_path, old_cfg)
#
#     uniqueAssets = []
#     assets = []
#     asset_names = []
#     ref_paths = []
#     dirtyRefs = cmds.ls(references=True, long=True)
#     ref_paths = cmds.file(q=True, r=True)
#
#     # if dirtyRefs != None:
#     #     for ref in dirtyRefs:
#     #         if ref[-18:] != '_UNKNOWN_REF_NODE_':
#     #             refs.append(ref)
#     #         # if '_UNKNOWN_REF_NODE_' in ref:
#     #         #     refs.append(ref)
#     for ref_path in ref_paths:
#         ref = cmds.referenceQuery(ref_path, referenceNode=True)
#         print('\n\n' + ref + '\n' + ref_path + '\n')
#         # ref_path = cmds.referenceQuery(ref, filename=True)
#         if ref_path[-1:] == '}':
#             ref_path = ref_path[:-3]
#         assetDict = {}
#         assetDict['path'] = ref_path
#         asset = getAssetNodeFromPath(ref_path, cfg_util, old_cfg)
#         if asset.getName() not in asset_names:
#             assetDict['uniqueAsset'] = asset
#             uniqueAssets.append(asset)
#             asset_names.append(asset.getName())
#         else:
#             for uniqueAsset in uniqueAssets:
#                 if uniqueAsset.getName() == asset.getName():
#                     assetDict['uniqueAsset'] = uniqueAsset
#
#         assetDict['name'] = asset.getName()
#         assetDict['node'] = asset
#         assetDict['longName'] = ref
#         assetDict['loaded'] = cmds.referenceQuery(ref, isLoaded=True)
#
#         referencedNodes = cmds.referenceQuery(assetDict['longName'], nodes=True)
#         for node in referencedNodes:
#             if node.split(':')[-1] == 'Top_Group':
#                 parent = cmds.listRelatives(node, parent=True, fullPath=True)
#                 if parent != None:
#                     assetDict['parent'] = parent[0]
#                     print('\n' + node + "'s parent" + '\n')
#                     print(parent[0])
#                     print('\n\n')
#                 else:
#                     assetDict['parent'] = None
#
#         assets.append(assetDict)
#
#     print(uniqueAssets)
#     print('\n\n')
#
#     print('111111111111111111\n') * 10
#
#     processes = []
#     for uniqueAsset in uniqueAssets:
#         if uniqueAsset.getAssetType().lower() == 'setdress':
#             if os.path.exists(uniqueAsset.getUrl()):
#                 print('Transfering ' + uniqueAsset.getUrl())
#                 new_asset_path, process = copyAsset(uniqueAsset)
#                 print("This is the process: %s" % process)
#                 processes.append(process)
#     print("all procs:\n %s" % processes)
#     Q.CreateProcQueue(processes)
#
#     print('1.5 1.5 1.5 1.5 1.5 1.5\n') * 10
#
#     print(str(assets) + '\n') * 20
#     # riggedSetdress = []
#     # for asset in assets:
#     #     if asset['name'] in ['BushE', 'FaceFlowerA', 'MushroomA', 'MushroomB', 'MushroomC', 'RockA', 'RockB', 'RockC',
#     #                       'RockY', 'StickA', 'StickB', 'TwigPileA', 'voleyballBall', 'voleyballScoreBoard',
#     #                       'WhirleyBallNetA', 'BabyCrystalA', 'SmallBluePlanet', 'SpaceBubbleA', 'BigTreeA',
#     #                       'BranchLongA', 'PineTreeU', 'ConePlantA', 'CoralPlantB', 'PlantB', 'StaggeredHills',
#     #                       'StaggeredHillsA', 'StaggeredHillsB', 'StaggeredHillsC', 'StarfishA', 'UWPlantB',
#     #                       'UWPlantBA', 'UWRockA', 'UWRockB', 'UWRockC', 'VineB']:
#     #         riggedSetdress.append(asset)
#
#     assets = [i for i in assets if not (i['name'] in ['BushE', 'FaceFlowerA', 'MushroomA', 'MushroomB', 'MushroomC',
#                                                       'RockA', 'RockB', 'RockC', 'RockY', 'StickA', 'StickB',
#                                                       'TwigPileA', 'voleyballBall', 'voleyballScoreBoard',
#                                                       'WhirleyBallNetA', 'BabyCrystalA', 'SmallBluePlanet',
#                                                       'SpaceBubbleA', 'BigTreeA', 'BranchLongA', 'PineTreeU',
#                                                       'ConePlantA', 'CoralPlantB', 'PlantB', 'StaggeredHills',
#                                                       'StaggeredHillsA', 'StaggeredHillsB', 'StaggeredHillsC',
#                                                       'StarfishA', 'UWPlantB', 'UWPlantBA', 'UWRockA', 'UWRockB',
#                                                       'UWRockC', 'VineB'])]
#
#     for asset in assets:
#         nodes = cmds.referenceQuery(asset['longName'], nodes=True)
#         superRoot = None
#         if nodes != None:
#             for node in nodes:
#                 if node[-14:] == 'SuperRoot_Ctrl':
#                     asset['superRoot'] = node
#                     asset['xform'] = cmds.xform(asset['superRoot'], query=True, matrix=True)
#                     attributes = cmds.listAttr(asset['superRoot'], userDefined=True)
#                     dict = {}
#                     if attributes != None:
#                         for attribute in attributes:
#                             dict[attribute] = cmds.getAttr(asset['superRoot'] + '.' + attribute)
#                         asset['customAttributes'] = dict
#
#     print('2222222222222222222\n') * 10
#
#     # for process in processes:
#     #     if process != None:
#     #         if not process.poll():
#     #             print('Waiting for assets being transferred')
#     #             process.wait()
#     #             print('Assets has finished transferring')
#     #         else:
#     #             print('Assets has been transferred')
#
#     commands = []
#     # publishProcesses = []
#     for uniqueAsset in uniqueAssets:
#         if uniqueAsset.getAssetType().lower() == 'setdress':
#             if os.path.exists(uniqueAsset.getUrl()):
#                 dict = uniqueAsset.generate_info_dict()
#                 dict['asset_step'] = 'Base'
#                 if dict['asset_category'] in ['Grounds', 'Bushes', 'Trees']:
#                     dict['asset_category'] = 'Forest'
#                 print('\nPublishing ' + str(dict))
#                 script_content = '''import maya.standalone
#     maya.standalone.initialize('python')
#     import maya.cmds as cmds
#     import BasicTreeView_ThumbnailTesting
#     cmds.loadPlugin('AbcExport')
#     cmds.loadPlugin('gpuCache')
#     BasicTreeView_ThumbnailTesting.QuickPublish('%s', '%s', '%s', '%s')
#     cmds.quit(f=True)''' % (dict['asset_name'], dict['asset_step'], dict['asset_type'], dict['asset_category'])
#                 script_content = ";".join(script_content.split("\n"))
#                 # base_command = 'mayapy.exe -c "%s"' % (script_content)
#                 commands.append(script_content)
#                 # publishProcess = subprocess.Popen(base_command, shell=False, universal_newlines=True, stdout=subprocess.PIPE)
#                 # publishProcess.communicate()
#                 # publishProcesses.append(publishProcess)
#                 # publishProcess.communicate(input=subprocess.PIPE)
#                 dict["asset_output"] = cfg.ref_steps[dict["asset_type"]][dict["asset_step"]][0]
#                 new_path = cfg_util.CreatePathFromDict(cfg.ref_paths[dict["asset_output"]], dict)
#                 for asset in assets:
#                     if asset['uniqueAsset'].getName() == uniqueAsset.getName():
#                         asset['uniqueAsset_new_path'] = new_path
#
#             else:
#                 print('I am' + uniqueAsset.getName() + ' and my path does not exist! Eww!')
#                 print('Here is the fake path: ' + uniqueAsset.getUrl())
#         else:
#             print('I am' + uniqueAsset.getName() + ' and I am not a setdress element. I suck!')
#
#     Q.CreateProcQueue(commands)
#
#     # for publishProcess in publishProcesses:
#     #     if publishProcess != None:
#     #         if not publishProcess.poll():
#     #             print('Waiting for assets being published')
#     #             publishProcess.wait()
#     #             print('Assets has finished published')
#     #         else:
#     #             print('Assets has been published')
#
#     print('333333333333333333\n') * 10
#
#     for asset in assets:
#         if 'uniqueAsset_new_path' in asset:
#             for string in ['Trees', 'Bushes', 'Grounds']:
#                 if '/Setdress/' + string in asset['uniqueAsset_new_path']:
#                     asset['uniqueAsset_new_path'] = asset['uniqueAsset_new_path'].replace('/Setdress/' + string,
#                                                                                           '/Setdress/Forest')
#             if os.path.exists(asset['uniqueAsset_new_path']):
#                 cmds.lockNode(asset['longName'], lock=False)
#                 old_ref_path = cmds.referenceQuery(asset['longName'], filename=True)
#                 namespace = cmds.referenceQuery(asset['longName'], ns=True)
#                 cmds.file(old_ref_path, rr=True)
#                 reference = cmds.file(asset['uniqueAsset_new_path'], reference=True, namespace=namespace,
#                                       type="mayaBinary", loadReferenceDepth='all', mergeNamespacesOnClash=False,
#                                       options='v=0')
#                 referencedNodes = cmds.referenceQuery(reference, nodes=True)
#                 for node in referencedNodes:
#                     if node.split(':')[-1] == 'Proxy':
#                         cmds.xform(node, matrix=asset['xform'])
#                         if 'customAttributes' in assets:
#                             for attribute in asset['customAttributes']:
#                                 cmds.setAttr(node + '.' + attribute, asset['customAttributes'][attribute])
#                         else:
#                             print('I am ' + node + ' and I do not have a customAttributes key')
#                         if asset['parent'] != None:
#                             print('Attempting to parent ' + node + ' to ' + asset['parent'])
#                             cmds.parent(node, asset['parent'])
#                         else:
#                             print('I am ' + node + ' and I do not have a parent, sue me')
#                         if asset['loaded'] == False:
#                             print('I am ' + asset['longName'] + ' and I should not be loaded')
#                             cmds.file(unloadReference=node)
#
#             else:
#                 print('I am ' + asset['name'] + ' and my uniqueAsset_new_path does not exist, I am a fraud!!')
#                 print('Here is the fake path: ' + asset['uniqueAsset_new_path'])
#         else:
#             print('I am ' + asset['name'] + ' and I do not have a uniqueAsset_new_path, I am a failure!')
#
#
#
#
#
# def getAssetNodeFromPath(path, cfg_util, cfg):
#     dict = cfg_util.CreateDictFromAssetPath(path, cfg)
#     node_list = createTreeNodes(dict['asset_top_path'])
#     asset_types = node_list.returnList()
#     for asset_type in asset_types:
#         if asset_type.getName() == dict['asset_type']:
#             categories = node_list.find_category(asset_type)
#             for category in categories:
#                 if category.getName() == dict['asset_category']:
#                     names = node_list.find_asset(category)
#                     for name in names:
#                         if name.getName() == dict['asset_name']:
#                             node = name
#     return node