# from PySide2 import QtWidgets, QtCore, QtGui
import shiboken6.Shiboken
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

import os
import json

import sys
# sys.path.append( r"C:\Program Files (x86)\Toon Boom Animation\Toon Boom Harmony 22 Premium\win64\bin\python-packages")
#TODO Add selection clears all other tv items and also doesn't set the selection mode back so it doens't connect when you click
#more stuff
try:
	from ToonBoom import harmony
	in_toonboom = True
except Exception as e:
	in_toonboom = False

def log(message):
	if in_toonboom:
		sess = harmony.session()
		sess.log(str(message))
	else:
		print(message)

if in_toonboom:
	log("Launching inside Toonboom")

def tbScene():
	sess = harmony.session()  # Fetch the currently active session of Harmony
	project = sess.project  # The project that is already loaded.
	return project.scene()



# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# BACKEND ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

class Node(object):
	def __init__(self, name=None, parent=None,type=None,subsel=None):
		self.__name = name
		self.type = type
		self._parent = parent
		self.children = []
		self.node_dict = {}
		self.collection_node_dict = {}
		self.icon_type = "Default"
		self.decideIcon()
		self.subsel = subsel

	def decideIcon(self):
		if self.type in ["READ"]:
			self.icon_type = "Drawing"
		elif self.type in ["PEG"]:
			self.icon_type = "Peg"
		elif self.type in ["Preset"]:
			self.icon_type = "Preset"
		elif self.type in ["GROUP"]:
			self.icon_type = "Group"
		elif self.type in ["Collection"]:
			self.icon_type = "Collection"
		else:
			self.icon_type = "Tech"
	# def setSubselection(self, sub):
	# 	sub_list = []
	# 	for s in sub:
	# 		sub_list.append(int(s))
	# 	self.subsel = sub_list

	def getSubselection(self):

		return self.subsel

	def append(self, c_obj):
		self.children.append(c_obj)
		self.children.sort(key=lambda x: x.getName())
		self._row = len(self.children)
		# self._row = len(self.children)

	def child(self, in_row):  # Treeview
		if in_row >= 0 and in_row < len(self.children):
			return self.children[in_row]

	def row(self):  # Treeview
		return self._row

	def setName(self, new_name):
		self.__name = new_name

	def getName(self):
		return self.__name

	def getParent(self):
		return self._parent

	def setParent(self, parent):
		self._parent = parent

	def getType(self):
		return self.type

	def getFullPath(self):
		if self.type and not self.type in ["Preset","Collection"]:
			safe = 0
			full_path = self.__name
			cur_parent = self._parent
			if not cur_parent.getType() == "Collection":
				while(not cur_parent.getType() == "Preset" and safe<10):
					full_path = "%s/%s" % (cur_parent.getName(), full_path)
					cur_parent = cur_parent.getParent()
					safe = safe +1
			full_path = "Top/%s" % full_path
			return full_path

	def getUINode(self,node_type=None):
		log("type: %s. parent: %s. name: %s" % (self.type, self._parent.getName(),self.__name))
		# if self.type =="root":
		# 	return False
		if self._parent == None:
			return self
		elif self._parent.getType() == "root":
			return self
		elif self.type == node_type:
			return self
		else:
			return self._parent.getUINode(node_type=node_type)
			# safe = 0
			# cur_node = self._parent
			# while (not cur_node.getType() == "root" and safe < 10):
			# 	cur_node = cur_node.getParent()
			# return cur_node


	def getAllChildren(self):
		return_children = self.getChildrenOfChildren(self.children)
		return return_children

	def getChildrenOfChildren(self, children):
		return_children = []
		for child in children:
			return_children.append(child)
			if child.getChildren():
				return_children.extend(self.getChildrenOfChildren(child.getChildren()))
		return return_children

	def setChildren(self, c_list=None):
		for cur_child in c_list:
			cur_child.setParent(parent=self)
		self.children = c_list
		self._row = len(self.children)


	def removeChild(self,row):
		if row < 0 or row > len(self.children):
			return False
		child = self.children.pop(row)
		child._parent = None
		return True

	def removeChildNode(self,cur_node):
		self.children.remove(cur_node)
		cur_node.setParent(None)
		self.buildNodeDictFromNode()

	def getChildren(self):
		return self.children

	def setNodeDict(self, node_dict):
		# log("setting node-dict of %s to %s" % (self.__name,node_dict))
		self.node_dict = node_dict

	def getNodeDict(self):
		return self.node_dict

	def updateNodeDict(self):

		# self.buildNodeDictFromNode(self)
		p_node = self.getUINode()
		log("Updating node: From %s -> using %s " % (self.__name,p_node.getName()))
		if p_node:
			node_dict = {}
			name, node_dict = self.buildNodeDictFromNode(p_node)
			return_dict = {name:node_dict}
			# for node in p_node.getChildren():
			# 	name,temp_dict = self.buildNodeDictFromNode(node)
			# 	node_dict[name] = temp_dict
			# log(str(node_dict))
			p_node.setNodeDict(return_dict)
		else:
			return {}

	def buildNodeDictFromNode(self, cur_node=None):
		if not cur_node:
			cur_node = self
		name = cur_node.getName()
		c_type = cur_node.getType()
		c_children = cur_node.getChildren()
		return_dict = {"name":name,"type":c_type,"children":{},"sub_nodes":cur_node.getSubselection()}
		for child in c_children:
			child_name,child_dict = self.buildNodeDictFromNode(child)
			return_dict["children"][child_name] = child_dict
		# if c_type in ["Collection", "Preset"]:
		set_dict = {name: return_dict}
		# log("from buildNode")
		cur_node.setNodeDict(set_dict)
		return (name,return_dict)



