from PySide2 import QtWidgets, QtCore, QtGui
from Log.CoboLoggers import getLogger
logger = getLogger()
#This is the tales of woe 123
import Preview.file_util
import TB.updatePalettes

try:
	import maya.cmds as cmds
	in_maya = True
except:
	in_maya = False

import os


# import ClearImportedModules as CIM
# CIM.dropCachedImports("CategoryHandler","ffmpeg_wrapper","Multiplicity.Signals","CheckAudioVisual","PixmapUtil","getConfig","ClearImportedModules")

from Log.CoboLoggers import getLogger
logger = getLogger()

from getConfig import getConfigClass
CC = getConfigClass()

from runtimeEnv import getRuntimeEnvFromConfig
run_env = getRuntimeEnvFromConfig(config_class=CC)

import re
import shutil

import PublishReport as PR
import OIDManager

import ffmpeg_wrapper as ffmpeg
from Multiplicity import ThreadPool as thread_pool
from Multiplicity import ThreadPool2 as ThreadPool2
from Multiplicity.Signals import Signals
import CheckAudioVisual
from PixmapUtil import PixmapUtil
from CategoryHandler import CategoryHandler


from functools import partial
# from HookUp import HookUp
import subprocess
import json

import TB.Harmony_RR_RenderSubmit as SubmitTB
import TB.HarmonySceneSetup as SetupTB
import AfterEffectFunctions as SetupAE

if in_maya:
	import MayaDockable
	import reloadModules

##COLLECT IMAGE FROM MOV
"""
def execute_this_fn(self, progress_callback):
	c_in = self.preview_path #Take from here
	c_out = self.output_folder
	c_shot = self.shot
	cur_length = self.GetLength(c_in)
	times = [0.05, 0.5, 0.90] #DISREGARD THESE Just use [0.05]
	for cur_t in range(len(times)):
		temp_time = cur_length * times[cur_t]
		cur_file_out = "%s%s_%s.jpg" % (c_out, c_shot, cur_t) #SAVE HERE
		f = "ffmpeg -i %s -ss %s -y -frames 1 %s" % (c_in, temp_time, cur_file_out)
		subprocess.run(f, shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		progress_callback.emit((cur_t + 1) * 100 / len(times))
	return "Done."
"""

shot_dict = {"episode_name": "E26", "seq_name": "SQ030", "shot_name": "SH050"}
# anim_preview_file = cfg_util.CreatePathFromDict(cfg.project_paths["shot_animatic_file"], shot_dict)
anim_preview_file = CC.get_shot_animatic_file(**shot_dict)


# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# BACKEND ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


# REPOSITORY ---------------------------------------------------------------------------------------------------------

# TODO Have shot selection UI. Maybe a "To" - "From" selection window?

# TODO Make filter to only show shots with either renders or comp_file or comp_output or all of those.

# TODO add make scene-setup


class Node(object):
	def __init__(self, name=None, url=None, parent=None, type=None):
		self.__name = name
		self.__url = url
		self.__parent = parent
		self.__children = []
		self._row = 0
		self.__type = type
		self.__thumb_path = None
		self.comp_style = CC.project_style["default_comp_style"]
		self.animation_style = CC.project_style["default_animation_style"]
		self.title = None

		# children = self.__populate()
		# if isinstance(children, list):
		#     self.__children = children
		# else:
		#     raise TypeError("Method 'populate' must return type 'list'")

	def getTitle(self):
		return self.title

	def setTitle(self, title):
		self.title = title

	def getInfoDict(self):
		shot_dict = {}
		if self.__type == "episode":
			shot_dict = {}
			shot_dict["episode_name"] = self.__name
		if self.__type == "seq":
			shot_dict = {}
			shot_dict["episode_name"], shot_dict["seq_name"] = self.__name.split("_")
		if self.__type == "shot":
			shot_dict = {}
			shot_dict["episode_name"], shot_dict["seq_name"], shot_dict["shot_name"] = self.__name.split("_")
		return shot_dict

	def getAnimationStyle(self):
		return self.animation_style

	def getCompStyle(self):
		return self.comp_style

	def setAnimationStyle(self, animation_style):
		self.animation_style = animation_style

	def setCompStyle(self, comp_style):
		self.comp_style = comp_style

	def setThumbPath(self, new_path):
		self.__thumb_path = new_path

	def getThumbPath(self):
		return self.__thumb_path

	def getType(self):
		return self.__type

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

	def getUrl(self):
		return self.__url

	def getParent(self):
		return self.__parent

	def factory(self, name):
		return None

	def setChildren(self, c_list=None):
		self.__children = c_list
		self._row = len(self.__children)

	def getChildren(self):
		return self.__children

	def getAllChildren(self,cur_node=None):
		if not cur_node:
			cur_node = self
		return_list = []
		for child in cur_node.getChildren():
				if child.getType() =="shot":
					return_list.append(child)
				else:
					return_list.extend(self.getAllChildren(child))
		return return_list



class Shot(Node):
	"""Holds all thumbs for a shot: Directly contains 'string' objects in a dictionary"""

	def __init__(self, name, url, parent):
		super(Shot, self).__init__(name=name, url=url, parent=parent, type="shot")
		self.range = 0

	# def getInfoDict(self):
	#     cur_name = self.getName()
	#     shot_dict = {}
	#     shot_dict["episode_name"], shot_dict["seq_name"], shot_dict["shot_name"] = cur_name.split("_")
	#     return shot_dict

	# def setRange(self, new_range):
	#     self.range = new_range
	#
	# def getRange(self):
	#     return self.range

	# def factory(self, name):
	#     result = {"animatic": [], "anim": [], "comp": []}
	#     for thumb in os.listdir(self.__url + "/Thumbs"):
	#         if "animatic" in thumb:
	#             result["animatic"].append(thumb)
	#         elif "anim" in thumb:
	#             result["anim"].append(thumb)
	#         elif "comp" in thumb:
	#             result["comp"].append(thumb)
	#     return result


class Sequence(Node):
	"""Holds all shots for a sequence: Directly contains 'Shot' objects"""

	def __init__(self, name, url, parent):
		super(Sequence, self).__init__(name=name, url=url, parent=parent, type="seq")

	def factory(self, name):
		return Shot(name=name, url=self.getUrl() + "/" + name, parent=self)


class Episode(Node):
	"""Holds all sequences for a episode: Directly contains 'Sequence' objects"""

	def __init__(self, name, url, parent):
		super(Episode, self).__init__(name=name, url=url, parent=parent, type="episode")

	def factory(self, name):
		return Sequence(name=name, url=self.getUrl() + "/" + name, parent=self)


class Repository(Node):
	"""Holds all episodes and higher methods for retrieving specific data: Directly contains 'Episode' objects"""

	def __init__(self, content, content_dict):
		self.__content = content
		self.__content_dict = content_dict

	def getEpisode(self, name):
		return self.__content_dict[name]["children"]

	def getType(self, name):
		return self.__content_dict[name]["type"]

	def GetByParent(self, parent_name, recursive_look=False):
		if recursive_look:
			pass
		return self.__content_dict[parent_name]["children"]

	def GetByName(self, name):
		if name in self.__content_dict.keys():
			return self.__content_dict[name]
		else:
			return None

	def GetByFilter(self, name_filter=None, type_filter=None, parent_filter=None):
		return_list = []
		filter_list = [name_filter, type_filter, parent_filter]
		for c_con in self.__content_dict.keys():
			if name_filter:
				if not name_filter in c_con:
					continue
					# key_list.append(c_con)
			if type_filter:
				if not self.__content_dict[c_con]["type"] == type_filter:
					continue
					# key_list.append(c_con)
			if parent_filter:
				if self.__content_dict[c_con]["parent"]:
					if not self.__content_dict[c_con]["parent"].getName() == parent_filter:
						continue
				else:
					continue

			return_list.append(self.__content_dict[c_con]["object"])

		# for c_name in key_list:
		#     return_list.append(self.__content_dict[c_name]["object"])
		# return_list = sorted(return_list,  key=lambda([x.getName() for x in return_list]))
		return return_list


class RepositoryFactory(object):
	"""Creates repository type objects"""

	def __init__(self, filmPath):
		self.__filmPath = filmPath
		self.__footage_dict = {}

	def __createEpisodes(self):
		dirs = os.listdir(self.__filmPath)
		result = []
		for episodename in dirs:
			# if not "E" in episodename or len(episodename) > 3:
			#     continue
			if not self.FindEpisode(episodename):
				continue
			episode = Episode(episodename, self.__filmPath + "/" + episodename, None)

			self.__footage_dict[episodename] = {}
			self.__footage_dict[episodename]["object"] = episode
			self.__footage_dict[episodename]["children"] = []
			self.__footage_dict[episodename]["parent"] = None
			self.__footage_dict[episodename]["type"] = "episode"

			episode.append(self.__createSequences(episode))
			result.append(episode)
			episode.setChildren(self.__footage_dict[episodename]["children"])

		return result

	def __createSequences(self, episode):
		dirs = os.listdir(episode.getUrl())
		result = []
		for sequencename in dirs:
			# if "PREVIS" in sequencename or "TEST" in sequencename:
			#     continue
			if not self.FindSequence(sequencename):
				continue

			sequence = Sequence(sequencename, episode.getUrl() + "/" + sequencename, episode)
			self.__footage_dict[episode.getName()]["children"].append(sequence)
			self.__footage_dict[sequencename] = {}
			self.__footage_dict[sequencename]["object"] = sequence
			self.__footage_dict[sequencename]["type"] = "seq"
			self.__footage_dict[sequencename]["children"] = []
			self.__footage_dict[sequencename]["parent"] = episode

			sequence.append(self.__createShots(sequence))
			sequence.setChildren(self.__footage_dict[sequencename]["children"])
			result.append(sequence)

		return result

	def __createShots(self, sequence):
		dirs = os.listdir(sequence.getUrl())
		result = []
		for shotname in dirs:
			# if "Preview" in shotname or "PREVIS" in shotname:
			#     continue
			if not self.FindShot(shotname):
				continue

			shot = Shot(shotname, sequence.getUrl() + "/" + shotname, sequence)

			self.__footage_dict[shotname] = {}
			self.__footage_dict[sequence.getName()]["children"].append(shot)
			self.__footage_dict[shotname]["object"] = shot
			self.__footage_dict[shotname]["type"] = "shot"
			self.__footage_dict[shotname]["children"] = []
			self.__footage_dict[shotname]["parent"] = sequence

			result.append(shot)

		return result

		# REGEX FOR CHECKING FOLDER NAMES:

	def FindEpisode(self, content):
		# test = "^(s)\d{3}$"
		low_case = content.lower()
		# re_compile = re.compile("^(s)\d{3}$")
		re_compile = re.compile("%s$" % CC.episode_regex)
		if re_compile.search(low_case):
			return True
		else:
			return False

	def FindSequence(self, content):
		low_case = content.lower()
		re_compile = re.compile("%s%s$" % (CC.episode_regex, CC.seq_regex))
		if re_compile.search(low_case):
			return True
		else:
			return False

	def FindShot(self, content):
		low_case = content.lower()
		# re_compile = re.compile("^(s)\d{3}(_sq)\d{3}(_sh)\d{3}$")
		re_compile = re.compile(
			"%s%s%s$" % (CC.episode_regex, CC.seq_regex, CC.shot_regex))
		if re_compile.search(low_case):
			return True
		else:
			return False

	def create(self):
		# Create episode objects
		episodes = self.__createEpisodes()
		repository = Repository(episodes, self.__footage_dict)
		return repository


# VIEWER -------------------------------------------------------------------------------------------------------------
class TreeModel(QtCore.QAbstractItemModel):
	def __init__(self, nodes, pixmap_util):
		QtCore.QAbstractItemModel.__init__(self)
		self.root = Node("root", "", None)
		self.__pixmap_util = pixmap_util
		# self.folder_picture = cfg_util.CreatePathFromDict(cfg.thumbnail_paths["folder_icon_path"])
		self.folder_picture = CC.get_folder_icon_path()
		# self.no_thumb_picture = cfg_util.CreatePathFromDict(cfg.thumbnail_paths["no_thumb_icon_path"])
		self.no_thumb_picture = CC.get_no_thumb_icon_path()
		self.nodes = nodes
		self.root.setChildren(nodes)


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

	def data(self, index, role):
		if not index.isValid():
			return None
		node = index.internalPointer()
		if role == QtCore.Qt.DisplayRole:
			if node.getTitle():
				return "%s_%s" % (node.getName(), node.getTitle())
			return node.getName()
		if role == QtCore.Qt.DecorationRole:
			image_path = self.folder_picture
			if not node.getType() == "shot":
				pixmap = self.__pixmap_util.convertPathToPixmap(cache_name=None, image_path=image_path, width=20,
																height=20, added_name="tree_folder")
			else:
				pixmap = self.__pixmap_util.convertPathToPixmap(cache_name=node.getName(),
																image_path=node.getThumbPath(), width=80, height=45,
																added_name="_tree")

			# return convertPathToPixmap(cache_name=cur_node.getName(), image_path=cur_node.getThumbPath())
			return pixmap
			# else:
			#     image_path = node.GetImage()
			#     pixmap = convertPathToPixmap(image_path=image_path, width=75, height=75, added_name="tree_thumb")
			#     return pixmap
		return None

	# def getPathFromIndex(self, index):
	#     node = index.internalPointer()
	#     path = node._path
	#     return path

	# def getPathToThumbnail(self, index):
	#     node = index.internalPointer()
	#     pic_path = node.icon_dir
	#     return pic_path

	def getNode(self, index):
		return index.internalPointer()

	def getNodes(self, list_of_index):
		result = []
		for index in list_of_index:
			node = self.getNode(index)
			if node:
				result.append(node)
		return result

	def update(self, index):
		pass

	# def saveModelState(self, view, workingNode=None):
	#     expanded_folders = []
	#     for index in self.persistentIndexList():
	#         if view.isExpanded(index):
	#             expanded_folders.append(self.getNode(index).GetName())
	#     if workingNode != None:
	#         expanded_folders.append(workingNode.GetName())
	#     for name in expanded_folders:
	#         if name == '':
	#             expanded_folders.remove(name)
	#
	#     return expanded_folders

	# if view.isExpanded(index):
	# index_list.append(index.data(Qt.DisplayRole).toString())


# Add unique name and size arguments?
class TableModel(QtCore.QAbstractListModel):
	"""
	How to get selected nodes from View of current TableModel object.

	Consider <QListView> to be a view widget having a user selection, this is important
	because the view contains the selection.

	We get the model containing all nodes and query by index, inputting selected indexes
	from the view.

	Syntax:
	<QListView>.model().getNodesByIndex(<QListView>.selectedIndexes()).
	"""

	def __init__(self, name=None, nodes=None, pixmap_util=None):
		super(TableModel, self).__init__()
		self.pixmap_util = pixmap_util
		# self.__picture_placeholder = cfg_util.CreatePathFromDict(cfg.thumbnail_paths["no_thumb_icon_path"])
		self.nodes = nodes
		if self.nodes:
			self.nodes = sorted(self.nodes, key=lambda x: x.getName())
		elif self.nodes == None:
			self.nodes = []
		if not name:
			self.setObjectName("DefaultModel")
		else:
			self.setObjectName(name)

	def getAllNodes(self):
		return self.nodes

	def addNode(self, node):
		self.nodes.append(node)
		self.nodes = sorted(self.nodes)

	def addNodes(self, nodes):
		self.nodes.extend(nodes)
		self.nodes = sorted(self.nodes)

	def removeNode(self, node):
		self.nodes.remove(node)

	def removeAllNodes(self):
		self.nodes = []

	def getNode(self, index):
		# TODO Possible overhead from complicated procedure of conditions. Consider that this method is constantly
		#  called from self.getNodesByIndex(). See TreeModel.getNode()'s use of index.internalPointer() method.
		if index.isValid():
			r = index.row()
			try:
				node = self.nodes[r]
				return node
			except IndexError:
				return None
		return None

	def getNodesByIndex(self, indexes):
		return_list = []
		for c_i in indexes:
			i = self.getNode(c_i)
			if i:
				return_list.append(i)
		return return_list

	def rowCount(self, parent=None):
		"""Implemented due to 'QtCore.QAbstractListModel' abstract requirements"""
		return len(self.nodes)

	def data(self, index, role):

		if not index.isValid():
			logger.warning("Index is not valid")
			return None

		cur_row = index.row()
		cur_node = self.nodes[cur_row]

		if role == QtCore.Qt.TextAlignmentRole:
			return int(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)

		if role == QtCore.Qt.DisplayRole:
			return cur_node.getName()
		# if role == QtCore.Qt.TextAlignmentRole:
		#     return QtCore.Qt.AlignTop()
		#     # return QtCore.Qt.AlignVCenter()
		if role == QtCore.Qt.DecorationRole:
			# image_path = self.__picture_placeholder
			# qimg = QtGui.QImage(image_path)
			# pixmap = convertPathToPixmap(image_path,160,90,"",False)
			if cur_node.getType() == "shot":
				return self.pixmap_util.convertPathToPixmap(cache_name=cur_node.getName(),
															image_path=cur_node.getThumbPath())
			else:
				return self.pixmap_util.convertPathToPixmap(cache_name="TableFolder")


