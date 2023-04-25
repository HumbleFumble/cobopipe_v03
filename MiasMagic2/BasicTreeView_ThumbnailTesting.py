from PySide2 import QtWidgets, QtCore, QtGui

import Configs.OLD_CONFIGS.Config_MiasMagic2 as cfg
import Configs.OLD_CONFIGS.Config_MiasMagic as old_cfg
import Configs.OLD_CONFIGS.ConfigUtil as ConfigUtil

import AssetFunctions as AF
cfg_util = ConfigUtil.ConfigUtilClass(cfg)
old_cfg_util = ConfigUtil.ConfigUtilClass(old_cfg)

from getConfig import getConfigClass
CC = getConfigClass('MiasMagic2')

# import json
import os
import shutil

from PublishAssets import PublishMaster


# {'asset_name': 'HillB', 'asset_step': 'Base', 'asset_type': 'Setdress', 'asset_category': 'Forest'}
def QuickPublish(asset_name, asset_step, asset_type, asset_category):
    asset_info = {'asset_name': asset_name, 'asset_step': asset_step, 'asset_type': asset_type, 'asset_category': asset_category}
    print("quick publish")
    PubClass = PublishMaster.ReadyPublish(asset_info=asset_info)
    PubClass.StartPublish()

#TODO Put together with OIDManager.
#TODO Put in add button for aim(episodes/sequence/shot) and right click functions for adding rules and targets

# class C_Signals(QtCore.QObject):
#     finished: QtCore.Signal() = QtCore.Signal(bool)
#     result: QtCore.Signal() = QtCore.Signal(object)
#
#
# class ThreadPool(QtCore.QObject):
#     cnt = 0
#
#     def __init__(self):
#         super(ThreadPool, self).__init__()
#         self.pool = QtCore.QThreadPool.globalInstance()
#         self.signals = C_Signals()
#         self.pool.setMaxThreadCount(4)
#         self.list_of_workers = []
#
#     def getPoolObj(self):
#         return self.pool
#
#     def addWorker(self,worker=None,name=None):
#         self.list_of_workers.append(worker)
#
#     def startBatch(self, workers=None):
#         """
#         :param use_max:
#         :param workers: Takes a list of Worker objects
#         """
#
#         clear = False
#         if not workers:
#             workers = self.list_of_workers
#             clear = True
#         for worker in workers:
#             if isinstance(worker, Worker):
#                 # Pass signal on from Worker through ThreadPool to outside
#                 worker.signals.result.connect(self.signals.result.emit)
#                 self.pool.start(worker)
#
#             else:
#                 raise TypeError("Worker must be inherited from type 'Worker' from ThreadPool module")
#         if clear:
#             self.list_of_workers = []
#
#     def cancelBatch(self):
#         """
#         Removes all non-started threads from the pool
#         """
#         print("Pool's Cleared")
#         self.pool.clear()
#

# class Worker(QtCore.QRunnable):
#     def __init__(self, func=None, *args):
#         super(Worker, self).__init__()
#         self.signals = C_Signals()
#         self.func = func
#         self.args = args
#
#     def run(self):
#         if self.func:
#             result = self.func(self.args)
#             self.signals.result.emit(result)
#         else:
#
#             time.sleep(3)
#             self.signals.result.emit(self.args)
#             # print(self.args)
#         # self.signals.finished.emit(True)

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
        # self.thumb_signals = C_Signals()

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

    def generate_thumbnail(self):
        # print("NEW THUMB FOR %s" % self.__name)
        if self.__type == "asset":
            self.__thumb_path = cfg_util.CreatePathFromDict(cfg.thumbnail_paths["asset_thumbnail_path"],self.generate_info_dict())

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

    def initiate(self, cur_index=None):
        pass
        # print("%s initiate" % self.__name)
        # self.thumb_run = Worker(self.generate_thumbnail,cur_index)
        # self.thumb_run.signals.result.connect(self.thumb_signals.result.emit)
        # return self.thumb_run