# VIEWER -------------------------------------------------------------------------------------------------------------

class TreeModel(QAbstractItemModel):
	def __init__(self, nodes):
		QAbstractItemModel.__init__(self)
		self.root = Node("root", None,"root")

		if in_toonboom:
			# self.dir_for_icons =  os.path.dirname(os.path.dirname(os.path.realpath(__file__))).replace(os.sep,"/") + "/icon/" #CC.get_folder_icon_path()
			if os.environ.get("BOM_PIPE_PATH"):
				self.dir_for_icons = "%s/icon/" % os.environ["BOM_PIPE_PATH"]
			else:
				self.dir_for_icons = "%s/Toon Boom Animation/Toon Boom Harmony Premium/2200-scripts/icon/" % os.path.expandvars("APPDATA")

		else:
			self.dir_for_icons = os.path.realpath(__file__).split("TB")[0].replace(os.sep,"/") + "/icon/"  # CC.get_folder_icon_path()
		# log(self.dir_for_icons)
		self.icon_dict = {}
		self.icon_dict["Group"] = self.dir_for_icons + "TB_Group_01.png"
		self.icon_dict["Preset"] = self.dir_for_icons + "selection_02.png"
		self.icon_dict["Drawing"] = self.dir_for_icons + "Objects-03.png"
		self.icon_dict["Peg"] = self.dir_for_icons + "Objects-02.png"
		self.icon_dict["Tech"] = self.dir_for_icons + "wrench_and_star_01.png"
		self.icon_dict["Collection"] = self.dir_for_icons + "Char-02.png"
		self.icon_dict["Default"] =None

		self.no_thumb_picture = "" #CC.get_no_thumb_icon_path()
		self.nodes = nodes
		self.root.setChildren(nodes)

	# def insertRows(self, position, rows, index, parent):
	# 	self.beginInsertRows(index, position, position + rows - 1)
	# 	self.endInsertRows()
	# 	return True

	# def beginRemoveRows(self, parent, first: int, last: int):

	def rowCount(self, index):
		if index.isValid():
			node = index.internalPointer()
			return len(node.getChildren())
		return len(self.root.getChildren())

	# def removeIndex(self,index):
	# 	self.beginResetModel()
	# 	node = index.internalPointer()
	# 	del node
	# 	self.endResetModel()

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
			image_path = self.icon_dict[node.icon_type]
			if image_path:
				pixmap = QPixmap(image_path)
				pixmap = pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation)
				# pixmap = self.__pixmap_util.convertPathToPixmap(cache_name=None, image_path=image_path, width=20,height=20, added_name="tree_folder")
				return pixmap
		return None

	def removeRow(self, row, parent):
		if not parent.isValid():
			# parent is not valid when it is the root node, since the "parent"
			# method returns an empty QModelIndex
			parentNode = self.root
		else:
			parentNode = parent.internalPointer()  # the node

		parentNode.removeChild(row)
		return True
	def insertRow(self, row, parent):
		pass

	def getNode(self, index):
		if not index.isValid():
			return None
		return index.internalPointer()

	def getRootNode(self):
		return self.root

	def setRootNode(self,root_children):
		self.beginResetModel()
		self.root = Node("root",None,"root")
		self.root.setChildren(root_children)
		self.endResetModel()

	def getNodes(self, list_of_index):
		result = []
		for index in list_of_index:
			if index:
				node = self.getNode(index)
				if node:
					result.append(node)
		return result


# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# CONTROL-LAYER ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

