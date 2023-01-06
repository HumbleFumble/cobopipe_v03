import os
from getConfig import getConfigClass
CC = getConfigClass('MiasMagic2')

def getEmptyFiles(asset_type):
    base_files, asset_names, asset_categories = getBaseFiles(asset_type)
    for i, base_file in enumerate(base_files):
        if os.path.getsize(base_file) < 95000:
            print(asset_names[i])

def getBaseFiles(asset_type):
    base_files = []
    asset_names = []
    asset_categories = []
    asset_top_path = CC.get_asset_top_path()
    asset_type_path = os.path.join(asset_top_path, asset_type).replace(os.sep, '/')
    for asset_category in os.listdir(asset_type_path):
        asset_category_path = os.path.join(asset_type_path, asset_category).replace(os.sep, '/')
        for asset_name in os.listdir(asset_category_path):
            base_file = CC.get_asset_work_file(**{'asset_name': asset_name, 'asset_type': asset_type,
                                                'asset_category': asset_category, 'asset_step': 'Rig'})
            asset_names.append(asset_name)
            asset_categories.append(asset_category)
            base_files.append(base_file)
    return base_files, asset_names, asset_categories

def smoothSetdress(base_file, asset_info):
    import maya.cmds as cmds
    import IncSave as IncSave
    cmds.file(base_file, open=True)
    isGeoGrp = False
    for node in cmds.sets('Smooth_Set', query=True):
        if node.split('|')[-1].split(':')[-1] == 'Geo_Group':
            isGeoGrp = True
    if not isGeoGrp:
        print('>> Smoothing ' + asset_info['asset_name'])
        cmds.sets('Root_Group|Geo_Group', addElement='Smooth_Set')
        IncSave.incrementalSave()
        from PublishAssets.PublishMaster import ReadyPublish
        pc = ReadyPublish(asset_info)
        pc.StartPublishInMayaPy()
    print('>> Done with ' + asset_info['asset_name'])

def runSmoothSetdress():
    base_files, asset_names, asset_categories = getBaseFiles('Setdress')
    for i, base_file in enumerate(base_files):
        print('>> Now working on ' + asset_names[i])
        asset_info = {}
        asset_info['asset_name'] = asset_names[i]
        asset_info['asset_category'] = asset_categories[i]
        asset_info['asset_type'] = 'Setdress'
        asset_info['asset_step'] = 'Base'
        import QThreads as Q
        process = """import maya.standalone
                    maya.standalone.initialize('python')
                    import maya.cmds as cmds
                    from MiasMagic2.assetTransferUtil import smoothSetdress
                    smoothSetdress('%s', %s)""" % (base_file, asset_info)
        process = ";".join(process.split("\n"))
        Q.CreateProcQueue([process])

def updateRefsByAssetType(asset_type):
    import QThreads as Q
    from MiasMagic2.transfer_functions import getMayaFiles
    base_files, asset_names, asset_categories = getBaseFiles(asset_type)
    print(asset_names)
    for i, asset_name in enumerate(asset_names):
        print('>> Now starting on ' + asset_name + ' <<')
        asset_info = {'asset_name': asset_name, 'asset_category': asset_categories[i], 'asset_type': asset_type}
        asset_work_folder = CC.get_asset_work_folder(**asset_info)
        old_base_path = CC.old.get_base_path()
        new_base_path = CC.get_base_path()
        mayaFiles = getMayaFiles(asset_work_folder, [], ignore=['_History'])
        processes = []
        for mayaFile in mayaFiles:
            #if mayaFile.replace(new_base_path, '') == '/Assets/3D_Assets/Char/Main/Oskar/01_Work/Maya/Oskar_Blendshape.ma':
            #    continue
            print('>> Now starting on ' + mayaFile.replace(new_base_path, '') + ' <<')
            process = """import maya.standalone
maya.standalone.initialize('python')
import maya.cmds as cmds
cmds.file('%s', open=True, f=True)
from MiasMagic2.UpdateTextures import updateRef
updateRef('%s', '%s')
cmds.file(save=True)
print('>> Saved %s <<')
cmds.quit(f=True)""" % (mayaFile, old_base_path, new_base_path, mayaFile)
            process = ";".join(process.split("\n"))
            processes.append(process)
        Q.CreateProcQueue(processes)

if __name__ == '__main__':
    #updateRefsByAssetType('Setdress')
    getEmptyFiles('Char')