class ToFromTableModel(TableModel):
	def __init__(self, name=None, nodes=None, pixmap_util=None):
		super(ToFromTableModel, self).__init__(name, nodes, pixmap_util)

	def data(self, index, role):
		if not index.isValid():
			logger.warning("Index is invalid")
			return None

		cur_row = index.row()
		cur_node = self.nodes[cur_row]

		if role == QtCore.Qt.TextAlignmentRole:
			return int(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)

		if role == QtCore.Qt.DisplayRole:
			return cur_node.getName()

		if role == QtCore.Qt.DecorationRole:

			if cur_node.getType() == "shot":
				return self.pixmap_util.convertPathToPixmap(cache_name=cur_node.getName(),
															image_path=cur_node.getThumbPath(),
															width=320, height=180, added_name="ToFrom")
			else:
				return self.pixmap_util.convertPathToPixmap(cache_name="TableFolder")


# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# CONTROL-LAYER ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


class FrontController(QtCore.QObject):
	def __init__(self):
		super(FrontController, self).__init__()
		self.signals = Signals()
		# filmPath = cfg_util.CreatePathFromDict(cfg.project_paths["film_path"])
		self.__repository = RepositoryFactory(filmPath=CC.get_film_path()).create()
		# self.saveNodeInfo()
		self.loadNodeInfo()
		self.__pixmapUtil = PixmapUtil()
		self.__threadPool = thread_pool.ThreadPool()
		self.__ffmpeg = ffmpeg.FFMPEG()

		self.OIDM = OIDManager.OID_Functions()

		self.pr = PR.PublishReport()
		self.intiate_publish_report = False

		# self.__AV = CheckAudioVisual
		# self.__hookUp = HookUp()

		self.__imgTable = None
		self.__imgTree = None
		self.__toTable = None
		self.__fromTable = None

		self.to_node_list = []  # list to hold nodes that goes into toTable
		self.from_node = []  # Node that goes into fromTable

		self.__categoryHandler = CategoryHandler()

		self.__threadPool.signals.progressbar_init.connect(self.signals.progressbar_init.emit)
		self.__threadPool.signals.progressbar_value.connect(self.signals.progressbar_value.emit)
		# self.__threadPool.signals.progressbar_reset.connect(self.signals.progressbar_reset.emit)
		self.__threadPool.signals.ch01.connect(self.ThreadPoolFinished)
		# self.__threadPool.signals.ch03.connect(self.signals.ch03.emit)
		# self.__threadPool.signals.thread_result.connect(self.signals.thread_result.emit)
		# self.ClearPixCache()

		# self.runSetRangeOnAllEpisodes()

	# TODO MAKE EVENT TO SET STYLES/TITLE ON RIGHT CLICK
	def loadNodeInfo(self, cur_node=None):
		logger.debug("Loading node information")
		episodes = self.__repository.GetByFilter(type_filter="episode")
		if "episode_info_file" in CC.__dict__.keys():
			for ep in episodes:
				ep_info_file = CC.get_episode_info_file(episode_name=ep.getName())
				ep_info_dict = self.loadSettings(ep_info_file)
				if ep_info_dict:
					for info_node_name in ep_info_dict.keys():
						info_node_dict = self.__repository.GetByName(info_node_name)
						if info_node_dict:
							info_node = info_node_dict["object"]
							for set_info in ep_info_dict[info_node_name].keys():
								if set_info == "title":
									info_node.setTitle(ep_info_dict[info_node_name][set_info])
								if set_info == "animation_style":
									info_node.setAnimationStyle(ep_info_dict[info_node_name][set_info])
									if info_node_dict["type"] == "seq":
										self.setInfoOnChildren(info_node, "animation_style",
															   ep_info_dict[info_node_name][set_info])
								if set_info == "comp_style":
									info_node.setCompStyle(ep_info_dict[info_node_name][set_info])
									if info_node_dict["type"] == "seq":
										self.setInfoOnChildren(info_node, "comp_style", ep_info_dict[info_node_name][set_info])
								# if info_node_dict["type"] == "seq":
								#     for child_node in info_node_dict["children"]:
								#         if set_info == "animation_style":
								#             child_node.setAnimationStyle(ep_info_dict[info_node_name][set_info])
								#         if set_info == "comp_style":
								#             child_node.setCompStyle(ep_info_dict[info_node_name][set_info])

	def get_ftp_directory(self, user):
		ftp_folder = CC.get_ftp_path()
		if os.path.exists(ftp_folder):
			from_path = os.path.join(ftp_folder, '_ANIMATION', user, 'FROM_CB').replace(os.sep, '/').replace('//', os.sep + os.sep)

			# Making sure folders exists
			for path in [from_path, from_path.replace('FROM_CB', 'TO_CB')]:
				if not os.path.exists(path):
					try:
						os.makedirs(path)
					except:
						logger.warning("Can't access " + path)

			return from_path

		else:
			return None

 
	def setInfoOnChildren(self, parent_node=None, c_key=None, c_value=None):
		for child_node in parent_node.getChildren():
			if c_key == "animation_style":
				child_node.setAnimationStyle(c_value)
			if c_key == "comp_style":
				child_node.setCompStyle(c_value)
			self.setInfoOnChildren(parent_node=child_node, c_key=c_key, c_value=c_value)

	def publishAnimation(self, nodes=[]):
		from Multiplicity.ThreadPool2 import ThreadPool, Worker
		from PublishAnimScene import RunMayaPy

		final_nodes = []
		for node in nodes:
			if node.getType() in ['episode','seq']:
				final_nodes.extend(node.getAllChildren())
			elif node.getType() == 'shot':
				final_nodes.append(node)

		pool = ThreadPool()
		workers = []

		for cur_node in nodes:
			if cur_node.getAnimationStyle() == 'Maya':
				info_dict = cur_node.getInfoDict()
				scene_path = CC.get_shot_anim_path(**info_dict)
				worker = Worker(RunMayaPy, scene_path, True)
				pool.addWorker(worker)
				workers.append(worker)

		pool.signals.finished.connect(lambda: self.deletePool(pool))
		pool.run()


	def deletePool(self, pool):
		del pool


	def publishReport(self, parent=None, type='Overview', scope=None,filter_type=None):
		title = scope + ' - Shot info'
		popup = Popup(parent=parent, title=title)
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
		popup.popupSetPalette()
		popup.show()
		QtWidgets.QApplication.processEvents()

		if not self.intiate_publish_report:
			self.pr.getData(scope="Assets")
		self.pr.getData(scope=scope)

		if type.lower() == 'overview':
			_string = self.formatScopeOverview(scope)
		elif type.lower() == 'breakdown':
			_string = self.formatScopeBreakdown(scope)

		infoWidget = QtWidgets.QWidget()
		infoLayout = QtWidgets.QVBoxLayout()
		infoLayout.setMargin(0)
		infoWidget.setLayout(infoLayout)

		infoLabel = QtWidgets.QPlainTextEdit(_string, readOnly=True)
		infoLayout.addWidget(infoLabel)

		popupLayout.removeWidget(loadingWidget)
		popupLayout.addWidget(infoWidget)

		popup.resize(300, 450)

	def formatScopeOverview(self, scope):
		assetDict = self.pr.gatherShotAssetLists(scope=scope,
											step_list=["AnimScene", "LightScene"],
											filter_type=['Char', 'Prop', 'Setdress', 'Set'])

		usedAssets = {}
		for shot, assets in assetDict.items():
			for asset in assets:
				if asset:
					print(asset)
					type, category, name = asset.split('_')
					if type not in usedAssets.keys():
						usedAssets[type] = []
					if name not in usedAssets[type]:
						usedAssets[type].append(name)

		_string = ''
		tab = '    '
		lineBreak = '\n'
		for type, names in usedAssets.items():
			_string = _string + tab + type
			for name in names:
				_string = _string + lineBreak + 2*tab + name
			_string = _string + lineBreak

		return _string

	def formatScopeBreakdown(self, scope):
		assetDict = self.pr.gatherShotAssetLists(scope=scope,
											step_list=["AnimScene", "LightScene"],
											filter_type=['Char', 'Prop', 'Setdress', 'Set'])
		_string = ''
		tab = '    '
		lineBreak = '\n'
		for shot, assets in sorted(assetDict.items()):
			_string = _string + tab + shot
			sortedAssetDict = {}
			for asset in assets:
				if asset.split('_')[0] not in sortedAssetDict.keys():
					sortedAssetDict[asset.split('_')[0]] = []
				sortedAssetDict[asset.split('_')[0]].append(asset.split('_')[2])
			for type, names in sortedAssetDict.items():
				_string = _string + lineBreak + 2*tab + type
				for name in names:
					_string = _string + lineBreak + 3 * tab + name
			_string = _string + lineBreak * 2

		return _string


	def buildOIDBasedOnPublishReport(self, scope=None):
		"""
		Add the rule for a sequence, based on the publish reports.
		:param scope: example: E15_SQ010
		:return:
		"""
		if not self.intiate_publish_report:
			self.pr.getData(scope="Assets")
		self.pr.getData(scope=scope)
		shot_list = self.pr.gatherShotAssetLists(scope)
		# self.OIDM.CreateRulesFromPublishData(scope=scope,shot_list=shot_list)
		self.OIDM.CreateSmartRulesFromPublishData(scope=scope, shot_list=shot_list)

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

	def saveNodeInfo(self, cur_node=None, info_keys=[], clear=False):
		info_dict = cur_node.getInfoDict()
		name = cur_node.getName()
		# save_dict = {'E90': {'TITLE': 'TestingVFX'},
		#              'E90_SQ010': {
		#         'TITLE': 'FirstTry',
		#         'animation_style': 'Toonboom',
		#         'comp_style': 'AE'}}
		# info_dict = cur_node.getInfoDict()
		ep_info_file = CC.get_episode_info_file(**info_dict)
		old_dict = self.loadSettings(ep_info_file)
		if not clear:
			save_content = {}
			for cur_key in info_keys:
				if cur_key == "title":
					save_content['title'] = cur_node.getTitle()
				if cur_key == "animation_style":
					save_content["animation_style"] = cur_node.getAnimationStyle()
				if cur_key == "comp_style":
					save_content["comp_style"] = cur_node.getCompStyle()
			save_content = {name: save_content}
			if name in old_dict.keys():
				old_dict[name].update({k: v for k, v in save_content[name].items() if v is not None})
			else:
				old_dict.update(save_content)

		else:
			if name in old_dict.keys():
				old_dict.pop(name)

		self.saveSettings(ep_info_file, old_dict)

	def ThreadPoolFinished(self):
		# print("FINISHED WITH THREADS")
		self.__imgTable.beginResetModel()
		self.__imgTable.endResetModel()
		# pass
		# self.__imgTree.update()
		# self.__imgTree.endResetModel()

	# def ThreadUpdateModel(self, temp_dict):
	#     print("UPDATING MODEL")
	#     print(temp_dict["result"])
	#     self.__imgTable.findIndexFromNode(temp_dict["result"])

	def setThumbSize(self, size):
		self.__pixmapUtil.setSize(size)

	def getCategories(self):
		return self.__categoryHandler.getCategories()

	def getCategoryNodes(self, category):
		cur_nodes = self.__categoryHandler.getCategoryNodes(category)
		return_list = []
		if cur_nodes:
			for cur_node in cur_nodes:
				return_list.append((self.__repository.GetByName(cur_node))["object"])
		return return_list

	def CreateCategory(self, name="", list_of_nodes=[]):
		new_category = self.__categoryHandler.CreateNewCategory(name, list_of_nodes)
		return new_category

	def deleteCategory(self, category):
		self.__categoryHandler.DeleteCategory(category)

	def AddToCategory(self, category="", list_of_nodes=[]):
		self.__categoryHandler.AddToCategory(category, list_of_nodes)

	def RemoveFromCategory(self, category="", list_of_nodes=[]):
		self.__categoryHandler.RemoveFromCategory(category, list_of_nodes)

	def findShotsInParent(self, cur_node):
		to_return = []
		if cur_node.getType() == "shot":
			to_return.append(cur_node)
		else:
			cur_children = cur_node.getChildren()
			for cur_child in cur_children:
				to_return.extend(self.findShotsInParent(cur_child))
		return to_return

	def createPixmapsFromParent(self, parent_node):
		threads = self.__pixmapUtil.createFactoryThreads(parent_node=parent_node)
		self.__threadPool.startBatch(workers=threads)

	def createPixmap(self, cur_node=None, overwrite=False, overwrite_cache=False):
		threads = [
			self.__pixmapUtil.createFactoryThread(node=cur_node, overwrite=overwrite, overwrite_cache=overwrite_cache)]
		self.__threadPool.startBatch(workers=threads)

	def ClearPixCache(self):
		# print("CLEARING CACHE")
		QtGui.QPixmapCache.clear()
		self.__threadPool.cancelBatch()

	def zipFolders(self, nodes, destination=None, user_name="zip", local=True):
		if local:
			import zipUtil
		else:
			import RoyalRender.submit
		
		shots = []
		for node in nodes:
			if node.getType() == 'episode':
				for sequence in node.getChildren():
					for shot in sequence.getChildren():
						shots.append(shot)
			elif node.getType() == 'seq':
				for shot in node.getChildren():
					shots.append(shot)
			else:
				shots.append(node)

		print('')
		for shot in shots:
			if shot.getCompStyle() == 'AE':
				info = shot.getInfoDict()
				shot_path = CC.get_shot_path(**info)
				shot_content = os.listdir(shot_path)
				shot_folders = []

				for s_con in shot_content:
					s_path = "%s/%s" % (shot_path, s_con)
					if os.path.isdir(s_path):
						shot_folders.append(s_con)
				folder = self.FindVersion(name_list=shot_folders, file_regex="(%s)" % shot.getName().lower(),
												file_ext="")[0]
				
				source = shot_path + '/' + folder
				if not destination:
					dest = source + '.zip'
				else:
					dest = destination + '/' + folder + '.zip'

				if local:
					zipUtil.zip([source, CC.get_shot_sound_file(**info)], dest)
					print(' >> Done zipping ' + source + '\n')
				else:
					_string = "@echo off\n\npython "+ CC.get_python_path() +"zipUtil.py " + source + ' ' + CC.get_shot_sound_file(**info) + ' ' + dest + "\n\nEXIT /B 0"
					_string = _string.replace('T:/', '\\\\192.168.0.225/tools/')
					if CC.project_name in ['MiasMagic2', 'Boerste-Season2']:
						_string = _string.replace('P:/', '\\\\192.168.0.235/projekter/')
					else:
						_string = _string.replace('P:/', '\\\\192.168.0.225/production/')

					temp_folder = shot_path
					if not os.path.exists(temp_folder):
						os.mkdir(temp_folder)
					batchPath = os.path.join(temp_folder + '/' + shot.getName() + '_Zip.bat')
					batchPath = os.path.abspath(batchPath).replace(os.sep, '/')
					logger.debug(_string)
					with open(batchPath, 'w') as batchFile:
						batchFile.write(_string)

					project_name = CC.project_name
					# client_pool = 'ALL'
					client_pool = 'PythonJobs' # TODO: CREATE RR POOL
					user_name = 'zip'
					RoyalRender.submit.batchScriptSubmit(batchPath, project_name=project_name, client_pool=client_pool, user_name=user_name, priority=90,episode="zip")

		print(' >> BATCH DONE << \n')

	def refreshThumbs(self, cur_nodes=[], overwrite=True, overwrite_cache=False, use_threads=True):
		"""Finds the paths to the highest level of thumbnail, then creates a pixmap from that.
		If no thumbnail is found or 'overwrite' is True, it looks for the footage to make a thumbnail out from.
		If 'overwrite_cache' is True, it replaces the pixmap key in the pixmap cache.
		Added option to not use threads, because it seemed like threads where giving us issues in UI.
		Fixed it by running a pixmap remake after its done rebuilding
		"""
		# self.__imgTable.beginResetModel()
		# self.__imgTree.beginResetModel()
		if use_threads:
			threads = []
			for shot in cur_nodes:
				threads.append(self.__pixmapUtil.createFactoryThread(node=shot, overwrite=overwrite,
																	 overwrite_cache=overwrite_cache))

			self.__threadPool.startBatch(workers=threads, use_max=True)
			# print("No Threads: Total time elapsed: {:.4f}s".format(time.time() - start_time))
		# self.__imgTable.endResetModel()

	def updateViewState(self, new_view_state):
		self.__pixmapUtil.changeViewState(view_state=new_view_state)

	def FindVersion(self, name_list=[], file_regex="", version_regex="(_v)(\d{3})", file_ext=""):
		to_return = None
		version = 0
		version_file = None
		for name in sorted(name_list):
			if file_ext == "" or name.endswith(file_ext):
				v_name = name.lower()
				re_compile = re.compile("%s%s" % (file_regex, version_regex))
				re_search = re_compile.search(v_name)
				if re_search:
					if version <= int(re_search.groups()[-1]):
						version = int(re_search.groups()[-1])
						version_file = name
		if version == 0:
			logger.debug("Cannot find version in %s" % name_list)
			version = None
			v_compile = re.compile("%s" % file_regex)

			for name in sorted(name_list):
				if file_ext == "" or name.endswith(file_ext):
					temp_name = name.lower()
					re_search = v_compile.search(temp_name)
					if re_search:
						version_file = name
		logger.info("Found: %s version: %s" % (version_file, version))
		if version_file:
			to_return = [version_file]
			if version:
				to_return = [version_file, version]
		return to_return

	def openDir(self, folder_path):
		"""Opens folder"""
		if os.path.exists(folder_path):
			os.startfile(folder_path)
		else:
			logger.warning("Can't find path: %s" % folder_path)

	def newPopup(self, warning="Warning", info="info info info", title="Hey you"):
		popup = QtWidgets.QMessageBox()
		popup.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
		popup.setIcon(QtWidgets.QMessageBox.Information)
		popup.setText(warning)
		popup.setInformativeText(info)
		popup.setWindowTitle(title)
		popup.setStandardButtons(
			QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel)
		reply = popup.exec_()

		if reply == QtWidgets.QMessageBox.Yes:
			return "yes"
		elif reply == QtWidgets.QMessageBox.No:
			return "no"
		else:
			return "cancel"
	
	def openMayaFile(self, file_path=None, ask=True):
		# If Maya is open ------------------------------
		if in_maya == True:
			if ask and cmds.file(q=True, mf=True):
				save_before_open = self.newPopup("You are about to open another Maya file",
												 "Do you want to save your current work before you continue?",
												 "Warning")
				if save_before_open == "yes":

					# cmds.file(save=True, type="mayaAscii")
					cmds.file(save=True)

				elif save_before_open == "cancel":
					return True
			########################^^^^^^^^^^####################Save file here ##############################################

			if not file_path:
				cmds.file(new=True, f=True)
				cmds.file(mf=False)
				return True

			cmds.file(file_path, open=True, f=True)
			cmds.file(mf=False)
			return True
		else:
			if file_path:
				if os.path.exists(file_path):  # If running UI without maya, open scene in a new maya.
					run_command = 'START maya -file "%s"' % file_path
				else:
					logger.warning("Can't find file: %s" % file_path)
					return False
			else:
				run_command = 'START maya'
			subprocess.Popen(run_command, shell=True, env=run_env)

	def openTooonboomFile(self, file_path):
		# toonboom_env = run_env
		# toonboom_env[""] = ;
		run_command = 'wstart-wcc.exe HarmonyPremium.exe -scene "%s"' % file_path
		subprocess.Popen(run_command, shell=True, env=run_env)

	def openAEFile(self, file_path):
		run_command = 'START afterfx.exe "%s" -m' % file_path
		subprocess.Popen(run_command, shell=True, env=run_env)

	def openFusionFile(self, file_path):
		run_command = '"%s"' % file_path  #Removed START and fusion from the cmd, to avoid that the file is opened in a seperate instance of fusion instead of the one running.
		subprocess.Popen(run_command, shell=True, env=run_env)
		# subprocess.Popen(run_command,shell=True)

	def openAnimationFile(self, cur_node=None):
		"""
		should check type of node style : maya/toonboom
		:param cur_node:
		:return:
		"""
		info_dict = cur_node.getInfoDict()

		if cur_node.getAnimationStyle() == "Maya":
			scene_path = CC.get_shot_anim_path(**info_dict)
			self.openMayaFile(scene_path)
			return True
		if cur_node.getAnimationStyle() == "AE":
			scene_path = CC.get_shot_path(**info_dict)
			latest = self.FindVersion(name_list=os.listdir(scene_path), file_regex="(%s)" % cur_node.getName().lower(),file_ext=".aep")
			self.openAEFile("%s/%s" % (scene_path,latest[0]))

		if cur_node.getAnimationStyle() == "Toonboom":
			# Find latest version of the scene to open

			# shot_path = CC.get_shot_path(**info_dict)
			# shot_content = os.listdir(shot_path)
			# shot_folders = []
			#
			# for s_con in shot_content:
			#     s_path = "%s/%s" % (shot_path, s_con)
			#     if os.path.isdir(s_path):
			#         shot_folders.append(s_con)
			# folder_version = self.FindVersion(name_list=shot_folders, file_regex="(%s)" % cur_node.getName().lower(),
			#                                   file_ext="")
			# if folder_version:
			#     latest_folder = "%s/%s" % (shot_path, folder_version[0])
			#     if os.path.exists(latest_folder):
			#         find_shot_version = self.FindVersion(name_list=os.listdir(latest_folder),
			#                                              file_regex="(%s)*?" % cur_node.getName().lower(),
			#                                              file_ext=".xstage")
			#         if find_shot_version:
			#             scene_path = "%s/%s" % (latest_folder, find_shot_version[0])
			#             self.openTooonboomFile(scene_path)
			#             return True
			# logger.warning("Can't find animation file for: %s" % cur_node.getName())
			# return False
			scene_path = self.findToonboomAnimationFile(cur_node=cur_node)
			if scene_path:
				self.openTooonboomFile(scene_path)
		logger.debug("No match of animation style")
		return False

	def findToonboomAnimationFile(self,cur_node):
		info_dict = cur_node.getInfoDict()
		shot_path = CC.get_shot_path(**info_dict)
		shot_content = os.listdir(shot_path)
		shot_folders = []

		for s_con in shot_content:
			s_path = "%s/%s" % (shot_path, s_con)
			if os.path.isdir(s_path):
				shot_folders.append(s_con)
		folder_version = self.FindVersion(name_list=shot_folders, file_regex="(%s)" % cur_node.getName().lower(),
										  file_ext="")
		if folder_version:
			latest_folder = "%s/%s" % (shot_path, folder_version[0])
			if os.path.exists(latest_folder):
				find_shot_version = self.FindVersion(name_list=os.listdir(latest_folder),
													 file_regex="(%s)*?" % cur_node.getName().lower(),
													 file_ext=".xstage")
				if find_shot_version:
					scene_path = "%s/%s" % (latest_folder, find_shot_version[0])
					return scene_path
		logger.warning("Can't find animation file for: %s" % cur_node.getName())
		return False

	def createPreviewFromToonboom(self,cur_node):
		shot_name = cur_node.getName()
		logger.info("Trying to make preview off: %s" % shot_name)
		scene_path = self.findToonboomAnimationFile(cur_node=cur_node)
		if scene_path:
			script = "include('CB_CreateAnimPreview_WithSlate.js');runAnimPreview();"
			tb_cmd = 'HarmonyPremium -script "%s" -scene "%s"' % (script, scene_path)
			logger.info("Cmd: %s" % tb_cmd)
			tb_subp = subprocess.Popen(tb_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=run_env)
			out,err = tb_subp.communicate()
			print(err)
			logger.info("Finished with preview off: %s" % shot_name)


	def openCompFile(self, cur_node=None):
		info_dict = cur_node.getInfoDict()
		if cur_node.getCompStyle() == "Fusion":
			scene_folder = CC.get_shot_comp_folder(**info_dict)
			if os.path.exists(scene_folder):
				find_version = self.FindVersion(
					name_list=os.listdir(scene_folder),
					file_regex="(%s)*?" % cur_node.getName().lower(),
					file_ext=".comp"
				)
				if find_version:
					scene_path = "%s%s" % (scene_folder, find_version[0])
					logger.debug("Trying to open {scene_path}".format(scene_path=scene_path))
					self.openFusionFile(scene_path)
					return True
				else:
					logger.debug("No comp found, opening folder instead")
					self.openDir(scene_folder)

		if cur_node.getCompStyle() == "AE":
			scene_folder = CC.get_shot_comp_folder(**info_dict)
			if os.path.exists(scene_folder):
				find_version = self.FindVersion(name_list=os.listdir(scene_folder),
												file_regex="(%s)*?" % cur_node.getName().lower(), file_ext=".aep")
				if find_version:
					scene_path = "%s/%s" % (scene_folder, find_version[0])
					self.openAEFile(scene_path)
					return True
				else:
					self.openDir(scene_folder)
					return True
		logger.debug("Cannot find folder for comp in %s" % cur_node.getName())
		return False

	def openLightFile(self, cur_node=None):
		info_dict = cur_node.getInfoDict()
		scene_path = CC.get_shot_light_file(**info_dict)
		if os.path.exists(scene_path):
			self.openMayaFile(scene_path)
		else:
			logger.warning("Cannot find light scene: %s" % scene_path)

	def openPreivsFile(self, cur_node=None):
		info_dict = cur_node.getInfoDict()
		scene_path = CC.get_sequence_previs_file(**info_dict)
		if os.path.exists(scene_path):
			self.openMayaFile(scene_path)
		else:
			logger.warning("Cannot find previs scene: %s" % scene_path)

	def FindSceneAndOpen(self, scene_type="Animation", cur_node=None):
		"""should take the name of the shot and find the animation file from that.
		maybe these type of functions should be placed in a seperate class?
		"""
		scene_path = None
		if cur_node:
			# shot_name = cur_node.getName()
			# shot_dict = cur_node.returnInfoDict()
			# get node node_animation_style
			if scene_type == "Animation":
				self.openAnimationFile(cur_node=cur_node)
			elif scene_type == "Light":
				self.openLightFile(cur_node=cur_node)
			elif scene_type == "Comp":
				self.openCompFile(cur_node=cur_node)
			elif scene_type == "Previs":
				self.openPreivsFile(cur_node=cur_node)

	def applyComp(self):
		if self.from_node and self.to_node_list:
			from_node = self.from_node[0]

			from_shot_dict = from_node.getInfoDict()
			from_comp_folder = CC.get_shot_comp_folder(**from_shot_dict)
			if (os.path.exists(from_comp_folder)):
				if from_node.getCompStyle() == "Fusion":
					# Find current version
					from_find_version = self.FindVersion(
						name_list=os.listdir(from_comp_folder),
						file_regex="(%s)*?" % from_node.getName().lower(),
						file_ext=".comp"
					)
					from_comp_file = "%s/%s" % (from_comp_folder, from_find_version[0])

					#
					for to_node in self.to_node_list:

						# create path to new comp file
						name = to_node.getName()
						to_shot_dict = to_node.getInfoDict()
						to_comp_folder = CC.get_shot_comp_folder(**to_shot_dict)
						to_find_version = self.FindVersion(
							name_list=os.listdir(to_comp_folder),
							file_regex="(%s)*?" % from_node.getName().lower(),
							file_ext=".comp"
						)
						# TODO Change HARDCODED NAMING
						if not to_find_version:
							final_path = to_comp_folder + name + "_Comp_V001.comp"
							logger.debug("No file exists: Making first version: <<{0}>>".format(final_path))
						else:
							final_path = to_comp_folder + name + "_Comp_V" + str(to_find_version[1] + 1).zfill(
								3) + ".comp"
							logger.debug("File already exists: Making new version: <<{0}>>".format(final_path))
						shutil.copy(from_comp_file, final_path)
					logger.info("Finished applying comp")
					return True

				if from_node.getCompStyle() == "AE":
					from_find_version = self.FindVersion(name_list=os.listdir(from_comp_folder),
														 file_regex="(%s)*?" % from_node.getName().lower(),
														 file_ext=".aep")
					from_comp_file = "%s/%s" % (from_comp_folder, from_find_version[0])
					file_type = "png"
					if "tb_output_format" in CC.project_settings.keys():
						file_type = CC.project_settings["tb_output_format"]
						if file_type[-1] == "4":
							file_type = file_type[0:-1]

					for to_node in self.to_node_list:
						to_shot_dict = to_node.getInfoDict()
						# passes_folder = cfg_util.CreatePathFromDict(cfg.project_paths["shot_passes_folder"],to_shot_dict)
						passes_folder = CC.get_shot_2D_passes_folder(**to_shot_dict)
						to_comp_file = CC.get_shot_ae_precomp_file(**to_shot_dict)  # cfg_util.CreatePathFromDict(cfg.project_paths["shot_precomp_file"], to_shot_dict) # MISSING get_shot_precomp_file
						# to_comp_file = CC.get_shot_precomp_file(**to_shot_dict)
						logger.info("Applying comp from %s to %s. Looking in %s. File-type: %s. From %s To %s" % (
						from_find_version, to_comp_file, passes_folder,file_type.lower(),from_node.getName(),to_node.getName()))
						if (os.path.exists(passes_folder)):

							SetupAE.ApplyCompToFocus(to_comp_file, from_comp_file, passes_folder,file_type.lower(),from_node.getName(),to_node.getName())
							self.createAECompFolders(to_node)
						else:
							logger.warning("Can't find %s. Aborted action" % passes_folder)
					logger.info("Finished applying comp")
				else:
					logger.warning("Can't find comp folder or file from %s" % from_node.getName())

	def createAECompFolders(self,node):
		shot_dict = node.getInfoDict()
		comp_folder = CC.get_shot_comp_folder(**shot_dict)
		output_folder = CC.get_shot_comp_folder(**shot_dict)
		f_list = [comp_folder,output_folder]
		for f in f_list:
			if not os.path.exists(f):
				os.mkdir(f)
		pass
	def createAEPrecomp(self, list_of_nodes):
		for cur_node in list_of_nodes:
			if cur_node.getType() == "shot":
				shot_dict = cur_node.getInfoDict()
				# comp_folder = cfg_util.CreatePathFromDict(cfg.project_paths["shot_comp_folder"], shot_dict)
				base_file = CC.get_ae_precomp_template_file()  # cfg_util.CreatePathFromDict(cfg.project_paths["ae_precomp_template_file"]) # MISSING - ae_precomp_template_file ??
				comp_folder, precomp_file = os.path.split(CC.get_shot_ae_precomp_file(**shot_dict)) # cfg_util.CreatePathFromDict(cfg.project_paths["shot_precomp_file"],shot_dict)) # MISSING shot_precomp_file
				# passes = cfg_util.CreatePathFromDict(cfg.project_paths["shot_passes_folder"],shot_dict)
				passes = CC.get_shot_2D_passes_folder(**shot_dict)
				SetupAE.CreatePrecomp(base_file, passes, comp_folder, precomp_file)
				self.createAECompFolders(cur_node)
				if not os.path.exists(CC.get_shot_comp_output_folder(**shot_dict)):
					os.mkdir(CC.get_shot_comp_output_folder(**shot_dict))
		logger.info("Finished with pre-comps")

	def getAllNodes(self):
		return self.__repository.GetByFilter()

	def getType(self, cur_name=None):
		return self.__repository.getType(cur_name)

	def createTreeModel(self):
		cur_nodes = self.__repository.GetByFilter(type_filter="episode")
		# cur_nodes = sorted(cur_nodes,key=lambda x:x.getName())
		self.__imgTree = TreeModel(nodes=cur_nodes, pixmap_util=self.__pixmapUtil)
		return self.__imgTree

	# def updateTreeModel(self,parent_node,new_node):
	# 	self.__imgTree.beginResetModel()
	# 	parent_node.addChildren(new_node)
	# 	self.__imgTree.endResetModel()

	def setTableByFilter(self, name_filter=None, type_filter=None, parent_filter=None):
		cur_nodes = self.__repository.GetByFilter(name_filter=name_filter, type_filter=type_filter,
												  parent_filter=parent_filter)
		return self.setTableModel(cur_nodes)

	def setTableModel(self, table_nodes=None):
		self.__imgTable = TableModel(name="ImageTable", nodes=table_nodes, pixmap_util=self.__pixmapUtil)
		return self.__imgTable

	def setFromTable(self, table_nodes=None):
		if table_nodes:
			self.from_node = [table_nodes]
		else:
			self.from_node = []
		self.__fromTable = ToFromTableModel(name="FromTable", nodes=self.from_node, pixmap_util=self.__pixmapUtil)
		return self.__fromTable

	def setToTable(self, table_nodes=[], add=False):
		if add:
			self.to_node_list.extend(table_nodes)
			self.to_node_list = list(set(self.to_node_list))
		else:
			self.to_node_list = table_nodes
		self.__toTable = ToFromTableModel(name="ToTable", nodes=self.to_node_list, pixmap_util=self.__pixmapUtil)
		return self.__toTable

	""""    
	#TODO check if the list.remove causes issues??
	def ClearToTable(self):
		self.to_node_list = []
		self.table_model_to = TableModel(name="ToTable", nodes=self.to_node_list, pixmap_util=self.__pixmapUtil)
		self.table_view_to.setModel(self.table_model_to)
		min_height = (self.height+30) * len(self.to_node_list)
		self.table_view_to.setMinimumHeight(min_height)
	"""

	def RemoveTo(self, cur_nodes):
		temp_node_list = [x for x in self.to_node_list if x not in cur_nodes]
		self.setToTable(temp_node_list)

	def RemoveFrom(self):
		self.from_node = []
		self.__fromTable = ToFromTableModel(name="FromTable", nodes=self.from_node, pixmap_util=self.__pixmapUtil)
		# self.table_view_from.setModel(self.table_model_from)

	def getToTable(self):
		return self.__toTable

	def getFromTable(self):
		return self.__fromTable

	def SwitchFromAndTo(self, to_node=None):
		if not to_node and self.to_node_list:
			to_node = self.to_node_list[0]
		self.to_node_list.extend(self.from_node)
		self.from_node = [to_node]
		self.to_node_list.remove(self.from_node[0])

		self.__toTable = ToFromTableModel(name="ToTable", nodes=self.to_node_list, pixmap_util=self.__pixmapUtil)
		# self.table_view_to.setModel(self.table_model_to)

		self.__fromTable = ToFromTableModel(name="FromTable", nodes=self.from_node, pixmap_util=self.__pixmapUtil)
		# self.table_view_from.setModel(self.table_model_from)

	def openPreview(self, cur_node, level="anim"):
		if not "preview_dict" in CC.__dict__.keys():
			preview_paths = {"comp": ["shot_comp_preview_file"],  # "shot_comp_output_file",
							 "anim": ["shot_anim_preview_file"],  # "shot_anim_preview_file",
							 "animatic": ["shot_animatic_file"]}  # "shot_animatic_file"}}
		else:
			preview_paths = CC.preview_dict
		preview_type_list = ["comp", "anim", "animatic"]
		preview_type_list = preview_type_list[preview_type_list.index(level):]
		if cur_node.getType() == "shot":
			shot_dict = cur_node.getInfoDict()
			for preview_level in preview_type_list:
				for preview in preview_paths[preview_level]:
					path_func = getattr(CC, "get_{func_name}".format(func_name=preview))
					path = path_func(**shot_dict)
					logger.info("Preview: %s -> %s" % (preview, path))
					print("Preview: %s -> %s" % (preview, path))
					if os.path.exists(path):
						preview_path = path
						os.startfile(preview_path)
						return True
			return False

	def __compareLengthsMsg(self, context, node, fps, silent=True):
		info_dict = node.getInfoDict()

		if context == "comp":
			# path01 = cfg_util.CreatePathFromDict(cfg.project_paths["shot_comp_output_file"], info_dict)
			path01 = CC.get_shot_comp_output_file(**info_dict)
			if not (os.path.exists(path01)):
				context = "anim"
		if context == "anim":
			# path01 = cfg_util.CreatePathFromDict(cfg.project_paths["shot_anim_preview_file"], info_dict)
			path01 = CC.get_shot_anim_preview_file(**info_dict)
			if not (os.path.exists(path01)):
				context = "animatic"
		if context == "animatic":
			# path01 = cfg_util.CreatePathFromDict(cfg.project_paths["shot_animatic_file"], info_dict)
			path01 = CC.get_shot_animatic_file(**info_dict)
			if not (os.path.exists(path01)):
				msg = "%s: Can't find footage for shot!" % info_dict["shot_name"]
				return -1, msg
		path02 = CC.shot_get_sound_file(
			**info_dict)  ##cfg_util.CreatePathFromDict(cfg.project_paths["shot_sound_file"], info_dict) # MISSING get_shot_sound_file
		if not os.path.exists(path02):
			return -1, "No sound file found!"
		try:
			msg = self.__AV.lengths.compare_equal(path01=path01, path02=path02, fps=fps, silent=silent)[1]
			return 0, msg
		except CheckAudioVisual.MediaLengthException as e:
			msg = e.getMsg()
			return -1, msg

	def compareLengths(self, context, node, fps, silent=True):
		"""
		changed so that we get a list of nodes and then do the same methods at the end.
		"""
		msg_box = QtWidgets.QMessageBox()
		msg_box.setIcon(QtWidgets.QMessageBox.Information)
		msg_box.setWindowTitle("Compare Video->Audio")
		list_of_nodes = []
		error_print = ""
		if isinstance(node, Episode):
			# list = QtWidgets.QListWidget()
			# msg_box.layout().addWidget(list)
			# msg_box.setText("                                    ")
			for s in node.getChildren():
				for n in s.getChildren():
					list_of_nodes.append(n)
					# try:
					#     list.addItem(self.__compareLengthsMsg(context=context, node=n, fps=fps, silent=silent)[1])
					# except subprocess.CalledProcessError:
					#     try:
					#         list.addItem(self.__compareLengthsMsg(context="animatic", node=n, fps=fps, silent=silent)[1])
					#     except subprocess.CalledProcessError:
					#         list.addItem(self.__compareLengthsMsg(context="anim", node=n, fps=fps, silent=silent)[1])
		elif isinstance(node, Sequence):
			# list = QtWidgets.QListWidget()
			# msg_box.layout().addWidget(list)
			# msg_box.setText("                                    ")
			for n in node.getChildren():
				list_of_nodes.append(n)
				# try:
				#     list.addItem(self.__compareLengthsMsg(context=context, node=n, fps=fps, silent=silent)[1])
				# except subprocess.CalledProcessError:
				#     try:
				#         list.addItem(self.__compareLengthsMsg(context="animatic", node=n, fps=fps, silent=silent)[1])
				#     except subprocess.CalledProcessError:
				#         list.addItem(self.__compareLengthsMsg(context="anim", node=n, fps=fps, silent=silent)[1])
		else:
			list_of_nodes.append(node)
			# try:
			#     msg = self.__compareLengthsMsg(context=context, node=node, fps=fps, silent=silent)[1]
			# except subprocess.CalledProcessError:
			#     try:
			#         msg = self.__compareLengthsMsg(context="animatic", node=node, fps=fps, silent=silent)[1]
			#     except subprocess.CalledProcessError:
			#         msg = self.__compareLengthsMsg(context="anim", node=node, fps=fps, silent=silent)[1]
		for cur_node in list_of_nodes:
			cur_info = self.__compareLengthsMsg(context=context, node=cur_node, fps=fps, silent=silent)
			if cur_info[0] == -1:
				error_print = error_print + "\n" + cur_info[1]

		logger.error(error_print)

		msg_box.setText(error_print)

		msg_box.exec_()

	def makeHookUpFromNodes(self, list_of_nodes=[],hookup_name=None,level="anim"):

		if in_maya: #Skipping if in maya since we use ffmpeg python that is not available in python 2.7
			msg_box = QtWidgets.QMessageBox()
			msg_box.setIcon(QtWidgets.QMessageBox.Warning)
			msg_box.setText("Please run hookup from shotBrowser OUTSIDE of maya")
			msg_box.exec_()
			return False
		import Preview.ffmpeg_util as preview_util
		if not "preview_dict" in CC.__dict__.keys():
			preview_paths = {"comp": ["shot_comp_preview_file"],  # "shot_comp_output_file",
							 "anim": ["shot_anim_preview_file"],  # "shot_anim_preview_file",
							 "animatic": ["shot_animatic_file"]}  # "shot_animatic_file"}}
		else:
			preview_paths = CC.preview_dict
		preview_type_list = ["comp", "anim", "animatic"]
		preview_type_list = preview_type_list[preview_type_list.index(level):]
		list_of_paths = []
		list_of_nodes = sorted(list_of_nodes, key=lambda x: x.getName())
		for node in list_of_nodes:
			if node.getType() == "shot":
				output_path = None
				shot_dict = node.getInfoDict()
				for preview_level in preview_type_list:
					if output_path:
						break
					for preview in preview_paths[preview_level]:
						# ep, seq, shot = node.getName().split("_")  # create shot dict
						# shot_dict = {"episode_name": ep, "seq_name": seq, "shot_name": shot}

						# path = preview_paths[preview](**shot_dict)
						path_func = getattr(CC, "get_{func_name}".format(func_name=preview))
						path = path_func(**shot_dict)
						if os.path.exists(path):
							output_path = path
							break
				#Check if we need to fix audio length or add new audio before creating hookup
				audio_check = preview_util.needAudioCheck(output_path)
				if audio_check:
					temp_path = Preview.file_util.makeTempFile(output_path)
					try:
						if audio_check == True:
							print("Adding new sound to %s" % node.getName())
							sound_wav = CC.get_shot_sound_file(**shot_dict)
							# sound_wav = "%s/%s_Sound.wav" % (CC.get_shot_path(**node.getInfoDict()),node.getName())
							if os.path.exists(sound_wav):
								preview_util.AddSoundToVideo(temp_path, sound_wav, output_path)
							else:
								print("Can't find sound file: %s" % sound_wav)
								continue
						else:
							print("Sound not the correct duration for %s. Trying to trim or prolong it" % node.getName())
							preview_util.AddSoundToVideo(temp_path, temp_path, output_path)
						if os.path.exists(temp_path):
							os.remove(temp_path)
					except Exception as e:
						print(e)
						if os.path.exists(temp_path):
							os.remove(temp_path)
				list_of_paths.append(output_path)

		output_path = "%s/HOOKUP/%s.mov" % (CC.get_film_path(), hookup_name)

		preview_util.concat(input_path_list=list_of_paths,output_path=output_path, force_h264=True)
		os.startfile(output_path)

	def makeHookUpFromNodesOLDandOUTDATED(self, list_of_nodes=[], hookup_name=None, level="anim"):
		preview_paths = {"comp": CC.get_shot_comp_preview_file,  # "shot_comp_output_file",
						 "anim": CC.get_shot_anim_preview_file,  # "shot_anim_preview_file",
						 "animatic": CC.get_shot_animatic_file}  # "shot_animatic_file"}}
		preview_type_list = ["comp", "anim", "animatic"]
		preview_type_list = preview_type_list[preview_type_list.index(level):]
		list_of_paths = []
		list_of_nodes = sorted(list_of_nodes, key=lambda x: x.getName())
		for node in list_of_nodes:
			if node.getType() == "shot":
				for preview in preview_type_list:
					ep, seq, shot = node.getName().split("_")  # create shot dict
					shot_dict = {"episode_name": ep, "seq_name": seq, "shot_name": shot}
					path = preview_paths[preview](
						**shot_dict)  # cfg_util.CreatePathFromDict(cfg.project_paths[preview_paths[preview]], shot_dict) # MISSING preview_paths ??
					if os.path.exists(path):
						list_of_paths.append(path)
						break
		file_text_list = ""
		clean_up_paths = []

		# skipping new class for testing:
		for cur_path in list_of_paths:
			new_folder, new_file = os.path.split(cur_path)
			new_file = new_file.replace(".mov", "_HookUpTemp.mov")
			new_path = "%s/%s" % (new_folder, new_file)
			new_path = os.path.abspath(new_path)
			self.__ffmpeg.prores_convert(input_path=cur_path, output_path=new_path)
			file_text_list = "%sfile '%s'\n" % (file_text_list, new_path.split("Film")[1])
			clean_up_paths.append(new_path)
		# save_location = "%s/Hookup_temp_list.txt" % cfg_util.CreatePathFromDict(cfg.project_paths["film_path"])
		save_location = "%s/Hookup_temp_list.txt" % CC.get_film_path()
		with open(save_location, 'w') as saveFile:
			saveFile.write(file_text_list)
		saveFile.close()

		# output_path = "%s/HOOKUP/%s.mov" %(cfg_util.CreatePathFromDict(cfg.project_paths["film_path"]), hookup_name)
		output_path = "%s/HOOKUP/%s.mov" % (CC.get_film_path(), hookup_name)

		# self.__ffmpeg.setCwd(cwd=cfg_util.CreatePathFromDict(cfg.project_paths["film_path"]))
		self.__ffmpeg.setCwd(cwd=CC.get_film_path())
		self.__ffmpeg.concat_protocol(save_location, output_path)

		for clean_path in clean_up_paths:
			os.remove(clean_path)
		os.remove(save_location)
		os.startfile(output_path)
		return output_path
	def toonboomRenderExternally(self,nodes):
		shots = []
		for node in nodes:
			if not node.getType() in ["episode","seq"]:
				shots.append(node)
			else:
				shots.extend(node.getAllChildren())
		pool = ThreadPool2.ThreadPool()
		workers = []
		for shot in shots:
			scene_path = self.findToonboomAnimationFile(shot)
			if scene_path:
				worker = None
				worker = ThreadPool2.Worker(self.toonboomRenderExternallyCmd, scene_path)
				if worker:
					pool.addWorker(worker)
					workers.append(worker)
		if workers:
			pool.signals.finished.connect(createCompPreviewDone)
			pool.run()
			# pool.wait()
			print('\n >> Rendering! <<')
	def toonboomRenderExternallyCmd(self,scene_path):
		cmd = r"Python T:\_Pipeline\cobopipe-v02-001\TB\ToonBoom_PythonExternal_Funcs.py %s" % scene_path
		subprocess.Popen(cmd,shell=True,universal_newlines=True,env=run_env)

	def updateHarmonyPalettes(self, nodes):
		shots = []
		for node in nodes:
			if node.getType() == 'episode':
				for sequence in node.getChildren():
					for shot in sequence.getChildren():
						shots.append(shot)
			elif node.getType() == 'seq':
				for shot in node.getChildren():
					shots.append(shot)
			else:
				shots.append(node)

		print('\n')

		pool = ThreadPool2.ThreadPool()
		workers = []

		for shot in shots:
			scene_path = self.findToonboomAnimationFile(shot)
			if scene_path:
				worker = None
				worker = ThreadPool2.Worker(TB.updatePalettes.process, scene_path)
				if worker:
					pool.addWorker(worker)
					workers.append(worker)

		if workers:
			pool.signals.finished.connect(createCompPreviewDone)
			pool.run()
			pool.wait()
			print('\n >> Done updating harmony palettes <<')

	def createCompPreview(self, nodes, force):
		from Preview.general import getPreview
		shots = []
		for node in nodes:
			if node.getType() == 'episode':
				for sequence in node.getChildren():
					for shot in sequence.getChildren():
						shots.append(shot)
			elif node.getType() == 'seq':
				for shot in node.getChildren():
					shots.append(shot)
			else:
				shots.append(node)

		print('\n')

		pool = ThreadPool2.ThreadPool()
		workers = []

		for shot in shots:
			worker = None
			if shot.getCompStyle() == 'Fusion':
				# def getPreview(shot, type='comp', create=True, force=False, local=True, waitForJobID=None):
				worker = ThreadPool2.Worker(getPreview, shot.getName(), type='comp', force=force, local=True)
			elif shot.getCompStyle() == 'AE':
				worker = ThreadPool2.Worker(getPreview, shot.getName(), type='comp_2D', force=force, local=True)
			if worker:
				pool.addWorker(worker)
				workers.append(worker)

		if workers:
			pool.signals.finished.connect(createCompPreviewDone)
			pool.run()
			pool.wait()
			print('\n >> Done creating comp previews <<')
		else:
			print('All previews up to date')

		#print('\nDone creating previews')


	def submitCompPreviewToRR(self, nodes, force=False, user='Unknown'):
		from Preview.general import getPreview
		shots = []
		for node in nodes:
			if node.getType() == 'episode':
				for sequence in node.getChildren():
					for shot in sequence.getChildren():
						shots.append(shot)
			elif node.getType() == 'seq':
				for shot in node.getChildren():
					shots.append(shot)
			else:
				shots.append(node)

		print('\n')

		pool = ThreadPool2.ThreadPool()
		workers = []

		for shot in shots:
			if shot.getCompStyle() == 'Fusion':
				worker = ThreadPool2.Worker(getPreview, shot=shot.getName(), type='comp',
											force=force, local=False, user=user)
				# worker = ThreadPool2.Worker(comp.submitShotPreview, shot.getName(),
				#                             force=force,
				#                             user=user)
				pool.addWorker(worker)
				workers.append(worker)

		if workers:
			pool.signals.finished.connect(createCompPreviewDone)
			pool.run()
			pool.wait()
			print('\n >> Done submitting comp previews <<')
		else:
			print('All relevant previews have been submitted')


	def submitFusionToRoyalRender(self,list_of_nodes=[],user=None,comp=True,preview=False,submit_to_RR=True):
		import Fusion_Functions.FusionRRSubmitter as fusion_rr
		# import Fusion_Functions.CreateMovFromStack as fusion_preview
		for cur_node in list_of_nodes:
			if cur_node.getType() == "shot":
				shot_name = cur_node.getName()
				shot_dict = cur_node.getInfoDict()
				comp_folder = CC.get_shot_comp_folder(**shot_dict)
				from_find_version = self.FindVersion(
					name_list=os.listdir(comp_folder),
					file_regex="(%s)*?" % shot_name.lower(),
					file_ext=".comp"
				)
				render_file = "%s%s" % (comp_folder, from_find_version[0])
				preview_comp_file = "%s/04_Publish/%s_MovRender.comp" % (CC.get_shot_path(**shot_dict), shot_name)
				project_name = CC.project_name + "_Fusion"
				if preview:
				#     if os.path.exists(CC.get_shot_comp_output_file(**shot_dict)):
				#         fusion_preview.RunOutsideFusion(project_name=project_name,user = user,_input=CC.get_shot_comp_output_file(**shot_dict),_output=CC.get_shot_comp_preview_file(**shot_dict),submit=submit_to_RR,comp_file=render_file,preview_file=preview_comp_file,shot_info=shot_dict)
				#     else:
				#         logger.warning("Can't render out comp-preview, because no comp-output found!")
				#         print("Can't render out comp-preview, because no comp-output found!")
					pass
				else:
					#P:/tools/RoyalRender/bin/win64/rrSubmitterconsole.exe P:/_WFH_Projekter/930486_MiaMagicPlayground_S3-4/4_Production/Film/E04/E04_SQ070/E04_SQ070_SH010/03_Comp/E04_SQ070_SH010_Comp_V001.comp -AutoDeleteEnabled -S fusion -V 17.4.3 -SOS win -DB P:/_WFH_Projekter/930486_MiaMagicPlayground_S3-4/4_Production "CSCN=0~E04" "CSHN=0~SQ070" "CVN=0~SH010" "UN=0~Christian" "CropEXR=1~0" "PreviewGamma2.2=1~1" "CPN=0~MiasMagic2_Fusion" "DCG=0~CompNodes" "Priority=1~90"
					#P:/tools/RoyalRender/bin/win64/rrSubmitterconsole.exe P:/_WFH_Projekter/930486_MiaMagicPlayground_S3-4/4_Production/Film/E04/E04_SQ070/E04_SQ070_SH010/03_Comp//E04_SQ070_SH010_Comp_V001.comp -AutoDeleteEnabled -S fusion -V 17.4.3 -SOS win -DB P:/_WFH_Projekter/930486_MiaMagicPlayground_S3-4/4_Production "CSCN=0~E04" "CSHN=0~SQ070" "CVN=0~SH010" "UN=0~Christian" "CropEXR=1~0" "PreviewGamma2.2=1~1" "CPN=0~MiasMagic2_Fusion" "DCG=0~CompNodes" "Priority=1~90"
					jobID = fusion_rr.runOutsideFusion(project_name=project_name, project_path="%s" % CC.get_film_path(),
										   render_file=render_file, user=user, episode=shot_dict["episode_name"],
										   sequence=shot_dict["seq_name"], shot=shot_dict["shot_name"],single_out=False,waitForJobID=False)
					# print("This is the job id:%s" % jobID )
					# # Comp Preview
					# duration = fusion_preview.GetDurationFromFile(comp_file=render_file)
					# fusion_preview.DuplicateTemplate(dest_path=preview_comp_file)
					# fusion_preview.replaceInTemplate(input_path=CC.get_shot_comp_output_file(**shot_dict), output_path=CC.get_shot_comp_preview_file(**shot_dict),
					#                                  preview_comp_file=preview_comp_file, duration=duration)
					# fusion_rr.runOutsideFusion(project_name=project_name, project_path=CC.get_base_path(),
					#                            render_file=preview_comp_file, user=user, episode=shot_dict["episode_name"],
					#                            sequence=shot_dict["seq_name"], shot=shot_dict["shot_name"],
					#                            single_out=True, waitForJobID=jobID)



	def submitToonBoomToRoyalRender(self, list_of_nodes=[],user=None):

		output_format = "PNG4"
		leading_zero = "3"
		if "tb_output_format" in CC.project_settings.keys():
			output_format = CC.project_settings["tb_output_format"]
		if "tb_number_padding" in CC.project_settings.keys():
			leading_zero = CC.project_settings["tb_number_padding"]

		for cur_node in list_of_nodes:
			if cur_node.getType() == "shot":
				shot_name = cur_node.getName()
				# shot_path = CC.get_shot_path(**shot_dict)
				#
				# shot_content = os.listdir(shot_path)
				# shot_folders = []
				#
				# for s_con in shot_content:
				#     s_path = "%s/%s" % (shot_path, s_con)
				#     if os.path.isdir(s_path):
				#         shot_folders.append(s_con)
				# folder_version = self.FindVersion(name_list=shot_folders,
				#                                   file_regex="(%s)" % cur_node.getName().lower(),
				#                                   file_ext="")
				# if folder_version:
				#     latest_folder = "%s/%s" % (shot_path, folder_version[0])
				#     if os.path.exists(latest_folder):
				#         find_shot_version = self.FindVersion(name_list=os.listdir(latest_folder),
				#                                              file_regex="(%s)*?" % cur_node.getName().lower(),
				#                                              file_ext=".xstage")
				#         if find_shot_version:
				#             scene_path = "%s/%s" % (latest_folder, find_shot_version[0])

				# logger.debug("Running render-node script:\n%s" % tb_cmd)
				scene_path = self.findToonboomAnimationFile(cur_node=cur_node)
				if scene_path:
					# run_env["TOONBOOM_GLOBAL_SCRIPT_LOCATION"] = "%s/TB" % os.path.dirname(os.path.realpath(__file__))
					script = "include('CB_ToonBoom_Include_SetRenderNode.js');PrepareForRender('%s','%s');" % (output_format,leading_zero)
					tb_cmd = 'HarmonyPremium -script "%s" -scene "%s"' % (script, scene_path)
					logger.debug("Running render-node script:\n%s" % tb_cmd)

					# subprocess.Popen(final_cmd)
					rr_cmd = SubmitTB.RenderSubmitInfo(render_file=scene_path, return_cmd=True,project_name=CC.project_name,user_name=user)
					# final_cmd = "%s %s" %(tb_cmd,rr_cmd)
					# print(final_cmd)
					# subprocess.Popen(final_cmd,shell=True)
					print("Preparing Scene for Render: %s" % scene_path)
					tb_subp = subprocess.Popen(tb_cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE,env=run_env)
					tb_subp.wait()
					subprocess.Popen(rr_cmd)

	def runToonBoomCleanUp(self,list_of_nodes=[]):
		#Meant to move toonboom into its own folder if saved unto of the shot folder. NOT currently used.
		for n in list_of_nodes:
			cur_dict = n.getInfoDict()
			cur_folder = CC.get_shot_path(**cur_dict)
			destination = "%s/%s_V001" % (cur_folder, n.getName())
			if not os.path.exists(destination):

				skip_list = [n.getName(),"%s_Animatic.mov" % n.getName(),"%s_setup_script.js" % n.getName(),"Preview",destination]
				print(skip_list)
				cont_list = os.listdir(cur_folder)
				run_it = False
				for c_check in cont_list:
					if ".xstage" in c_check:
						run_it = True
				if run_it:
					for c in os.listdir(cur_folder):
						if not c in skip_list:
							source = "%s/%s" % (cur_folder, c)
							if c in ["%s.xstage" % n.getName(), "%s.aux" % n.getName()]:
								new_name = "%s_V001.%s" % (c.split(".")[0], c.split(".")[1])
								new_source = "%s/%s" % (cur_folder,new_name)
								os.rename(source,new_source)
								source = new_source
							print("Moving %s to %s" %(c,destination))
							shutil.move(source,destination)

				else:
					print("SKIPPING %s - can't see a xstage file" % n.getName())
			else:
				print("SKIPPING %s - already a V001" % n.getName())

	def runEmptySceneSetup(self, seq_node):
		if seq_node.getAnimationStyle() == "Toonboom":
			self.EmptySceneSetupToonboom(seq_node)
		if seq_node.getAnimationStyle() == "Maya":
			self.createEmptyMayaScene(seq_node)

	def runSceneSetup(self,list_of_nodes=[]):
		ae_nodes = []
		tb_nodes = []
		for cur_node in list_of_nodes:
			if cur_node.getAnimationStyle() == "Toonboom":
				tb_nodes.append(cur_node)
			if cur_node.getAnimationStyle() == "AE":
				ae_nodes.append(cur_node)

		if ae_nodes:
			self.SceneSetupAE(ae_nodes)
		if tb_nodes:
			self.SceneSetupToonBoom(tb_nodes)

	def SceneSetupAE(self,list_of_nodes=[]):
		print_list = []
		overwrite_all = False
		ask_for_all_check = True
		for cur_node in list_of_nodes:
			print("RUNNING SCENE SETUP FOR %s" % cur_node)
			# self.project_path = cfg_util.CreatePathFromDict(cfg.project_paths["base_path"])
			template_path = CC.get_ae_anim_template_file()
			template_folder, template_file = os.path.split(template_path)
			shot_dict = cur_node.getInfoDict()
			movie_path = CC.get_shot_animatic_file(**shot_dict)
			scene_file = CC.get_shot_ae_anim_path(**shot_dict)
			scene_path = CC.get_shot_anim_folder(**shot_dict)
			#script_path = "%s/%s_setup_script.js" % (cur_node.getUrl(), cur_node.getName())

			# if os.path.exists(scene_path) and not os.path.exists("%s/%s_V001.xstage" % (scene_path,cur_node.getName())):
			if not os.path.exists(scene_path):
				continue
			if os.path.exists(scene_file):
				# check if another version exists, to see if its save to overwrite the basefile
				# if os.path.exists(scene_file):
				#     print_list.append("%s: Found version file, skipping overwrite" % cur_node.getName())
				#     continue
				if overwrite_all:  # Skip asking the user, if the user has already set yes to overwrite all.
					button_reply = QtWidgets.QMessageBox.Yes
				else:
					ask = QtWidgets.QMessageBox()
					button_reply = ask.question(ask, "File Exists:",
												"Overwrite %s Scene?" % (cur_node.getName()),
												QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
												QtWidgets.QMessageBox.No)
				if button_reply == QtWidgets.QMessageBox.Yes:
					pass
				else:
					print_list.append("%s: Overwrite not approved. Skipping" % cur_node.getName())
					continue
				if ask_for_all_check and len(list_of_nodes) > 1:  # Run a extra ask box to ask if you want to overwrite all shots
					ask_for_all = QtWidgets.QMessageBox()
					all_button_reply = ask_for_all.question(ask_for_all, "For All Files:", "Overwrite for all files?",
															QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
															QtWidgets.QMessageBox.No)
					if all_button_reply == QtWidgets.QMessageBox.Yes:
						overwrite_all = True
					ask_for_all_check = False

			if os.path.exists(movie_path):
				print("Building now!")
				print("template_file=%s,anim_folder=%s,shot_name=%s,animatic=%s" % (template_file,scene_file,cur_node.getName(),movie_path))
				SetupAE.CreateAEShot(template_file=template_path,anim_folder=scene_path,shot_file=scene_file,animatic=movie_path)
				print_list.append("%s: Finished scene set up in AE" % cur_node.getName())
			else:
				print_list.append("%s: No Movie Found" % cur_node.getName())
				continue
		for cur_print in print_list:
			logger.info(cur_print)

	def EmptySceneSetupToonboom(self, node):
		"""NEW FUNCTION MIGHT NEED TWEAKING"""
		tb_height = 1080
		tb_width = 1920
		tb_size_multi = 1.1
		if 'tb_height' in CC.project_settings.keys():
			tb_height = CC.project_settings['tb_height']
			tb_width = CC.project_settings['tb_width']
			tb_size_multi = CC.project_settings['tb_size_multi']
		template_path = CC.get_tb_scene_template_file()
		#get name
		my_input = QtWidgets.QInputDialog()

		info_dict = node.getInfoDict()
		number,check = QtWidgets.QInputDialog().getInt(my_input,"SET SHOT NUMBER","Write the shot number: aka 040|40",10)
		if check:
			print(number)
			shot_name = "SH%s" % str(number).zfill(3)
			tb_shot_path = CC.get_shot_tb_anim_path(shot_name=shot_name,**node.getInfoDict())
			shot_path = CC.get_shot_path(shot_name=shot_name,**node.getInfoDict())
			script_path = "%s/%s_%s_%s_setup_script.js" % (shot_path, info_dict["episode_name"],info_dict["seq_name"],shot_name)
			print(tb_shot_path,script_path)

			if not os.path.exists(tb_shot_path):
				tb_shot_path_file = tb_shot_path + ".xstage"
				SetupTB.createEmptyScene(template_scene_path=template_path, script_path=script_path,output_scene_path=tb_shot_path,height=tb_height,width=tb_width, res_multi=tb_size_multi)
			else:
				print("NAME EXISTS! Pick another")

	def createEmptyMayaScene(self,node):
		import Maya_Functions.file_util_functions as file_util
		import Maya_Functions.file_util_functions as file_util
		info_dict = node.getInfoDict()
		my_input = QtWidgets.QInputDialog()
		number, check = QtWidgets.QInputDialog().getInt(my_input, "SET SHOT NUMBER",
														"Write the shot number: aka 040|40", 10)
		if check:
			shot_name = "SH%s" % str(number).zfill(3)
			shot_path = CC.get_shot_path(shot_name=shot_name, **node.getInfoDict())
			anim_shot_path = CC.get_shot_anim_path(shot_name=shot_name, **node.getInfoDict())
			if not os.path.exists(anim_shot_path):
				if file_util.createFolderFromTemplate(destination=shot_path,template_folder="3D_Shot_Template",create_folder=True):
					script_content = """import maya.standalone
					maya.standalone.initialize('python')
					import maya.cmds as cmds
					import Maya_Functions.anim_util_functions as anim_util
					cmds.file(new=True, f=True)
					anim_util.CreateShotNode(name='{shot_name}',range=50, start=1, seq_start=1, ep='{episode_name}', seq='{seq_name}')
					cmds.file(rename='{anim_shot_path}')
					cmds.file(type='mayaAscii')
					cmds.file(save=True)
					cmds.quit(f=True)""".format(shot_path=shot_path, shot_name=shot_name,anim_shot_path=anim_shot_path,episode_name=info_dict["episode_name"],seq_name=info_dict["seq_name"])
					script_content = ";".join(script_content.split("\n"))
					base_command = 'mayapy.exe -c "%s"' % (script_content)  # Not being run here, only for printing.
					logger.debug(base_command)
					subprocess.Popen(base_command, shell=False, universal_newlines=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE, env=run_env)
					print("Finished creating new scene")
			else:
				print("Animation file already exists.. Not overwriting it")


	def SceneSetupToonBoom(self, list_of_nodes=[]):
		print_list = []
		overwrite_all = False
		ask_for_all_check = True
		tb_height = 1080
		tb_width = 1920
		tb_size_multi = 1.1
		if 'tb_height' in CC.project_settings.keys():
			tb_height = CC.project_settings['tb_height']
			tb_width = CC.project_settings['tb_width']
			tb_size_multi = CC.project_settings['tb_size_multi']

		for cur_node in list_of_nodes:
			print("RUNNING SCENE SETUP FOR %s" % cur_node)
			# self.project_path = cfg_util.CreatePathFromDict(cfg.project_paths["base_path"])
			template_path = CC.get_tb_scene_template_file()  # cfg_util.CreatePathFromDict(cfg.project_paths["tb_scene_template_path"]) # MISSING get_tb_scene_template_path ??
			template_folder, template_file = os.path.split(template_path)
			ep, seq, shot = cur_node.getName().split("_")
			shot_dict = {"episode_name": ep, "seq_name": seq, "shot_name": shot}
			# movie_path = cfg_util.CreatePathFromDict(cfg.project_paths["shot_animatic_file"], shot_dict)
			movie_path = CC.get_shot_animatic_file(**shot_dict)
			# scene_path = cfg_util.CreatePathFromDict(cfg.project_paths["shot_anim_path"], shot_dict)
			scene_path = CC.get_shot_tb_anim_path(**shot_dict)
			script_path = "%s/%s_setup_script.js" % (cur_node.getUrl(), cur_node.getName())

			# if os.path.exists(scene_path) and not os.path.exists("%s/%s_V001.xstage" % (scene_path,cur_node.getName())):
			if os.path.exists(scene_path):
				# check if another version exists, to see if its save to overwrite the basefile
				if os.path.exists("%s/%s_V001.xstage" % (scene_path, cur_node.getName())):
					print_list.append("%s: Found version file, skipping overwrite" % cur_node.getName())
					continue
				if overwrite_all:  # Skip asking the user, if the user has already set yes to overwrite all.
					button_reply = QtWidgets.QMessageBox.Yes
				else:
					ask = QtWidgets.QMessageBox()
					button_reply = ask.question(ask, "File Exists:",
												"Overwrite %s TB Scene" % (cur_node.getName()),
												QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
												QtWidgets.QMessageBox.No)
				if button_reply == QtWidgets.QMessageBox.Yes:
					shutil.rmtree(scene_path)
					while os.path.exists(scene_path):
						pass
					shutil.copytree(template_folder, scene_path)
					template_path = "%s/%s" % (scene_path, template_file)
					new_name = "%s/%s.xstage" % (scene_path, cur_node.getName())
					print(scene_path)
					os.rename(template_path, new_name)
					template_path = new_name
				else:
					print_list.append("%s: Overwrite not approved. Skipping" % cur_node.getName())
					continue
				if ask_for_all_check and len(
						list_of_nodes) > 1:  # Run a extra ask box to ask if you want to overwrite all shots
					ask_for_all = QtWidgets.QMessageBox()
					all_button_reply = ask_for_all.question(ask_for_all, "For All Files:", "Overwrite for all files?",
															QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
															QtWidgets.QMessageBox.No)
					if all_button_reply == QtWidgets.QMessageBox.Yes:
						overwrite_all = True
					ask_for_all_check = False

			if os.path.exists(movie_path):
				print("Building now!")
				SetupTB.CreateSceneSetup(template_scene_path=template_path, script_path=script_path,
															output_scene_path=scene_path, movie_file_path=movie_path, height=tb_height, width=tb_width, res_multi=tb_size_multi)
				print_list.append("%s: Finished scene set up in TB" % cur_node.getName())
			else:
				print_list.append("%s: No Movie Found" % cur_node.getName())
				continue
		for cur_print in print_list:
			logger.info(cur_print)

	def createPublishReport(self,node_list=[]):
		from Maya_Functions.publish_util_functions import updatePublishReport_MayaPyCmd
		threads = []
		for n in node_list:
			info_dict = n.getInfoDict()
			scene_path = CC.get_shot_anim_path(**info_dict)
			print(scene_path)
			threads.append(thread_pool.Worker(func=updatePublishReport_MayaPyCmd,info_dict=info_dict,scene_path=scene_path))

			#updatePublishReport_MayaPyCmd(info_dict,scene_path)

		self.__threadPool.startBatch(workers=threads)

	def removeVirusFromScene(self,node_list):
		from Maya_Functions.file_util_functions import runRemoveVirusInMayaPy
		for cur_node in node_list:
			info_dict = cur_node.getInfoDict()
			if cur_node.getAnimationStyle() == "Maya":
				scene_path = CC.get_shot_anim_path(**info_dict)
				runRemoveVirusInMayaPy(cur_file=scene_path)
		print("FINISHED WITH VIRUS CHECKING SCENES")
		logger.info("FINISHED WITH VIRUS CHECKING SCENES")

	# def SlateOnPlayblast(self, playblast_path, shot_name): #SLATE ON PLAYBLASTS
	#     temp_path = "%s_Temp.mov" % playblast_path.split(".")[0]
	#     # os.rename(playblast_path, )
	#     slate_name = "%s_%s_%s" % (self.ep, self.seq, shot_name)
	#     now = datetime.now()
	#     dt_string = now.strftime("%d/%m/%Y %H.%M")
	#     try:
	#         slate_cmd = """ffmpeg -i  %s -vf "drawtext=fontfile="/Windows/Fonts/arial.ttf":fontsize=35:fontcolor=darkred@1:text='%s\: Frame\: %%{frame_num}':start_number=1:x=50:y=50:box=1:boxcolor=white@.3:boxborderw=5" -c:a copy -c:v libx264 -y %s""" % (playblast_path, slate_name, temp_path)
	#         # slate_cmd = """ffmpeg -i  %s -vf "drawtext=fontfile="/Windows/Fonts/arial.ttf":fontsize=35:fontcolor=darkred@1:text='%s\: Frame\: %%{frame_num}':start_number=1:x=50:y=50:box=1:boxcolor=white@.3:boxborderw=5, drawtext=fontfile="/Windows/Fonts/arial.ttf":fontsize=35:fontcolor=darkred@1:text='Created %s':x=800:y=50:box=1:boxcolor=white@.3:boxborderw=5" -c:a copy -c:v libx264 -y %s""" % (playblast_path, slate_name, dt_string, temp_path) #Added date to overlay
	#         print(slate_cmd)
	#         # slate_cmd = """ffmpeg -i  %s -vf "drawtext=fontfile=Arial.ttf: text='%s\: Frame\: %%{frame_num}': start_number=1: x=(w-tw)/2: y=h-(2*lh): fontcolor=black: fontsize=20: box=1: boxcolor=white: boxborderw=5" -c:a copy -c:v libx264 -y %s""" % (playblast_path, slate_name, temp_path)
	#         c_p = subprocess.Popen(slate_cmd, shell=False, universal_newlines=True, stdout=subprocess.PIPE)
	#         stdout = c_p.communicate()[0]
	#         print(stdout)
	#         return True
	#     except:
	#         print("overlay didn't work")
	#         return False


# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# FRONTEND |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


# TODO Make a filter/category mode for table-view, like in light helper. Should dis-connect the table-update from the
#  treeview, and then only show a collection of nodes.


class MainWindow(QtWidgets.QWidget):

	def __init__(self, parent=None):

		self.__threadPool = thread_pool.ThreadPool()
		self.__ctrl = FrontController()
		super(MainWindow, self).__init__(parent)
		self.setWindowTitle("Comp Contact Sheet")
		self.setWindowFlags(QtCore.Qt.Window)

		# self.user_save_file = "C:/Temp/%s/UI_User.json" % cfg.project_name
		self.user_save_file = "C:/Temp/%s/UI_User.json" % CC.project_name
		QtGui.QPixmapCache.setCacheLimit(200 * 10240)
		self.last_selection = None
		self.current_progress = []

		self.to_from_width = 320
		self.to_from_height = 180

		self.__create_window()
		self.populateUser()
		self.populateTree()
		# self.updateTable(type_filter="episode")
		self.createSearchCompleter()
		self.populateTableStateCombo()
		# Set startup table model
		self.table_model = self.__ctrl.setTableByFilter(type_filter="episode")
		self.table_view.setModel(self.table_model)

		self.resize(1000, 800)
		self.tree.resize(280,self.tree.height()) #allow the whole name to be visible
		self.show()


	# TODO change so double click on item checks if its a shot, and if its not, should "open" and show children instead (also in tree)
	# TODO Hook up TO-From buttons with functions.
	# TODO Add progress-bar to threading? Would be nice to show how close to done a thread-function is. Such as gathering thumbnails.
	# TODO Make from to tables Icons have locked sizes

	def __create_window(self):
		self.layout_top = QtWidgets.QVBoxLayout(self)

		self.top_row_layout = QtWidgets.QHBoxLayout()


		#START OF PROJECT ICON TEST
		# self.project_icon_bttn = QtWidgets.QPushButton()
		# self.project_icon_bttn.setFlat(True)
		# self.project_icon_bttn.setFixedSize(100,100)
		# self.project_icon = QtGui.QIcon("icon/shotBrowser/Borste.png")
		# self.project_icon_bttn.setIcon(self.project_icon)
		# self.top_row_layout.addWidget(self.project_icon_bttn)

		self.top_row = QtWidgets.QToolBar()
		self.menu_bar = QtWidgets.QToolBar()

		self.search_bar_label = QtWidgets.QLabel("Search/Filter: ")
		self.menu_search_bar = QtWidgets.QLineEdit()
		self.menu_search_bar.setMaximumWidth(150)
		self.menu_bar.addWidget(self.search_bar_label)
		self.menu_bar.addWidget(self.menu_search_bar)
		self.menu_bar.addSeparator()

		self.user_label = QtWidgets.QLabel(" USER: ")
		self.user_combobox = QtWidgets.QComboBox()
		self.user_combobox.setMinimumWidth(150)
		self.top_row.addWidget(self.user_label)
		self.top_row.addWidget(self.user_combobox)
		self.top_row.addSeparator()

		self.thumb_label = QtWidgets.QLabel(" Thumbnail Stage: ")

		self.thumb_show_combo = QtWidgets.QComboBox()
		self.thumb_show_combo.addItems(["comp", "render", "anim", "animatic"])
		self.thumb_show_combo.currentTextChanged.connect(self.ThumbComboChanged)
		self.top_row.addWidget(self.thumb_label)
		self.top_row.addWidget(self.thumb_show_combo)
		self.top_row.addSeparator()

		#### Create radio bttns
		self.radiobttn_grp_table = QtWidgets.QButtonGroup()
		self.radiobttn_table_sync = QtWidgets.QRadioButton("Sync", self.menu_bar)
		self.radiobttn_table_freeze = QtWidgets.QRadioButton("Freeze", self.menu_bar)
		# self.radiobttn_table_isolate = QtWidgets.QRadioButton("Isolate", self.menu_bar)
		self.radiobttn_table_category = QtWidgets.QRadioButton("Category", self.menu_bar)
		self.radiobttn_table_sync.setChecked(True)
		self.radiobttn_grp_table.addButton(self.radiobttn_table_sync)
		self.radiobttn_grp_table.addButton(self.radiobttn_table_freeze)
		# self.radiobttn_grp_table.addButton(self.radiobttn_table_isolate)
		self.radiobttn_grp_table.addButton(self.radiobttn_table_category)

		self.radiobttn_grp_table.buttonClicked.connect(self.tableStateRadioGrpChanged)

		self.menu_bar.addWidget(self.radiobttn_table_sync)
		self.menu_bar.addWidget(self.radiobttn_table_freeze)
		# self.menu_bar.addWidget(self.radiobttn_table_isolate)
		self.menu_bar.addWidget(self.radiobttn_table_category)

		self.table_category_combo = QtWidgets.QComboBox()
		self.table_category_combo.setMinimumWidth(120)
		self.table_category_combo.currentTextChanged.connect(self.tableStateComboChanged)
		self.menu_bar.addWidget(self.table_category_combo)
		self.menu_bar.addSeparator()

		self.radiobttn_grp_thumbsize = QtWidgets.QButtonGroup()
		self.radiobttn_thumb_small = QtWidgets.QRadioButton("Small")
		self.radiobttn_thumb_medium = QtWidgets.QRadioButton("Medium")
		self.radiobttn_thumb_big = QtWidgets.QRadioButton("Large")
		self.radiobttn_thumb_big.setChecked(True)
		self.radiobttn_grp_thumbsize.addButton(self.radiobttn_thumb_small)
		self.radiobttn_grp_thumbsize.addButton(self.radiobttn_thumb_medium)
		self.radiobttn_grp_thumbsize.addButton(self.radiobttn_thumb_big)
		self.radiobttn_grp_thumbsize.buttonClicked.connect(self.thumbSizeRadioGrpChange)

		self.thumb_size_label = QtWidgets.QLabel(" Thumbnail Size: ")
		self.top_row.addWidget(self.thumb_size_label)
		self.top_row.addWidget(self.radiobttn_thumb_small)
		self.top_row.addWidget(self.radiobttn_thumb_medium)
		self.top_row.addWidget(self.radiobttn_thumb_big)

		self.progressBar = QtWidgets.QProgressBar(self)
		self.progressBar.setMaximumWidth(300)
		self.progressBar.setMinimum(0)
		self.progressBar.setMaximum(100)
		self.progress_bar_label = QtWidgets.QLabel("")
		self.progress_bar_label.setMinimumHeight(5)
		self.progress_bar_label.setWordWrap(True)
		self.__ctrl.signals.progressbar_init.connect(self.progressBar.setMaximum)
		self.__ctrl.signals.progressbar_value.connect(self.progressBar.setValue)

		self.splitter_tree_table = QtWidgets.QSplitter()
		# self.splitter_tree_table.setContentsMargins(5, 0, 5, 5)

		self.tree = QtWidgets.QTreeView(self)


		self.tree.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		self.tree.setHeaderHidden(True)
		self.tree.setExpandsOnDoubleClick(True)
		self.tree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
		self.tree.expanded.connect(self.TestExpand)

		self.tree.setAnimated(True)
		self.tree.setIndentation(20)
		self.tree.setSortingEnabled(True)
		# self.tree.sortByColumn(1,QtCore.Qt.AscendingOrder)
		self.tree.setWindowTitle("Dir View")
		self.tree.installEventFilter(self)

		self.table_view = QtWidgets.QListView(self)
		self.table_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
		self.table_view.setViewMode(QtWidgets.QListView.IconMode)
		self.table_view.setFlow(QtWidgets.QListView.LeftToRight)
		self.table_view.setResizeMode(QtWidgets.QListView.Adjust)
		self.table_view.setContentsMargins(0,0,0,0)
		if in_maya:
			self.table_view.setSpacing(2)
		else:
			self.table_view.setSpacing(-3)
		self.table_view.setFrameStyle(1)
		self.table_view.installEventFilter(self)
		self.table_view.doubleClicked.connect(self.tableDoubleClicked)
		self.ApplySelectionFrame()
		self.splitter_tree_table.addWidget(self.tree)
		self.splitter_tree_table.addWidget(self.table_view)

		self.top_row_toolbar_layout = QtWidgets.QVBoxLayout()
		self.top_row_layout.addLayout(self.top_row_toolbar_layout)

		self.top_row_toolbar_layout.addWidget(self.top_row)
		self.top_row_toolbar_layout.addWidget(self.menu_bar)

		self.layout_top.addLayout(self.top_row_layout)

		# self.layout_top.addWidget(self.top_row)
		# self.layout_top.addWidget(self.menu_bar)

		self.splitter_treetable_tofrom = QtWidgets.QSplitter()
		self.splitter_treetable_tofrom.addWidget(self.splitter_tree_table)
		self.splitter_treetable_tofrom.addWidget(self.from_to_widget)
		self.layout_top.addWidget(self.splitter_treetable_tofrom)
		self.layout_top.addWidget(self.progressBar)
		# self.layout_top.addWidget(self.progress_bar_label)

		self.splitter_tree_table.setStretchFactor(0, 0)
		self.splitter_tree_table.setStretchFactor(1, 1)
		self.splitter_treetable_tofrom.setStretchFactor(0, 1)
		self.splitter_treetable_tofrom.setStretchFactor(1, 0)
		self.splitter_treetable_tofrom.setSizes([1, 0])
		# print("spacing: ", self.table_view.spacing())
		# print("margin: ", self.table_view.contentsMargins())
		# print("alignment: ", self.table_view.itemAlignment())

		self.__setPalette()

	def TestExpand(self, cur_index):
		# print("EXPANDED %s" % cur_index)
		proxy_index = self.proxyModel.mapToSource(cur_index)
		cur_node = self.tree_model.getNode(proxy_index)
		if cur_node:
			logger.debug(cur_node.getName())
			if cur_node.getType() == "seq":
				self.__ctrl.refreshThumbs(cur_node.getChildren(), overwrite=False)

	def __setPalette(self):
		#TODO setting palette in maya does NOT look great
		if not in_maya:
			magenta = {"R": 142, "G": 45, "B": 197}
			blue = {"R": 50, "G": 50, "B": 255}

			hi_lgt = blue
			palette = QtGui.QPalette()
			palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
			palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
			palette.setColor(QtGui.QPalette.Base, QtGui.QColor(40, 40, 40))
			palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
			palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
			palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
			palette.setColor(QtGui.QPalette.Text, QtCore.Qt.lightGray)
			palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
			palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
			palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
			palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(hi_lgt["R"], hi_lgt["G"], hi_lgt["B"]).lighter(100))
			palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.white)
			self.setPalette(palette)
			QtWidgets.QApplication.instance().setStyle('Fusion')

	def ApplySelectionFrame(self):
		self.from_to_widget = QtWidgets.QWidget(self)
		self.from_node = None
		self.to_node_list = []

		self.width = 320
		self.height = 180

		self.from_to_layout = QtWidgets.QVBoxLayout()

		self.from_label = QtWidgets.QLabel("FROM THIS SHOT:")
		self.from_label.setFixedSize(self.width, 25)
		self.from_label.setObjectName("from_label")
		self.from_label.setStyleSheet("QLabel#from_label{font-size:18px}")
		self.from_label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)

		self.from_toolbar = QtWidgets.QToolBar()
		self.from_add_bttn = QtWidgets.QPushButton("Set 'From' to selection")
		self.from_add_bttn.clicked.connect(self.Btn_SetFROM)
		self.from_clear_bttn = QtWidgets.QPushButton("Clear 'From' shot")
		self.from_clear_bttn.clicked.connect(self.Btn_ClearFROM)
		self.from_add_bttn.setMinimumWidth(self.width * 0.5)
		self.from_clear_bttn.setMinimumWidth(self.width * 0.5)

		self.from_toolbar.addWidget(self.from_add_bttn)
		self.from_toolbar.addWidget(self.from_clear_bttn)

		# self.from_shot_label = QtWidgets.QLabel("SHOT NAME")

		self.table_view_from = QtWidgets.QListView()
		self.table_view_from.setFrameStyle(2)
		self.table_view_from.setLineWidth(2)
		self.table_view_from.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
		self.table_view_from.setViewMode(QtWidgets.QListView.IconMode)
		self.table_view_from.setFlow(QtWidgets.QListView.TopToBottom)
		self.table_view_from.setResizeMode(QtWidgets.QListView.Adjust)
		self.table_view_from.installEventFilter(self)
		self.table_view_from.setFixedSize(self.width + 10, self.height + 30)

		self.table_model_from = self.__ctrl.setFromTable(None)
		self.table_view_from.setModel(self.table_model_from)
		self.table_view_from.installEventFilter(self)

		self.to_label = QtWidgets.QLabel("APPLYING TO SHOTS:")
		self.to_label.setFixedSize(self.width, 30)
		self.to_label.setObjectName("from_label")
		self.to_label.setStyleSheet("QLabel#from_label{font-size:18px}")
		self.to_label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)

		self.table_view_to = QtWidgets.QListView()
		self.table_view_to.setFrameStyle(2)
		self.table_view_to.setLineWidth(2)
		self.table_view_to.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
		# self.table_view_to.setResizeMode(QtWidgets.QListView.Fixed)
		# self.table_view_to.setLayoutMode(QtWidgets.QListView.SinglePass)
		self.table_view_to.setWrapping(True)
		self.table_view_to.setViewMode(QtWidgets.QListView.IconMode)
		# self.table_view_to.doubleClicked.connect(self.RemoveTo)

		self.table_view_to.setFixedWidth(self.width + 10)
		# min_height = (self.height + 30) * len(self.to_node_list)
		min_height = (self.height + 30) * 2
		self.table_view_to.setMinimumHeight(min_height)
		self.table_view_to.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

		self.table_view_to.installEventFilter(self)
		self.table_model_to = self.__ctrl.setToTable([])
		self.table_view_to.setModel(self.table_model_to)

		self.to_toolbar = QtWidgets.QToolBar()
		self.to_add_bttn = QtWidgets.QPushButton("Add shots to 'TO'-list")
		self.to_add_bttn.clicked.connect(self.Btn_AddTO)
		self.to_clear_bttn = QtWidgets.QPushButton("Clear 'TO'-list")
		self.to_clear_bttn.clicked.connect(self.Btn_ClearTO)
		self.to_add_bttn.setMinimumWidth(self.width * 0.5)
		self.to_clear_bttn.setMinimumWidth(self.width * 0.5)
		# self.to_add_bttn.clicked.connect(self.AddSelectionToTableTo)
		# self.to_clear_bttn.clicked.connect(self.ClearToTable)

		self.to_toolbar.addWidget(self.to_add_bttn)
		self.to_toolbar.addWidget(self.to_clear_bttn)

		self.apply_comp_bttn = QtWidgets.QPushButton("Apply Comp From >> To")
		self.apply_comp_bttn.setObjectName("apply_comp_bttn")
		self.apply_comp_bttn.setStyleSheet("QPushButton#apply_comp_bttn{font-size:16px}")
		self.apply_comp_bttn.clicked.connect(self.ApplyCompFromTo)

		self.from_to_layout.addWidget(self.from_label)
		self.from_to_layout.addWidget(self.from_toolbar)
		self.from_to_layout.addWidget(self.table_view_from)
		self.from_to_layout.addWidget(self.to_label)
		self.from_to_layout.addWidget(self.to_toolbar)
		self.from_to_layout.addWidget(self.table_view_to)
		self.from_to_layout.addWidget(self.apply_comp_bttn)

		self.from_to_widget.setLayout(self.from_to_layout)

	def ApplyCompFromTo(self):
		self.__ctrl.applyComp()

	# TODO Open Preview folder
	# TODO Open Personal HookUp

	def eventFilter(self, source, event):
		if event.type() == QtCore.QEvent.ContextMenu:
			if (source is self.tree
					or source is self.table_view
					or source is self.table_view_from
					or source is self.table_view_to):
				menu = QtWidgets.QMenu()
				nodes = []
				source_type = None
				if source == self.tree:
					if source.selectedIndexes():
						for sel in source.selectedIndexes():
							si = self.tree_model.getNode(self.proxyModel.mapToSource(sel))
							if si:
								nodes.append(si)
					else:
						return super(MainWindow, self).eventFilter(source, event)
				if (source == self.table_view
						or source == self.table_view_from
						or source == self.table_view_to):
					# Does not register click
					if source.selectedIndexes():
						nodes = source.model().getNodesByIndex(source.selectedIndexes())
					else:
						return super(MainWindow, self).eventFilter(source, event)

				if source == self.tree or source == self.table_view:
					# node = self.table_model.getNode(source)
					node = nodes[0]
					comp_style = node.getCompStyle()
					animation_style = node.getAnimationStyle()

					# open_menu = QtWidgets.QMenu("Open", menu)
					view_menu = QtWidgets.QMenu("Previews", menu)
					create_menu = QtWidgets.QMenu("Create/Build", menu)
					category_menu = QtWidgets.QMenu("Edit Category", menu)
					category_add_menu = QtWidgets.QMenu("Add Selection To:", category_menu)

					# TODO Make this less hardcoded. Build from config info.

					# menu.addMenu(open_menu)
					if node.getType() == "episode":
						if animation_style == "Maya":
							create_menu.addAction("Publish Animation")
							create_menu.addSeparator()
							create_menu.addAction("PublishReport Overview")
							create_menu.addAction("PublishReport Breakdown")
							create_menu.addAction("Create Prop-OIDs from Report")
							create_menu.addSeparator()
					if node.getType() == "seq":
						if animation_style == "Maya":
							menu.addAction("Open Previs File")
							create_menu.addAction("Publish Animation")
							create_menu.addSeparator()
							create_menu.addAction("PublishReport Overview")
							create_menu.addAction("PublishReport Breakdown")
							create_menu.addAction("Create Prop-OIDs from Report")
							create_menu.addSeparator()
					if node.getType() == "shot":
						menu.addAction("Open Animation File")
						if animation_style == "Maya":
							menu.addAction("Open Light File")
							create_menu.addAction("Publish Animation")
							create_menu.addSeparator()
							create_menu.addAction("PublishReport Overview")
							create_menu.addAction("PublishReport Breakdown")
							create_menu.addSeparator()
						menu.addAction("Open Comp File")

					menu.addAction("Open Folder")
					menu.addSeparator()
					menu.addMenu(create_menu)
					create_menu.addAction("Create HookUp")
					create_menu.addAction("Compare AV")
					create_menu.addAction("Create Comp Preview")
					create_menu.addAction("Create Comp Preview (Force)")
					create_menu.addAction("Submit Comp Preview to RR")
					create_menu.addAction("Submit Comp Preview to RR (Force)")
					if animation_style in ["Toonboom","AE","Maya"]:
						create_menu.addAction("Run SceneSetup")
						create_menu.addAction("Create Empty Scene")
					if animation_style in ["Toonboom"]:
						create_menu.addAction("Update Harmony Palettes")
						create_menu.addAction("Render Scene Externally")

					menu.addSeparator()
					if node.getType() == "shot":
						menu.addMenu(view_menu)
						view_menu.addAction("Open Animatic")
						view_menu.addAction("Open Anim Preview")
						view_menu.addAction("Open Comp Preview")

						menu.addSeparator()
						menu.addAction("Set as FROM shot")
						menu.addAction("Add to (apply) TO shots")
						menu.addSeparator()
						menu.addAction("Create Category")
						menu.addMenu(category_menu)
						category_menu.addMenu(category_add_menu)
						category_menu.addAction("Remove Selection From Category")
						category_menu.addSeparator()
						category_menu.addAction("Delete Current Category")
						if comp_style == "AE":
							create_menu.addSeparator()
							create_menu.addAction("Create PreComp")
						if animation_style == "Toonboom":
							create_menu.addAction("Create Toonboom Preview Locally")
							create_menu.addAction("Submit Toonboom Scene to RR")
						if comp_style == "Fusion":
							create_menu.addAction("Submit Comp Scene to RR")
							#create_menu.addAction("Submit Comp_preview to RR")
							# create_menu.addAction("Create Comp Preview")
					menu.addSeparator()

					if animation_style == "Toonboom":
						#create_menu.addAction("Zip Anim Folder")
						#create_menu.addAction("Zip Anim Folder to FTP")
						create_menu.addAction("Zip Anim Folder (Local)")
						create_menu.addAction("Zip Anim Folder to FTP (Local)")
					create_menu.addAction("Rebuild Anim Publish Report")
					create_menu.addSeparator()
					create_menu.addAction("Rebuild Thumbnails")
					create_menu.addAction("Check Files for Virus")


					# For Adding to category
					for category in self.__ctrl.getCategories():
						add_temp = QtWidgets.QAction(category, category_add_menu)
						add_temp.triggered.connect(
							partial(self.AddToCategory, category_name=category, list_of_nodes=nodes))
						category_add_menu.addAction(add_temp)

					# Making actions for adding info to ep/seq. Such as title and style/program
					if source == self.tree:
						if node.getType() in ["episode", "seq"]:

							cur_anim_style = node.getAnimationStyle()
							cur_comp_style = node.getCompStyle()

							menu.addSeparator()
							anim_style_menu = QtWidgets.QMenu("Animation Style", menu)
							comp_style_menu = QtWidgets.QMenu("Comp Style", menu)

							anim_style_group = QtWidgets.QActionGroup(menu)
							comp_style_group = QtWidgets.QActionGroup(menu)

							menu.addAction("Set Title")
							menu.addMenu(anim_style_menu)
							menu.addMenu(comp_style_menu)
							anim_style_list = CC.project_style["animation_style"]
							comp_style_list = CC.project_style["comp_style"]
							# anim_style_list = ["Maya", "Toonboom"]
							# comp_style_list = ["Fusion", "AE"]

							for a_style in anim_style_list:
								a_ac = QtWidgets.QAction(a_style, anim_style_group)
								a_ac.setCheckable(True)
								anim_style_group.addAction(a_ac)
								if a_style == cur_anim_style:
									a_ac.setChecked(True)
								anim_style_menu.addAction(a_ac)

							for c_style in comp_style_list:
								c_ac = QtWidgets.QAction(c_style, comp_style_group)
								c_ac.setCheckable(True)
								comp_style_group.addAction(c_ac)
								if c_style == cur_comp_style:
									c_ac.setChecked(True)
								comp_style_menu.addAction(c_ac)
							menu.addAction("Clear Info")

				if source == self.table_view_from:
					menu.addAction("Clear FROM")
				if source == self.table_view_to:
					menu.addAction("Switch Shot With FROM")
					menu.addAction("Remove Shot from list")
				action = menu.exec_(event.globalPos())
				if not action == None:
					if action.text() == "Open Folder":
						self.__ctrl.openDir(node.getUrl())
					if action.text() == "Refresh Thumbnails":  # NOT USED ANYMORE
						for cur_node in nodes:
							self.__ctrl.refreshThumbs(cur_nodes=self.__ctrl.findShotsInParent(cur_node=cur_node),
													  overwrite=True, overwrite_cache=True, use_threads=False)
					if action.text() == "Rebuild Thumbnails":
						for cur_node in nodes:
							self.__ctrl.refreshThumbs(cur_nodes=self.__ctrl.findShotsInParent(cur_node=cur_node),
													  overwrite=True, overwrite_cache=True, use_threads=True)
					if action.text() == "Zip Anim Folder":
						self.__ctrl.zipFolders(nodes,user_name=self.user_combobox.currentText(), local=False)
					if action.text() == "Zip Anim Folder to FTP":
						self.__ctrl.zipFolders(nodes, destination=self.__ctrl.get_ftp_directory(self.user_combobox.currentText()),user_name=self.user_combobox.currentText(), local=False)
					if action.text() == "Zip Anim Folder (Local)":
						self.__ctrl.zipFolders(nodes,user_name=self.user_combobox.currentText(), local=True)
					if action.text() == "Zip Anim Folder to FTP (Local)":
						self.__ctrl.zipFolders(nodes, destination=self.__ctrl.get_ftp_directory(self.user_combobox.currentText()),user_name=self.user_combobox.currentText(), local=True)
					if action.text() == "Rebuild Anim Publish Report":
						cur_list = nodes
						if node.getType() in ["episode","seq"]:
							cur_list = node.getAllChildren()
						self.__ctrl.createPublishReport(node_list=cur_list)
					if action.text() == "Publish Animation":
						self.__ctrl.publishAnimation(nodes)
					if action.text() == "PublishReport Overview":
						self.__ctrl.publishReport(parent=self, type='overview', scope=node.getName(),filter_type="Prop")
					if action.text() == "Create Prop-OIDs from Report":
						self.__ctrl.buildOIDBasedOnPublishReport(scope=node.getName())
					if action.text() == "PublishReport Breakdown":
						self.__ctrl.publishReport(parent=self, type='breakdown', scope=node.getName())
					if action.text() == "Open Animation File":
						self.__ctrl.FindSceneAndOpen(scene_type="Animation", cur_node=node)
					if action.text() == "Open Light File":
						self.__ctrl.FindSceneAndOpen(scene_type="Light", cur_node=node)
					if action.text() == "Open Comp File":
						self.__ctrl.FindSceneAndOpen(scene_type="Comp", cur_node=node)
					if action.text() == "Create Category":
						self.CreateCategory(list_of_nodes=nodes)
					if action.text() == "Delete Current Category":
						self.DeleteCategory()
					if action.text() == "Remove Selection From Category":
						self.RemoveFromCategory()
					if action.text() == "Open Previs File":
						self.__ctrl.FindSceneAndOpen(scene_type="Previs", cur_node=node)
					if action.text() == "Check Files for Virus":
						shot_nodes = []
						if node.getType() in ["seq","episode"]:
							shot_nodes.extend(node.getAllChildren(node))
						else:
							shot_nodes = nodes
						self.__ctrl.removeVirusFromScene(node_list=shot_nodes)
					if action.text() == "Run SceneSetup":
						setup_nodes = []
						if node.getType() == "seq":
							setup_nodes.extend(node.getAllChildren(node))
						else:
							setup_nodes = nodes
						self.__ctrl.runSceneSetup(setup_nodes)
					if action.text() == "Create Empty Scene":
						if node.getType() == "seq":
							self.__ctrl.runEmptySceneSetup(node)
					if action.text() == "Update Harmony Palettes":
						self.__ctrl.updateHarmonyPalettes(nodes)
					if action.text() == "Render Scene Externally":
						self.__ctrl.toonboomRenderExternally(nodes)
					### OPEN PREVIEW ###
					if action.text() == "Open Anim Preview":
						self.__ctrl.openPreview(node, "anim")
					if action.text() == "Open Animatic":
						self.__ctrl.openPreview(node, "animatic")
					if action.text() == "Open Comp Preview":
						self.__ctrl.openPreview(node, "comp")
					if action.text() == "Create HookUp":
						if len(nodes) == 1:
							if node.getType() == "seq":
								logger.debug("seq!")
								cur_list = node.getChildren()
								cur_name = "%s_HookUp" % node.getName()
						else:
							cur_list = nodes
							cur_name = "%s_Hookup" % self.user_combobox.currentText()

						self.__ctrl.makeHookUpFromNodes(cur_list, cur_name, self.thumb_show_combo.currentText().lower())
						# self.__ctrl.SceneSetupToonBoom(nodes)
					if action.text() == "Compare AV":
						self.__ctrl.compareLengths(self.thumb_show_combo.currentText(), node=node, fps=25, silent=True)
					if action.text() == "Submit Toonboom Scene to RR":
						self.__ctrl.submitToonBoomToRoyalRender(list_of_nodes=nodes,
																user=self.user_combobox.currentText())
					if action.text() == "Submit Comp Scene to RR":
						self.__ctrl.submitFusionToRoyalRender(list_of_nodes=nodes,
															  user=self.user_combobox.currentText(),
															  comp=True)
					# if action.text() == "Submit Comp_preview to RR":
					#     self.__ctrl.submitFusionToRoyalRender(list_of_nodes=nodes,user=self.user_combobox.currentText(),preview=True)
					if action.text() == "Create Toonboom Preview Locally":
						for cur_node in nodes:
							if cur_node.getAnimationStyle() == "Toonboom":
								self.__ctrl.createPreviewFromToonboom(cur_node)
					if action.text() == "Create Comp Preview":
						self.__ctrl.createCompPreview(nodes=nodes, force=False)
					if action.text() == "Create Comp Preview (Force)":
						self.__ctrl.createCompPreview(nodes=nodes, force=True)
					if action.text() == "Submit Comp Preview to RR":
						self.__ctrl.submitCompPreviewToRR(nodes=nodes, force=False, user=self.user_combobox.currentText())
					if action.text() == "Submit Comp Preview to RR (Force)":
						self.__ctrl.submitCompPreviewToRR(nodes=nodes, force=True, user=self.user_combobox.currentText())
						# self.__ctrl.submitFusionToRoyalRender(list_of_nodes=nodes,
						#                                       user=self.user_combobox.currentText(), preview=True,submit_to_RR=False)
					#### APPLY TABLES ACTIONS ####
					if action.text() == "Set as FROM shot":
						self.SetFromShot(node)
					if action.text() == "Add to (apply) TO shots":
						self.AddToListShots(nodes)
					if action.text() == "Create PreComp":
						self.__ctrl.createAEPrecomp(nodes)
					if action.text() == "Switch Shot With FROM":
						self.SwitchToFromShots(nodes[0])
					if action.text() == "Remove Shot from list":
						self.RemoveShotsInTOList(nodes)
					if action.text() == "Clear FROM":
						self.SetFromShot(None)
					if action.text() == "Set Title":
						self.SetTitle(cur_node=node)
					if action.text() == "Clear Info":
						node.setTitle("")
						self.__ctrl.saveNodeInfo(cur_node=node, clear=True)
					if action.text() in ["Maya", "Toonboom", "Fusion", "AE"]:  # Checking the info of anim/comp style
						if action.actionGroup() == anim_style_group:
							if node.getType() == "seq":
								for n in node.getAllChildren():
									n.setAnimationStyle(anim_style_group.checkedAction().text())
									self.__ctrl.saveNodeInfo(cur_node=n, info_keys=["animation_style"])
							node.setAnimationStyle(anim_style_group.checkedAction().text())
							self.__ctrl.saveNodeInfo(cur_node=node, info_keys=["animation_style"])
						elif action.actionGroup() == comp_style_group:
							if node.getType() == "seq":
								for n in node.getAllChildren():
									n.setCompStyle(comp_style_group.checkedAction().text())
									self.__ctrl.saveNodeInfo(cur_node=n, info_keys=["comp_style"])
							node.setCompStyle(comp_style_group.checkedAction().text())
							self.__ctrl.saveNodeInfo(cur_node=node, info_keys=["comp_style"])


		return QtWidgets.QWidget.eventFilter(self, source, event)

	def progressBarLabelUpdate(self, create_dict):
		if "created" in create_dict:
			self.current_progress.append(create_dict["created"])
			# self.progress_bar_label.setMaximumHeight(len(self.current_progress) * 20)
		if "result" in create_dict:
			temp = "Creating Pixmap for %s" % create_dict["result"].getName()
			if temp in self.current_progress:
				self.current_progress.remove(temp)
				# self.progress_bar_label.setMaximumHeight(len(self.current_progress)*20)
		self.progress_bar_label.setText("\n".join(self.current_progress))

	def populateUser(self):
		user_list = []
		for temp_list in CC.users.values():
			user_list.extend(temp_list)
		user_list = sorted(list(set(user_list)))
		self.user_combobox.addItems(user_list)
		cur_dict = self.loadSettings(self.user_save_file)
		if cur_dict:
			if "CompContactSheet" in cur_dict:
				if(cur_dict["CompContactSheet"] in user_list):
					self.user_combobox.setCurrentText(cur_dict["CompContactSheet"])
		run_env["BOM_USER"] = self.user_combobox.currentText()
		self.user_combobox.currentTextChanged.connect(self.saveUser)

	def loadSettings(self, load_file):
		logger.info("Loading Settings")
		if os.path.isfile(load_file):
			with open(load_file, 'r') as cur_file:
				return json.load(cur_file)
		else:
			logger.warning("Can't find %s file" % load_file)
			return {}

	def saveUser(self):
		user = self.user_combobox.currentText()
		run_env["BOM_USER"] = user
		user_save_dict = {"CompContactSheet": user}
		# check if a folder exists:
		if not os.path.exists(os.path.split(self.user_save_file)[0]):
			os.mkdir(os.path.split(self.user_save_file)[0])
		with open(self.user_save_file, 'w+') as saveFile:
			json.dump(user_save_dict, saveFile)
		saveFile.close()

	def tableDoubleClicked(self, cur_index):
		cur_node = self.table_model.getNode(cur_index)
		# if cur_node.getType() == "shot":
		#     logger.debug(cur_node.getRange())
		# else:
		cur_nodes = cur_node.getChildren()
		if cur_node.getType() == "seq":
			self.__ctrl.refreshThumbs(cur_nodes=cur_nodes, overwrite=False, overwrite_cache=True)
		self.table_model = self.__ctrl.setTableModel(cur_nodes)
		self.table_view.setModel(self.table_model)
		self.ExpandToNode(cur_node)

	def ExpandToNode(self, cur_node, selected=None):
		node_list = self.FindPathToTop(cur_node, [cur_node.getName()])
		# name_list = [cur_node.parent().GetName(), cur_node.parent().parent().GetName()]
		if selected:
			selected = cur_node.getName()
		self.iterateOverProxyModelAndExpandAllMatches(node_list, selected)

	def FindPathToTop(self, cur_node=None, parent_list=[]):
		cur_parent = cur_node.getParent()
		if cur_parent:
			parent_list.append(cur_parent.getName())
			parent_list = self.FindPathToTop(cur_parent, parent_list)
		return parent_list

	def iterateOverProxyModelAndExpandAllMatches(self, name_list=[], selected=None, index=QtCore.QModelIndex()):
		for row in range(self.proxyModel.rowCount(index)):
			cur_index = self.proxyModel.index(row, 0, index)
			if self.tree_model.getNode(self.proxyModel.mapToSource(cur_index)).getName() in name_list:
				# print("expanding: %s" % cur_index.getName())
				self.tree.expand(cur_index)
				if self.proxyModel.rowCount(cur_index) > 0:
					self.iterateOverProxyModelAndExpandAllMatches(name_list, selected, cur_index)

			if self.tree_model.getNode(self.proxyModel.mapToSource(cur_index)).getName() == selected:
				# self.treeItemClicked(self.proxyModel.index(row, 0, index))
				self.tree.setCurrentIndex(self.proxyModel.index(row, 0, index))

	def SetFromShot(self, cur_node):
		self.table_model_from = self.__ctrl.setFromTable(cur_node)
		self.table_view_from.setModel(self.table_model_from)
		self.splitter_treetable_tofrom.setSizes([1, 1])

	def AddToListShots(self, cur_nodes):
		self.table_model_to = self.__ctrl.setToTable(cur_nodes, add=True)
		self.table_view_to.setModel(self.table_model_to)
		self.splitter_treetable_tofrom.setSizes([1, 1])

	def Btn_SetFROM(self):
		nodes = self.table_view.model().getNodesByIndex(self.table_view.selectedIndexes())
		self.SetFromShot(nodes[0])

	def Btn_ClearFROM(self):
		self.table_view_to.setModel(self.__ctrl.getFromTable().removeAllNodes())
		self.__ctrl.from_node = []

	def Btn_AddTO(self):
		nodes = self.table_view.model().getNodesByIndex(self.table_view.selectedIndexes())
		self.AddToListShots(nodes)

	def Btn_ClearTO(self):
		self.__ctrl.to_node_list = []
		self.table_view_to.setModel(self.__ctrl.getToTable().removeAllNodes())
		# self.__ctrl.to_node_list = []

	def RemoveShotsInTOList(self, cur_nodes):
		# for node in cur_nodes:
		self.__ctrl.RemoveTo(cur_nodes)
		self.table_view_to.setModel(self.__ctrl.getToTable())

	def SwitchToFromShots(self, cur_node):
		self.__ctrl.SwitchFromAndTo(cur_node)
		self.table_view_from.setModel(self.__ctrl.getFromTable())
		self.table_view_to.setModel(self.__ctrl.getToTable())

	### CATEGORY CALLS ###

	def AddToCategory(self, category_name=None, list_of_nodes=[]):
		if not list_of_nodes:
			for selected_index in self.table_view.selectedIndexes():
				temp_node = self.table_model.getNode(selected_index)
				if temp_node:
					list_of_nodes.append(temp_node)
		if not category_name:
			category_name = self.table_category_combo.currentText()
		self.__ctrl.AddToCategory(category_name, list_of_nodes)
		if self.radiobttn_table_category.isChecked():
			self.updateTable()

	def RemoveFromCategory(self, category_name=None):
		if self.radiobttn_table_category.isChecked():
			table_selected_nodes = []
			for selected_index in self.table_view.selectedIndexes():
				temp_node = self.table_model.getNode(selected_index)
				if temp_node:
					table_selected_nodes.append(temp_node)
			if not category_name:
				category_name = self.table_category_combo.currentText()
			self.__ctrl.RemoveFromCategory(category_name, table_selected_nodes)
			self.updateTable()

	def SetTitle(self, cur_node):
		if cur_node.getTitle():
			cur_title = cur_node.getTitle()
		else:
			cur_title = ""
		text, ok = QtWidgets.QInputDialog().getText(self, "Set Title", "example: BirthdayParty:",
													QtWidgets.QLineEdit.Normal, cur_title)
		if ok and text and not text == "" and not text == cur_title:
			new_title = text
		else:
			logger.info("no new title given")
			return
		cur_node.setTitle(new_title)
		self.__ctrl.saveNodeInfo(cur_node=cur_node, info_keys=["title"])

	def CreateCategory(self, list_of_nodes=[]):
		text, ok = QtWidgets.QInputDialog().getText(self, "Create New Category", "example: Forest:",
													QtWidgets.QLineEdit.Normal, "")
		if ok and text and not text == "":
			category_name = text
		else:
			logger.info("Cancel creation because no name was given")
			return
		if not list_of_nodes:
			list_of_nodes = []
			for selected_index in self.table_view.selectedIndexes():
				temp_node = self.table_model.getNode(selected_index)
				if temp_node:
					list_of_nodes.append(temp_node)
		category = self.__ctrl.CreateCategory(category_name, list_of_nodes)
		if not category:
			logger.info("Already a category with that name. Please pick a new name!")
		else:
			self.populateTableStateCombo(category_name)

	def DeleteCategory(self):  # TODO Add confirmation prompt
		category_name = self.table_category_combo.currentText()
		self.__ctrl.deleteCategory(category_name)
		self.populateTableStateCombo()

	def ThumbComboChanged(self):
		logger.info("Changing thumb view to show: %s" % self.thumb_show_combo.currentText())
		QtGui.QPixmapCache.clear()
		if self.last_selection:
			self.__ctrl.updateViewState(new_view_state=self.thumb_show_combo.currentText())
			self.__ctrl.refreshThumbs(cur_nodes=self.__ctrl.findShotsInParent(cur_node=self.last_selection),
									  overwrite=False, overwrite_cache=True)

	def setProxyModel(self):
		# THE RIGHT ORDER
		self.proxyModel = QtCore.QSortFilterProxyModel(self.tree)
		self.proxyModel.setSourceModel(self.tree_model)
		self.proxyModel.setRecursiveFilteringEnabled(True)
		self.proxyModel.setSortCaseSensitivity(QtCore.Qt.CaseInsensitive)
		self.proxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
		# self.tree.setModel(self.proxyModel)
		self.tree.setModel(self.proxyModel)
		self.proxyModel.sort(0, QtCore.Qt.AscendingOrder)
		self.tree.selectionModel().selectionChanged.connect(self.TreeviewSelectionChanged)

	def TreeviewSelectionChanged(self):
		index = self.tree.currentIndex()
		if index:
			# cur_node = self.proxyModel.mapToSource(index).internalPointer()
			cur_node = self.tree_model.getNode(self.proxyModel.mapToSource(index))
		else:
			cur_node = self.tree_model.root
		if cur_node:
			if cur_node.getType() == "episode":
				if self.last_selection:
					if not cur_node.getName() in self.last_selection.getName() and self.radiobttn_grp_table.checkedButton() == "Sync":
						self.__ctrl.ClearPixCache()
			elif cur_node.getType() == "seq":
				if not self.radiobttn_grp_table.checkedButton() == "Sync":
					self.__ctrl.refreshThumbs(cur_nodes=self.__ctrl.findShotsInParent(cur_node=cur_node),
											  overwrite=False, use_threads=True)
			# if not self.__ctrl.getType(cur_node.getName()) == "shot":
			#     self.__ctrl.refreshThumbs(cur_nodes=self.__ctrl.findShotsInParent(cur_node=cur_node), overwrite=False,use_threads=True)
			# self.__ctrl.createPixmap(cur_node=cur_node) #For shot ?
			self.updateTable()
			self.last_selection = cur_node

	def updateTable(self):
		self.table_model.beginResetModel()
		table_state = self.radiobttn_grp_table.checkedButton().text()
		if table_state == "Sync":
			cur_node = self.tree_model.getNode(self.proxyModel.mapToSource(self.tree.currentIndex()))
			if cur_node:
				self.table_model = self.__ctrl.setTableModel(self.__ctrl.findShotsInParent(cur_node))
				self.__ctrl.refreshThumbs(cur_nodes=self.__ctrl.findShotsInParent(cur_node), overwrite=False,
										  overwrite_cache=True)
		if table_state == "Freeze":
			pass
		if table_state == "Isolate":
			pass
		if table_state == "Category":
			cur_nodes = self.__ctrl.getCategoryNodes(self.table_category_combo.currentText())
			self.__ctrl.refreshThumbs(cur_nodes=cur_nodes, overwrite=False, overwrite_cache=True)
			self.table_model = self.__ctrl.setTableModel(cur_nodes)
		self.table_model.endResetModel()
		self.table_view.setModel(self.table_model)

	def thumbSizeRadioGrpChange(self):
		cur_button = self.radiobttn_grp_thumbsize.checkedButton().text()
		if cur_button == "Large":
			self.__ctrl.setThumbSize("large")
		elif cur_button == "Medium":
			self.__ctrl.setThumbSize("medium")
		else:
			self.__ctrl.setThumbSize("small")
		self.table_model.beginResetModel()
		self.__ctrl.ClearPixCache()
		self.table_model.endResetModel()

	def tableStateRadioGrpChanged(self):
		"""
		Runs when any of the radiobttns are clicked.
		Makes the table view update its content.
		"""
		self.updateTable()

	def tableStateComboChanged(self):
		"""
		Runs when a new category is clicked
		Makes the table view update its content.
		"""
		# print(self.table_state_combo.currentText())
		# node = self.tree_model.getNode(self.proxyModel.mapToSource(self.tree.currentIndex()))
		self.updateTable()

	def populateTableStateCombo(self, current_text=None):
		self.table_category_combo.currentTextChanged.disconnect()
		current_categories = self.__ctrl.getCategories()
		self.table_category_combo.clear()
		self.table_category_combo.addItems(current_categories)
		self.table_category_combo.currentTextChanged.connect(self.tableStateComboChanged)
		if current_text:
			self.table_category_combo.setCurrentText(current_text)

	def populateTree(self):
		self.tree_model = self.__ctrl.createTreeModel()
		# self.tree_model.sort(0, order=QtCore.Qt.AscendingOrder)
		# self.tree.setModel(self.tree_model)
		self.setProxyModel()

	def createSearchCompleter(self):
		self.completer = QtWidgets.QCompleter(self.menu_search_bar)
		self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
		self.completer.setModelSorting(QtWidgets.QCompleter.CaseInsensitivelySortedModel)
		self.completer.setFilterMode(QtCore.Qt.MatchContains)
		self.completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
		self.completer_list = [x.getName() for x in self.__ctrl.getAllNodes()]
		self.completer.setModel(QtCore.QStringListModel(self.completer_list))
		self.menu_search_bar.setCompleter(self.completer)

		self.menu_search_bar.textChanged.connect(self.ProxyUpdate)
		self.menu_search_bar.returnPressed.connect(self.SearchEnter)

	def ProxyUpdate(self, text):
		my_pattern = QtCore.QRegularExpression()
		my_pattern.setPatternOptions(QtCore.QRegularExpression.CaseInsensitiveOption)
		my_pattern.setPattern(text)
		self.proxyModel.setFilterRegularExpression(my_pattern)

	def SearchEnter(self):  # opens or closes the tree view after search
		if self.menu_search_bar.text() == "":
			self.tree.collapseAll()
		else:
			self.tree.expandAll()
			# self.updateTable(name_filter=self.menu_search_bar.text()) #Changes the table view