class FrontController(QObject):
	def __init__(self):
		super(FrontController, self).__init__()

		if in_toonboom:
			self.sess = harmony.session()
			self.scene = self.sess.project.scene
		else:
			self.sess = None
			self.scene = None
		self.save_dir = "C:/Temp/TB/"
		self.scene_note_node = None
		self.tree_model = None

	def findLocalNoteNodes(self):
		scene_nodes = self.scene.nodes
		node_list = []
		for x in scene_nodes:
			if "Top/LocalPresetData" in x.path:
				# log("Found top data: %s" % x.name)
				self.scene_note_node = x
			elif "LocalPresetData" in x.path:
				# log("Found data: %s" % x.name)
				node_list.append(x)
		if not self.scene_note_node:
			self.scene_note_node = self.scene.nodes.create("NOTE", "LocalPresetData")
		return node_list

	def updateFromLocalData(self,load_from_sub_data=False):
		if in_toonboom:
			node_list = self.findLocalNoteNodes()
			start_text_value = self.scene_note_node.attributes["TEXT"].get_text_value(1)
			if start_text_value:
				start_dict = self.loadSettings(start_text_value)
				# start_dict = json.loads(start_text_value)
			else:
				start_dict = {}
				load_from_sub_data=True
			if load_from_sub_data:
				for cur_node in node_list:
					text_value = cur_node.attributes["TEXT"].get_text_value(1)
					if text_value:
						temp_dict = json.loads(text_value)
						for key in temp_dict.keys():
							if not key in start_dict.keys():
								start_dict[key] = temp_dict[key]
			my_nodes = self.buildNodesFromDict(start_dict,None)
			self.createTreeModel(my_nodes)


		# for cur_node in node_list:
		# 	cur_node.attributes["TEXT"].get_text_value(1)

	def saveLocalData(self):
		data_dict = {}
		self.tree_model.getRootNode().buildNodeDictFromNode()
		# log(self.tree_model.getRootNode().getNodeDict())
		for tv_node in self.tree_model.getRootNode().getChildren():
			c_dict = tv_node.getNodeDict()
			for k in c_dict:
				data_dict[k] = c_dict[k]
		if in_toonboom:
			t_attr = self.scene_note_node.attributes["TEXT"]
			t_attr.set_text_value(1,(json.dumps(data_dict)))
		# for a in self.scene_note_node.attributes:#["Text"] #(json.dumps(data_dict))
		# 	log(a)




	def createTreeModel(self,nodes=[]):
		nodes.sort(key=lambda x: x.getName())
		self.tree_model = TreeModel(nodes=nodes)
		return self.tree_model

	def getTreeModel(self):
		if not self.tree_model:
			self.tree_model = self.createTreeModel()
		return self.tree_model

	def tbSelectFromIndex(self,tree_indexes,add_children=True):
		tree_nodes_to_select = []
		for i in tree_indexes:
			cur_node = self.tree_model.getNode(i)
			if cur_node:
				# log(cur_node.getSubselection())
				if not cur_node.getType() == "Collection":
					all_children = cur_node.getAllChildren()
					tree_nodes_to_select.append(cur_node)
					if add_children:
						tree_nodes_to_select.extend(all_children)
			# log("TO SELECT: %s" % str(tree_nodes_to_select))
		self.sess.project.scene.selection.select_none()
		p_select_list = []
		for cur_n in tree_nodes_to_select:
			if not cur_n.getType() in ["GROUP","Preset","Collection"]:
				sub = cur_n.getSubselection()

				js_select.set_subselection.call([cur_n.getFullPath(),str(sub)])


	def selectTBNodesFromPath(self,list_of_paths,clear=False):
		if in_toonboom:
			if clear:
				self.sess.project.scene.selection.select_none()
			for n in self.sess.project.scene.nodes:
				# log("Selecting %s" % n.path)
				if n.path in list_of_paths:
					log("Selecting %s" % n.path)
					self.sess.project.scene.selection.add(n)
					# log("Selecting %s" % n.path)
					list_of_paths.remove(n.path)

	def moveNodes(self, move_list, destination_node):
		# log(move_list, destination_node)

		for m_node in move_list:
			if not m_node.getType() =="Collection":
				if not destination_node in m_node.getAllChildren():
					if m_node.getType() == "Preset":
						if not destination_node.getType() == "Collection":
							continue
					# if not m_node.getType() == destination_node.getType():
					log("MOVING: %s" % m_node.getName())
					m_p = m_node.getParent()
					m_p.removeChildNode(m_node)
					m_node.setParent(destination_node)
					destination_node.append(m_node)
					log("doing the move to %s" % destination_node.getName())
		self.saveLocalData()

		# self.tree_model.beginResetModel()
		# self.tree_model.endResetModel()


	def compareDicts(self,main,sec):
		for key in sec.keys():
			log("Checking key: %s" % str(key))
			if not key in main.keys():
				log("Adding %s to %s" % (key, main))
				main[key] = sec[key]
			elif not main[key]["sub_nodes"] == sec[key]["sub_nodes"]:
				sec[key]["sub_nodes"].extend(main[key]["sub_nodes"])
				main[key] = sec[key]
			else:
				self.compareDicts(main[key]["children"],sec[key]["children"])

	def duplicateTVNode(self, cur_node,parent_node):
		new_nodes = self.buildNodesFromDict(cur_node.getNodeDict())
		orig_children = parent_node.getChildren()
		orig_children.extend(new_nodes)
		orig_children.sort(key=lambda x: x.getName())
		parent_node.setChildren(orig_children)
		self.saveLocalData()
		self.tree_model.beginResetModel()
		self.tree_model.endResetModel()


	def createCollection(self, name="Char", selected_nodes=[]):
		"""create a node to insert itself between root and preset nodes"""
		collection_node = Node(name=name,parent=None,type="Collection")

		collection_children_dict = {}
		for n in selected_nodes:
			log("including in preset: %s" % n.getName())
			preset_node = n.getUINode()
			node_dict = preset_node.getNodeDict()
			# collection_children_dict[preset_node.getName()] = node_dict
			for k in node_dict.keys():
				collection_children_dict[k] = node_dict[k]
			preset_node.getParent().removeChildNode(preset_node)


		collection_node_dict = {name:{"name":name,"type":"Collection","children":collection_children_dict}}
		collection_node.setNodeDict(collection_node_dict)
		log("COLLECTION: %s" % collection_node_dict)

		tree_nodes = self.buildNodesFromDict(collection_children_dict, collection_node)

		for c in tree_nodes:
			c.setParent(collection_node)
		collection_node.setChildren(tree_nodes)

		self.addNodesToModel([collection_node])

	def renameNode(self, node, new_name):
		"""change name of node (group?) and then reload model"""
		node.setName(new_name)
		self.saveLocalData()


	def createPreset(self, name="SAFE", node_dict={},parent_node=None):
		"""create a preset based on the name, now it should gather nodes and then add them to the tree_model root node"""
		p = self.createPresetNode(name=name, node_dict=node_dict, parent_node=parent_node)
		# log("%s -> %s" % (p, p.getNodeDict()))
		tree_nodes = self.buildNodesFromDict(node_dict,p)
		p.setChildren(tree_nodes)
		# node_dict
		if parent_node:
			parent_node.append(p)
			self.saveLocalData()
		else:
			self.addNodesToModel([p])
		self.tree_model.beginResetModel()
		self.tree_model.endResetModel()




	def createPresetNode(self, name="Test", node_dict={}, parent_node=None, node_type="Preset"):
		top_node = Node(name=name,parent=parent_node,type=node_type)
		n_d_p = {name:{"name":name,"type":node_type,"children":node_dict}}
		top_node.setNodeDict(n_d_p)
		return top_node

	def addNodesToModel(self,tree_nodes):
		root = self.tree_model.getRootNode()
		# self.tree_model.beginResetModel()
		orig_children = root.getChildren()
		# log(str(tree_nodes))
		tree_nodes.extend(orig_children)
		tree_nodes.sort(key=lambda x: x.getName())
		# log("BUILD: %s" % str(tree_nodes))
		self.createTreeModel(tree_nodes)
		self.saveLocalData()


	def addSelectionToPreset(self, node,selected_nodes=[]):
		if not node.getType() =="Collection":
			preset_node = node.getUINode(node_type="Preset")
			node_dict = preset_node.getNodeDict()
			# log("This is the node dict:" + str(node_dict))
			new_dict = self.createDictFromTBSelection()
			new_children_dict = node_dict[preset_node.getName()]["children"].copy()
			self.compareDicts(new_children_dict,new_dict)
			new_children = self.buildNodesFromDict(new_children_dict)
			# for c in preset_node.getChildren():
			# 	log("removing %s" % c.getName())
			# 	preset_node.removeChildNode(c)
			preset_node.setChildren(new_children)

			self.saveLocalData()

	def buildNodesFromDict(self, node_dict={}, top_node=None):
		children_return = []
		for child_node in node_dict.keys():
			child_dict = node_dict[child_node]["children"]
			sub_nodes = []
			if "sub_nodes" in node_dict[child_node].keys():
				sub_nodes = node_dict[child_node]["sub_nodes"]
			if child_dict:
				grp_node = Node(name=child_node, parent=top_node, type=node_dict[child_node]["type"],subsel=sub_nodes)
				children_return.append(grp_node)
				grp_children = self.buildNodesFromDict(child_dict, top_node=grp_node)
				grp_children.sort(key=lambda x: x.getName())
				grp_node.setChildren(grp_children)
				grp_node.buildNodeDictFromNode(grp_node)
			else:
				children_return.append(Node(name=child_node, parent=top_node, type=node_dict[child_node]["type"],subsel=sub_nodes))
		children_return.sort(key=lambda x: x.getName())
		return children_return

	def savePreset(self, node,name=None):
		preset_node = node.getUINode()
		if preset_node:
			if not name:
				name = preset_node.getName()
			save_path = "%s%s_Preset.json" %(self.save_dir,name)
			node_dict = preset_node.getNodeDict()
			if node_dict:
				self.saveSettings(save_path,preset_node.getNodeDict())
			else:
				log("Can't find the node dict! Contact TD for help")
		else:
			log("Can't find the preset node! Contact TD for help")

	def loadPreset(self,file_path):
		preset_dict = self.loadSettings(file_path)
		if preset_dict:
			# log("Creating Preset with: %s - %s" %(file_path.split("/")[-1].split("_Preset")[0],str(preset_dict)))
			self.addNodesToModel(self.buildNodesFromDict(preset_dict, None))
			# self.createPreset(name=file_path.split("/")[-1].split("_Preset")[0],node_dict=preset_dict)

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

	# def createSubnodeList(self):
	def removeKeyOnSelection(self):
		pro = self.sess()
		his = pro.history
		his.begin("Remove Keys")
		current_frame = int(js_frame.current())
		log(current_frame)
		for n in self.scene.selection.nodes:
			for a in self.getAllAtributes(n.attributes):
				if a.column:
					c = a.column
					if not c.type == "DRAWING":
						if c.keyframe_exists(current_frame):
							c.keyframe_remove(current_frame)
		his.end()
	# 	Check nodes + columns in selection
	def addKeyOnSelection(self):
		pro = self.sess()
		his = pro.history
		his.begin("Add Keys")
		# current_frame = self.scene.selection.frame_start
		current_frame = int(js_frame.current())
		log(current_frame)
		for n in self.scene.selection.nodes:
			for a in self.getAllAtributes(n.attributes):
				if a.column:
					c = a.column
					if not c.type =="DRAWING":
						if not c.keyframe_exists(current_frame):
							c.keyframe_create(current_frame)
		his.end()
	# 	Check nodes + columns in selection
	def getAllAtributes(self, attr_list):
		return_list = []
		for a in attr_list:
			return_list.append(a)
			if a.subattributes:
				return_list.extend(self.getAllAtributes(a.subattributes))
		return return_list

	def createDictFromTBSelection(self,nodes=[]):
		return_dict = {}
		if not nodes and in_toonboom:
				nodes = self.scene.selection.nodes  # The node list of the nodes contained within the 'Top' group.
			# nodes = js_select.get_selection.call()
		for node in nodes:
			if node.parent_group().name == "Top":
				sub_nodes = list(js_select.get_subsel_from_node.call([node.path]))
				if not sub_nodes:
					sub_nodes = []
				return_dict[node.name] = {"name":node.name,"type":node.type, "children":{},"sub_nodes":sub_nodes}
			else:
				node_list = []
				safe = 0
				cur_node = node
				while(not cur_node.name == "Top" and safe<20):
					node_list.append(cur_node)
					cur_node = cur_node.parent_group()
					safe = safe +1
				node_list.reverse()
				return_dict = self.createHierachyFromTBNodes(return_dict, node_list)
		return return_dict

	def createHierachyFromTBNodes(self, parent_dict, parent_list):
		next_dict = parent_dict
		for node in parent_list:
			name = node.name
			sub_nodes = list(js_select.get_subsel_from_node.call([node.path]))
			if not sub_nodes:
				sub_nodes = []
			node_type = node.type
			if not name in next_dict.keys():
				next_dict[name] = {"name":name,"type":node_type, "children":{},"sub_nodes":sub_nodes}
				next_dict = next_dict[name]["children"]
			else:
				next_dict = next_dict[name]["children"]
		return parent_dict

# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
# FRONTEND |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

class SelectionPreset_UI(QDialog):

	def __init__(self, parent=None):
		self._ctrl = FrontController()
		super(SelectionPreset_UI, self).__init__(parent)
		self.setWindowTitle("SelectionPreset_UI")
		self.setObjectName("SelectionPreset_UI")
		self.setWindowFlags(self.windowFlags()|Qt.Window|Qt.WindowStaysOnTopHint)

		self.setParent(parent)
		QPixmapCache.setCacheLimit(200 * 1024)
		# self.setParent(pythonManager.appWidget())
		self.__create_window()
		self.populateTree()
		# self.createSearchCompleter()
		self.resize(700, 400)
		self.show()


	def __create_window(self):
		self.layout_top = QVBoxLayout(self)

		self.menu_bar = QToolBar()


		self.create_bttn = QPushButton("Create Preset")
		self.create_coll_bttn = QPushButton("Create Collection")
		self.add_bttn = QPushButton("Add Selection")
		self.select_bttn = QPushButton("Select")
		self.save_preset_bttn = QPushButton("Save to file")
		self.load_preset_bttn = QPushButton("Load from file")
		self.add_key_bttn = QPushButton("Set Key")
		self.remove_key_bttn = QPushButton("Remove Key")


		self.menu_bar.addWidget(self.create_coll_bttn)
		self.menu_bar.addWidget(self.create_bttn)
		self.menu_bar.addSeparator()
		self.menu_bar.addWidget(self.add_bttn)
		self.menu_bar.addWidget(self.select_bttn)
		self.menu_bar.addSeparator()
		self.menu_bar.addWidget(self.save_preset_bttn)
		self.menu_bar.addWidget(self.load_preset_bttn)
		self.menu_bar.addWidget(self.add_key_bttn)
		self.menu_bar.addWidget(self.remove_key_bttn)


		self.create_bttn.clicked.connect(self.createPreset)
		self.create_coll_bttn.clicked.connect(self.createCollection)
		self.add_bttn.clicked.connect(self.AddSelectionToPreset)
		self.select_bttn.clicked.connect(self.select_items)

		self.save_preset_bttn.clicked.connect(self.saveAsFile)
		self.load_preset_bttn.clicked.connect(self.loadFromFile)
		self.remove_key_bttn.clicked.connect(self.removeKeyCall)
		self.add_key_bttn.clicked.connect(self.addKeyCall)

		self.tree = QTreeView(self)

		self.tree.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.tree.setHeaderHidden(True)
		self.tree.setExpandsOnDoubleClick(True)
		self.tree.setSelectionMode(QAbstractItemView.ExtendedSelection)

		self.tree.setAnimated(True)
		self.tree.setIndentation(20)
		self.tree.setSortingEnabled(True)
		self.tree.sortByColumn(0,Qt.AscendingOrder)


		self.tree.setWindowTitle("Dir View")
		self.tree.installEventFilter(self)

		self.layout_top.addWidget(self.menu_bar)
		self.layout_top.addWidget(self.tree)
	def removeKeyCall(self):
		self._ctrl.removeKeyOnSelection()

	def addKeyCall(self):
		self._ctrl.addKeyOnSelection()
	def getTVNodes(self):
		return_list = []
		root = self.tree_model.getRootNode()
		for c in root.getChildren():
			return_list.append(c)
			if c.getType() == "Collection":
				c_children = c.getChildren()
				for c_c in c_children:
					if c_c.getType() == "Preset":
						return_list.append(c_c)
		log(return_list)

		return reversed(return_list)

	def eventFilter(self, source, event):
		if event.type() == QEvent.ContextMenu:
			if (source is self.tree):
				menu = QMenu()
				nodes = []
				sel_index = []
				if source.selectedIndexes():
					for sel in source.selectedIndexes():
						si = self.tree_model.getNode(sel)
						if si:
							sel_index.append(sel)
							nodes.append(si)

					node = nodes[0]
					if not node.getType() in ["Collection", "Preset"]:
						menu.addAction("Select Only")
					if not node.getType() == "Collection":
						menu.addAction("Select Hierachy")
						menu.addAction("Add Selection")
					menu.addAction("Remove Node and Children")
					menu.addAction("Rename Node")

					menu.addSeparator()
					menu.addAction("Duplicate Node")

					if len(nodes) > 1:
						menu.addAction("Move Selection under last item Selected")

					action = menu.exec_(event.globalPos())
					if not action == None:
						if action.text() == "Select Only":
							self._ctrl.tbSelectFromIndex([sel_index[0]],False)
						if action.text() == "Select Hierachy":
							self.select_items()
						if action.text() == "Add Selection":
							self.AddSelectionToPreset()
						if action.text() == "Remove Node and Children":
							self.tree.clearFocus()
							# self.tree.setCurrentIndex(self.tree_model.index(0, 0, QModelIndex()))
							for cur_index in reversed(sel_index):
								self.tree_model.beginRemoveRows(cur_index.parent(),cur_index.row(),cur_index.row())
								self.tree_model.removeRow(cur_index.row(), parent=cur_index.parent())
								self.tree_model.endRemoveRows()
								self._ctrl.saveLocalData()

						if action.text() == "Rename Node":
							if self.renameNodeDialog(node):
								self.tree_model.beginRemoveRows(sel_index[0].parent(), sel_index[0].row(),
																sel_index[0].row())
								self.tree_model.endRemoveRows()

						if action.text()=="Move Selection under last item Selected":
							self.tree.clearFocus()
							# self.tree.setCurrentIndex(self.tree_model.index(0,0,QModelIndex()))
							self._ctrl.moveNodes(nodes[0:-1],nodes[-1])
							self.tree_model.beginRemoveRows(sel_index[0].parent(), sel_index[0].row(),
															sel_index[0].row())
							self.tree_model.endRemoveRows()
							# self.updateTreeModel()
						if action.text() == "Duplicate Node":
							if len(nodes)>1:
								p_node = nodes[-1]
								dup_nodes = nodes[:-1]
							else:
								p_node = self.tree_model.getRootNode()
								dup_nodes = nodes
							for cur_node in dup_nodes:
								self.duplicateNodeDialog(cur_node,p_node)
				else:
					node = self.tree_model.getRootNode()
					menu.addAction("Create Collection")
					menu.addAction("Create Preset")
					menu.addAction("Load from Local Data")
					action = menu.exec_(event.globalPos())
					if not action == None:
						if action.text() == "Create Collection":
							self.createCollection()
						if action.text() == "Create Preset":
							self.createPreset()
						if action.text() == "Load from Local Data":
							self.updateFromLocalCall()


		return QWidget.eventFilter(self, source, event)

	def saveAsFile(self):
		index = self.tree.currentIndex()
		if index:
			cur_node = self.tree_model.getNode(index)
			name = self.getTextInput("Save Selection", "Pick Name For File")
			if name:
				self._ctrl.savePreset(node=cur_node,name=name)

	def loadFromFile(self):
		self.save_dir = "C:/Temp/TB/"
		fdia = QFileDialog.getOpenFileNames(parent=self,caption="Pick Presets",dir=self.save_dir,filter="Json Files (*.json)")
		# fname = QFileDialog.getOpenFileName('Open file', self.base_path, "Text Files (*.txt)")
		log(str(fdia))
		my_files = fdia[0]
		if my_files != []:
			for f in my_files:
				self._ctrl.loadPreset(f)
			self.updateTreeModel()

	def renameNodeDialog(self,cur_node):
		get_input = self.getTextInput("Duplicate Name:","Pick New Name",cur_node.getName())
		if get_input:
			self._ctrl.renameNode(cur_node,get_input)
			return True
		else:
			return False

	def duplicateNodeDialog(self,cur_node,new_parent):
		# new_name = self.getTextInput("Duplicate Name:","New Name")
		self._ctrl.duplicateTVNode(cur_node,new_parent)
		self.updateTreeModel()
	def getTextInput(self,title, info_text,default_text=""):
		# no_space_validator = QRegularExpressionValidator(QRegularExpression("^[A-Za-z0-9]+"))
		# my_input = QInputDialog()
		text, ok = QInputDialog().getText(self, title, "%s\nNo Spaces or Underscores:" % info_text,QLineEdit.Normal, default_text)
		if ok and text and not text == "" and not text == default_text:
			new_title = text
			return new_title
		else:
			return False
	def TreeviewSelectionChanged(self):
		index = self.tree.currentIndex()
		if index:
			cur_node = self.tree_model.getNode(index)
		else:
			cur_node = self.tree_model.root
		if cur_node:
			self.select_items()
			# self._ctrl.saveLocalData()
			# pass
			# log(cur_node.getNodeDict())

	def select_items(self):
		self._ctrl.tbSelectFromIndex(self.tree.selectedIndexes())
		# for sel_index in self.tree.selectedIndexes():
		# 	cur_node = self.tree_model.getNode(sel_index)

	def updateFromLocalCall(self):
		self._ctrl.updateFromLocalData(True)
		self.updateTreeModel()
	def populateTree(self):
		self._ctrl.updateFromLocalData()
		self.tree_model = self._ctrl.getTreeModel()
		self.tree.setModel(self.tree_model)
		self.tree.selectionModel().selectionChanged.connect(self.TreeviewSelectionChanged)

	# def UpdateModel(self):
	# 	self._ctrl.findAllNodesAndSubs()
	# 	self.tree_model = self._ctrl.createTreeModel()
	# 	self.tree.setModel(self.tree_model)

	def AddSelectionToPreset(self):

		index = self.tree.currentIndex()
		self.tree.clearFocus()
		if index:
			node = self.tree_model.getNode(index)
			log("Adding based on: %s" % node.getName())
			if not node.getType() == "Collection":
				# self.tree_model.beginRemoveRows(index.parent().parent(),index.parent().row(),index.parent().row())
				self.tree_model.beginResetModel()
				self._ctrl.addSelectionToPreset(node)
				# self.tree_model.endRemoveRows()
				# self.tree.clearFocus()
				self.tree_model.endResetModel()
			# 	# self.updateTreeModel()


	def createPreset(self):
		current_name = self.getTextInput("Preset Name:","Pick New Name")
		parent_node = self.tree_model.getNode(self.tree.currentIndex())
		if parent_node:
			if not parent_node.getType() == "Collection":
				parent_node = None
		if current_name:
			return_dict = self._ctrl.createDictFromTBSelection()
			self._ctrl.createPreset(current_name, return_dict,parent_node=parent_node)
			self.updateTreeModel()
		else:
			log("PLEASE PICK A NAME")

	def updateTreeModel(self):
		self.tree_model = self._ctrl.getTreeModel()
		self.tree.setModel(self.tree_model)
		self.tree.selectionModel().selectionChanged.connect(self.TreeviewSelectionChanged)

	# def removeNodesFromUI(self,sel_index=[]):
	# 	for cur_index in reversed(sel_index):
	# 		self.tree_model.beginRemoveRows(cur_index.parent(), cur_index.row(), cur_index.row())
	# 		self.tree_model.removeRow(cur_index.row(), parent=cur_index.parent())
	# 		self.tree_model.endRemoveRows()

	def createCollection(self):
		current_name = self.getTextInput("Duplicate Name:","Pick New Name")
		if current_name:
			t_is = self.tree.selectedIndexes()
			my_nodes = self.tree_model.getNodes(t_is)
			# if not t_is:
			# 	return
			# else:

			# log("BUILDING with name: %s - nodes: %s" %(current_name,my_nodes[0].getName()))
			# self.removeNodesFromUI(t_is)
			self._ctrl.createCollection(current_name, my_nodes)
			self.updateTreeModel()
		else:
			log("PLEASE PICK A NAME")

