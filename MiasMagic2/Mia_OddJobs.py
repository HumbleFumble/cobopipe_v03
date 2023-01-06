from getConfig import getConfigClass
CC = getConfigClass()
import os



def getRiggedSetdressList():
    top_path = CC.get_asset_top_path()
    tn = createTreeNodes(top_path)
    _list = tn.returnList()
    riggedSetdress = []
    for node in _list:
        if node.getAssetType() == "SetDress":
            all_nodes = node.getChildren()
            for a_node in all_nodes:
                for b_node in a_node.getChildren():
                    path = CC.get_Render(node.getName(), a_node.getName(), b_node.getName(), 'Render')
                    #paths.append(output)
                    output = isRig(path)
                    if output != []:
                        riggedSetdress.append(a_node.getName() + ' > ' + b_node.getName())
    for setdress in riggedSetdress:
        print(setdress)

    # for path in paths:
    #     if path[-3:] in ['.ma', '.mb']:
    #         isRig(path)

def isRig(path):
    import maya.cmds as cmds
    uniqueCurves = []
    if os.path.exists(path):
        cmds.file(path, open=True, f=True)
        curves = cmds.ls(type='nurbsCurve')
        for curve in curves:
            if curve not in ['SuperRoot_CtrlShape', 'Root_CtrlShape', 'Root_CtrlShape1', 'Root_CtrlShape2', 'Root_CtrlShape3', 'SuperRoot_Ctrl1Shape', 'SuperRoot_Ctrl2Shape', 'SuperRoot_Ctrl_Group|SuperRoot_Ctrl|SuperRoot_CtrlShape', 'UWBushARNfosterParent1|SuperRoot_Ctrl|SuperRoot_CtrlShape']:
                print('Unique curve: ' + curve)
                uniqueCurves.append(curve)
    return uniqueCurves



class Node(object):
    def __init__(self, name=None,url=None,parent=None, type=None, assetType=None):
        self.__name = name
        self.__parent = parent
        self.__children = []
        self._row = 0
        self.__type = type
        self.__assetType = assetType
        self.__thumb_path = None
        self.url = url

    def getType(self):
        return self.__type

    def getAssetType(self):
        if self.__assetType:
            return self.__assetType
        else:
            if self.__type == "asset":
                return self.__parent.getParent().getName()
            else:
                return None

    def getUrl(self):
        return self.url

    def append(self, c_obj):
        self.__children.append(c_obj)
        self._row = 0
        # self._row = len(self.__children)

    def child(self, in_row):  # Treeview
        if in_row >= 0 and in_row < len(self.__children):
            return self.__children[in_row]

    def generate_info_dict(self):
        if self.__type =="asset":
            cate = self.__parent.getName()
            type_name = self.__parent.getParent().getName().capitalize()

            # print("INFO: %s-%s-%s" % (ep,seq,shot))
            return {"asset_type":"%s" % type_name,"asset_category":"%s" % cate,"asset_name":"%s" % self.__name}

        #     # self.__thumb_path = self.temp_path
        #     return args
        # else:
        #     return None
            # print(self.__thumb_path)
        #     return self.__thumb_path
        # else:
        #     return "Not a shot"

    #def CopyAssetToNewConfig(self, new_config):
        #temp_dict = self.generate_info_dict()
        #new_config.update(temp_dict)

       # return cfg_util.CreatePathFromDict(cfg.project_paths["asset_base_path"],new_config)

    def getThumb(self):
        return self.__thumb_path

    def row(self):
        return self._row

    def getName(self):
        return self.__name


    def getParent(self):
        return self.__parent

    def setChildren(self, c_list=None):
        self.__children = c_list
        if c_list:
            self._row = len(self.__children)
        else:
            self._row = 0

    def getChildren(self):
        return self.__children


class createTreeNodes(object):
    """Creates repository type objects"""

    def __init__(self, base_path):
        self.base_path = base_path
        self.__footage_dict = {}
        self.node_list = self.find_type()

    def returnList(self):
        return self.node_list


    def find_type(self):
        dirs = os.listdir(self.base_path)
        result = []
        for cur_type in dirs:
            if cur_type.startswith("."):
                continue
            type_node = Node(cur_type, self.base_path + "/" + cur_type, None,"asset_type", cur_type)


            type_node.setChildren(self.find_category(type_node))
            result.append(type_node)
        return result

    def find_category(self, type_node):
        dirs = os.listdir(type_node.getUrl())
        result = []
        for cate_name in dirs:
            if cate_name.startswith("."):
                continue
            cate_node = Node(cate_name, type_node.getUrl() + "/" + cate_name, type_node,"asset_category", cate_name)
            cate_node.setChildren(self.find_asset(cate_node))

            result.append(cate_node)
        return result

    def find_asset(self, cate_node):
        dirs = os.listdir(cate_node.getUrl())
        result = []
        for cur_asset in dirs:
            if cur_asset.startswith("."):
                continue
            asset_node = Node(cur_asset, cate_node.getUrl() + "/" + cur_asset, cate_node,"asset")
            result.append(asset_node)
        return result


