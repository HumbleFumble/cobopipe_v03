# To run in maya, tried importing from Qt instead of loading directly from PyQt5

#path = python -m cProfile -s cumulative C:/Users/cg/PycharmProjects/bombay_base_production/AssetBrowser_Optimize.py

# import AssetBrowser_Optimize as AB
# reload(AB)
# AB.Run()


#TODO Test thumbnail creation!
#TODO Type and Category Folder creation is currently disabled.
#TODO Move and copy asset is also not working.
# TODO publish - add/remove from Delete set functionality currently not hooked up
# TODO Add work-ref to open/ref tab? Maybe add as option down the road? It gets super messy to pick the right ref if there is too many.
# TODO Low Prio: - Add user option? Dropdown or icon maybe?

# TODO User settings - remember the location of the last opening of the program. In a text file? Remember settings for tabs? Maybe. Make a reset button (delete user settings)?
# import cProfile
# pr = cProfile.Profile()
from Log.CoboLoggers import getLogger
logger = getLogger()
from maya import mel

import runtimeEnv as runtime
#import ClearImportedModules as CIM
#CIM.dropCachedImports("PublishAssets.PublishSetdress","PublishAssets.PublishSet","PublishAssets.PublishProp","PublishAssets.PublishChar","PublishAssets.PublishMaster", "AssetFunctions","Maya_Functions.asset_util_functions","Maya_Functions.publish_util_functions","Maya_Functions.set_util_functions","Maya_Functions.vray_util_functions","Maya_Functions.general_util_functions","getConfig","ClearImportedModules")
from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtWidgets import QInputDialog
from getConfig import getConfigClass
CC = getConfigClass()
# CC = getConfigClass(pick)

from PublishReport import PublishReport

try:
	logger.info("IN MAYA!")
	import maya.cmds as cmds
	in_maya = True
	import Maya_Functions.asset_util_functions as asset_util
except:
	logger.info("NOT IN MAYA!")
	in_maya = False

from functools import partial
# import json
import file_util
import AssetFunctions as AF
import os
import subprocess
import shutil
import Multiplicity.ThreadPool2
if in_maya:
	import MayaDockable
	import reloadModules

script_thread_pool = Multiplicity.ThreadPool2.ThreadPool()
script_thread_pool.setMaxThreads(keep=2)
# file_check_count = 0
# node_list = []
#
# def CountThreads(cur_value,cur_node=None): #Count backtracking
# 	global file_check_count
# 	global node_list
# 	file_check_count = file_check_count + cur_value
# 	if cur_node:
# 		node_list.append(cur_node)
# 	if file_check_count ==len(node_list):
# 		print("Found filepaths now looking for images!")
# 		for node in node_list:
# 			QtCore.QThreadPool.globalInstance().start(CollectAssetImageThread(target_node=node))
# 		node_list = []
# 		file_check_count = 0