# def QuickSlider():
# 	dia = QDialog()
# 	vlay = QVBoxLayout()
# 	dia.setLayout(vlay)
# 	slider = QSlider(dia)
# 	vlay.addWidget(slider)
# 	slider.valueChanged.connect(change)
# 	return dia
#
# def change(*args):
# 	log(*args)
def getParentWidget():
	topWidgets = QApplication.topLevelWidgets()
	for tw in topWidgets:
		if isinstance(tw, QMainWindow) and not tw.parentWidget():
			return tw
	return None

def run():
	# sess = harmony.session()
	# scene = sess.project.scene
	# nodes = scene.nodes
	# log(nodes)
	# sel_obj = js_sub.get_subselection.call()
	# log(sel_obj)
	# for s in sel_obj:
	# 	log(s)
	# 	log(type(s))
	# 	name = s["node"]
	# 	sub = s["subobjects"]
	# 	log(name)
	# 	log(sub)
	# test_nodes = ("Top/Deformation-Drawing/Curve_2",4)
	# js_sub.set_subselection.call(test_nodes)
	# log(js_sub.get_subselection.call())

	# TestSelection()
	global my_ui
	my_ui = SelectionPreset_UI(getParentWidget())


def TestSelection():
	from ToonBoom import harmony  # Import the Harmony Module
	sess = harmony.session()  # Get access to the Harmony session, this class.
	proj = sess.project  # Get the active session's currently loaded project.
	scene = proj.scene  # Get the top scene in the project.
	node_path = "Top/Deformation-Drawing/Curve_2"

	node = scene.nodes[node_path]
	log(node.attributes)
	if node:
		for attrbs in node.attributes:
			if attrbs.subattributes:
				log("Attrb %s has %s subattributes." % (attrbs.full_keyword, len(attrbs.subattributes)))
			else:
				log("Attrb %s has no subattributes." % (attrbs.full_keyword))
	else:
		log("Unable to find node: %s" % (node_path))

