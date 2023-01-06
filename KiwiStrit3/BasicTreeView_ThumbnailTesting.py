from PySide2 import QtWidgets, QtCore, QtGui

CC = ConfigClass_KiwiStrit3.ConfigClass()
CC_Old = ConfigClass_KiwiStrit2.ConfigClass()

import transferAsset
TA = transferAsset.transferAssetClass()
import json
import os

#TODO Put in add button for aim(episodes/sequence/shot) and right click functions for adding rules and targets



class C_Signals(QtCore.QObject):
    finished: QtCore.Signal() = QtCore.Signal(object)
    result: QtCore.Signal() = QtCore.Signal(object)
    error = QtCore.Signal(tuple)
    progress = QtCore.Signal(int)

#
# @QtCore.Slot(bool)
class MyThreadPool(QtCore.QObject):
    cnt=0
    def __init__(self):
        super(MyThreadPool, self).__init__()
        self.signals = C_Signals()
        self.pool = QtCore.QThreadPool.globalInstance()
        self.worker_len = 0
        self.mute = QtCore.QMutex()

    def getPoolObj(self):
        return self.pool

    def startBatch(self, workers=None,pool_key=None):
        """
        :param use_max:
        :param workers: Takes a list of Worker objects
        """
        # if not pool_key:
        #     pool_key = "default"
        # self.worker_len[pool_key] = len(workers)
        self.worker_len = len(workers)
        for worker in workers:
            if isinstance(worker, Worker):
                # Pass signal on from Worker through ThreadPool to outside
                # worker.signals.result.connect(self.emitResult)
                worker.signals.finished.connect(self.workerFinished)

                # worker.signals.finished.connect(partial(self.workerFinished,pool_key=pool_key))
                # self.signals.result.connect(worker.signals.result)
                self.pool.start(worker)
            else:
                raise TypeError("Worker must be inherited from type 'Worker' from ThreadPool module")
        # if clear:
        #     self.list_of_workers = []'

    def workerFinished(self,*args,**kwargs):
        self.mute.lock()
        self.cnt += 1
        # print("COUNT: %s" % self.cnt)
        self.mute.unlock()
        if self.worker_len == self.cnt:
            self.mute.lock()
            self.cnt = 0
            self.worker_len = 0
            self.mute.unlock()
            self.signals.finished.emit(*args)

    # def workerFinished(self, pool_key="default", *args, **kwargs):
    #     print("hey?")
    #     self.mute.lock()
    #     if "pool_key" in kwargs:
    #         pool_key = kwargs["pool_key"]
    #     print("worker finished: %s" % pool_key)
    #     self.cnt[pool_key] += 1
    #     # print("COUNT: %s" % self.cnt)
    #     self.mute.unlock()
    #     if self.worker_len[pool_key] == self.cnt[pool_key]:
    #         self.mute.lock()
    #         self.cnt.pop(pool_key, None)
    #         self.worker_len.pop(pool_key, None)
    #         self.mute.unlock()
    #         self.signals.finished.emit(*args)


    def cancelBatch(self):
        """
        Removes all non-started threads from the pool
        """
        print("Pool's Cleared")
        self.pool.clear()

#TODO TRYING TO GET THREADPOOL TO WORK WITH POOL_KEYS FOR MULTIPLE THREAD_POOLS FROM ONE FUNCTIONS
# @QtCore.Slot(bool)
class Worker(QtCore.QRunnable):
    def __init__(self, func=None, *args,**kwargs):
        super(Worker, self).__init__()
        self.signals = C_Signals()

        self.func = func
        self.args = args
        self.kwargs = kwargs
        # self.mute = QtCore.QMutex()

    @QtCore.Slot()
    def run(self):
        if self.func:
            result = self.func(*self.args,**self.kwargs)
            # print("print",result)
            # self.mute.lock()
            self.signals.result.emit(result)
            self.signals.finished.emit("finished")
            # self.mute.unlock()
        # else:
        #     time.sleep(1)
        #     self.signals.result.emit("False")
            # print(self.args)
        # self.signals.finished.emit(True)