def convertPathToPixmap(image_path, width, height,added_name="",overwrite=False):
	if image_path:
		key_value = "%s%s" % (image_path, added_name)
		# if os.path.exists(image_path):
		# 	key_value = "%s%s" % (image_path, added_name)
		# else:
		# 	image_path = CC.get_no_thumb_icon_path()
		# 	key_value = "no_thumb_icon"
	else:
		image_path = CC.get_no_thumb_icon_path()
		key_value = "no_thumb_icon"
	pixmap = QtGui.QPixmapCache.find(key_value)
	if pixmap and overwrite:  # Remove the key value from the cache so it will refresh with a new pixmap
		QtGui.QPixmapCache.remove(key_value)
		# try to remove the other 2 thumbnails of image:
		if QtGui.QPixmapCache.find("%s_quick_thumbnail" % image_path):
			QtGui.QPixmapCache.remove("%s_quick_thumbnail" % image_path)
		if QtGui.QPixmapCache.find("%s_thumbnail" % image_path):
			QtGui.QPixmapCache.remove("%s_thumbnail" % image_path)
		pixmap=None

	# If pixmap is not in Qt cache memory, create it.
	if not pixmap:

		pixmap = QtGui.QPixmap(image_path)
		# If image size is greater than 160x90: copy and resize image
		if pixmap.width() > 160:
			logger.info("A large thumbnail was found in use. Copying and resizing now:")

			img_folder, image_file = os.path.split(image_path)
			new_image_file = "Big_" + image_file
			new_image_path = os.path.join(img_folder, new_image_file)

			shutil.copy(image_path, new_image_path)

			pixmap = pixmap.scaled(160, 90, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
			pixmap.save(image_path)

			logger.info("    +'{0}' - copied to - {1}\n".format(image_file, new_image_file))

		pixmap = pixmap.scaled(width, height, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)

		QtGui.QPixmapCache.insert(key_value, pixmap)
		# print("Created %s" % key_value)
		# pixmap = QtGui.QPixmapCache.find(key_value)

	return QtGui.QPixmap(pixmap)

class MainWindow(QtWidgets.QWidget):
	def __init__(self, parent=None):
		super(MainWindow, self).__init__(parent)
		self.setObjectName("MainWindow")
		self.setWindowFlags(QtCore.Qt.Window)
		QtGui.QPixmapCache.setCacheLimit(100 * 10240)

		self.base_project = CC.get_base_path()
		self.base_path = CC.get_asset_top_path()
		self.template_folder = CC.get_template_path()

		self.publishReport = PublishReport()
		self.publishReportDataRetrieved = False

		if in_maya:
			# self.UF = UF.PublishFunctions()
			pass

		# FIND ASSET NODES:

		self.node_dict_path = "C:/Temp/%s/AssetBrowser_Nodes.json" % CC.project_name
		self.custom_nodes = []

		# self.all_node_list = self.LoadSettings(self.node_dict_path) #check and load it, if we have a saved json of our nodes
		self.all_node_list = None
		if not self.all_node_list:
			self.all_node_list = []
			self.populate() #Go through our asset folder and gather node info into a list

		self.MakeNodesFromDict(self.all_node_list,None)
		script_thread_pool.run()
		self.tree_model = CustomModel(self.custom_nodes, self)

		self.chosen_node = self.tree_model._root
		# self.chosen_node = None
		self.maya_node = None
		# type_node = [x for x in self.tree_model._root.GetChildren() if (x.GetName()=="Char")]
		# print(type_node[0].GetName())


		self.tableview_nodes = []
		self.table_model = TableModel(self.tableview_nodes,self)
		# self.all_node_list.clear()

		self.CreateWindow()

	def ExpandToNode(self,cur_node):
		name_list = [cur_node.parent().GetName(),cur_node.parent().parent().GetName()]
		selected = cur_node.GetName()
		self.iterateOverProxyModelAndExpandAllMatches(name_list,selected)

	# def iterateOverModelAndExpandAllMatches(self, name_list=[], selected=None, index=QtCore.QModelIndex()): ORIGNAL FOR USE WITHOUT PROXY MODEL
	# 	for row in range(self.tree_model.rowCount(index)):
	# 		if self.tree_model.index(row, 0, index).data() in name_list:
	# 			self.tree.expand(self.tree_model.index(row, 0, index))
	#
	# 		if self.tree_model.index(row, 0, index).data() == selected:
	# 			self.treeItemClicked(self.tree_model.index(row, 0, index))
	# 			self.tree.setCurrentIndex(self.tree_model.index(row, 0, index))
	#
	# 		if self.tree_model.rowCount(self.tree_model.index(row, 0, index)) > 0:
	# 			self.iterateOverModelAndExpandAllMatches(name_list, selected, self.tree_model.index(row, 0, index))
	#
	# 			# for child in range(self.tree_model.index(row,0,index).childCount):
	# 			#     self.tree_model.index(child,0,self.tree_model.index(row,0,index))
	# 			# iterateOverModelAndExpandAllMatches(name,child)

	def iterateOverProxyModelAndExpandAllMatches(self, name_list=[], selected=None, index=QtCore.QModelIndex()):
		for row in range(self.proxyModel.rowCount(index)):
			cur_index = self.proxyModel.index(row,0,index)
			# cur_index = self.tree_model.index(row, 0, index)
			if self.tree_model.getNode(self.proxyModel.mapToSource(cur_index)).GetName() in name_list:
				logger.info(cur_index.data())
				self.tree.expand(cur_index)

			if self.tree_model.getNode(self.proxyModel.mapToSource(cur_index)).GetName() == selected:
				# self.treeItemClicked(self.proxyModel.index(row, 0, index))
				self.tree.setCurrentIndex(self.proxyModel.index(row, 0, index))
			#
			if self.proxyModel.rowCount(cur_index) > 0:
				self.iterateOverProxyModelAndExpandAllMatches(name_list, selected, cur_index)
	def findNodeByName(self,):
		pass
	# @QtCore.pyqtSlot(str) # <--Not sure if this is needed
	def ProxyUpdate(self,text):
		my_pattern = QtCore.QRegularExpression()
		my_pattern.setPatternOptions(QtCore.QRegularExpression.CaseInsensitiveOption)
		my_pattern.setPattern(text)
		self.proxyModel.setFilterRegularExpression(my_pattern)


	def SearchEnter(self): #opens or closes the tree view after search
		if self.menu_search_bar.text() == "":
			self.tree.collapseAll()
		else:
			self.tree.expandAll()

	def TreeviewSelectionChanged(self):
		self.treeItemClicked(self.tree.currentIndex())

	def CreateWindow(self):
		# Layout
		self.setWindowTitle("TEMP AssetBrowser - Minimize me :)")
		# Gridlayout: When adding layouts,  arguments in AddLayout(x,x,x) goes : ( Layout , Row(vertical pos) , Column (horizontal pos), Rowspan, colspan)
		self.main_layout = QtWidgets.QGridLayout()
		self.main_layout.setContentsMargins(0, 0, 0, 0)
		self.main_layout.setSpacing(0)

		##---- SPLITTER TO MOVE SIZE OF TREEVIEW COMPARED TO TABS---###
		self.main_splitter = QtWidgets.QSplitter()
		self.main_splitter.setContentsMargins(5, 0, 5, 5)

		###--- Toolbar for some extra options----###
		self.main_menu_bar = QtWidgets.QToolBar()
		self.main_layout.addWidget(self.main_menu_bar, 0, 0)
		self.icons_on_off = QtWidgets.QCheckBox("Show Icons") #On off checkbox for having icons show. Save in settings.
		self.icons_on_off.setChecked(True)

		self.update_nodes_bttn = QtWidgets.QPushButton("UPDATE")
		self.update_nodes_bttn.clicked.connect(self.UpdateUI)

		self.menu_bttn_collapse = QtWidgets.QPushButton("Collapse All")
		self.menu_bttn_expand = QtWidgets.QPushButton("Expand All")

		#SEARCH BAR TESTING
		self.menu_search_bar = QtWidgets.QLineEdit()

		self.completer = QtWidgets.QCompleter(self.menu_search_bar)
		self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
		self.completer.setModelSorting(QtWidgets.QCompleter.CaseInsensitivelySortedModel)
		self.completer.setFilterMode(QtCore.Qt.MatchContains)
		self.completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
		self.completer_list = [x.GetName() for x in self.custom_nodes]
		self.completer.setModel(QtCore.QStringListModel(self.completer_list))
		self.menu_search_bar.setCompleter(self.completer)

		#TODO ADD SEARCH BAR FUNCTION! NICE TO HAVE :) Could sort in TableView instead of treeview?
		self.main_menu_bar.addWidget(self.update_nodes_bttn)
		self.main_menu_bar.addWidget(self.menu_bttn_collapse)
		self.main_menu_bar.addWidget(self.menu_bttn_expand)
		self.main_menu_bar.addSeparator()
		self.main_menu_bar.addWidget(self.icons_on_off)
		self.main_menu_bar.addWidget(QtWidgets.QLabel("Search: "))
		self.main_menu_bar.addWidget(self.menu_search_bar)
		#----------------------#

		# Widgets for layouts
		# ---- Tree ---------
		self.tree = QtWidgets.QTreeView()


		self.tree.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		self.tree.setHeaderHidden(True)
		self.tree.setExpandsOnDoubleClick(True)
		# self.tree.clicked.connect(self.treeItemClicked)

		# Give names and specify values
		self.tree.setObjectName("treeView")
		# -- Values --  (Mainly tree initation)

		#CONNECTING THE SEARCH BAR
		self.menu_search_bar.textChanged.connect(self.ProxyUpdate)
		self.menu_search_bar.returnPressed.connect(self.SearchEnter)



		# self.tree.setModel(self.tree_model) #TODO TAKEN OUT FOR PROXY TEST

		self.tree.setAnimated(True)
		self.tree.setIndentation(20)
		self.tree.setSortingEnabled(True)
		self.tree.setWindowTitle("Dir View")

		#THE RIGHT ORDER
		self.proxyModel = QtCore.QSortFilterProxyModel(self.tree)
		self.proxyModel.setSourceModel(self.tree_model)
		self.proxyModel.setRecursiveFilteringEnabled(True)
		self.proxyModel.setSortCaseSensitivity(QtCore.Qt.CaseInsensitive)
		self.proxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
		self.tree.setModel(self.proxyModel)
		self.proxyModel.sort(0, QtCore.Qt.AscendingOrder)
		#Connect buttons to tree
		self.menu_bttn_collapse.clicked.connect(self.tree.collapseAll)
		self.menu_bttn_expand.clicked.connect(self.tree.expandAll)

		self.tree.selectionModel().selectionChanged.connect(self.TreeviewSelectionChanged)

		# --------------Tabs-------------------------------------

		self.tabs = QtWidgets.QTabWidget()

		self.tabs.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		self.tab1 = QtWidgets.QWidget()
		self.tab1.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

		# self.tab2 = QtWidgets.QWidget()
		self.tab3 = QtWidgets.QWidget()
		self.tab4 = QtWidgets.QWidget()
		self.tab3.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		self.tab4.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		self.tabs.addTab(self.tab1, "Open")
		self.tabs.addTab(self.tab3, "Create")
		self.tabs.addTab(self.tab4, "Publish")
		# ---------Tabs-Layout----
		self.tab1.layout = QtWidgets.QGridLayout()
		# self.tab2.layout = QtWidgets.QGridLayout()
		self.tab3.layout = QtWidgets.QGridLayout()
		self.tab4.layout = QtWidgets.QGridLayout()


		# ------------------------------------------------ [ Tab 1 ] -----------------------------------------------

		# # -------------- Asset files list --------------
		self.tab1AssetFiles = QtWidgets.QListWidget()
		self.tab1AssetFiles.itemDoubleClicked.connect(self.OpenFileFromAssetlist)
		#
		# # -------------- Asset Ref list ----------------
		self.tab1AssetRefFiles = QtWidgets.QListWidget()
		self.tab1AssetRefFiles.itemDoubleClicked.connect(self.Tab1RefFile)
		#
		# # -------------- Asset Ref Button --------------
		self.tab1OpenRefButton = QtWidgets.QPushButton("Ref into file")
		self.tab1OpenRefButton.clicked.connect(self.Tab1RefFile)
		#
		# # -------------- Asset Files Button ------------
		self.tab1OpenButton = QtWidgets.QPushButton("Open file")
		self.tab1OpenButton.clicked.connect(self.OpenFileFromAssetlist)
		#
		# # -------------- Asset Thumbnail Holder---------
		self.tab1AssetThumbnailHolder = QtWidgets.QLabel()
		self.tab1AssetThumbnailHolder.setStyleSheet("*{qproperty-alignment:'AlignHCenter|AlignVCenter';}")

		# ------------- Quick Folder View -------------
		self.tab1FolderView = QtWidgets.QListView()
		self.tab1FolderView.setViewMode(QtWidgets.QListView.IconMode)
		self.tab1FolderView.setFlow(QtWidgets.QListView.LeftToRight)
		self.tab1FolderView.setResizeMode(QtWidgets.QListView.Adjust)
		self.tab1FolderView.setSpacing(20)
		self.tab1FolderView.setFrameStyle(1)
		self.tab1FolderView.clicked.connect(self.folderQuickviewClicked)

		# # -------------- Labels ------------------------

		self.tab1AssetFilesLabel = QtWidgets.QLabel("Files:")
		self.tab1ImageReferenceLabel = QtWidgets.QLabel("Image Reference: ")
		self.tab1ImageReferenceLabel.setStyleSheet("*{font:18pt;qproperty-alignment:'AlignHCenter|AlignVCenter';}")
		self.tab1RefsLabel = QtWidgets.QLabel("Reference Files:")
		#
		#
		# # -------------- Groups -------------------------
		#
		# # -- AssetFiles Area ---
		self.tab1AssetFilesArea = QtWidgets.QWidget()

		self.tab1AssetFilesArea.layout = QtWidgets.QVBoxLayout()

		self.tab1AssetFilesArea.layout.addWidget(self.tab1AssetFilesLabel)
		self.tab1AssetFilesArea.layout.addWidget(self.tab1AssetFiles)
		self.tab1AssetFilesArea.layout.addWidget(self.tab1OpenButton)
		self.tab1AssetFilesArea.setLayout(self.tab1AssetFilesArea.layout)
		# # -- RefFiles Area ---
		self.tab1RefFilesArea = QtWidgets.QWidget()

		self.tab1RefFilesArea.layout = QtWidgets.QVBoxLayout()
		self.tab1RefFilesArea.layout.addWidget(self.tab1RefsLabel)
		self.tab1RefFilesArea.layout.addWidget(self.tab1AssetRefFiles)
		self.tab1RefFilesArea.layout.addWidget(self.tab1OpenRefButton)
		self.tab1RefFilesArea.setLayout(self.tab1RefFilesArea.layout)
		#
		# # -------------- Add Widgets to tab1 layout ---
		self.tab1.layout.addWidget(self.tab1ImageReferenceLabel, 	1, 0, 1, 4)
		self.tab1.layout.addWidget(self.tab1AssetThumbnailHolder, 	2, 0, 1, 2)
		self.tab1.layout.addWidget(self.tab1AssetFilesArea, 		3, 0, 1, 1)
		self.tab1.layout.addWidget(self.tab1RefFilesArea, 			4, 0, 1, 1)

		self.tab1.layout.addWidget(self.tab1FolderView, 			0, 0, 6, 4)
		self.tab1.setLayout(self.tab1.layout)
		self.ShowQuickView(True)
		# ------------------------------------------------ [ Tab3 ] -----------------------------------------------------[ Tab3 ]

		# TODO : Add Folder creation, Asset Creation Function

		self.tab3PathLabel = QtWidgets.QLabel("Create location:")
		self.tab3Path = QtWidgets.QLabel("No path chosen")
		self.tab3PathHolder = QtWidgets.QGroupBox()
		self.tab3PathHolder.layout = QtWidgets.QHBoxLayout()
		self.tab3PathHolder.layout.addWidget(self.tab3Path)
		self.tab3PathHolder.setLayout(self.tab3PathHolder.layout)

		self.tab3SyncEnableRadioButton = QtWidgets.QRadioButton("Synchronize with selected folder")
		self.tab3SyncDisabledRadioButton = QtWidgets.QRadioButton("Free creation")
		self.tab3SyncEnableRadioButton.clicked.connect(partial(self.DisableFreeCreate,False))
		self.tab3SyncDisabledRadioButton.clicked.connect(partial(self.DisableFreeCreate,True))
		self.tab3SyncEnableRadioButton.setChecked(True)


		self.tab3TypeDropdown = QtWidgets.QComboBox()
		self.tab3CategoryDropdown = QtWidgets.QComboBox()

		self.tab3NameTextField = QtWidgets.QLineEdit()
		self.tab3NameTextField.setPlaceholderText("Enter name of new asset here")
		self.tab3NameTextField.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

		self.tab3CreateButton = QtWidgets.QPushButton("Create")

		self.tab3CreateButton.clicked.connect(self.Tab3CreateAsset)


		self.tab3SyncEnabledOrDisabledGroup = QtWidgets.QGroupBox()
		self.tab3SyncEnabledOrDisabledGroup.layout = QtWidgets.QHBoxLayout()

		self.tab3SyncEnabledOrDisabledGroup.setAlignment(QtCore.Qt.AlignCenter)

		self.tab3SyncEnabledOrDisabled = QtWidgets.QButtonGroup()
		self.tab3SyncEnabledOrDisabled.addButton(self.tab3SyncEnableRadioButton)
		self.tab3SyncEnabledOrDisabled.addButton(self.tab3SyncDisabledRadioButton)
		self.tab3SyncEnabledOrDisabled.setExclusive(True)


		self.tab3SyncEnabledOrDisabledGroup.layout.addWidget(self.tab3SyncEnableRadioButton)
		self.tab3SyncEnabledOrDisabledGroup.layout.addWidget(self.tab3SyncDisabledRadioButton)
		self.tab3SyncEnabledOrDisabledGroup.setLayout(self.tab3SyncEnabledOrDisabledGroup.layout)

		self.tab3TypeLabel = QtWidgets.QLabel("Type:")
		self.tab3CategoryLabel = QtWidgets.QLabel("Category:")
		self.tab3NameLabel = QtWidgets.QLabel("File Name:")

		self.tab3AddTypeFolderButton = QtWidgets.QPushButton("+")
		self.tab3AddCategoryFolderButton = QtWidgets.QPushButton("+")
		self.tab3AddTypeFolderButton.setFixedSize(22, 22)
		self.tab3AddCategoryFolderButton.setFixedSize(22, 22)

		self.tab3AddTypeFolderButton.clicked.connect(self.CreateNewTypeFolder)
		self.tab3AddCategoryFolderButton.clicked.connect(self.CreateNewCategoryFolder)

		self.tab3OpenAfterCheckbox = QtWidgets.QCheckBox("Open file in Maya after creation")
		self.tab3OpenAfterRadioButtonHolder = QtWidgets.QGroupBox()
		self.tab3OpenAfterRadioButtonHolder.layout = QtWidgets.QHBoxLayout()
		self.tab3OpenAfterRadioButtonHolder.layout.addWidget(self.tab3OpenAfterCheckbox)
		self.tab3OpenAfterRadioButtonHolder.setLayout(self.tab3OpenAfterRadioButtonHolder.layout)
		self.tab3OpenAfterCheckbox.setChecked(True)

		self.tab3TypeBox = QtWidgets.QGroupBox()
		self.tab3TypeBox.layout = QtWidgets.QHBoxLayout()
		self.tab3TypeBox.layout.addWidget(self.tab3AddTypeFolderButton)
		self.tab3TypeBox.layout.addWidget(self.tab3TypeDropdown)
		self.tab3TypeDropdown.currentTextChanged.connect(self.UpdateCategoryDropdownTab3)
		self.tab3TypeBox.setLayout(self.tab3TypeBox.layout)



		self.tab3CategoryBox = QtWidgets.QGroupBox()
		self.tab3CategoryBox.layout = QtWidgets.QHBoxLayout()
		self.tab3CategoryBox.layout.addWidget(self.tab3AddCategoryFolderButton)
		self.tab3CategoryBox.layout.addWidget(self.tab3CategoryDropdown)
		self.tab3CategoryBox.setLayout(self.tab3CategoryBox.layout)

		self.tab3.layout.addWidget(self.tab3SyncEnabledOrDisabledGroup, 1, 0, 1, 1)
		self.tab3.layout.addWidget(self.tab3PathLabel, 					2, 0, 1, 1)
		self.tab3.layout.addWidget(self.tab3PathHolder, 				3, 0, 1, 1)
		self.tab3.layout.addWidget(self.tab3TypeLabel, 					4, 0, 1, 1)
		self.tab3.layout.addWidget(self.tab3TypeBox, 					5, 0, 1, 1)
		self.tab3.layout.addWidget(self.tab3CategoryLabel, 				6, 0, 1, 1)
		self.tab3.layout.addWidget(self.tab3CategoryBox, 				7, 0, 1, 1)
		self.tab3.layout.addWidget(self.tab3NameLabel, 					8, 0, 1, 1)
		self.tab3.layout.addWidget(self.tab3NameTextField, 				9, 0, 1, 1)
		self.tab3.layout.addWidget(self.tab3OpenAfterRadioButtonHolder, 10, 0, 1, 1)
		self.tab3.layout.addWidget(self.tab3CreateButton, 				11, 0, 1, 1)

		self.tab3.layout.setAlignment(QtCore.Qt.AlignCenter)

		self.tab3.setLayout(self.tab3.layout)
		self.DisableFreeCreate(False) #locking up the Dropdowns as default
		# ----------------------------------------------- [ Tab4 ] --------------------------------------------------- [ Tab4]

		# --------------------- Labels ----------------------------
		self.tab4AssetNameLabel = QtWidgets.QLabel("")

		self.tab4FileToPublishLabel = QtWidgets.QLabel("File to publish:")
		self.tab4AfterPublishLabel = QtWidgets.QLabel("After publishing:")

		self.tab4PublishLabels = QtWidgets.QWidget()
		self.tab4PublishLabels.layout = QtWidgets.QHBoxLayout()
		self.tab4PublishLabels.layout.addWidget(self.tab4FileToPublishLabel)
		self.tab4PublishLabels.layout.addWidget(self.tab4AfterPublishLabel)
		self.tab4PublishLabels.setLayout(self.tab4PublishLabels.layout)


		# --------------------- Asset Thumbnail Holder ----------------------
		self.tab4AssetThumbnailHolder = QtWidgets.QLabel()

		# --------------------- Asset Thumbnail Change button ---------------
		self.tab4AssetThumbnailChangeButton = QtWidgets.QPushButton("Change Thumbnail To Current Maya Screen")
		self.tab4AssetThumbnailChangeButton.clicked.connect(self.tab4ChangeThumbnail) #TODO CHeck if works

		# ------------------- Asset Choice to publish (Can be more than one file) ----
		self.tab4FileToPublishChoice = QtWidgets.QGroupBox()
		self.tab4FileToPublishChoice_layout = QtWidgets.QVBoxLayout()
		#TODO Make this dynamic after asset type

		self.tab4FilesToPublish = {} #TODO place checkboxes in here dynamically on change of asset
		# self.tab4FileToPublish_Model = QtWidgets.QCheckBox("Model")
		# self.tab4FileToPublish_Rig = QtWidgets.QCheckBox("Rig")
		# self.tab4FileToPublish_Shading = QtWidgets.QCheckBox("Shading")
		#
		# self.tab4FileToPublishChoice.layout.addWidget(self.tab4FileToPublish_Model)
		# self.tab4FileToPublishChoice.layout.addWidget(self.tab4FileToPublish_Rig)
		# self.tab4FileToPublishChoice.layout.addWidget(self.tab4FileToPublish_Shading)
		self.tab4FileToPublishChoice.setLayout(self.tab4FileToPublishChoice_layout)

		# ------------------- Selected / Current choice box -------------------
		self.tab4SelectedOrCurrentBox = QtWidgets.QGroupBox()
		self.tab4SelectedOrCurrentBox.layout = QtWidgets.QHBoxLayout()

		self.tab4CurrentRadioButton = QtWidgets.QRadioButton("Currently Open Maya File")
		self.tab4SelectedRadioButton = QtWidgets.QRadioButton("Selected File")
		self.tab4RadioGroup = QtWidgets.QButtonGroup()
		self.tab4RadioGroup.setExclusive(True)
		self.tab4RadioGroup.addButton(self.tab4CurrentRadioButton,1)
		self.tab4RadioGroup.addButton(self.tab4SelectedRadioButton,2)

		self.tab4SelectedOrCurrentBox.layout.addWidget(self.tab4CurrentRadioButton)
		self.tab4SelectedOrCurrentBox.layout.addWidget(self.tab4SelectedRadioButton)
		self.tab4SelectedOrCurrentBox.setLayout(self.tab4SelectedOrCurrentBox.layout)

		self.tab4CurrentRadioButton.clicked.connect(self.RefreshTab4)
		self.tab4SelectedRadioButton.clicked.connect(self.RefreshTab4)


		# self.tab4CurrentRadioButton.clicked.connect(self.InitPublishTab)

		# ------------------- After Publish Selection ---------------------
		self.tab4AfterPublishSelection = QtWidgets.QGroupBox()
		self.tab4AfterPublishSelection.layout = QtWidgets.QVBoxLayout()

		self.tab4OpenFileAfterRadioButton = QtWidgets.QRadioButton("Reopen the file")
		self.tab4OpenNextStepAfterRadioButton = QtWidgets.QRadioButton("Open next step")
		self.tab4OpenRefAfterRadioButton = QtWidgets.QRadioButton("ref into empty scene")
		self.tab4DoNothingAfterRadioButton = QtWidgets.QRadioButton("Do nothing")

		self.tab4AfterPublishButtonsGroup = QtWidgets.QButtonGroup()
		self.tab4AfterPublishButtonsGroup.addButton(self.tab4OpenNextStepAfterRadioButton, 0)
		self.tab4AfterPublishButtonsGroup.addButton(self.tab4OpenFileAfterRadioButton, 1)
		self.tab4AfterPublishButtonsGroup.addButton(self.tab4OpenRefAfterRadioButton, 2)
		self.tab4AfterPublishButtonsGroup.addButton(self.tab4DoNothingAfterRadioButton, 3)


		self.tab4AfterPublishSelection.layout.addWidget(self.tab4OpenNextStepAfterRadioButton)
		self.tab4AfterPublishSelection.layout.addWidget(self.tab4OpenFileAfterRadioButton)
		self.tab4AfterPublishSelection.layout.addWidget(self.tab4OpenRefAfterRadioButton)
		self.tab4AfterPublishSelection.layout.addWidget(self.tab4DoNothingAfterRadioButton)
		self.tab4AfterPublishSelection.setLayout(self.tab4AfterPublishSelection.layout)

		self.tab4PublishChoiceAndAfterArea = QtWidgets.QWidget()
		self.tab4PublishChoiceAndAfterArea.layout = QtWidgets.QHBoxLayout()

		self.tab4PublishChoiceAndAfterArea.layout.addWidget(self.tab4FileToPublishChoice)
		self.tab4PublishChoiceAndAfterArea.layout.addWidget(self.tab4AfterPublishSelection)
		self.tab4PublishChoiceAndAfterArea.setLayout(self.tab4PublishChoiceAndAfterArea.layout)

		# --------------------- Extra Features ----------------------------------------------
		# ---- Holder for all features
		self.tab4PublishActions = QtWidgets.QGroupBox()
		self.tab4PublishActions.layout = QtWidgets.QGridLayout()
		# -----------
		self.tab4GeofixButton = QtWidgets.QPushButton("Fix Geo-Group")
		self.tab4AddToSetButton = QtWidgets.QPushButton("Add to Set")
		self.tab4RemoveFromSetButton = QtWidgets.QPushButton("Remove from Set")
		self.tab4RefBackUpButton = QtWidgets.QPushButton("Make Ref BackUp")
		# self.tab4RefBackUpButton.clicked.connect(self.SaveCopyOfReference)


		# self.tab4GeofixButton.clicked.connect(self.GeoFix)
		# self.tab4AddToSetButton.clicked.connect(self.AddToSet)
		# self.tab4RemoveFromSetButton.clicked.connect(self.RemoveFromSet)

		self.tab4PublishActions.layout.addWidget(self.tab4GeofixButton, 1, 1, 1, 1)
		self.tab4PublishActions.layout.addWidget(self.tab4AddToSetButton, 1, 2, 1, 1)
		self.tab4PublishActions.layout.addWidget(self.tab4RemoveFromSetButton, 2, 2, 1, 1)
		self.tab4PublishActions.layout.addWidget(self.tab4RefBackUpButton, 2, 1, 1, 1)
		# self.tab4RefBackUpButton.setEnabled(False)
		self.tab4PublishActions.setLayout(self.tab4PublishActions.layout)

		# self.tab4ProxyCheckbox = QtWidgets.QCheckBox("Create V-ray Proxy")
		# self.tab4ProxyCheckbox.setEnabled(False)
		# self.tab4ProxyCheckboxHolder = QtWidgets.QGroupBox()
		# self.tab4ProxyCheckboxHolder.layout = QtWidgets.QHBoxLayout()
		# self.tab4ProxyCheckboxHolder.layout.addWidget(self.tab4ProxyCheckbox)
		# self.tab4ProxyCheckboxHolder.setLayout(self.tab4ProxyCheckboxHolder.layout)

		# -------------------- Big Fat Publish Button ---------------------
		self.tab4PublishButton = QtWidgets.QPushButton("Publish")
		# self.tab4PublishButton.setFixedSize(300,60)

		self.tab4PublishButton.clicked.connect(self.Publish)

		# --------------------- Add widgets to tab4 layout ---------------------
		self.tab4.layout.addWidget(self.tab4SelectedOrCurrentBox, 1, 1, 1, 2)
		self.tab4.layout.addWidget(self.tab4AssetNameLabel, 2, 1, 1, 2)
		self.tab4.layout.addWidget(self.tab4AssetThumbnailHolder, 3, 1, 1, 2)
		self.tab4.layout.addWidget(self.tab4AssetThumbnailChangeButton, 4, 1, 1, 2)
		self.tab4.layout.addWidget(self.tab4PublishActions, 5, 1, 1, 2)
		self.tab4.layout.addWidget(self.tab4PublishLabels, 6, 1, 1, 2)
		self.tab4.layout.addWidget(self.tab4PublishChoiceAndAfterArea, 7, 1, 1, 2)
		# self.tab4.layout.addWidget(self.tab4ProxyCheckboxHolder, 8, 1, 1, 2)
		self.tab4.layout.addWidget(self.tab4PublishButton, 9, 1, 1, 2)

		self.tab4.setLayout(self.tab4.layout)
		self.tab4SelectedRadioButton.setChecked(True)

		self.tab4FileToPublishChoice.setObjectName("Radiobox")
		self.tab4AfterPublishSelection.setObjectName("Radiobox")

		# --------------------------------------------- [ Feature Disabling/Change if not in Maya] ---------------------
		# ---- PUBLISH ----
		if not in_maya: #TODO Make publish by mayapy!
			# Gray out "Current File" option and Autopick other option
			# self.tab4CurrentRadioButton.setEnabled(False)
			self.tab4SelectedRadioButton.setChecked(True)
			# # Disable ability to change thumbnail based on current open Maya file
			# self.tab4AssetThumbnailChangeButton.setEnabled(False)
			# self.tab4DoNothingAfterRadioButton.setChecked(True)
			# self.tab1RefFilesArea.setEnabled(False)
			self.tab4.setEnabled(False)

		else:
			# Assume that the published file should be the currently open one
			self.tab4CurrentRadioButton.setChecked(True)
			self.tab4OpenNextStepAfterRadioButton.setChecked(True)

		# ---------------------------------------------- [ Main Layout ] -----------------------------------------------

		# -- Popup box --

		self.generalMessagePopup = QtWidgets.QMessageBox()
		self.generalMessagePopup.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

		# -----
		self.tabs.tabBarClicked.connect(self.TabsClicked)
		# Give names and specify values
		# self.tab4PublishButton.setObjectName("publish")

		self.tab1FolderView.setObjectName("tab1FolderView")
		# ----------------------------Add Widgets to Layouts--------------------

		self.main_splitter.addWidget(self.tree)
		self.main_splitter.addWidget(self.tabs)
		# self.tree_layout.addWidget(self.tree)
		# self.create_layout.addWidget(self.tabs)

		# Add layouts to main layout

		self.main_layout.addWidget(self.main_splitter,1,0)
		# Set layout
		self.setLayout(self.main_layout)
		self.UpdateDropdownTab3()
		# Add Event-listeners
		self.tree.installEventFilter(self)
		self.tab1FolderView.installEventFilter(self)


	# --- When item in Tree is clicked -----
	def Test(self): #TODO DELETE LATER
		logger.debug("somthing")

	# def TreeSelectionChanged(self, cur_index, previous_index):
	# 	self.treeItemClicked(self.tree.currentIndex())
	# 	# self.tree.selectedIndexes()
	# 	# self.treeItemClicked(cur_index)

	def treeItemClicked(self, index=None):
		if index:
			# cur_node = self.proxyModel.mapToSource(index).internalPointer()
			cur_node = self.tree_model.getNode(self.proxyModel.mapToSource(index))
		else:
			cur_node = self.tree_model._root
		if cur_node:
			# print(cur_node)
			# self.tree_model.getNode((self.proxyModel.mapToSource(index)))
			# cur_node = self.tree_model.getNode(index)
			# print("Type: %s -> Name: %s"% (cur_node.GetAssetType(),cur_node.GetName()))
			self.chosen_node=cur_node
			self.RefreshTab1()
			if self.tabs.currentIndex() == 1:
				self.RefreshTab3()
			if self.tabs.currentIndex()==2:
				self.RefreshTab4()

	def TabsClicked(self, index):
		if index == 1:
			self.RefreshTab3()
		elif index == 2:  # Publish
			self.RefreshTab4()

	def tab4ChangeThumbnail(self):
		if in_maya:
			# IMPORT SAVE VIEWPORT FUNCTIONALITY
			import maya.mel as mel
			import maya.OpenMaya as api
			import maya.OpenMayaUI as apiUI

			if self.tab4CurrentRadioButton.isChecked():
				cur_node = self.maya_node
			else:
				cur_node = self.chosen_node
			choice = self.ThumbnailPopup()
			if not choice == "cancel":
				thumb_path = CC.get_asset_thumbnail_path(**cur_node.GetAssetInfo())
				thumb_folder, thumb_file = os.path.split(thumb_path)
				print(thumb_folder)
				if not os.path.exists(thumb_folder):
					os.makedirs(thumb_folder)
				if choice == "Render": #Save image in vray frame buffer!
					noext = os.path.splitext(thumb_path)[0]
					self.SetRenderer(noext)
				
				elif choice == "Viewport": #Save image from maya viewport
					# mel.eval('vray hideVFB')
					view = apiUI.M3dView.active3dView()
					image = api.MImage()
					view.readColorBuffer(image, True)
					image.writeToFile(thumb_path, "png")

				#Update thumbnail of asset:
				c_pix = convertPathToPixmap(thumb_path,300,300,added_name="_Big",overwrite=True)
				self.tab4AssetThumbnailHolder.setPixmap(c_pix)

	def getRenderCamera(self):
		current_focus = cmds.getPanel(withFocus=True)
		try:
			cam = cmds.modelPanel(current_focus, q=True, camera=True)
			# cmds.modelPanel(self.focus_view, edit=True, camera="%s_Cam" % _sh)
			cam_shape = cmds.listRelatives(cam,type="camera")
			if cam_shape:
				return cam_shape[0]
		except:
			cmds.warning("Please be sure that the right panel has focus")
			return False


	def SetRenderer(self, render_dir):
		# Get current render width and height
		current_width = cmds.getAttr('defaultResolution.width')
		current_height = cmds.getAttr('defaultResolution.height')

		# Set resolution parameters
		width = 960
		height = 540

		# Set current renderer to the project renderer
		if cmds.getAttr("defaultRenderGlobals.currentRenderer") != CC.project_settings['maya_render']:
			cmds.setAttr("defaultRenderGlobals.currentRenderer", CC.project_settings['maya_render'], type="string")
		if CC.project_settings['maya_render'] == "vray":
			mel.eval('vray vfbControl -saveimage "%s"' % render_dir)
		if CC.project_settings['maya_render'] == "arnold":
			attr_list = {"defaultArnoldDriver.aiTranslator":None,"defaultRenderGlobals.imageFilePrefix":None,"defaultResolution.width":None
				,"defaultResolution.height":None,"defaultRenderGlobals.animation":None}
			for a in attr_list.keys():
				attr_list[a] = cmds.getAttr(a)
			#TODO Set frame to be single
			cmds.setAttr("defaultArnoldDriver.aiTranslator", "png", type="string")
			cmds.setAttr('defaultRenderGlobals.imageFilePrefix', render_dir, type="string")
			mel.eval('setMayaSoftwareFrameExt(1,0)') #set to single picture
			# cmds.setAttr("defaultRenderGlobals.animation", 0)
			# Set resolution
			cmds.setAttr("defaultResolution.width", width)
			cmds.setAttr("defaultResolution.height", height)
			render_cam = self.getRenderCamera()
			if render_cam:
				# cmds.setAttr("defaultArnoldDriver.colorManagement", 1)

				cmds.arnoldRender(cam=render_cam, width=width, height=height, seq=None)

				old_name = cmds.getAttr('defaultRenderGlobals.imageFilePrefix') + '_1' + ".png"
				new_name = render_dir + ".png"
				if os.path.exists(new_name):
					os.remove(new_name)
				os.rename(old_name, new_name)
				# cmds.setAttr("defaultArnoldDriver.colorManagement", 2)
			# Set resolution back to what it was before
			# cmds.setAttr("defaultArnoldDriver.colorManagement", 2)
			for k in attr_list.keys():
				a_type = cmds.attributeQuery(k.split(".")[1],node=k.split(".")[0],attributeType=True)
				cmds.setAttr(k, attr_list[k],type=a_type)
			cmds.setAttr("defaultResolution.width", current_width)
			cmds.setAttr("defaultResolution.height", current_height)

		# Set image name/location empty
		cmds.setAttr('defaultRenderGlobals.imageFilePrefix', '', type="string")
  
  

    	
 
	def RefreshTab1(self):
		if self.chosen_node.GetNodeType() == "asset":  # Changed to look for asset type instead of if it had children
			self.ShowQuickView(False)

		# 	# Set display image ---
			if self.chosen_node.GetImage():
				currentThumbnail = convertPathToPixmap(self.chosen_node.GetImage(), 300, 300)
			else:
				currentThumbnail = convertPathToPixmap(CC.get_no_thumb_icon_path(), 300, 300)
			self.tab1AssetThumbnailHolder.setPixmap(currentThumbnail)
			self.tab1ImageReferenceLabel.setText(self.chosen_node.GetName())

			self.tab1AssetFiles.clear()
			self.tab1AssetRefFiles.clear()

			self.tab1AssetFiles.addItems(list([item[1] for item in self.chosen_node.GetMayaWorkFiles()]))
			self.tab1AssetRefFiles.addItems(list([item[1] for item in self.chosen_node.GetMayaRefFiles()]))
		else:
			self.RefreshQuickView(self.chosen_node)

	def RefreshTab3(self):
		if self.tab3SyncEnableRadioButton.isChecked():
			self.UpdateDropdownTab3()
		path_to_display = "/%s/%s/%s" %(self.tab3TypeDropdown.currentText(),self.tab3CategoryDropdown.currentText(),self.tab3NameTextField.text())
		self.tab3Path.setText(path_to_display)

	# def RefreshPopup(self):
	# 	if self.popupSyncEnableRadioButton.isChecked():
	# 		self.UpdateDropdownPopup()
	# 	path_to_display = "/%s/%s/%s" %(self.popupTypeDropdown.currentText(),self.popupCategoryDropdown.currentText(),self.popupNameTextField.text())
	# 	print(path_to_display)
	# 	self.popupPath.setText(path_to_display)

	def RefreshTab4(self):  # initiate the publish window
			if in_maya:
				if self.tab4CurrentRadioButton.isChecked():
					# if not self.maya_node:
					self.maya_node = None
					asset_info = asset_util.GetAssetInfoFromFile()
					if asset_info:

						for x in self.custom_nodes:
							if x.GetName()==asset_info["asset_name"]:
								if x.GetAssetType() == asset_info["asset_type"] and x.GetAssetCategory()==asset_info["asset_category"]:
									self.maya_node = x
									x.asset_step = asset_info["asset_step"]
					else:
						# print("Can't publish from this file type!")
						self.tab4AssetNameLabel.setText("Not a known asset!")
						self.tab4AssetThumbnailHolder.setPixmap(
							convertPathToPixmap(CC.get_no_thumb_icon_path(),300, 300))
						self.tab4PublishButton.setEnabled(False)
					if self.maya_node:
						self.tab4AssetNameLabel.setText(self.maya_node.GetName())
						self.tab4AssetThumbnailHolder.setPixmap(convertPathToPixmap(self.maya_node.GetImage(),300,300,"_Big"))
						self.UpdateRefFiles(self.maya_node)
						self.tab4PublishButton.setEnabled(True)

		# ----------------------Publish Tab Selected Enabled-----------------------------------------------------
				if self.tab4SelectedRadioButton.isChecked():
					# cur_node = self.tree_model.getNode(index)
					if self.chosen_node and self.chosen_node.GetNodeType()=="asset":
						self.tab4AssetNameLabel.setText(self.chosen_node.GetName())
						self.tab4AssetThumbnailHolder.setPixmap(convertPathToPixmap(self.chosen_node.GetImage(),300,300,"_Big"))
						self.tab4PublishButton.setEnabled(True)
					else:
						self.UpdateRefFiles(self.chosen_node)
						self.tab4AssetNameLabel.setText("Pick Asset to publish")
						self.tab4AssetThumbnailHolder.setPixmap(convertPathToPixmap(CC.get_no_thumb_icon_path(), 300, 300))
						self.tab4PublishButton.setEnabled(False)
					self.UpdateRefFiles(self.chosen_node)
			# else:
			# 	self.UpdatesRefFiles(self.chosen_node)

	def UpdateRefFiles(self, cur_node):
		self.tab4FilesToPublish = []
		for x in reversed(range(self.tab4FileToPublishChoice_layout.count())):
			self.tab4FileToPublishChoice_layout.itemAt(x).widget().deleteLater()
		if cur_node.GetNodeType()=="asset":
			cur_step = cur_node.GetAssetStep()
			my_steps = CC.ref_order[cur_node.GetAssetType()]

			check_from_cur_step = False #Check boxes from the open file. So if rig is open, don't check model publish
			for step in my_steps:
				temp_check = QtWidgets.QCheckBox("%s" % step)
				if cur_step:
					if step == cur_step or check_from_cur_step:
						temp_check.setChecked(True)
						check_from_cur_step = True
				else:
					temp_check.setChecked(True)
				self.tab4FileToPublishChoice_layout.addWidget(temp_check)
				self.tab4FilesToPublish.append(temp_check)

	def Publish(self, this_node=None):

		# self.publish_step_types = ["Model", "Rig", "Shading"]
		self.publish_step_types = [x.text() for x in self.tab4FilesToPublish if x.isChecked()]
		print(self.tab4FilesToPublish)
		# from PublishAssets import PublishMaster
		import PublishAssets.PublishMaster
		if self.tab4CurrentRadioButton.isChecked():
			asset_info = self.maya_node.GetAssetInfo()
			cmds.file(save=True) #Try to save file before publish
		if self.tab4SelectedRadioButton.isChecked():
			asset_info = self.chosen_node.GetAssetInfo()
			if self.publish_step_types:
				asset_info["asset_step"] = self.publish_step_types[0]
				self.OpenMayaFile("%s" % CC.get_asset_work_file(**asset_info),True)
		for cur_step in self.publish_step_types:
			# self.UF.OpenFile("%s.ma" % cfg_util.CreatePathFromDict(cfg.project_paths["asset_work_path"], asset_info), True)
			asset_info["asset_step"] = cur_step
			PubClass = PublishAssets.PublishMaster.ReadyPublish(asset_info=asset_info)
			pub_success = PubClass.StartPublish()
			if not pub_success:
				popup = QtWidgets.QMessageBox()
				popup.setIcon(QtWidgets.QMessageBox.Information)
				popup.setText("Warning: Publish Failed")
				popup.setInformativeText("The publish of %s->%s failed. Check log for more info" % (asset_info["asset_name"],asset_info["asset_step"]))
				popup.setWindowTitle("Warning")
				popup.setStandardButtons(QtWidgets.QMessageBox.Ok)
				popup.exec_()

		####### After publishing is done ####################
		next_step = self.tab4AfterPublishButtonsGroup.buttons()[self.tab4AfterPublishButtonsGroup.checkedId()].text()
		if next_step == "Reopen the file":
			self.OpenMayaFile("%s" % CC.get_asset_work_file(**asset_info),False)
		elif next_step=="ref into empty scene":
			self.OpenMayaFile(None,False)
			# print(asset_info)
			for cur_ref in CC.ref_steps[asset_info["asset_type"]][asset_info["asset_step"]]:
				asset_info["asset_output"] = cur_ref
				get_ref_file_function = getattr(CC, "get_{asset_output}".format(asset_output=asset_info["asset_output"]))
				ref_path = get_ref_file_function(**asset_info)
				# ref_path = cfg_util.CreatePathFromDict(cfg.ref_paths[cur_ref],asset_info)
				# print(ref_path)
				self.RefFileIntoMaya("%s_%s" % (asset_info["asset_name"],cur_ref),ref_path)
		elif next_step == "Open next step":
			all_steps = [x.text() for x in self.tab4FilesToPublish]
			place = all_steps.index(asset_info["asset_step"])
			if not place==len(all_steps)-1:
				asset_info["asset_step"] = all_steps[place+1]
			self.OpenMayaFile("%s"% CC.get_asset_work_file(**asset_info),False)
		if next_step=="Do nothing":
			pass

	def PublishSave(self, cur_path):
		if self.in_maya and self.tab4CurrentRadioButton.isChecked():
			if not cmds.file(q=True, sn=True) == "":
				cmds.file(save=True)
			self.OpenMayaFile(cur_path, False)
		elif self.in_maya and self.tab4SelectedRadioButton.isChecked():
			if len(self.next_steps) > 1:
				self.OpenMayaFile(cur_path, False)
			else:
				self.OpenMayaFile(cur_path, True)
		else:
			self.OpenMayaFile(cur_path, False)

	# A right-click menu for all assets. Runs the openfile function based on selection. Ie: Clicking shading opens the shader-file
	def eventFilter(self, source, event):
		if event ==None:
			return QtWidgets.QWidget.eventFilter(self, source, event)
		if (event.type() == QtCore.QEvent.ContextMenu and source is self.tree or event.type() == QtCore.QEvent.ContextMenu and source is self.tab1FolderView):
			menu = QtWidgets.QMenu()
			if source == self.tree:
				if source.selectedIndexes():
					# node = self.tree_model.getNode(source.selectedIndexes()[0]) None proxy version
					node = self.tree_model.getNode(self.proxyModel.mapToSource(source.currentIndex()))

				else:
					return super(MainWindow, self).eventFilter(source, event)
			if source == self.tab1FolderView:
				# Does not register click
				if self.tab1FolderView.selectedIndexes():
					node = self.table_model.getNode(self.tab1FolderView.selectedIndexes()[0])
				else:
					return super(MainWindow, self).eventFilter(source, event)
				# node = self.table_model.getNode(source)

			menu.addAction("Show in Directory")
			menu.addSeparator()
			ref_file_actions = {}
			work_file_actions = {}

			if node.GetNodeType()=="asset":
				work_file = node.GetMayaWorkFiles()
				for c_file in work_file:
					cur_action = "Open %s" % c_file[1]
					menu.addAction(cur_action)
					work_file_actions[cur_action] = "%s/%s" % (c_file[0],c_file[1])

				if work_file and in_maya:
					ref_files = node.GetMayaRefFiles()
					menu.addSeparator()
					if node.IsAssetAModule() and ref_files: #If rig module make special menu
						cur_action = "Ref Module"
						menu.addAction(cur_action)
					else:
						for ref in ref_files:
							cur_action = "Ref %s" % ref[1]
							menu.addAction(cur_action)
							ref_file_actions[cur_action] = "%s/%s" % (ref[0], ref[1])
					menu.addSeparator()
					# menu.addAction("Replace Selected Ref")
					# menu.addSeparator()
					# menu.addAction("Run Update")
					# menu.addAction("Rename")


			if node.GetNodeType() in ["category","asset_type"] and in_maya:
				menu.addAction("Publish All Children")
			menu.addAction("Show Asset Info")
			menu.addAction("Show Dependent Shots")
			menu.addSeparator()
			menu.addAction("Duplicate")

			# if node.GetNodeType() == "category": #Not needed anymore
			# 	menu.addAction("Collect Thumbnails")
			action = menu.exec_(event.globalPos())
			if not action == None:

				if action.text() in work_file_actions.keys():
					self.OpenMayaFile(work_file_actions[action.text()])

				if action.text() in ref_file_actions.keys():
					self.RefFileIntoMaya(node.GetName(),file_path=ref_file_actions[action.text()])
				if action.text() == "Ref Module":
					self.RefFileIntoMaya(node.GetName(),file_path="%s/%s" % (ref_files[0][0], ref_files[0][1]),ask=True) #Quick and dirty way to get the ref path
				if action.text() == "Show Asset Info":
					for cur_node in node.getAllChildren():
						self.displayAssetInfo(cur_node)
				if action.text() == "Show Dependent Shots":
					for cur_node in node.getAllChildren():
						self.displayDependentShots(cur_node)
				if action.text() == "Publish All Children":
					self.PublishChildren(node)
				if action.text() == "Collect Thumbnails":
					self.CollectThumbnails(node)
				if action.text() == "Show in Directory":
					fileToOpen = "%s" % (node.GetPath())
					self.OpenDir(fileToOpen)
				if action.text() == "Duplicate":
					self.DuplicatePopup(node)
					self.UpdateDropdownPopup()


		return QtWidgets.QWidget.eventFilter(self, source, event) #Tried using this methode instead of:  return super(MainWindow, self).eventFilter(source, event)

	def displayAssetInfo(self, node):
		title = node.GetName() + ' - Asset Info'
		popup = Popup(parent=self, title=title)
		popup.resize(300, 450)
		popupLayout = QtWidgets.QVBoxLayout()
		popupLayout.setMargin(0)

		loadingWidget = QtWidgets.QWidget()
		loadingVBox = QtWidgets.QVBoxLayout()
		loadingHBox = QtWidgets.QHBoxLayout()
		loadingLabel = QtWidgets.QLabel('Loading')
		loadingWidget.setLayout(loadingVBox)
		loadingVBox.addStretch()
		loadingVBox.addLayout(loadingHBox)
		loadingVBox.addStretch()
		loadingHBox.addStretch()
		loadingHBox.addWidget(loadingLabel)
		loadingHBox.addStretch()

		popup.setLayout(popupLayout)
		popupLayout.addWidget(loadingWidget)
		# popup.popupSetPalette()
		popup.show()
		QtWidgets.QApplication.processEvents()

		asset_info = node.GetAssetInfo()
		identifier = '_'.join([
			asset_info['asset_type'],
			asset_info['asset_category'],
			asset_info['asset_name']]
		)
		self.publishReport.getData(identifier)
		prNode = self.publishReport.data[identifier]
		_string = self.formatReferenceInfo(prNode)

		infoWidget = QtWidgets.QWidget()
		infoLayout = QtWidgets.QVBoxLayout()
		infoLayout.setMargin(0)
		infoWidget.setLayout(infoLayout)

		infoLabel = QtWidgets.QPlainTextEdit(_string, readOnly=True)
		infoLayout.addWidget(infoLabel)

		popupLayout.removeWidget(loadingWidget)
		popupLayout.addWidget(infoWidget)

		popup.resize(300, 450)

	def formatReferenceInfo(self, node):
		_string = 'References'
		for type, dict in node.references.items():
			_string = _string + '\n  ' + type
			for path, value in dict.items():
				_string = _string + '\n    ' + str(value) + 'x ' + path.split('/')[-1].replace('.mb', '').replace('.ma', '')
			_string = _string + '\n'

		_string = _string + '\n\nTextures'
		for type, dict in node.textures.items():
			_string = _string + '\n  ' + type
			for path, value in dict.items():
				_string = _string + '\n    ' + str(value) + 'x ' + path.split('/')[-1].replace('.mb', '').replace('.ma',  '')
			_string = _string + '\n'

		_string = _string + '\n\nIDs'

		_string = _string + '\n  Object IDs'
		for oid, _list in node.OIDs.items():
			_string = _string + '\n    ' + oid + ': ' + ', '.join(_list)

		_string = _string + '\n\n  Material IDs'
		for mid, _list in node.MIDs.items():
			_string = _string + '\n    ' + mid + ': ' + ', '.join(_list)

		return _string


	def displayDependentShots(self, node):
		title = node.GetName() + ' - Asset Info'
		popup = Popup(parent=self, title=title)
		popup.resize(450, 450)
		popupLayout = QtWidgets.QVBoxLayout()
		popupLayout.setMargin(0)

		loadingWidget = QtWidgets.QWidget()
		loadingVBox = QtWidgets.QVBoxLayout()
		loadingHBox = QtWidgets.QHBoxLayout()
		loadingLabel = QtWidgets.QLabel('Loading')
		loadingWidget.setLayout(loadingVBox)
		loadingVBox.addStretch()
		loadingVBox.addLayout(loadingHBox)
		loadingVBox.addStretch()
		loadingHBox.addStretch()
		loadingHBox.addWidget(loadingLabel)
		loadingHBox.addStretch()

		popup.setLayout(popupLayout)
		popupLayout.addWidget(loadingWidget)
		# popup.popupSetPalette()
		popup.show()
		QtWidgets.QApplication.processEvents()

		if not self.publishReportDataRetrieved:
			self.publishReport.getData()

		asset_info = node.GetAssetInfo()
		identifier = '_'.join([
			asset_info['asset_type'],
			asset_info['asset_category'],
			asset_info['asset_name']]
		)

		prNode = self.publishReport.data[identifier]
		_string = self.formatDependentShots(prNode)

		infoWidget = QtWidgets.QWidget()
		infoLayout = QtWidgets.QVBoxLayout()
		infoLayout.setMargin(0)
		infoWidget.setLayout(infoLayout)

		infoLabel = QtWidgets.QPlainTextEdit(_string, readOnly=True)
		infoLayout.addWidget(infoLabel)

		popupLayout.removeWidget(loadingWidget)
		popupLayout.addWidget(infoWidget)

		popup.resize(450, 450)

	def formatDependentShots(self, node):
		shotDict = {}
		for shot in self.publishReport.getShotsByAsset(node.identity):
			episode, sequence, shot = shot.split('_')
			if episode not in shotDict.keys():
				shotDict[episode] = {}
			if sequence not in shotDict[episode].keys():
				shotDict[episode][sequence] = []
			shotDict[episode][sequence].append(shot)

		_string = u''
		for i, episode in enumerate(sorted(shotDict.keys())):
			if i != 0:
				_string = _string + u'\n\u2502\n'
			_string = _string + u'\u251C-- ' + episode
			for j, sequence in enumerate(sorted(shotDict[episode].keys())):
				j += 1
				if j == len(shotDict[episode].keys()):
					_string = _string + u'\n\u2502   \u2514-- ' + sequence + u'\n\u2502         \u2514-- '
				else:
					_string = _string + u'\n\u2502   \u251C-- ' + sequence + u'\n\u2502   \u2502   \u251C-- '
				for k, shot in enumerate(sorted(shotDict[episode][sequence])):
					k += 1
					if k == len(shotDict[episode][sequence]):
						_string = _string + shot
					elif k % 10 == 0:
						_string = _string + shot + u',\n\u2502   \u2502          '
					else:
						_string = _string + shot + u', '

		return _string


	def PublishChildren(self, parent_node):
		for cur_node in parent_node.getAllChildren():
			my_steps = CC.ref_order[cur_node.GetAssetType()]
			import PublishAssets.PublishMaster
			asset_info = cur_node.GetAssetInfo()
			for cur_step in my_steps:
				asset_info["asset_step"] = cur_step
				PubClass = PublishAssets.PublishMaster.ReadyPublish(asset_info=asset_info)
				PubClass.StartPublish()

	# def checkForColorManagement(self, cur_node):
	# 	CheckForColorManagementClass(cur_node)
	# 	print("Checking CM for %s" % cur_node.GetName())
	# 	save_path = "C:/Temp/CM_Check.txt"
	# 	if cur_node.work_files:
	# 		cur_file = "%s/%s" % (cur_node.work_files[-1][0],cur_node.work_files[-1][1])
	# 	else:
	# 		import Maya_Functions.file_util_functions as file_util
	# 		file_util.saveFile(save_path,'Error for %s' % cur_node.GetName(),False)
	# 		return
	# 	script_content = """import maya.standalone
	# 	    maya.standalone.initialize('python')
	# 	    import Maya_Functions.file_util_functions as file_util
	# 	    import maya.cmds as cmds
	# 	    cmds.file('%s', open=True,f=True)
	# 	    cm = cmds.colorManagementPrefs(q=True,cme=True)
	# 	    file_util.saveFile('%s',str(cm) + ' for %s',False)
	# 	    cmds.quit(f=True)
	# 	    """ % (cur_file,save_path,cur_node.GetName(),)
	# 	script_content = ";".join(script_content.split("\n"))
	# 	base_command = 'mayapy.exe -c "%s"' % (script_content)
	# 	print(base_command)
	# 	subprocess.Popen(base_command, shell=False, universal_newlines=True)

	def CollectThumbnails(self,parent_node): #quick thumbnail collector
		import shutil
		resource_folder = "%s/Pipeline/Resource/thumbnail/" % self.base_project
		logger.info("updating:%s" %parent_node.GetName())
		for child_node in parent_node.GetChildren():
			logger.info("Now updating: %s" % child_node.GetName())
			thumb = child_node.GetImage()
			logger.info(thumb)
			if thumb:
				thumb_folder,thumb_file = os.path.split(thumb)
				logger.info(thumb_file)
				shutil.copy(thumb,"%s%s" %(resource_folder,thumb_file))



	def RunUpdateForChildren(self,parent_node):
		pass
		# print("updating:%s" %parent_node.GetName())
		# for child_node in parent_node.GetChildren():
		# 	print("Now updating: %s" % child_node.GetName())
		# 	update_class = AF.UpdateAssetFile(asset_info=child_node.GetAssetInfo())
		# 	update_class.Run()
		#
		# #Save Update log as the right name
		# update_log = cfg.project_paths["update_log_path"]
		# prefix = "%s_%s" % (parent_node.parent().GetName(),parent_node.GetName())
		# if os.path.exists(update_log):
		# 	u_path,u_name = os.path.split(update_log)
		# 	update_path = "%s/%s_%s" % (u_path,prefix,u_name)
		#
		# 	if os.path.exists(update_path):
		# 		with open(update_log, 'r') as orig_update_file:
		# 			orig_content = orig_update_file.read()
		# 		with open(update_path, 'a+') as update_file:
		# 			update_file.write("%s\n" % (orig_content))
		# 		os.remove(update_log)
		# 	else:
		# 		os.rename(update_log,update_path)


	###########################################################
	#################### FUNCTIONS ############################
	###########################################################

	def UpdateUI(self): #Goes through and rebuilds nodes and dicts and tree model
		#TODO Select last chosen node again after update
		self.maya_node = None
		self.chosen_node = None

		self.tree_model.ClearNodes() #very important. Deletes old nodes so it wont rebuild untop of itself
		self.tree_model.deleteLater()
		self.proxyModel.deleteLater()

		self.populate()
		self.custom_nodes[:] = []
		self.MakeNodesFromDict(self.all_node_list, None)
		self.tree_model = CustomModel(self.custom_nodes,self)


		self.proxyModel = QtCore.QSortFilterProxyModel(self.tree)
		self.proxyModel.setSourceModel(self.tree_model)
		self.proxyModel.setRecursiveFilteringEnabled(True)
		self.proxyModel.setSortCaseSensitivity(QtCore.Qt.CaseInsensitive)
		self.proxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

		self.tree.setModel(self.proxyModel)
		self.proxyModel.sort(0, QtCore.Qt.AscendingOrder)
		self.tree.selectionModel().selectionChanged.connect(self.TreeviewSelectionChanged)
		# self.tree.setModel(self.tree_model)
		self.chosen_node = self.tree_model._root
		self.treeItemClicked()
		# self.SaveSettings(self.node_dict_path, self.all_node_list)
		file_util.save_json(self.node_dict_path, self.all_node_list)


	def populate(self):
		self.all_node_list[:] = []
		for fol_type in os.listdir(self.base_path):
			if "." in fol_type:
				continue
			type_dict = {"column_count": 1, "children": [], "parent": None, "row": 0, "node_name":fol_type,
						 "node_type": "type", "asset_type": fol_type, "asset_category": None,
						 "path": "%s/%s" % (self.base_path, fol_type)}
			for fol_category in os.listdir(type_dict["path"]):
				if "." in fol_category:
					continue
				category_dict = {"column_count": 1, "children": [], "parent": type_dict["asset_type"],
								 "row": 0, "node_name":fol_category, "node_type": "category",
								 "asset_type": type_dict["asset_type"], "asset_category": fol_category,
								 "path": "%s/%s" % (type_dict["path"], fol_category)}

				type_dict["children"].append(category_dict)
				for fol_asset in os.listdir(category_dict["path"]):
					if "." in fol_asset:
						continue
					asset_dict = {
						"column_count": 1, "children": [], "parent": category_dict["asset_category"],
									  "row": 0, "node_name":fol_asset,"node_type": "asset",
									  "asset_type": type_dict["asset_type"],
									  "asset_category": category_dict["asset_category"],
									  "path": "%s/%s" % (category_dict["path"], fol_asset)}
					category_dict["children"].append(asset_dict)
			self.all_node_list.append(type_dict)

	def MakeNodesFromDict(self,cur_list, cur_parent):
		for t in cur_list:
			cur_node = CustomNode(node_name=t["node_name"], node_type=t["node_type"], children=[], asset_type=t["asset_type"],asset_category=t["asset_category"],path=t["path"],_parent=cur_parent)
			if cur_parent:
				cur_parent.addChild(cur_node)
			self.MakeNodesFromDict(t["children"], cur_node)
			self.custom_nodes.append(cur_node)


	########### QUICK SELECT FUNCTIONS #################

	def ShowQuickView(self, show): #Hide and unhide quickview when clicking treeview objects
		if show:
			self.tab1FolderView.show()
			self.tab1ImageReferenceLabel.hide()
			self.tab1OpenButton.hide()
		else:
			self.tab1FolderView.hide()
			self.tab1ImageReferenceLabel.show()
			self.tab1OpenButton.show()

	def RefreshQuickView(self,cur_node=None): #Updates the quick select view
		# pr.enable()

		self.ShowQuickView(True)
		# --   Populate tableview with nodes in chosen folder
		self.tableview_nodes = []
		self.listEndChildren(cur_node)
		run_threads = False
		for tab_node in self.tableview_nodes:
			image_path = tab_node.GetImage()
			if not QtGui.QPixmapCache.find("%s_quickview_thumbnail"  % image_path):
				script_thread_pool.addWorker(Multiplicity.ThreadPool2.Worker(self.createThreadQuickPixmap, image_path))
				run_threads = True

				# convertPathToPixmap(image_path = image_path, width = 100, height = 100, added_name = "_quickview_thumbnail")
				# script_thread_pool.addWorker(Multiplicity.ThreadPool2.Worker(convertPathToPixmap,image_path=image_path,width=100,height=100,added_name="_quickview_thumbnail"))

		self.table_model = TableModel(self.tableview_nodes,self)
		self.tab1FolderView.setModel(self.table_model)
		if run_threads:
			script_thread_pool.run()
			script_thread_pool.signals.finished.connect(self.threadPoolResult)



	def threadPoolResult(self, result):
		for k in result.keys():
			if k.getFunc() == "createThreadQuickPixmap":
				v = result[k]
				self.InsertPixmap(pixmap=v[0],key=v[1])
		self.table_model.layoutChanged.emit()
		# script_thread_pool.signals.finished.disconnect(self.threadPoolResult)
		# self.table_model.beginResetModel()
		# self.table_model.endResetModel()

		# pr.disable()
		# pr.print_stats(sort=2)

	def createThreadQuickPixmap(self, image_path):
		"""
		meant to only be used by the threadpool
		:param image_path:
		:return:
		"""
		# cur_pix = convertPathToPixmap(image_path = image_path, width = 100, height = 100, added_name = "_quickview_thumbnail")
		pixmap = QtGui.QPixmap(image_path)
		pixmap = pixmap.scaled(100, 100, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
		# new_pix = QtGui.QPixmapCache.find("%s_quickview_thumbnail"  % image_path)
		# print("CREATED and found %s" % new_pix)
		return [pixmap,"%s_quickview_thumbnail"  % image_path]

	def InsertPixmap(self,pixmap,key):
		"""
		meant to only be used after the threadpool has created pixmaps, to insert them into the cache.
		:param pixmap:
		:param key:
		:return:
		"""
		QtGui.QPixmapCache.insert(key, pixmap)

	def folderQuickviewClicked(self, index):
		node = self.table_model.getNode(index)
		self.chosen_node = node

		# self.targeted_asset = "%s" % (node.GetPath())
		self.ExpandToNode(self.chosen_node)
		self.ShowQuickView(False)
		self.RefreshTab1()


	# TODO LOOK AT OS.PATH.JOIN ? Currently not used
	def createFolderPopup(self, path, isType=True):
		folder_name = QtWidgets.QInputDialog.getText(self, "Folder Creation", "Please input new folder name:")
		if folder_name[1] == True:
			full_path = "%s/%s" % (path, folder_name[0])
			try:
				return full_path
			# beginInsertRows() and endInsertRows() into model
			except OSError:
				logger.info("Creation of the directory %s failed" % full_path)
		else:
			return True

	def CreateNewTypeFolder(self): #Currently not used
		full_path = self.createFolderPopup(self.base_path)
		os.mkdir(full_path)
		self.insertNewNode(full_path.split("/")[-1],full_path,"type",parent=self.tree_model._root)
		# self.insertNewNode(full_path.split("/")[-1], full_path, 1, "type")
	#
	def CreateNewCategoryFolder(self): #Currently not used
		mid_path = "%s/%s" % (self.base_path, self.tab3TypeDropdown.currentText())
		full_path = self.createFolderPopup(mid_path, False)
		os.mkdir(full_path)
		# self.insertNewNode(full_path.split("/")[-1], full_path, "category")
	def CreateNewCategoryFolderPopup(self): #Currently not used
		mid_path = "%s/%s" % (self.base_path, self.popupTypeDropdown.currentText())
		full_path = self.createFolderPopup(mid_path, False)
		os.mkdir(full_path)
		# self.insertNewNode(full_path.split("/")[-1], full_path, "category")
	def Tab3CreateAsset(self):

		asset_dict = {"asset_type": self.tab3TypeDropdown.currentText(),
					  "asset_category": self.tab3CategoryDropdown.currentText(),
					  "asset_name": self.tab3NameTextField.text(),"node_name":self.tab3NameTextField.text(),"node_type":"asset",}
		create_path = CC.get_asset_base_path(**asset_dict)
		asset_dict["path"]=create_path

		if asset_dict["node_name"].lower() in list(x.GetName().lower() for x in self.custom_nodes):
			logger.warning("Already an Asset named that. Please pick another name")
			return False

		if (os.path.exists(asset_dict["path"])):
			# TODO Make sure no other node named same.
			logger.warning("Already an Asset named that. Please pick another name")
			# cmds.warning("Already an Asset named that. Please pick another name")
			return False
		else:

			create_class = AF.CreateAsset(asset_info=asset_dict) 	#initiate the create class
			create_class.Run() 										#Run the asset creations /folder copy and name replacing.

		if self.tab3OpenAfterCheckbox.isChecked():
			asset_dict["asset_step"] = CC.ref_order[asset_dict["asset_type"]][0]
			self.OpenMayaFile("%s" % CC.get_asset_work_file(**asset_dict))

		asset_parent = None #FIND PARENT OF NODE:
		for c in self.custom_nodes:
			if c.GetName()==asset_dict["asset_category"]:
				if c.GetAssetType()==asset_dict["asset_type"]:
					asset_parent = c

		self.insertNewNode(name=asset_dict["node_name"],node_type="asset",
						   path=asset_dict["path"], asset_category=asset_dict["asset_category"],
						   asset_type=asset_dict["asset_type"],parent=asset_parent)
		self.tab3NameTextField.clear()


	def DuplicateAsset(self,orig_asset_info=None):
		orig_asset_info["asset_name"] = orig_asset_info["node_name"]
		asset_dict = {"asset_type": self.popupTypeDropdown.currentText(),
					  "asset_category": self.popupCategoryDropdown.currentText(),
					  "asset_name": self.popupNameTextField.text(),"node_name":self.popupNameTextField.text(),"node_type":"asset"}
		create_path = CC.get_asset_base_path(**asset_dict)
		asset_dict["path"]=create_path

		if asset_dict["node_name"].lower() in list(x.GetName().lower() for x in self.custom_nodes):
			logger.warning("Already an Asset named that. Please pick another name")
			return False

		if (os.path.exists(asset_dict["path"])):
			# TODO Make sure no other node named same.
			logger.warning("Already an Asset named that. Please pick another name")
			# cmds.warning("Already an Asset named that. Please pick another name")
			return False
		else:

			create_class = AF.DuplicateAsset(orig_asset_info=orig_asset_info,asset_info=asset_dict) 	#initiate the create class
			create_class.Run() 										#Run the asset creations /folder copy and name replacing.

		if self.popupOpenAfterCheckbox.isChecked():
			asset_dict["asset_step"] = CC.ref_order[asset_dict["asset_type"]][0]
			self.OpenMayaFile("%s" % CC.get_asset_work_file(**asset_dict))

		asset_parent = None #FIND PARENT OF NODE:
		for c in self.custom_nodes:
			if c.GetName()==asset_dict["asset_category"]:
				if c.GetAssetType()==asset_dict["asset_type"]:
					asset_parent = c

		node = self.insertNewNode(name=asset_dict["node_name"],node_type="asset",
						   path=asset_dict["path"], asset_category=asset_dict["asset_category"],
						   asset_type=asset_dict["asset_type"],parent=asset_parent)
		self.popupNameTextField.clear()

		# ea_asset_type = self.popupTypeDropdown.currentText()
		# ea_category = self.popupCategoryDropdown.currentText()
		# ea_name = self.popupNameTextField.text()

		import PublishAssets.PublishMaster
		for c_step in CC.ref_steps[asset_dict["asset_type"]]:
			asset_dict["asset_step"] = c_step
			w_path = CC.get_asset_work_file(**asset_dict)
			if os.path.exists(w_path):
				if c_step in ["Base", "Rig"]:
					print("FOUND %s" % c_step)

					script_content = f"""import sys
import maya.standalone
maya.standalone.initialize('python')
import maya.cmds as cmds
path_rig = '{w_path}'
cmds.file(path_rig, open=True,f=True)
cmds.setAttr('Root_Group.asset_type', '{asset_dict["asset_type"]}', type='string')
cmds.setAttr('Root_Group.asset_category', '{asset_dict["asset_category"]}', type='string')
cmds.setAttr('Root_Group.asset_name', '{asset_dict["asset_name"]}', type='string')
cmds.file(save=True,f=True)
"""
					script_content = ";".join(script_content.split("\n"))
					base_command = 'mayapy.exe -c "%s"' % (script_content)
					logger.info(base_command)
					print(base_command)
					rc = subprocess.Popen(base_command, shell=False, universal_newlines=True, env=runtime.getRuntimeEnvFromConfig(CC),stdout=subprocess.PIPE,
								  stderr=subprocess.PIPE)
					print_out = rc.communicate()

				PubClass = PublishAssets.PublishMaster.ReadyPublish(asset_info=asset_dict)
				pub_success = PubClass.StartPublish()


		# Check if "Open file" is checked
		# If so, open shading

		# self.Publish(node)
		# Update extra attributes


	def insertNewNode(self, name, path, node_type,asset_type=None, asset_category=None, parent=None):
		new_node = CustomNode(node_name=name, node_type=node_type, children=[],
							  asset_type=asset_type,
							  asset_category=asset_category, path=path, _parent=parent)
		parent.addChild(new_node)
		self.custom_nodes.append(new_node)
		self.UpdateUI()

		return new_node



		# expanded_folders = self.tree_model.saveModelState(self.tree, new_node)
		# self.tree_model = CustomModel(self.custom_nodes, self)
		# self.tree.setModel(self.tree_model)
		# self.UpdateDropdownTab3()
		# self.iterateOverProxyModelAndExpandAllMatches(expanded_folders, new_node, QtCore.QModelIndex())
		# self.populate()

	def UpdateDropdownTab3(self):
		# ------------------- Create Tab Selected and Synch Enabled -------------------------------------------
		cur_node = self.chosen_node

		self.tab3TypeDropdown.clear()

		self.tab3TypeDropdown.addItems(list(x.GetAssetType() for x in self.tree_model._root.GetChildren()))

		temp_dict = cur_node.GetAssetInfo()
		print(temp_dict)
		if temp_dict["asset_type"]:
			self.tab3TypeDropdown.setCurrentIndex(self.tab3TypeDropdown.findText(temp_dict["asset_type"]))
			# type_node = [x for x in self.tree_model._root.GetChildren() if (x.GetName()==temp_dict["asset_type"])][0]

		if temp_dict["asset_category"]:
			self.tab3CategoryDropdown.setCurrentIndex(self.tab3CategoryDropdown.findText(temp_dict["asset_category"]))

	def UpdateDropdownPopup(self):
		# ------------------- Create Tab Selected and Synch Enabled -------------------------------------------
		cur_node = self.chosen_node

		self.popupTypeDropdown.clear()

		self.popupTypeDropdown.addItems(list(x.GetAssetType() for x in self.tree_model._root.GetChildren()))

		temp_dict = cur_node.GetAssetInfo()
		print(temp_dict)
		if temp_dict["asset_type"]:
			self.popupTypeDropdown.setCurrentIndex(self.popupTypeDropdown.findText(temp_dict["asset_type"]))
			# type_node = [x for x in self.tree_model._root.GetChildren() if (x.GetName()==temp_dict["asset_type"])][0]

		if temp_dict["asset_category"]:
			self.popupCategoryDropdown.setCurrentIndex(self.popupCategoryDropdown.findText(temp_dict["asset_category"]))
		path_to_display = "/%s/%s/%s" % (self.popupTypeDropdown.currentText(), self.popupCategoryDropdown.currentText(), self.popupNameTextField.text())
		self.popupPath.setText(path_to_display)

	def UpdateCategoryDropdownTab3(self):
		type_node = self.tree_model._root.GetChildren()[self.tab3TypeDropdown.currentIndex()]
		self.tab3CategoryDropdown.clear()
		for child in type_node.GetChildren():
			self.tab3CategoryDropdown.addItem(child.GetName())

	def UpdateCategoryDropdownPopup(self):
		type_node = self.tree_model._root.GetChildren()[self.popupTypeDropdown.currentIndex()]
		self.popupCategoryDropdown.clear()
		for child in type_node.GetChildren():
			self.popupCategoryDropdown.addItem(child.GetName())
	################################# UI UTIL FUNCTIONS #####################################################

	def DisableFreeCreate(self,on_off):
		self.tab3TypeDropdown.setEnabled(on_off)
		self.tab3CategoryDropdown.setEnabled(on_off)

	def IconOnOff(self):
		return self.icons_on_off.checkState()

	def listEndChildren(self, node):
		if node.GetNodeType() == "asset":
			self.tableview_nodes.append(node)
		children = node.GetChildren()
		for child in children:
			self.listEndChildren(child)

	def infoPopup(self, warning, info, title):
		self.generalMessagePopup.setIcon(QtWidgets.QMessageBox.Information)
		self.generalMessagePopup.setText(warning)
		self.generalMessagePopup.setInformativeText(info)
		self.generalMessagePopup.setWindowTitle(title)
		self.generalMessagePopup.setStandardButtons(QtWidgets.QMessageBox.Ok)

	def newPopup(self, warning="Warning", info="info info info", title="Hey you"):
		self.generalMessagePopup.setIcon(QtWidgets.QMessageBox.Information)
		self.generalMessagePopup.setText(warning)
		self.generalMessagePopup.setInformativeText(info)
		self.generalMessagePopup.setWindowTitle(title)
		self.generalMessagePopup.setStandardButtons(
			QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel)
		reply = self.generalMessagePopup.exec_()

		if reply == QtWidgets.QMessageBox.Yes:
			return "yes"
		elif reply == QtWidgets.QMessageBox.No:
			return "no"
		else:
			return "cancel"

	def ThumbnailPopup(self, title="Update Thumbnail"):
		temp_popup = QtWidgets.QMessageBox()
		temp_popup.setIcon(QtWidgets.QMessageBox.Question)
		temp_popup.setText("Update Thumbnail?\n(Viewport thumbnail only works if the viewport has focus\n Just click something in the wanted viewport )")
		temp_popup.setWindowTitle(title)
		temp_popup.addButton("Viewport", QtWidgets.QMessageBox.ActionRole)
		temp_popup.addButton("Render", QtWidgets.QMessageBox.ActionRole)
		temp_popup.setStandardButtons(QtWidgets.QMessageBox.Cancel)
		temp_popup.exec_()
		to_return = temp_popup.clickedButton().text()
		temp_popup.deleteLater()
		return to_return

	def DuplicatePopup(self,cur_node):
		popup = Popup(self, 'Duplicate Asset')
		popup_Layout = QtWidgets.QGridLayout()

		#--------------------------------------------------------------------------------------------
		self.popupTypeDropdown = QtWidgets.QComboBox()
		self.popupCategoryDropdown = QtWidgets.QComboBox()

		self.popupNameTextField = QtWidgets.QLineEdit()
		self.popupNameTextField.setPlaceholderText("Enter name of new asset here")
		self.popupNameTextField.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

		#--------------------------------------------------------------------------------------------
		self.popupCreateButton = QtWidgets.QPushButton("Duplicate")
		self.popupCreateButton.clicked.connect(partial(self.DuplicateAsset, cur_node.GetNodeDict()))

		#--------------------------------------------------------------------------------------------
		self.popupPathLabel = QtWidgets.QLabel("Create location:")
		self.popupPath = QtWidgets.QLabel("No path chosen")
		self.popupPathHolder = QtWidgets.QGroupBox()
		self.popupPathHolder.layout = QtWidgets.QHBoxLayout()
		self.popupPathHolder.layout.addWidget(self.popupPath)
		self.popupPathHolder.setLayout(self.popupPathHolder.layout)

		#--------------------------------------------------------------------------------------------
		self.popupTypeLabel = QtWidgets.QLabel("Type:")
		self.popupCategoryLabel = QtWidgets.QLabel("Category:")
		self.popupNameLabel = QtWidgets.QLabel("File Name:")

		#--------------------------------------------------------------------------------------------
		self.popupAddTypeFolderButton = QtWidgets.QPushButton("+")
		self.popupAddCategoryFolderButton = QtWidgets.QPushButton("+")
		self.popupAddTypeFolderButton.setFixedSize(22, 22)
		self.popupAddCategoryFolderButton.setFixedSize(22, 22)

		self.popupAddTypeFolderButton.clicked.connect(self.CreateNewTypeFolder)
		self.popupAddCategoryFolderButton.clicked.connect(self.CreateNewCategoryFolder)

		# --------------------------------------------------------------------------------------------
		self.popupOpenAfterCheckbox = QtWidgets.QCheckBox("Open file in Maya after creation")
		self.popupOpenAfterRadioButtonHolder = QtWidgets.QGroupBox()
		self.popupOpenAfterRadioButtonHolder.layout = QtWidgets.QHBoxLayout()
		self.popupOpenAfterRadioButtonHolder.layout.addWidget(self.popupOpenAfterCheckbox)
		self.popupOpenAfterRadioButtonHolder.setLayout(self.popupOpenAfterRadioButtonHolder.layout)
		self.popupOpenAfterCheckbox.setChecked(True)

		# --------------------------------------------------------------------------------------------
		self.popupTypeBox = QtWidgets.QGroupBox()
		self.popupTypeBox.layout = QtWidgets.QHBoxLayout()
		self.popupTypeBox.layout.addWidget(self.popupAddTypeFolderButton)
		self.popupTypeBox.layout.addWidget(self.popupTypeDropdown)
		self.popupTypeDropdown.currentTextChanged.connect(self.UpdateCategoryDropdownPopup)
		self.popupTypeBox.setLayout(self.popupTypeBox.layout)

		# --------------------------------------------------------------------------------------------
		self.popupCategoryBox = QtWidgets.QGroupBox()
		self.popupCategoryBox.layout = QtWidgets.QHBoxLayout()
		self.popupCategoryBox.layout.addWidget(self.popupAddCategoryFolderButton)
		self.popupCategoryBox.layout.addWidget(self.popupCategoryDropdown)
		self.popupCategoryBox.setLayout(self.popupCategoryBox.layout)

		# --------------------------------------------------------------------------------------------

		popup_Layout.addWidget(self.popupPathLabel, 					1, 0, 1, 1)
		popup_Layout.addWidget(self.popupPathHolder, 					2, 0, 1, 1)
		popup_Layout.addWidget(self.popupTypeLabel, 					3, 0, 1, 1)
		popup_Layout.addWidget(self.popupTypeBox, 						4, 0, 1, 1)
		popup_Layout.addWidget(self.popupCategoryLabel, 				5, 0, 1, 1)
		popup_Layout.addWidget(self.popupCategoryBox, 					6, 0, 1, 1)
		popup_Layout.addWidget(self.popupNameLabel, 					7, 0, 1, 1)
		popup_Layout.addWidget(self.popupNameTextField, 				8, 0, 1, 1)
		popup_Layout.addWidget(self.popupOpenAfterRadioButtonHolder, 	9, 0, 1, 1)
		popup_Layout.addWidget(self.popupCreateButton, 					10, 0, 1, 1)

		popup_Layout.setAlignment(QtCore.Qt.AlignCenter)

		popup.setLayout(popup_Layout)


		popup.show()



		# dp_textfield = QtWidgets.QLineEdit()
		# dp_textfield.setPlaceholderText("Enter name of new asset here")
		# dp_textfield.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
		#
		# duplicate_popup.exec_()
		# to_return = duplicate_popup.clickedButton().text()
		# print(to_return)
		# duplicate_popup.deleteLater()
		# return to_return

	# def SaveSettings(self, save_location, save_info):
	# 	with open(save_location, 'w+') as saveFile:
	# 		json.dump(save_info, saveFile)
	# 	saveFile.close()

	# def LoadSettings(self, save_location):

	# 	if os.path.isfile(save_location):
	# 		with open(save_location, 'r') as saveFile:
	# 			loadedSettings = json.load(saveFile)
	# 		# if 'selected node' in loadedSettings.keys():
	# 		if loadedSettings:
	# 			return loadedSettings
	# 	else:
	# 		logger.warning("not a file")
	# 	return None

	def closeEvent(self, event):
		# self.user_data['username'] = self.user_name
		# self.user_data['expanded folders'] = self.tree_model.saveModelState(self.tree)
		# if self.chosen_node:
		# 	self.user_data['selected node'] = self.chosen_node.GetName()
		# self.SaveSettings(self.user_data)

		#Check for folder before saving:
		if not os.path.exists(os.path.split(self.node_dict_path)[0]):
			os.mkdir(os.path.split(self.node_dict_path)[0])
		# self.SaveSettings(self.node_dict_path, self.all_node_list)  # Save nodes
		file_util.save_json(self.node_dict_path, self.all_node_list)
		QtGui.QPixmapCache.clear()
		super(MainWindow, self).closeEvent(event)

	######### OPEN FUNCTIONS ################

	def OpenDir(self, path):
		os.startfile(path)

	def OpenFileFromAssetlist(self):
		cur_file = self.tab1AssetFiles.currentItem().text()
		file_path = "%s/%s" % (self.chosen_node.GetMayaWorkFiles()[0][0], cur_file)
		self.OpenMayaFile(file_path, True)

	def OpenMayaFile(self, file_path, ask=True):

		# If Maya is open ------------------------------
		if in_maya == True:

			if ask and cmds.file(q=True,mf=True):
				save_before_open = self.newPopup("You are about to open another Maya file",
				                                 "Do you want to save your current work before you continue?",
				                                 "Warning")
				if save_before_open == "yes":

					# cmds.file(save=True, type="mayaAscii")
					cmds.file(save=True)

				elif save_before_open == "cancel":
					return True
			########################^^^^^^^^^^####################Save file here ##############################################
				# cmds.file(file_path, open=True, f=True)
				# return True
			if not file_path:
				cmds.file(new=True,f=True)
				cmds.file(mf=False)
				return True
			logger.info("Opening : " + file_path)
			cmds.file(file_path, open=True, f=True)
			cmds.file(mf=False)
			return True
		else:
			# if Maya is not open -------------------------
			logger.info("Opening : " + file_path)
		if os.path.exists(file_path): #If running UI without maya, open scene in a new maya.
			if file_path:
				run_command = 'START maya -file "%s"' % file_path
			else:
				run_command = 'START maya'
			subprocess.call(run_command, shell=True)
		else:
			logger.warning('File does not exist!')

	def Tab1RefFile(self):
		if in_maya:
			file_path = "%s/%s" % (CC.get_asset_ref_folder(**self.chosen_node.GetAssetInfo()), self.tab1AssetRefFiles.currentItem().text())
			self.RefFileIntoMaya(self.chosen_node.GetName(),file_path=file_path)

	def RefFileIntoMaya(self,ref_namespace,file_path=None,ask=False):
		if ask: #Asking for a namespace instead of using the asset name
			text, ok = QtWidgets.QInputDialog().getText(self,"Set Ref Namespace",
														"Module NS (Arms,Legs ect.):", QtWidgets.QLineEdit.Normal,"")
			if ok and text:
				ref_namespace = text
			else:
				logger.warning("Cancel ref'ing in %s because no namespace given" % ref_namespace)
				return
		if os.path.exists(file_path):
			cmds.file(file_path, r=True, type="mayaBinary", loadReferenceDepth="all", mergeNamespacesOnClash=False,
					  namespace=ref_namespace, options="v=0") #Wonder if type=mayaBinary is nessessary?
		else:
			cmds.warning("For %s -> Can't find ref: %s" % (ref_namespace,file_path))


# class CollectAssetFilesThread(QtCore.QRunnable): #A thread function to run the asset checks so we don't have to wait for all images being loaded before ui becomes responsive.
# 	def __init__(self, target_node):
# 		super(CollectAssetFilesThread,self).__init__()
# 		self.target_node = target_node
# 	def run(self):
# 		self.target_node.FindMayaWorkFiles()
# 		self.target_node.FindMayaRefFiles()
# 		# CountThreads

class CheckForColorManagementClass(QtCore.QRunnable):
	def __init__(self, cur_node):
		super(CheckForColorManagementClass, self).__init__()
		self.cur_node = cur_node

	def run(self):
		print("Checking CM for %s" % self.cur_node.GetName())
		save_path = "C:/Temp/CM_Check.txt"
		if self.cur_node.work_files:
			cur_file = "%s/%s" % (self.cur_node.work_files[-1][0],self.cur_node.work_files[-1][1])
		else:
			import Maya_Functions.file_util_functions as file_util
			file_util.saveFile(save_path,'Error for %s' % self.cur_node.GetName(),False)
			return
		script_content = """import maya.standalone
			maya.standalone.initialize('python')
			import maya.cmds as cmds
			import AssetBrowser
			cmds.file('%s', open=True, f=True)
			AssetBrowser.DoCMCheck('%s','%s')
			cmds.quit(f=True)
			""" % (cur_file,save_path,self.cur_node.GetName())
		script_content = ";".join(script_content.split("\n"))
		base_command = 'mayapy.exe -c "%s"' % (script_content)
		print(base_command)
		subprocess.Popen(base_command, shell=False, universal_newlines=True)

def DoCMCheck(save_path, asset_name):
	import Maya_Functions.file_util_functions as file_util
	cm = cmds.colorManagementPrefs(q=True, cme=True)
	if not cm == True:
		file_util.saveFile(save_path, str(cm) + ' for %s' % asset_name, False)
	print("----------------- DONE WITH %s ----------------------" % asset_name)

class CollectAssetImageThread(): #A thread function to run the asset checks so we don't have to wait for all images being loaded before ui becomes responsive.
	def __init__(self, target_node):
		# super(CollectAssetImageThread, self).__init__()
		self.target_node = target_node
		# print("Running this node: %s" % target_node)
		self.run()

	def run(self):
		self.target_node.CheckImage()
		# self.target_node.FindMayaWorkFiles()
		# self.target_node.FindMayaRefFiles()

		# self.createPixmaps()
		# print("Collected for %s" % self.target_node.GetName())

	def createPixmaps(self):
		image_path = self.target_node.GetImage()
		if image_path:
			tree_value = "%s_thumbnail" % image_path
			tree_pixmap = QtGui.QPixmapCache.find(tree_value)
			if not tree_pixmap:
				tree_pixmap = QtGui.QPixmap(image_path).scaled(75, 75, QtCore.Qt.KeepAspectRatio,
														  QtCore.Qt.SmoothTransformation)
				QtGui.QPixmapCache.insert(tree_value, tree_pixmap)

			quick_value = "%s_quick_thumbnail" % image_path
			quick_pixmap = QtGui.QPixmapCache.find(quick_value)
			if not quick_pixmap:
				quick_pixmap = QtGui.QPixmap(image_path).scaled(100, 100, QtCore.Qt.KeepAspectRatio,
														  QtCore.Qt.SmoothTransformation)
			QtGui.QPixmapCache.insert(quick_value, quick_pixmap)


class TableModel(QtCore.QAbstractListModel): #Quick Selection mode on type/category selection
	def __init__(self, nodes,ui_parent):
		super(TableModel, self).__init__()
		self.setObjectName("MyTableModel")
		self.nodes = nodes
		self.size_factor = 1.5
		self.no_thumb_picture = CC.get_no_thumb_icon_path()
		self.ui_parent = ui_parent

	def GetName(self, elem):
		return elem.GetName()

	def rowCount(self, parent=None):
		return len(self.nodes)

	def getNode(self, index):
		if index.isValid():
			r = index.row()
			try:
				node = self.nodes[r]
				return node
			except IndexError:
				return None
		return None

	def flags(self, index):
		return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

	def data(self, index, role):

		if not index.isValid():
			logger.warning("index is not valid")
			return None

		cur_row = index.row()

		cur_node = self.nodes[cur_row]
		if role == QtCore.Qt.TextAlignmentRole:
			return QtCore.Qt.AlignHCenter

		# if role == QtCore.Qt.SizeHintRole:
		#     return QtCore.QSize(self.thumb_size[0],self.thumb_size[1]+20)

		if role == QtCore.Qt.DisplayRole:
			return "%s" % (cur_node.GetName())

		if role == QtCore.Qt.TextAlignmentRole:
			return QtCore.Qt.AlignVCenter()

		# if role == QtCore.Qt.ToolTipRole:
		#     if self.nodes[cur_row][cur_col].GetName():
		#         return "%s : %s : %s" % (self.nodes[cur_row][cur_col].Episode(),self.nodes[cur_row][cur_col].Sequence(), self.nodes[cur_row][cur_col].GetName() )
		if role == QtCore.Qt.DecorationRole:
			if self.ui_parent.IconOnOff():
				key_value = "%s_quickview_thumbnail" % cur_node.GetImage()
				cur_pixmap = QtGui.QPixmapCache.find(key_value)
				# print("FOUND PIXMAP: %s" % cur_pixmap)
				# image_path = cur_node.GetImage()
				# cur_pixmap = convertPathToPixmap(image_path=image_path,width=100,height=100,added_name="_quickview_thumbnail")
				return QtGui.QPixmap(cur_pixmap)

		# if role == QtCore.Qt.DecorationRole:
		#     image_path = cur_node.GetImage()
		#     value = "%s_tableIcon" % image_path
		#     pixmap = QtGui.QPixmapCache.find(value)
		#     if not pixmap:
		#         pixmap = QtGui.QPixmap(image_path).scaled(self.thumb_size[0],self.thumb_size[1],QtCore.Qt.KeepAspectRatio | QtCore.Qt.SmoothTransformation)
		#         QtGui.QPixmapCache.insert(value, pixmap)
		#         # print("making %s" % value)
		#     pixmap = QtGui.QPixmapCache.find(value)
		#     return QtGui.QImage(pixmap)

	# def headerData(self, section, orientation, role):
	#     if role == QtCore.Qt.DisplayRole:
	#         return None
	#     return None


class CustomModel(QtCore.QAbstractItemModel):
	def __init__(self, nodes,ui_parent):
		QtCore.QAbstractItemModel.__init__(self)
		self._root = CustomNode()
		self.folder_picture = CC.get_folder_icon_path()
		self.no_thumb_picture = CC.get_no_thumb_icon_path()
		self.ui_parent = ui_parent
		# self.nodes = nodes
		self.nodes = nodes
		# print(self.nodes)
		for node in self.nodes:
			# print(node.GetName())
			if node.parent()==None: #If they are root folders
				self._root.addChild(node)

	def ClearNodes(self): #Tries to clear all the previous node info, recursively
		self.nodes[:] = []
		self._root.ClearChildren()
		self._root._children = []
		self._root = None

	def insertRows(self, position, rows, index, parent):
		self.beginInsertRows(index, position, position + rows - 1)
		# self.setData(self.index(position,0,parent),QtCore.QVariant(111),role=QtCore.Qt.DisplayRole)

		self.endInsertRows()
		# self.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())
		return True

	def emitDataChanged(self):
		self.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())

	def rowCount(self, index):
		if index.isValid():
			# print(index.internalPointer())
			node = index.internalPointer()
			# return index.internalPointer()
			return node.childCount()
		return self._root.childCount()

	def addChild(self, node, _parent):
		if not _parent or not _parent.isValid():
			parent = self._root
		else:
			parent = _parent.internalPointer()
		parent.addChild(node)

	def index(self, row, column, _parent=None):
		if not _parent or not _parent.isValid():
			node_parent = self._root
		else:
			node_parent = _parent.internalPointer()

		if not QtCore.QAbstractItemModel.hasIndex(self, row, column, _parent):
			return QtCore.QModelIndex()

		child = node_parent.child(row)

		if child:
			return QtCore.QAbstractItemModel.createIndex(self, row, column, child)
		else:
			return QtCore.QModelIndex()

	def parent(self, index):
		if index.isValid():
			p = index.internalPointer().parent()
			if p:
				return QtCore.QAbstractItemModel.createIndex(self, p.row(), 0, p)
		return QtCore.QModelIndex()

	def columnCount(self, index):
		if index.isValid():
			return index.internalPointer().columnCount()
		return self._root.columnCount()

	def data(self, index, role):
		if not index.isValid():
			return None
		node = index.internalPointer()
		if role == QtCore.Qt.DisplayRole:
			return node.data(index.column())
		if role == QtCore.Qt.DecorationRole and self.ui_parent.IconOnOff():
			if not node.GetNodeType() == 'asset':
				image_path = self.folder_picture
				pixmap = convertPathToPixmap(image_path=image_path, width=20,height=20, added_name="tree_folder")
				return pixmap
			else:
				image_path = node.GetImage()
				if image_path:
					pixmap = convertPathToPixmap(image_path=image_path, width=75, height=75, added_name="tree_thumb")
					return pixmap
				else:
					return None
		return None

	def getPathFromIndex(self, index):
		node = index.internalPointer()
		path = node._path
		return path

	def getPathToThumbnail(self, index):
		node = index.internalPointer()
		pic_path = node.icon_dir
		return pic_path

	def getNode(self, index):
		return index.internalPointer()

	def update(self, index):
		pass

	def saveModelState(self, view, workingNode=None):
		expanded_folders = []
		for index in self.persistentIndexList():
			if view.isExpanded(index):
				expanded_folders.append(self.getNode(index).GetName())
		if workingNode != None:
			expanded_folders.append(workingNode.GetName())
		for name in expanded_folders:
			if name == '':
				expanded_folders.remove(name)

		return expanded_folders

		# if view.isExpanded(index):
		# index_list.append(index.data(Qt.DisplayRole).toString())

# class BaseNode(object):
# 	def __init__(self, node_name=None,node_type=None,path=None,asset_type=None,asset_category=None,_parent=None,children=[],row=0):
# 		self.path=path
# 		self.node_name = node_name
# 		self.node_type = node_type
# 		self.row = row
# 		self.column_count = 1
# 		self.work_files = []
# 		self.ref_files = []
# 		self.asset_step = None
# 		self._parent = _parent

# class ThumbnailNode(object):
# 	def __init__(self,_parent):
# 		self.pixmap = None
# 		self._parent = _parent
#
# 	def createPixmap(self):
# 		pass
#
# 	def getPixmap(self):
# 		return self.pixmap
#TODO Change GetImage to return the correct pixmap instead of a path, so we can premake the pixmaps
class CustomNode(object):
	# def __init__(self, node_info={},_parent=None):
	def __init__(self, column_count=1,children=[],row=0,node_name="root",node_type="root",asset_type=None,asset_category=None,path=None,_parent=None,work_files=[],icon=None):
		self._column_count = column_count
		self._row = row
		self.node_name = node_name
		self.node_type=node_type
		self.asset_type=asset_type
		self.asset_category=asset_category
		self._path=path

		self._parent = _parent
		self._children = children
		self.work_files = []
		self.ref_files = []
		self.work_check = True
		self.ref_check = True
		self.asset_step = None
		if self.asset_type == "RigModule":
			self.is_module = True
		else:
			self.is_module = False
		if self.node_type == "asset": #and work_files==[]and icon==None:
			self.icon=None
			self.UpdateNode()
		# self.quick_thumb = None

	def UpdateNode(self):
		# QtCore.QThreadPool.globalInstance().start(CollectAssetFilesThread(target_node=self))
		self.worker = Multiplicity.ThreadPool2.Worker(CollectAssetImageThread, target_node=self)
		script_thread_pool.addWorker(self.worker)
		# QtCore.QThreadPool.globalInstance().start(CollectAssetImageThread(target_node=self))

	# def createThumbnail(self,thumb_type=None):
	# 	if thumb_type == "quick":
	# 		self.quick_thumb = convertPathToPixmap(image_path=self.icon,width=100,height=100,added_name="_quickview_thumbnail")
	#
	# def getThumb(self, thumb_type=None):
	# 	if thumb_type == "quick":
	# 		print("Returning from %s - > %s" % (self.node_name,self.quick_thumb))
	# 		return self.quick_thumb

	def GetAssetStep(self):
		return self.asset_step

	def FindMayaWorkFiles(self):
		self.work_files = []
		work_folder = CC.get_asset_work_folder(**self.GetAssetInfo())
		# if(os.path.exists(work_folder)):
		try:
			work_content = os.listdir(work_folder)
			for con in work_content:
				if con[-3:] in [".ma",".mb"]:
					self.work_files.append((work_folder,con))
		except:
			pass


	def FindMayaRefFiles(self):
		self.ref_files = []
		ref_folder = CC.get_asset_ref_folder(**self.GetAssetInfo())

		if "Char/Module/" in ref_folder: #Special check for modules. A bit too hardcoded but it might work for now
			#TODO Fix so we can import moduless with selective namespaces
			# temp_dict = {}
			# temp_dict.update(self.GetAssetInfo())
			# temp_dict["asset_step"] = "Model"
			# model_ref = cfg_util.CreatePathFromDict(cfg.ref_paths["Model"],temp_dict)
			# if os.path.exists(model_ref):
			# 	self.ref_files.append((ref_folder,os.path.split(model_ref)[1]))
			# self.is_module=True
			temp_dict = {}
			pass
		else:
			# if (os.path.exists(ref_folder)):
			try:
				ref_content = os.listdir(ref_folder)
				# ref_content = os.scandir(ref_folder)
				for con in ref_content:
					# con = con_entry.name
					if con.endswith("_Render.mb") or con.endswith("_Anim.mb") or con.endswith("_Ingest.mb") or con.endswith("_Proxy.mb"): #hardcoded to only include output refs
						self.ref_files.append((ref_folder, con))
					if self.asset_type == "RigModule":
						if con.endswith(".mb"):
							self.ref_files.append((ref_folder, con))
					# if con.endswith(".ma") or con.endswith(".mb"): #For all refs
					# 	self.ref_files.append((ref_folder, con))
			except:
				pass

	def IsAssetAModule(self):
		return self.is_module

	def GetMayaRefFiles(self):
		if self.ref_check:
			self.FindMayaRefFiles()
			self.ref_check = False
		return self.ref_files

	def GetMayaWorkFiles(self):
		if self.work_check:
			self.FindMayaWorkFiles()
			self.work_check = False
		return self.work_files

	def GetImage(self):
		return self.icon

	def CheckImage(self):
		if self.node_type == "asset":
			thumbnail_path = CC.get_asset_thumbnail_path(**self.GetAssetInfo())
			if os.path.exists(thumbnail_path):
				self.icon = thumbnail_path
				return
		self.icon=None

	def GetNodeDict(self):
		return {"asset_type":self.asset_type,"asset_category":self.asset_category,"node_name":self.node_name,"path":self._path,"node_type":self.node_type,"children":self._children}

	def addChild(self, child):
		child._parent = self
		child._row = self.childCount()
		self._children.append(child)
		self._column_count = max(child.columnCount(), self._column_count)

	def GetPath(self):
		return self._path

	def GetName(self):
		# return self._name
		return self.node_name

	def GetChildren(self):
		return self._children

	def GetAssetType(self):
		# return self._type
		return self.asset_type

	def GetAssetCategory(self):
		return self.asset_category

	def GetNodeType(self):
		return self.node_type

	def GetAssetInfo(self):
		return {"asset_type":self.asset_type,"asset_category":self.asset_category,"asset_name":self.node_name}

	#### TREE NODE INFO ####
	def data(self, column):
		# if column == 0:
		return self.node_name
		# return self._name

	def columnCount(self):
		return self._column_count

	def ClearChildren(self):
		for cur_child in self._children:
			cur_child.ClearChildren()
			del cur_child
		self._children[:] = []

	def childCount(self):
		return len(self._children)

		# return len(self._children)

	def child(self, row):
		if row >= 0 and row < self.childCount():
			return self._children[row]

	def getAllChildren(self, cur_node=None):
		if not cur_node:
			cur_node = self
		return_list = []
		if self.node_type == "asset":
			return [self]
		for child in cur_node.GetChildren():
			if child.GetNodeType() == "asset":
				return_list.append(child)
			else:
				return_list.extend(self.getAllChildren(child))
		return return_list

	def parent(self):
		return self._parent

	def row(self):
		return self._row


def _maya_main_window():
	"""Return Maya's main window"""
	for obj in QtWidgets.QApplication.topLevelWidgets():
		if obj.objectName() == 'MayaWindow':
			return obj
	raise RuntimeError('Could not find MayaWindow instance')

class Popup(QtWidgets.QDialog):
    def __init__(self, parent=None, title='Popup'):
        super(Popup, self).__init__(parent)
        self.setWindowTitle(title)
        flags = self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint
        flags = flags | QtCore.Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)