def buildTestNodes():
	my_collection  = {"collection":{"name":"collection","type":"Collection","children":{}}}
	my_preset = {"preset":{"name":"preset","type":"Preset","children":{}}}

	my_child1_dict = {"child1":{"name":"child1","type":"PEG","children":{}}}
	my_child2_dict = {"child2":{"name":"child2","type":"PEG","children":{}}}
	my_child1_dict["child1"]["children"] = my_child2_dict
	my_preset["preset"]["children"] = my_child1_dict
	my_collection["collection"]["children"] = my_preset

	tv_nodes = my_ui._ctrl.buildNodesFromDict(my_collection)
	return tv_nodes

if __name__ == '__main__':
	import sys
	if not QApplication.instance():
		app = QApplication(sys.argv)
	else:
		app = QApplication.instance()
	my_ui = SelectionPreset_UI()


	my_ui._ctrl.createTreeModel(buildTestNodes())
	my_ui.updateTreeModel()
	app.exec()
	#sys.exit()
# sys.exit(app.exec_())
# if not in_maya:
# 	if __name__ == '__main__':
# 		import sys
# 		if not QtWidgets.QApplication.instance():
# 			app = QtWidgets.QApplication(sys.argv)
# 		else:
# 			app = QtWidgets.QApplication.instance()
# 		# addExtraEnv()
# 		mainWin = MainWindow()
# 		mainWin.show()
#
# 	# log(os.environ)
# 	app.exec_()