# class createTreeNodes():
#     def __init__(self):
#         self.node_list = []
#         self.save_dict_file = cfg_util.CreatePathFromDict(cfg.project_paths["OID_set_rules"])
#         self.rule_dict = {}
#         self.CreateNodes()
#
#
#     def CreateNodes(self):
#         self.rule_dict = LoadSettings(self.save_dict_file)
#         for aim in sorted(self.rule_dict.keys()):
#             aim_node = Node(aim,None,"aim")
#             for rule in sorted(self.rule_dict[aim].keys()):
#                 rule_node = Node(rule,aim_node,"rule")
#                 aim_node.append(rule_node)
#                 for target in sorted(self.rule_dict[aim][rule]):
#                     rule_node.append(Node(target,rule_node,"target"))
#             self.node_list.append(aim_node)
#     def returnList(self):
#         return self.node_list



# VIEWER -------------------------------------------------------------------------------------------------------------
class TreeModel(QtCore.QAbstractItemModel):
    def __init__(self, nodes):
        QtCore.QAbstractItemModel.__init__(self)
        self.root = Node("root", "", None)
        # self.pool = ThreadPool()
        # self.__pixmap_util = pixmap_util
        self.folder_picture = CC.get_folder_icon_path()
        # self.no_thumb_picture = cfg_util.CreatePathFromDict(cfg.thumbnail_paths["no_thumb_icon_path"])
        self.no_thumb_pix()
        self.nodes = nodes
        self.root.setChildren(nodes)


    def no_thumb_pix(self):
        pixmap = QtGui.QPixmap(self.folder_picture)
        pixmap = pixmap.scaled(19, 10, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        QtGui.QPixmapCache.insert("no_thumb_pix", pixmap)

    def updateNodes(self,start_index=QtCore.QModelIndex()):
        for row in range(self.rowCount(start_index)):
            cur_index = self.index(row,0,start_index)
            cur_node = cur_index.internalPointer()
            if cur_node.getType() == "asset":
                # cur_run = cur_node.initiate(cur_index)
                # cur_run.signals.result.connect(self.UpdateModel)
                # test = Worker(cur_node.generate_thumbnail, cur_node.getName())
                # test.signals.result.connect(self.UpdateModel)
                # self.pool.addWorker(test)
                # self.pool.signals.result.connect(self.UpdateModel)
                cur_node.generate_thumbnail()
            self.updateNodes(cur_index)
        # self.pool.startBatch()

    def updateModel(self,cur_index):
        # print(cur_index)
        if cur_index:
            self.dataChanged.emit(cur_index,cur_index)
        self.layoutChanged.emit()
        # for c_node in parent_node.getChildren():
        #     # c_node.thumb_signals.result.connect(self.printThis)
        #     node_run = c_node.initiate()
        #     self.pool.addWorker(node_run)
        #     self.updateNodes(c_node)


    def insertRows(self, position, rows, index, parent):
        self.beginInsertRows(index, position, position + rows - 1)
        self.endInsertRows()

        return True

    def rowCount(self, index):
        if index.isValid():
            node = index.internalPointer()
            # return index.internalPointer()
            return len(node.getChildren())
        return len(self.root.getChildren())

    def index(self, row, column, cur_parent=None):
        if not cur_parent or not cur_parent.isValid():
            node_parent = self.root
        else:
            node_parent = cur_parent.internalPointer()

        if not QtCore.QAbstractItemModel.hasIndex(self, row, column, cur_parent):
            return QtCore.QModelIndex()

        # child = node_parent.__children[row]
        child = node_parent.child(row)

        if child:
            return QtCore.QAbstractItemModel.createIndex(self, row, column, child)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if index.isValid():
            p = index.internalPointer().getParent()
            if p:
                return QtCore.QAbstractItemModel.createIndex(self, p.row(), 0, p)
        return QtCore.QModelIndex()

    def columnCount(self, index):
        return 1  # Only have 1 column
        # if index.isValid():
        #     return index.internalPointer().columnCount()
        # return self._root.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return None
        node = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return node.getName()

            # return node.data(index.column())
        if role == QtCore.Qt.DecorationRole:
            # node.generate_thumbnail()
            cur_map = node.getThumb()
            if cur_map:
                pixmap = QtGui.QPixmap(cur_map)
                pixmap = pixmap.scaled(192, 108, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)

                # QtGui.QPixmapCache.insert("%s_thumb" % self.__name, pixmap)
                # pixmap = QtGui.QPixmapCache.find(cur_map)
                # pixmap = cur_map
                return pixmap
            # else:
            #     pixmap = QtGui.QPixmapCache.find("no_thumb_pix")
            #     return pixmap
        #     pass
            # image_path = self.folder_picture
            # if not node.getType() == "shot":
            #     pixmap = ""
            # else:
            #     pixmap = ""

            # return pixmap
        return None

    def getNode(self, index):
        return index.internalPointer()

    def getNodes(self, list_of_index):
        return_list = []
        for c_i in list_of_index:
            i = self.getNode(c_i)
            if i:
                return_list.append(i)
        return return_list

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        # super(MainWindow, self).__init__(parent=self.__getFusionMainWindow())
        super(MainWindow, self).__init__()
        self.setWindowTitle("Basic Tree")
        QtGui.QPixmapCache.setCacheLimit(200 * 10240)
        self.asset_path = CC.old.get_asset_top_path()
        #self.asset_path = cfg_util.CreatePathFromDict(old_cfg.project_paths["asset_top_path"],old_cfg.project_paths)
        node_list = createTreeNodes(self.asset_path)
        self.nodes = node_list.returnList()
        self.createWindow()

        # Set startup table model
        self.resize(800, 800)
        self.show()
        self.populateTree()
        self.updateModel()

    def updateModel(self):
        #self.tree_model.updateNodes()
        self.tree_model.updateModel(None)

    def createWindow(self):
        self.layout_top = QtWidgets.QVBoxLayout(self)

        self.add_button = QtWidgets.QPushButton("Add")

        self.tree = QtWidgets.QTreeView(self)
        self.tree.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.tree.setHeaderHidden(True)
        self.tree.setExpandsOnDoubleClick(True)
        self.tree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.tree.setAnimated(True)
        self.tree.setIndentation(20)
        self.tree.setSortingEnabled(True)
        self.tree.installEventFilter(self)
        self.tree.clicked.connect(self.treeClicked)

        self.layout_top.addWidget(self.tree)
        self.layout_top.addWidget(self.add_button)
        self.setLayout(self.layout_top)

    def treeClicked(self, cur_index):
        cur_node = self.tree_model.getNode(cur_index)
        # cur_node.generate_thumbnail()
        # self.tree_model.dataChanged.emit(cur_index,cur_index)

        #temp_dict = cfg.project_paths
        #print(cur_node.getUrl())
        #print(cur_node.CopyAssetToNewConfig(temp_dict))
        path, process = runCopyAsset(cur_node)
        print(process)
        if process != None:
            base_command = 'mayapy.exe -c "%s"' % (process)
            #print(base_command)
            print("NOW RUNNING!")
            var = subprocess.Popen(base_command, shell=False, universal_newlines=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            # subprocess.run(base_command)
            print(var.communicate())
            print("NOW DONE WITH RUNNING")
            # Q.CreateProcQueue([process])

        # self.tree_model.updateNodes(cur_index)
        # for c_node in self.nodes:
        #     self.updateNodes(c_node)
        # self.pool.startBatch()


    def populateTree(self):
        self.tree_model = TreeModel(self.nodes)
        self.tree.setModel(self.tree_model)
        self.tree.expandAll()




        # new_work_folder = cfg_util.CreatePathFromDict(cfg.project_paths["asset_work_folder"],asset_info)
        #
        # old_ref_folder  = cfg_util.CreatePathFromDict(cfg.project_paths["asset_ref_folder"],old_asset_info)
        #
        # old_shading_file = None
        # for item in os.listdir(old_ref_folder):
        #     if item[-14:] == 'Shading_Ref.mb':
        #         old_shading_file = os.path.join(old_ref_folder, item).replace(os.sep, '/')
        #


        # import maya.standalone
        # maya.standalone.initialize("Python")
        #
        # import maya.cmds as cmds
        # cmds.loadPlugin("Mayatomr")


        """
        copy over texture folder from old asset - Done
        import render_ref with namespace "render"
        delete template super_root_group
        delete template geo group
        move "render" groups up under Top_Group
        rename Top_Group -> Root_Group
        change "file" node texture paths
        remove namespace of "render"
        save file :D
        run in maya.py -c 
        """

        # source = node.getUrl()
        # destination = node.CopyAssetToNewConfig(cfg.project_paths)
        # try:
        #     # Copy entire directory to new directory
        #     shutil.copytree(source, destination)
        #     # Run recursive cleaning function over every directory and file in directory
        #     self.updateMayaFiles(destination)
        # except:
        #     # Most likely failed due to the destination already existing
        #     print('Failed to copy')


    # def updateMayaFiles(self, directory):
    #     subfolders = os.listdir(directory)
    #     for folder in subfolders:
    #         path = os.path.join(directory, folder)
    #         path = path.replace(os.sep, '/')
    #         if os.path.isdir(path):
    #             self.updateMayaFiles(path)
    #         else:
    #             if path[-3:] in ['.ma', '.mb']:
    #                 print(path)



    def printThis(self,*args):
        print("PRINT_THIS: %s" % args)
        self.tree_model.layoutChanged.emit()
        self.tree_model.dataChanged.emit()

    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.ContextMenu):
            if(source is self.tree):
                menu = QtWidgets.QMenu()
                nodes = []

                if source.selectedIndexes():
                    for sel in source.selectedIndexes():
                        si = self.tree_model.getNode(source.selectedIndexes()[0])
                        if si:
                            nodes.append(si)
                else:
                    return super(MainWindow, self).eventFilter(source, event)

                if source == self.tree:
                    node = nodes[0]
                    open_menu = QtWidgets.QMenu("Print", menu)

                    menu.addMenu(open_menu)
                    menu.addAction("Open Folder")
                    open_menu.addAction("Print Name")
                    menu.addAction("Copy To New Season")


                action = menu.exec_(event.globalPos())
                if not action == None:
                    if action.text() == "Print Name":
                        print(node.getName())
                    if action.text() == "Copy To New Season":
                        print("NOW TO COPY!: %s" % node.getName())
                    if action.text() == "Open Folder":
                        openFolder(node.getUrl())



        return QtWidgets.QWidget.eventFilter(self, source, event)


def openFolder(folder_path):
    os.startfile(folder_path)

# def SaveSettings(save_location, save_info):
#     with open(save_location, 'w+') as saveFile:
#         json.dump(obj=save_info, fp=saveFile,indent=4, sort_keys=True)
#     saveFile.close()

# def LoadSettings(save_location):
#     if os.path.isfile(save_location):
#         with open(save_location, 'r') as saveFile:
#             loadedSettings = json.load(saveFile)
#         if loadedSettings:
#             return loadedSettings
#     else:
#         print("not a file")
#     return None



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
    #
    #     return result
    # # REGEX FOR CHECKING FOLDER NAMES:
    #
    # def FindEpisode(self, content):
    #     # test = "^(s)\d{3}$"
    #     low_case = content.lower()
    #     # re_compile = re.compile("^(s)\d{3}$")
    #     re_compile = re.compile("%s$" % cfg.regex_strings["episode"])
    #     if re_compile.search(low_case):
    #         return True
    #     else:
    #         return False
    #
    # def FindSequence(self, content):
    #     low_case = content.lower()
    #     re_compile = re.compile("%s%s$" % (cfg.regex_strings["episode"], cfg.regex_strings["seq"]))
    #     if re_compile.search(low_case):
    #         return True
    #     else:
    #         return False
    #
    # def FindShot(self, content):
    #     low_case = content.lower()
    #     # re_compile = re.compile("^(s)\d{3}(_sq)\d{3}(_sh)\d{3}$")
    #     re_compile = re.compile(
    #         "%s%s%s$" % (cfg.regex_strings["episode"], cfg.regex_strings["seq"], cfg.regex_strings["shot"]))
    #     if re_compile.search(low_case):
    #         return True
    #     else:
    #         return False

    # Copy assets from old project folder to a new project folder

def runCopyAsset(node):
    asset_info = node.generate_info_dict()
    path, process = copyAsset(asset_info)
    return path, process

def copyAsset(asset_info):
    import Configs.ConfigClasses.ConfigClass_MiasMagic2
    CC = Configs.ConfigClasses.ConfigClass_MiasMagic2.ConfigClass()
    return_path = None
    process = None
    if asset_info['asset_type'] == 'Char':
        #asset_info.update(cfg.project_paths)
        new_asset_base_path = CC.get_asset_base_path()
        #new_asset_base_path = cfg_util.CreatePathFromDict(cfg.project_paths["asset_base_path"], asset_info)

        old_asset_info = asset_info
        #old_asset_info.update(old_cfg.project_paths)
        old_asset_base_path = old_cfg_util.CreatePathFromDict(old_cfg.project_paths["asset_base_path"], old_asset_info)

        new_base_path = cfg_util.CreatePathFromDict(cfg.project_paths["base_path"], asset_info)
        old_base_path = old_cfg_util.CreatePathFromDict(old_cfg.project_paths["base_path"], old_asset_info)


        print(new_base_path)
        print(old_base_path)

        if not os.path.exists(new_asset_base_path):
            try:
                shutil.copytree(old_asset_base_path, new_asset_base_path, ignore=shutil.ignore_patterns('_History'))
                getMayaFiles(new_asset_base_path)

            except shutil.Error as err:
                print(r'Copy error')
                shutil.errors.extend(err.args[0])

            mayaFiles = getMayaFiles(new_asset_base_path)
            for file_path in mayaFiles:
                if file_path[-3:] == '.ma':
                    file_type = 'mayaAscii'
                elif file_path[-3:] == '.mb':
                    file_type = 'mayaBinary'
                else:
                    file_type = 'mayaAscii'
                cleanCharFiles(file_path, file_type, old_base_path, new_base_path)

        else:
            print('Folder already exists: ' + new_asset_base_path)


        return_path = new_asset_base_path




    if asset_info['asset_type'] == 'Prop':
        """Node info:"""
        #asset_info.update(cfg.project_paths) #add new config paths to asset info
        new_texture_folder = cfg_util.CreatePathFromDict(cfg.project_paths["asset_texture_folder"],asset_info)
        asset_info["asset_step"] = "Base"
        new_base_file = cfg_util.CreatePathFromDict(cfg.project_paths["asset_work_file"], asset_info)

        old_asset_info = asset_info
        #old_asset_info.update(old_cfg.project_paths)
        old_asset_info["asset_output"] = "Render"
        old_texture_folder  = cfg_util.CreatePathFromDict(cfg.project_paths["asset_texture_folder"], old_asset_info)
        render_ref = old_cfg_util.CreatePathFromDict(old_cfg.ref_paths["Render"], old_asset_info)

        new_base_path = cfg_util.CreatePathFromDict(cfg.project_paths["base_path"], asset_info)
        old_base_path = old_cfg_util.CreatePathFromDict(old_cfg.project_paths["base_path"])

        try:
            if os.path.exists(new_base_file):
                print('File already exists: ' + new_base_file)
            else:
                asset_functions = AF.CreateAsset(asset_info)  # create new empty asset based on the new config and asset info.
                asset_functions.Run()  # if asset_functions.Run():

                # Loop through folders inside texture folder
                for folder in os.listdir(old_texture_folder):
                    folderPath = os.path.join(old_texture_folder, folder).replace(os.sep, '/')

                    # Loop through items inside the folders
                    for item in os.listdir(folderPath):
                        itemPath = os.path.join(old_texture_folder, folder, item).replace(os.sep, '/')
                        destination = os.path.join(new_texture_folder, folder, item).replace(os.sep, '/')

                        # If item is folder
                        if os.path.isdir(itemPath):
                            # Attempts to copy folder
                            try:
                                shutil.copytree(itemPath, destination)
                            except:
                                print('Failed to copy ' + itemPath + ' to ' + destination)
                        else:
                            # Attempts to copy file
                            try:
                                shutil.copyfile(itemPath, destination)
                            except:
                                print('Failed to copy ' + itemPath + ' to ' + destination)
        except:
            pass

            return_path = new_base_file

        # file_path = r"P:\_WFH_Projekter\930486_MiaMagicPlayground_S3-4\4_Production\Assets\3D_Assets\Prop\Assessory\Donut\01_Work\Maya\Donut_Base.ma".replace(
        #     os.sep, '/')
        file_type = "mayaAscii"
        process = migrateProp(new_base_file, file_type, render_ref, old_base_path, new_base_path)


    if asset_info['asset_type'].lower() == 'setdress':
        if asset_info['name'] in ['BushE', 'FaceFlowerA', 'MushroomA', 'MushroomB', 'MushroomC', 'RockA', 'RockB', 'RockC',
                              'RockY', 'StickA', 'StickB', 'TwigPileA', 'voleyballBall', 'voleyballScoreBoard',
                              'WhirleyBallNetA', 'BabyCrystalA', 'SmallBluePlanet', 'SpaceBubbleA', 'BigTreeA',
                              'BranchLongA', 'PineTreeU', 'ConePlantA', 'CoralPlantB', 'PlantB', 'StaggeredHills',
                              'StaggeredHillsA', 'StaggeredHillsB', 'StaggeredHillsC', 'StarfishA', 'UWPlantB',
                              'UWPlantBA', 'UWRockA', 'UWRockB', 'UWRockC', 'VineB', 'FlipRockA']:
            pass
            # asset_info = node.generate_info_dict()
            # if asset_info['asset_category'] in ['Bushes', 'Grounds', 'Trees']:
            #     asset_info['asset_category'] = 'Forest'
            # # asset_info.update(cfg.project_paths)
            # new_asset_base_path = cfg_util.CreatePathFromDict(cfg.project_paths["asset_base_path"], asset_info)
            #
            # old_asset_info = node.generate_info_dict()
            # # old_asset_info.update(old_cfg.project_paths)
            # old_asset_base_path = old_cfg_util.CreatePathFromDict(old_cfg.project_paths["asset_base_path"],
            #                                                       old_asset_info)
            #
            # new_base_path = cfg_util.CreatePathFromDict(cfg.project_paths["base_path"], asset_info)
            # old_base_path = old_cfg_util.CreatePathFromDict(old_cfg.project_paths["base_path"], old_asset_info)
            #
            # print(new_base_path)
            # print(old_base_path)
            #
            # if not os.path.exists(new_asset_base_path):
            #     try:
            #         shutil.copytree(old_asset_base_path, new_asset_base_path, ignore=shutil.ignore_patterns('_History'))
            #         getMayaFiles(new_asset_base_path)
            #
            #     except shutil.Error as err:
            #         print(r'Copy error')
            #         shutil.errors.extend(err.args[0])
            #
            #     mayaFiles = getMayaFiles(new_asset_base_path)
            #     for file_path in mayaFiles:
            #         if file_path[-3:] == '.ma':
            #             file_type = 'mayaAscii'
            #         elif file_path[-3:] == '.mb':
            #             file_type = 'mayaBinary'
            #         else:
            #             file_type = 'mayaAscii'
            #         #cleanCharFiles(file_path, file_type, old_base_path, new_base_path)

            # else:
            #     print('Folder already exists: ' + new_asset_base_path)
            #
            # return_path = new_asset_base_path
        else:
            old_asset_info = asset_info.copy()
            print(old_asset_info)
            if asset_info['new_asset_category']:
                asset_info['asset_category'] = asset_info['new_asset_category']
            asset_info['asset_type'] = 'Setdress'
            # asset_info.update(cfg.project_paths) #add new config paths to asset info
            new_texture_folder = CC.get_asset_texture_folder(**asset_info)
            old_texture_folder = CC.old.get_asset_texture_folder(**old_asset_info)

            asset_info["asset_step"] = "Base"
            asset_info["asset_output"] = "Render"
            old_asset_info["asset_step"] = "Base"
            old_asset_info["asset_output"] = "Render"
            new_base_file = CC.get_asset_work_file(**asset_info)
            new_base_path = CC.get_base_path()
            old_base_path = CC.old.get_base_path()
            render_ref = CC.old.get_Render(**old_asset_info)
            # new_base_file = cfg_util.CreatePathFromDict(cfg.project_paths["asset_work_file"], asset_info)
            # new_base_path = cfg_util.CreatePathFromDict(cfg.project_paths["base_path"], asset_info)
            # old_base_path = old_cfg_util.CreatePathFromDict(old_cfg.project_paths["base_path"], asset_info)
            # render_ref = old_cfg_util.CreatePathFromDict(old_cfg.ref_paths["Render"], asset_info)

            if os.path.exists(new_base_file):
                print('File already exists: ' + new_base_file)
            else:
                asset_functions = AF.CreateAsset(asset_info)  # create new empty asset based on the new config and asset info.
                asset_functions.Run()  # if asset_functions.Run():

                # Loop through folders inside texture folder
                print(old_texture_folder)
                for folder in os.listdir(old_texture_folder):
                    folderPath = os.path.join(old_texture_folder, folder).replace(os.sep, '/')
                    if os.path.isdir(folderPath):

                        # Loop through items inside the folders
                        for item in os.listdir(folderPath):
                            itemPath = os.path.join(old_texture_folder, folder, item).replace(os.sep, '/')
                            destination = os.path.join(new_texture_folder, folder, item).replace(os.sep, '/')

                        # If item is folder
                            if os.path.isdir(itemPath):
                                # Attempts to copy folder
                                try:
                                    shutil.copytree(itemPath, destination)
                                except:
                                    print('Failed to copy ' + itemPath + ' to ' + destination)
                            else:
                                # Attempts to copy file
                                try:
                                    shutil.copyfile(itemPath, destination)
                                except:
                                    print('Failed to copy ' + itemPath + ' to ' + destination)

                    else:
                        # Someone fucked up and there is a file where there should not be.
                        # We will move it anyways
                        try:
                            shutil.copyfile(folderPath)
                        except:
                            print('Failed to copy ' + folderPath)


                file_type = "mayaAscii"
                print(new_base_file)
                print(new_base_path)
                print(old_base_path)
                print(render_ref)
                process = migrateSetdress(new_base_file, file_type, render_ref, old_base_path, new_base_path)
                print('Done migrating Setdress file: ' + asset_info['name'])
                return_path = new_base_file

    return return_path, process

def MyActualScript(*args):
    """Do something"""
    pass

import subprocess
def migrateProp(file_path, file_type, render_ref, old_base_path, new_base_path):
    print(render_ref)
    script_content = """import maya.standalone
maya.standalone.initialize('python')
import maya.cmds as cmds
import sys
sys.path.append('C:/Users/mmcb/PycharmProjects/bombay_base_production/')
cmds.file('%s', open=True,f=True)
cmds.file(type='%s')
from assetTransfer import propAssetTransfer
propAssetTransfer('%s')
from UpdateTextures import update_textures
update_textures('%s', '%s')
cmds.file(save=True)
cmds.quit(f=True)""" % (file_path, file_type, render_ref, old_base_path, new_base_path)
    script_content = ";".join(script_content.split("\n"))
    return script_content
    # base_command = 'mayapy.exe -c "%s"' % (script_content)
    # print(base_command)
    # return subprocess.Popen(base_command, shell=False, universal_newlines=True)


def migrateSetdress(file_path, file_type, render_ref, old_base_path, new_base_path, stdout=subprocess.PIPE):
    script_content = """import maya.standalone
maya.standalone.initialize('python')
import maya.cmds as cmds
import sys
sys.path.append('C:/Users/mmcb/PycharmProjects/bombay_base_production/')
cmds.file('%s', open=True,f=True)
cmds.file(type='%s')
from MiasMagic2.assetTransfer import setdressAssetTransfer
setdressAssetTransfer('%s')
from MiasMagic2.UpdateTextures import update_textures
update_textures('%s', '%s')
cmds.file(save=True) 
cmds.quit(f=True)""" % (file_path, file_type, render_ref, old_base_path, new_base_path)
    script_content = ";".join(script_content.split("\n"))
    # print(script_content)
    return script_content
    # Q.ProcRun()
    #base_command = 'mayapy.exe -c "%s"' % (script_content)
    #print(base_command)
    #return subprocess.Popen(base_command, shell=False, universal_newlines=True, stdout=subprocess.PIPE)


def cleanCharFiles(file_path, file_type, old_base_path, new_base_path):
    script_content = """import maya.standalone
maya.standalone.initialize('python')
import maya.cmds as cmds
import sys
sys.path.append('C:/Users/mmcb/PycharmProjects/bombay_base_production/')
cmds.file('%s', open=True,f=True)
cmds.file(type='%s')
from MiasMagic2.UpdateTextures import update_textures, updateRef, addPublishSet
update_textures('%s', '%s')
updateRef('%s', '%s')
addPublishSet()
cmds.file(save=True)
cmds.quit(f=True)""" % (file_path, file_type, old_base_path, new_base_path, old_base_path, new_base_path)
    script_content = ";".join(script_content.split("\n"))
    base_command = 'mayapy.exe -c "%s"' % (script_content)
    # return script_content
    return subprocess.Popen(base_command, shell=False, universal_newlines=True, stdout=subprocess.PIPE)

def getMayaFiles(directory, list=[]):
    for item in os.listdir(directory):
        path = os.path.join(directory, item).replace(os.sep, '/')
        if os.path.isdir(path):
            getMayaFiles(path, list)
        else:
            if path[-3:] in ['.ma', '.mb']:
                list.append(path)
    return list


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.resize(584, 662)
    mainWin.show()
    # mainWin.copyAsset()
    sys.exit(app.exec_())