def Run():
	objectName = 'AssetBrowserDock'
	if not MayaDockable.dockableExists(objectName):
		reloadModules.clearModules(["PublishAssets.PublishSetdress",
						 "PublishAssets.PublishSet",
						 "PublishAssets.PublishProp",
						 "PublishAssets.PublishChar",
						 "PublishAssets.PublishMaster",
						 "AssetFunctions",
						 "Maya_Functions.asset_util_functions",
						 "Maya_Functions.publish_util_functions",
						 "Maya_Functions.set_util_functions",
						 "Maya_Functions.vray_util_functions",
						 "Maya_Functions.general_util_functions",
						 "getConfig",
						 "ClearImportedModules"])
		MayaDockable.runDockable(objectName, 'Asset Browser', MainWindow())

	# mainWin = MainWindow(parent=_maya_main_window())
	# mainWin.resize(584, 662)
	# mainWin.show()
	# mainWin.raise_()

# def printMyThing():
# 	import pstats
# 	pr.enable()
# 	pr.disable()
# 	cur_stats = pstats.Stats(pr)
# 	cur_stats.sort_stats("cumulative")
# 	cur_stats.print_stats(15)
# 	pr.print_stats(sort=2)

if not in_maya:
	if __name__ == '__main__':
		import sys
		if not QtWidgets.QApplication.instance():
			app = QtWidgets.QApplication(sys.argv)
		else:
			app = QtWidgets.QApplication.instance()
		QtGui.QPixmapCache.clear()
		mainWin = MainWindow()
		mainWin.resize(584, 662)
		mainWin.show()
		# script_thread_pool.signals.finished.connect(printMyThing)
		# pr.disable()

	sys.exit(app.exec_())
