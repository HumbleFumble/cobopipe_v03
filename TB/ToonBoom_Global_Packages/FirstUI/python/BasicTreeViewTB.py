# from PySide2 import QtWidgets, QtCore, QtGui
import shiboken6.Shiboken
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

import os
import json

import sys
# sys.path.append( r"C:\Program Files (x86)\Toon Boom Animation\Toon Boom Harmony 22 Premium\win64\bin\python-packages")
from ToonBoom import harmony

def tbScene():
	sess = harmony.session()  # Fetch the currently active session of Harmony
	project = sess.project  # The project that is already loaded.
	return project.scene()

def log(message):
	sess = harmony.session()
	sess.log(message)
	# messageLog.trace(message)

# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# BACKEND ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

class Node(object):
	def __init__(self, name=None, parent=None):
		self.__name = name
		self.__parent = parent
		self.__children = []

	def append(self, c_obj):
		self.__children.append(c_obj)
		self._row = 0
		# self._row = len(self.__children)

	def child(self, in_row):  # Treeview
		if in_row >= 0 and in_row < len(self.__children):
			return self.__children[in_row]

	def row(self):  # Treeview
		return self._row

	def getName(self):
		return self.__name

	def getParent(self):
		return self.__parent

	def setChildren(self, c_list=None):
		self.__children = c_list
		self._row = len(self.__children)

	def getChildren(self):
		return self.__children

# VIEWER -------------------------------------------------------------------------------------------------------------

class TreeModel(QAbstractItemModel):
	def __init__(self, nodes):
		QAbstractItemModel.__init__(self)
		self.root = Node("root", None)
		self.folder_picture =  os.path.dirname(os.path.dirname(os.path.realpath(__file__))).replace(os.sep,"/") + "/icon/folder.png" #CC.get_folder_icon_path()
		log(self.folder_picture)
		self.no_thumb_picture = "" #CC.get_no_thumb_icon_path()
		self.nodes = nodes
		self.root.setChildren(nodes)
		log(self.nodes)

	def insertRows(self, position, rows, index, parent):
		self.beginInsertRows(index, position, position + rows - 1)
		self.endInsertRows()
		return True

	def rowCount(self, index):
		if index.isValid():
			node = index.internalPointer()
			return len(node.getChildren())
		return len(self.root.getChildren())

	def index(self, row, column, cur_parent=None):
		if not cur_parent or not cur_parent.isValid():
			node_parent = self.root
		else:
			node_parent = cur_parent.internalPointer()

		if not QAbstractItemModel.hasIndex(self, row, column, cur_parent):
			return QModelIndex()

		child = node_parent.child(row)

		if child:
			return QAbstractItemModel.createIndex(self, row, column, child)
		else:
			return QModelIndex()

	def parent(self, index):
		if index.isValid():
			p = index.internalPointer().getParent()
			if p:
				return QAbstractItemModel.createIndex(self, p.row(), 0, p)
		return QModelIndex()

	def columnCount(self, index):
		return 1  # Only have 1 column

	def data(self, index, role):
		if not index.isValid():
			return None
		node = index.internalPointer()
		if role == Qt.DisplayRole:
			return node.getName()
		if role == Qt.DecorationRole:
			image_path = self.folder_picture
			pixmap = QPixmap(image_path)
			pixmap = pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
			# pixmap = self.__pixmap_util.convertPathToPixmap(cache_name=None, image_path=image_path, width=20,height=20, added_name="tree_folder")
			return pixmap
		return None

	def getNode(self, index):
		return index.internalPointer()

	def getNodes(self, list_of_index):
		result = []
		for index in list_of_index:
			node = self.getNode(index)
			if node:
				result.append(node)
		return result


# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# CONTROL-LAYER ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

class Repository:
	def __init__(self):
		super(Repository,self).__init__()
		self.nodes = []
		self.buildTestNodes()


	def buildTestNodes(self):
		node_dict = [{"name":"Top", "children":[
			{"name":"Child1", "children":[]},
			{"name":"Child2", "children":[]},
			{"name":"Child3", "children":[]}]
					  },
					 {"name": "Top2", "children": [
						 {"name": "Child1", "children": []},
						 {"name": "Child2", "children": []},
						 {"name": "Child3", "children": []}]
					  }
					 ]
		for top in node_dict:
			top_node = Node(top["name"], None)
			self.nodes.append(top_node)
			top_node_children = []
			for child in top["children"]:
				top_node_children.append(self.buildNode(child, parent=top_node))
			top_node.setChildren(top_node_children)


	def buildNode(self,node_dict,parent):
		temp_node = Node(node_dict["name"],parent)
		children = []
		for child in node_dict["children"]:
			children.append(self.buildNode(child,parent=temp_node))
		temp_node.setChildren(children)
		return temp_node