class Node(object):
    def __init__(self, name=None,url=None,parent=None, type=None):
        self.name = name
        self.parent = parent
        self.__children = []
        self._row = 0
        self.__type = type
        self.__thumb_path = None
        self.thumb_key = QtGui.QPixmapCache.Key()
        self.url = url
        self.info_dict = {}
        self.asset_type = None
        self.asset_category = None
        self.generateInfoDict()
        # self.thumb_signals = C_Signals()

    def getType(self):
        return self.__type

    def getUrl(self):
        return self.url

    def append(self, c_obj):
        self.__children.append(c_obj)
        self._row = 0
        # self._row = len(self.__children)

    def child(self, in_row):  # Treeview
        if in_row >= 0 and in_row < len(self.__children):
            return self.__children[in_row]

    def generateInfoDict(self):
        if self.__type =="asset_type":
            self.asset_type = self.name
        if self.__type == "asset_category":
            self.asset_type =  self.parent.getName()
            self.asset_category = self.name
        if self.__type =="asset":
            self.asset_category = self.parent.getName()
            self.asset_type = self.parent.getParent().getName()
            # print("INFO: %s-%s-%s" % (ep,seq,shot))
        self.info_dict = {"asset_type":"%s" % self.asset_type,"asset_category":"%s" % self.asset_category,"asset_name":"%s" % self.name}

    def getThumbKey(self):
        return self.thumb_key

    def setThumbKey(self, key):
        self.thumb_key = key

    def generateThumbPath(self, node=None, cur_index=None):

        if self.__type == "asset":
            self.generateInfoDict()
            # self.__thumb_path = cfg_util_old.CreatePathFromDict(cfg.thumbnail_paths["asset_thumbnail_path"], self.generateInfoDict())
            self.__thumb_path = CC_Old.get_asset_thumbnail_path(asset_name=self.name,asset_type=self.asset_type,asset_category=self.asset_category)

            # pixmap = QtGui.QPixmap()
            # QtGui.QPixmap.load(pixmap, self.__thumb_path)
            # pixmap = pixmap.scaled(192, 108, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            # self.thumb_key = QtGui.QPixmapCache.insert(pixmap)
            return cur_index


    def CopyAssetToNewConfig(self,new_cc):
        old_path = CC_Old.get_asset_base_path(asset_type=self.asset_type,asset_name=self.name,asset_category=self.asset_category)
        new_path = new_cc.get_asset_base_path(asset_type=self.asset_type,asset_name=self.name,asset_category=self.asset_category)
        print("TRANSFERING!")
        TA.transferAssetRun(old_path,new_path,CC_Old.get_base_path(),new_cc.get_base_path())
        # return old_path,new_path

    def getThumb(self):
        return self.__thumb_path

    def row(self):
        return self._row

    def getName(self):
        return self.name


    def getParent(self):
        return self.parent

    def setChildren(self, c_list=None):
        self.__children = c_list
        if c_list:
            self._row = len(self.__children)
        else:
            self._row = 0

    def getChildren(self):
        return self.__children