def run():
	objectName = 'ShotBrowserDock'
	if not MayaDockable.dockableExists(objectName):
		reloadModules.clearModules(["getConfig"])
		MayaDockable.runDockable(objectName, 'Shot Browser', MainWindow())

	# # app = QtWidgets.QApplication(argv)
	# if not QtWidgets.QApplication.instance():
	#     app = QtWidgets.QApplication(sys.argv)
	# else:
	#     app = QtWidgets.QApplication.instance()
	#
	# window = MainWindow(parent=_maya_main_window())

def _maya_main_window():
	"""Return Maya's main window"""
	for obj in QtWidgets.QApplication.topLevelWidgets():
		if obj.objectName() == 'MayaWindow':
			return obj
	raise RuntimeError('Could not find MayaWindow instance')


def test_HookUp():
	ctrl = FrontController()
	nodes = [ctrl.getAllNodes()[3], ctrl.getAllNodes()[4]]
	ctrl.makeHookUpFromNodes(list_of_nodes=nodes, hookup_name="", level="anim")


def TestVersion():
	ctrl = FrontController()
	ctrl.FindVersion(
		name_list=["S207_SQ020_SH040_Comp_V001.aep", "S207_SQ020_SH040_Comp_V002.aep", "S207_SQ020_SH040_Precomp.aep"],
		file_regex="(s207_sq020_sh040)*?", file_ext=".aep")