class FrontController(QObject):
	def __init__(self):
		super(FrontController, self).__init__()
		self.repository = Repository()

	def createTreeModel(self):
		# cur_nodes = sorted(cur_nodes,key=lambda x:x.getName())
		self.tree_model = TreeModel(nodes=self.repository.nodes)
		return self.tree_model

	def openDir(self,node):
		log("OPENING DIR FROM %s" % node)

	def saveSettings(self, save_location, save_content):
		with open(save_location, 'w+') as saveFile:
			json.dump(save_content, saveFile)
		saveFile.close()

	def loadSettings(self, load_file):
		if os.path.isfile(load_file):
			with open(load_file, 'r') as cur_file:
				return json.load(cur_file)
		else:
			return {}

# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# FRONTEND |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

class MainWindow(QWidget):

	def __init__(self, parent=None):
		self.__ctrl = FrontController()
		super(MainWindow, self).__init__(parent)
		self.setWindowTitle("Comp Contact Sheet")
		self.setWindowFlags(Qt.Window)

		QPixmapCache.setCacheLimit(200 * 10240)
		# self.setParent(pythonManager.appWidget())
		self.__create_window()
		self.populateTree()
		# self.createSearchCompleter()
		self.resize(1000, 800)
		self.show()


	def __create_window(self):
		self.layout_top = QVBoxLayout(self)

		self.menu_bar = QToolBar()

		self.name_label = QLabel("Name: ")
		self.name_edit_bar = QLineEdit()
		self.name_edit_bar.setMaximumWidth(150)
		self.menu_bar.addWidget(self.name_label)
		self.menu_bar.addWidget(self.name_edit_bar)
		self.menu_bar.addSeparator()

		self.tree = QTreeView(self)

		self.tree.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.tree.setHeaderHidden(True)
		self.tree.setExpandsOnDoubleClick(True)
		self.tree.setSelectionMode(QAbstractItemView.ExtendedSelection)

		self.tree.setAnimated(True)
		self.tree.setIndentation(20)
		self.tree.setSortingEnabled(True)
		# self.tree.sortByColumn(1,Qt.AscendingOrder)
		self.tree.setWindowTitle("Dir View")
		self.tree.installEventFilter(self)

		self.layout_top.addWidget(self.menu_bar)
		self.layout_top.addWidget(self.tree)


	def eventFilter(self, source, event):
		if event.type() == QEvent.ContextMenu:
			if (source is self.tree):
				menu = QMenu()
				nodes = []
				if source.selectedIndexes():
					for sel in source.selectedIndexes():
						si = self.tree_model.getNode(sel)
						if si:
							nodes.append(si)
				node = nodes[0]
				menu.addAction("Open Folder")
				menu.addSeparator()
				action = menu.exec_(event.globalPos())
				if not action == None:
					if action.text() == "Open Folder":
						self.__ctrl.openDir(node.getUrl())
		return QWidget.eventFilter(self, source, event)

	def TreeviewSelectionChanged(self):
		index = self.tree.currentIndex()
		if index:
			cur_node = self.tree_model.getNode(index)
		else:
			cur_node = self.tree_model.root
		if cur_node:
			log(cur_node.getName())
			# messageLog.trace(new_obj_test3.second_attr)
			# messageLog.trace(new_obj_test3.third_func.call())

	def populateTree(self):
		self.tree_model = self.__ctrl.createTreeModel()
		self.tree_model.sort(0, order=Qt.AscendingOrder)
		self.tree.setModel(self.tree_model)
		self.tree.selectionModel().selectionChanged.connect(self.TreeviewSelectionChanged)
		# self.tree.setModel(self.tree_model)

def run():
	from inspect import getmembers, isfunction,getmro

	sess = harmony.session()
	try:
		global my_ui
		my_ui = MainWindow()
		my_widgets = []
		# for w in QApplication.topLevelWidgets():
		# 	# sess.log(str(w.__class__))
		# 	# my_widgets.append(str(w.__class__.__name__))
		# 	if w.__class__.__name__ == "QMainWindow":
		# 		sess.log("QMainWindow")
		# 	# 	my_ui = MainWindow()
		# 	if w.__class__.__name__ == "Harmony":
		# 		sess.log("Found Harmony")
		# 		to_print = getmembers(w)
		# 		# to_print = w.children()
		# 		for p in to_print:
		# 			sess.log(str(p))
	except Exception as E:
		sess.log(E)
	finally:
		sess.log("No Error")

# if __name__ == '__main__':
# 	import sys
# 	if not QApplication.instance():
# 		app = QApplication(sys.argv)
# 	else:
# 		app = QApplication.instance()
# 	# addExtraEnv()
# 	mainWin = MainWindow()
# 	mainWin.show()
# 	app.exec_()
# 	#sys.exit()
# # sys.exit(app.exec_())