# VIEWER -------------------------------------------------------------------------------------------------------------
class TreeModel(QtCore.QAbstractItemModel):
    def __init__(self, nodes):
        QtCore.QAbstractItemModel.__init__(self)
        self.root = Node("root", "", None)
        self.pool = MyThreadPool()
        self.pool.signals.finished.connect(self.TotalModelRefresh)
        # self.__pixmap_util = pixmap_util
        # self.folder_picture = cfg_util.CreatePathFromDict(cfg.thumbnail_paths["folder_icon_path"])
        self.folder_picture = CC.get_folder_icon_path()
        # print(self.folder_picture)
        # self.no_thumb_picture = cfg_util.CreatePathFromDict(cfg.thumbnail_paths["no_thumb_icon_path"])
        self.no_thumb_pix()
        self.nodes = nodes
        self.root.setChildren(nodes)
        self.all_nodes = []
        # self.getAllNodes(cur_index=QtCore.QModelIndex())

    def TotalModelRefresh(self):
        print("REFRESHING")
        self.beginResetModel()
        self.endResetModel()
        self.layoutChanged.emit()

    def no_thumb_pix(self):
        pixmap = QtGui.QPixmap(self.folder_picture)
        pixmap = pixmap.scaled(19, 10, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.folder_thumb_key = QtGui.QPixmapCache.insert(pixmap)

    def returnNodesAndIndex(self,start_index=QtCore.QModelIndex()):
        for row in range(self.rowCount(start_index)):
            cur_index = self.index(row,0,start_index)
            cur_node = cur_index.internalPointer()
            if cur_node.getType() == "asset":
                self.all_nodes.append((cur_node,cur_index))
            self.returnNodesAndIndex(cur_index)
        # self.pool.startBatch()

    def getAllNodes(self,cur_index):
        self.beginResetModel()
        self.returnNodesAndIndex(cur_index)

        list_of_workers = []
        for c_node in self.all_nodes:
            worker = Worker(c_node[0].generateThumbPath, cur_index=c_node[1])
            worker.signals.result.connect(self.updateModel)
            list_of_workers.append(worker)
        self.pool.startBatch(list_of_workers)
            # worker.signals.result.connect

    # def printResult(self,*args):
    #     print(*args)

    #
    def updateModel(self,cur_index):
        # print(cur_index)
        # if cur_index:
        #     self.dataChanged.emit(cur_index,cur_index)
        # else:
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
            if not node.getType() == "asset":
                pixmap = QtGui.QPixmap(w=19, h=10)
                QtGui.QPixmap.load(pixmap,self.folder_picture)
                pixmap = pixmap.scaled(19, 10, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                return pixmap
                # QtGui.QPixmapCache.find(self.folder_thumb_key,pixmap)
                # node.setThumbKey(self.folder_thumb_key)
            else:
                pixmap = QtGui.QPixmap(w=192, h=108)
                QtGui.QPixmap.load(pixmap, node.getThumb())
                pixmap = pixmap.scaled(192, 108, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                return pixmap
            # cur_key = node.getThumbKey()
            # if not cur_key.isValid():
            #     if not node.getType() == "asset":
            #         pixmap = QtGui.QPixmap()
            #         QtGui.QPixmapCache.find(self.folder_thumb_key,pixmap)
            #         node.setThumbKey(self.folder_thumb_key)
            #     else:
            #         print(node.getName())
            #         pixmap = QtGui.QPixmap(w=192,h=108)
            #         QtGui.QPixmap.load(pixmap,node.getThumb())
            #         pixmap = pixmap.scaled(192, 108, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            #         node.setThumbKey(QtGui.QPixmapCache.insert(pixmap))
            # else:
            #     pixmap = QtGui.QPixmap()
            #     QtGui.QPixmapCache.find(node.getThumbKey(), pixmap)
            #     return pixmap

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
        QtGui.QPixmapCache.clear()
        QtGui.QPixmapCache.setCacheLimit(400 * 10240)

        # self.asset_path = cfg_util.CreatePathFromDict(old_cfg.project_paths["asset_top_path"],old_cfg.project_paths)
        self.asset_path = CC_Old.get_asset_top_path()
        node_list = createTreeNodes(self.asset_path)

        self.nodes = node_list.returnList()
        self.createWindow()

        # Set startup table model
        self.resize(800, 800)
        self.show()
        self.populateTree()
        # self.updateModel()

    def updateModel(self):
        self.tree.expandAll()
        self.tree_model.getAllNodes(cur_index=QtCore.QModelIndex())


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
        cur_node.generateThumbPath()
        self.tree_model.dataChanged.emit(cur_index,cur_index)
        # self.tree_model.getAllNodes(cur_index)
        self.tree_model.layoutChanged.emit()



    def populateTree(self):
        self.tree_model = TreeModel(self.nodes)
        self.tree.setModel(self.tree_model)

        # self.tree_model.layoutChanged.emit()

        # self.tree.collapseAll()


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
                    open_menu.addAction("Print Name")
                    menu.addAction("Copy To New Season")


                action = menu.exec_(event.globalPos())
                if not action == None:
                    if action.text() == "Print Name":
                        print(node.getName())
                    if action.text() == "Copy To New Season":
                        print("NOW TO COPY!: %s" % node.getName())
                        print(node.CopyAssetToNewConfig(CC))



        return QtWidgets.QWidget.eventFilter(self, source, event)


def SaveSettings(save_location, save_info):
    with open(save_location, 'w+') as saveFile:
        json.dump(obj=save_info, fp=saveFile,indent=4, sort_keys=True)
    saveFile.close()

def LoadSettings(save_location):
    if os.path.isfile(save_location):
        with open(save_location, 'r') as saveFile:
            loadedSettings = json.load(saveFile)
        if loadedSettings:
            return loadedSettings
    else:
        print("not a file")
    return None



class createTreeNodes(object):
    """Creates repository type objects"""

    def __init__(self, base_path):
        self.base_path = base_path
        self.__footage_dict = {}
        # self.pool = MyThreadPool()
        # self.pool.signals.finished.connect(self.updateNodes)
        # self.all_nodes = []
        self.node_list = self.find_type()


    def updateNodes(self,*args):
        print("Now its ready!: %s" % args)

    def returnList(self):
        # print("SO MANY NODES: %s" % len(self.all_nodes))
        return self.node_list

    def find_type(self):
        dirs = os.listdir(path=self.base_path)
        result = []

        # temp_pool = MyThreadPool()
        # temp_pool.signals.finished.connect(self.updateNodes)
        # list_of_type_workers = []
        for cur_type in dirs:
            if cur_type.startswith("."):
                continue
            type_node = Node(cur_type, self.base_path + "/" + cur_type, None,"asset_type")
            # type_worker = Worker(self.find_category,type_node,pool_key=cur_type)
            #type_worker.signals.result.connect(type_node.setChildren)
            # list_of_type_workers.append(type_worker)
            type_node.setChildren(self.find_category(type_node))
            result.append(type_node)
            # self.all_nodes.append(type_node)
        # self.pool.startBatch(list_of_type_workers,pool_key=cur_type)
        # temp_pool.startBatch(list_of_type_workers)
        return result

    def find_category(self, type_node,**kwargs):
        dirs = os.listdir(path=type_node.getUrl())
        result = []
        for cate_name in dirs:
            if cate_name.startswith("."):
                continue
            cate_node = Node(cate_name, type_node.getUrl() + "/" + cate_name, type_node,"asset_category")
            cate_node.setChildren(self.find_asset(cate_node))

            result.append(cate_node)
            # self.all_nodes.append(cate_node)
        return result

    def find_asset(self, cate_node):
        dirs = os.listdir(path=cate_node.getUrl())
        result = []
        for cur_asset in dirs:
            if cur_asset.startswith("."):
                continue
            asset_node = Node(cur_asset, cate_node.getUrl() + "/" + cur_asset, cate_node,"asset")
            result.append(asset_node)
            # self.all_nodes.append(asset_node)
        return result


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.resize(584, 662)
    mainWin.show()
    mainWin.updateModel()
sys.exit(app.exec_())