class Popup(QtWidgets.QDialog):
	def __init__(self, parent=None, title='Popup'):
		super(Popup, self).__init__(parent)
		self.setWindowTitle(title)
		flags = self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint
		flags = flags | QtCore.Qt.WindowStaysOnTopHint
		self.setWindowFlags(flags)

	def popupSetPalette(self):
		#TODO setting palette in maya does NOT look great
		if not in_maya:
			magenta = {"R": 142, "G": 45, "B": 197}
			blue = {"R": 50, "G": 50, "B": 255}

			hi_lgt = blue
			palette = QtGui.QPalette()
			palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
			palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
			palette.setColor(QtGui.QPalette.Base, QtGui.QColor(40, 40, 40))
			palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
			palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
			palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
			palette.setColor(QtGui.QPalette.Text, QtCore.Qt.lightGray)
			palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
			palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
			palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
			palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(hi_lgt["R"], hi_lgt["G"], hi_lgt["B"]).lighter(100))
			palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.white)
			self.setPalette(palette)
			QtWidgets.QApplication.instance().setStyle('Fusion')


def createCompPreviewDone(result):
	for key in result.keys():
		if result[key]:
			print(result[key])

# def addExtraEnv():
#     run_env["TOONBOOM_GLOBAL_SCRIPT_LOCATION"] = "%s/TB/ToonBoom_Global_Scripts" % os.path.dirname(os.path.realpath(__file__))
#     run_env["BOM_USER"] = ""

if not in_maya:  
	if __name__ == '__main__':
		import sys
		if not QtWidgets.QApplication.instance():
			app = QtWidgets.QApplication(sys.argv)
		else:
			app = QtWidgets.QApplication.instance()
		# addExtraEnv()
		mainWin = MainWindow()
		mainWin.show()

	# print(os.environ)
	app.exec_()
	#sys.exit()
# sys.exit(app.exec_())
# print(os.environ)