def runRigModulesUpdate():
    asset_top_path = CC.get_asset_top_path()
    dict = {}
    typeList = ['Char', 'Prop', 'Setdress']
    assets = []
    for type in typeList:
        type_path = os.path.join(asset_top_path, type).replace(os.sep, '/')
        categoryList = os.listdir(type_path)
        for category in categoryList:
            category_path = os.path.join(type_path, category).replace(os.sep, '/')
            assetNameList = os.listdir(category_path)
            for assetName in assetNameList:
                if type == 'Char':
                    assets.append({'asset_name': assetName,
                                   'asset_type': type,
                                   'asset_category': category,
                                   'asset_step': 'Model'})
                    assets.append({'asset_name': assetName,
                                   'asset_type': type,
                                   'asset_category': category,
                                   'asset_step': 'Rig'})
                    assets.append({'asset_name': assetName,
                                   'asset_type': type,
                                   'asset_category': category,
                                   'asset_step': 'Shading'})
                else:
                    assets.append({'asset_name': assetName,
                                   'asset_type': type,
                                   'asset_category': category,
                                   'asset_step': 'Base'})

    import QThreads as Q
    from MiasMagic2.transfer_functions import getMayaFiles
    processes = []
    for i, asset in enumerate(assets):
        print('>> Now starting on ' + asset['asset_name'] + ' <<')
        work_path = CC.get_asset_work_file(**asset)
        process = """import maya.standalone
maya.standalone.initialize('python')
import maya.cmds as cmds
cmds.file('%s', open=True, f=True)
from MiasMagic2.Mia_OddJobs import updateRigModules
updateRigModules(%s)
cmds.quit(f=True)""" % (work_path, asset)
        process = ";".join(process.split("\n"))
        processes.append(process)
    Q.CreateProcQueue(processes)


def updateRigModules(asset_info):
    import maya.cmds as cmds
    eyeList = ['EyeA', 'EyeB', 'EyeC', 'EyeRainbowGuy', 'EyeSmallDragon']
    mouthList = ['MouthA']
    refs = cmds.file(reference=True, query=True)
    changed = False
    for ref in refs:
        ref_node = cmds.referenceQuery(ref, referenceNode=True)
        for item in eyeList:
            if item in ref:
                changed = True
                print('>> Updating ' + item + ' <<')
                cmds.file(ref.replace('RigModule/' + item, 'RigModule/Eyes/' + item), loadReference=ref_node)
                continue
        for item in mouthList:
            if item in ref:
                changed = True
                print('>> Updating ' + item + ' <<')
                cmds.file(ref.replace('RigModule/' + item, 'RigModule/Mouths/' + item), loadReference=ref_node)
    if changed:
        print('>> Saving <<')
        cmds.file(save=True)

        print('>> Publishing <<')
        import PublishAssets.PublishMaster
        PubClass = PublishAssets.PublishMaster.ReadyPublish(asset_info=asset_info)
        PubClass.StartPublish()


def moveThumbnailsOver():
    asset_top_path = CC.old.get_asset_top_path()
    dict = {}
    typeList = ['Char', 'Prop', 'Setdress']
    assets = []
    for type in typeList:
        type_path = os.path.join(asset_top_path, type).replace(os.sep, '/')
        categoryList = os.listdir(type_path)
        for category in categoryList:
            category_path = os.path.join(type_path, category).replace(os.sep, '/')
            assetNameList = os.listdir(category_path)
            for assetName in assetNameList:
                if type == 'Char':
                    assets.append({'asset_name': assetName,
                                   'asset_type': type,
                                   'asset_category': category,
                                   'asset_step': 'Model'})
                    assets.append({'asset_name': assetName,
                                   'asset_type': type,
                                   'asset_category': category,
                                   'asset_step': 'Rig'})
                    assets.append({'asset_name': assetName,
                                   'asset_type': type,
                                   'asset_category': category,
                                   'asset_step': 'Shading'})
                else:
                    assets.append({'asset_name': assetName,
                                   'asset_type': type,
                                   'asset_category': category,
                                   'asset_step': 'Base'})

    for asset in assets:
        old_thumbnail_folder = os.path.abspath(CC.old.get_asset_thumbnail_path(**asset) + '../..').replace(os.sep, '/')
        if os.path.exists(old_thumbnail_folder):
            if os.listdir(old_thumbnail_folder):
                if asset['asset_category'] in ['Bushs', 'Grounds', 'Trees']:
                    asset['asset_category'] = 'Forest'
                new_thumbnail_folder = None
                try:
                    new_thumbnail_folder = os.path.abspath(CC.get_asset_thumbnail_path(**asset) + '../..').replace(os.sep, '/')
                except:
                    pass
                if new_thumbnail_folder:
                    if os.path.exists(new_thumbnail_folder):
                        print('Copying ' + new_thumbnail_folder)
                        copytree(old_thumbnail_folder, new_thumbnail_folder)



import os, shutil
def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item).replace(os.sep, '/')
        d = os.path.join(dst, item).replace(os.sep, '/')
        while '//' in s:
            s = s.replace('//', '/')
        while '//' in d:
            d = d.replace('//', '/')
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

def checkRenderRef(path=None):
    if not path:
        path = 'P:/_WFH_Projekter/930486_MiaMagicPlayground_S3-4/4_Production/Assets/3D_Assets/Setdress'
    for item in os.listdir(path):
        if item not in ['01_Work', '03_Texture', '04_Design']:
            newPath = os.path.join(path, item).replace(os.sep, '/')
            if os.path.isdir(newPath):
                checkRenderRef(newPath)
            else:
                if newPath[-10:] == '_Render.mb':
                    renderSize = os.path.getsize(newPath)
                    ingestPath = newPath.replace('_Render.mb', '_Ingest.mb')
                    ingestSize = os.path.getsize(ingestPath)
                    if renderSize < ingestSize * 0.8:
                        print(newPath.split('/')[-4] + '/' + newPath.split('/')[-1].replace('_Render.mb', ''))


if __name__ == '__main__':
    checkRenderRef()