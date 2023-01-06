#TODO Set up project file structure at home. Test publish functions

#TODO Go through Animation Publish / Set Publish and MMCB Publish and gather all general/clean up functions here.



import Configs.OLD_CONFIGS.Config_MiasMagic2 as cfg

try:
	from PyQt5 import QtWidgets, QtCore, QtGui
	in_maya = False

except:
	# import site
	# site.addsitedir(cfg.project_paths["qt_vendor"])
	# from Qt import QtWidgets, QtCore, QtGui

	import maya.cmds as cmds
	import maya.mel as mel
	in_maya = True

import os
import shutil
import Configs.OLD_CONFIGS.ConfigUtil as ConfigUtil
cfg_util = ConfigUtil.ConfigUtilClass(cfg)

from Log.CoboLoggers import getLogger
logger = getLogger()

class PublishFunctions():
	def __init__(self):
		self.func_dict = {}
		self.delete_set = "RemoveInPublish" #Name of selection set, of items that should be deleted or removed in before publish.
		self.ref_remove_list = ["MeasureStickRN", "MeasureStick_AnimRN", "StudioLightRN"] #List of refs to be remove from assets before publish
		self.dump_info = ""  #A varible to collect log info


	######################################################################################
	####### GENERAL ASSET PUBLISH FUNCTIONS ##############################################
	######################################################################################

	def SaveLog(self, save_location, save_info):
		with open(save_location, 'a+') as saveFile:
			saveFile.write("%s\n" % (save_info))

	def SetAssetAttrsBasedOnFile(self): #Meant to gather the correct asset info to set on the root_group of an old asset
		cur_scene = cmds.file(q=True,sn=True)
		my_dict = cfg.project_paths.copy()
		compare_path = cfg_util.CreatePathFromDict(cfg.project_paths["asset_work_path"])
		attr_dict = cfg_util.ComparePartOfPath(cur_scene,compare_path,my_dict)
		return attr_dict

	def CleanRootAttributes(self,scene_info={}): #Deletes old attributes and set new ones based on the filepath
		from_file = self.SetAssetAttrsBasedOnFile()
		if cmds.objExists("Root_Group"):  # Rename root to top??
			self.DeleteOldRootAttributes()
			for key in scene_info.keys():
				cur_value = self.CheckAttribute("Root_Group", key)
				if not cur_value == from_file[key]:
					self.SetStringAttribute("Root_Group",key,from_file[key])

	def RemoveVisibilityKeys(self):
		all_tops = cmds.ls("Anim:*:Root_Group")
		for top in all_tops:
			if cmds.attributeQuery("asset_type", n=top, ex=True):
				cmds.cutKey(top, attribute='visibility', option="keys")
				cmds.setAttr("%s.visibility" % top, 1)


	def UnlockAndHideRigGroup(self):
		c_obj = "|Root_Group|Rig_Group"
		try:
			cmds.setAttr("%s.visibility" % c_obj, cb=True, l=False, k=True)
			cmds.setAttr("%s.visibility" % c_obj, 0)
		except:
			logger.error("Couldn't hide Rig_Group")

	def DeleteOldRootAttributes(self): #meant to delete all Afilm attributes on root_groups from kiwiOgStrit1
		c_obj = "Root_Group"
		if cmds.objExists(c_obj):
			# unlock visibility so we can remove the aiVisibility attribute
			cmds.setAttr("%s.visibility" % c_obj, cb=True, l=False, k=True)
			u_attrs = cmds.listAttr(c_obj, ud=True)  # get all attributes that are user generated
			if u_attrs:
				for c_a in u_attrs:  # check for ai attribute
					if c_a.startswith("ai"):
						cmds.deleteAttr(c_obj, at=c_a)  # delete it if possible

	def CleanRootGroup(self, cur_asset_info):
		c_obj = "|Root_Group"
		attr_order = ["asset_type", "asset_category", "asset_name"]

		c_root = "|Root_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl|Root_Ctrl_Group|Root_Ctrl"
		c_obj_super = "|Root_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl"

		for c_at in ["scaleX", "scaleY", "scaleZ"]:
			if cmds.objExists(c_root):
				cmds.setAttr("%s.%s" % (c_root, c_at), e=True, k=True, l=False)
			if cmds.objExists(c_obj_super):
				cmds.setAttr("%s.%s" % (c_obj_super, c_at), e=True, k=True, l=False)

		if cmds.objExists(c_root):
			cmds.deleteAttr(c_root, at="smooth")

		if cmds.objExists(c_obj):  # Clean up Root_Group
			self.DeleteOldRootAttributes()
			for my_attr in attr_order:
				self.SetStringAttribute(c_obj, my_attr, cur_asset_info[my_attr])

	def RemoveOldSetsAndAddNew(self):
		# Add and remove sets:
		unlock_and_remove = ["Anim_Set", "Model_Set", "Render_Set","Rig_Set"]
		add_and_lock = ['Anim_Delete_Set',"Rig_Delete_Set",'PublishSet']
		add_to_publish_set = ["Root_Group"]
		for r_set in unlock_and_remove:
			if cmds.objExists(r_set):
				cmds.lockNode(r_set, lock=False)
				cmds.delete(r_set)
		for c_set in add_and_lock:
			if not cmds.objExists(c_set):
				cmds.sets(n=c_set, empty=True)
			cmds.lockNode(c_set, lock=True)
		cmds.sets(add_to_publish_set, add="PublishSet")

	def CleanOldAssets(self,step=None): #Meant to clean up setdress assets from the old pipeline
		c_obj = "|Root_Group"
		attr_order = ["asset_type", "asset_category","asset_name"]

		##Extra cleanup part. Might fail.
		c_root = "Root_Ctrl"
		c_obj_super = "SuperRoot_Ctrl"
		cmds.setAttr("%s.__________Extra" % c_obj, l=False)
		cmds.deleteAttr(c_root, at="__________Extra")
		cmds.deleteAttr(c_root, at="smooth")

		for c_at in ["scaleX", "scaleY", "scaleZ"]:
			cmds.setAttr("%s.%s" % (c_root, c_at), e=True, k=True, l=False)
			cmds.setAttr("%s.%s" % (c_obj_super, c_at), e=True, k=True, l=False)

		file_type = cmds.file(q=True, type=True)
		file_cur_path = cmds.file(q=True,sn=True)
		# folder_path = "/".join(file_cur_path.split("/")[:-1])
		# file_name = cmds.file(q=True,sn=True,shn=True).split(".")[0]
		folder_path, file_name = os.path.split(file_cur_path)
		file_name = file_name.split(".")[0]
		if step:
			file_name = "%s_%s" % (file_name.split("_")[0], step)
		path_clean = "%s/%s" % (folder_path, file_name)
		if "mayaBinary" in file_type:
			if cmds.objExists(c_obj): #Clean up Root_Group
				self.DeleteOldRootAttributes()
				my_attr_dict = self.SetAssetAttrsBasedOnFile()
				for my_attr in attr_order:
					self.SetStringAttribute(c_obj,my_attr,my_attr_dict[my_attr])

			self.DeleteUnknown()
			self.DeleteUnusedNodes()
			#If ctrls are needed, then run replace ctrl script here: Otherwise delete the old nodes:
			old_ai_shapes = cmds.ls(type="unknownDag")
			for old in old_ai_shapes:
				cmds.delete(old)
			try:
				cmds.file(type="mayaAscii")  # change file format
				cmds.file(rename="%s.ma" % path_clean)
				cmds.file(save=True)
				#TRY TO MOVE ORIG FILE INTO HISTORY FOLDER
				history_folder = "%s/_History/" % folder_path
				if not os.path.exists(history_folder):
					os.mkdir(history_folder)
				move_file = "%s/%s_ORIG.mb" % (history_folder, file_name.split(".")[0])
				shutil.move(file_cur_path, move_file)
			except Exception as c_e:
				logger.error("Can't change fileformat?")
				return False

	def GetAssetInfoFromRoot(self,selection=None):
		asset_dict = {}
		if selection:
			root_group = cmds.ls("*%s:Root_Group" % ":".join(selection.split(":")[0:-1]))
			root_group = root_group[0]
		else:
			root_group = cmds.ls("*::Root_Group*", sl=True)
			if root_group:
				root_group = root_group[0]
			else:
				root_group = "Root_Group"
		if cmds.objExists(root_group):
			attribute_list = ["asset_type", "asset_category", "asset_name"]
			for cur_a in attribute_list:
				c_return = self.CheckAttribute(root_group, cur_a)
				if c_return:
					asset_dict[cur_a] = c_return
				else:
					logger.info("can't find: %s on %s" % (cur_a, root_group))
					return False
			return asset_dict
		return False

	def GetAssetInfoFromFile(self): #TODO Make this more efficient. Right now it always checks with file, because it asset_step is not included on root.
		import maya.cmds as cmds
		scene_info = {"asset_type": "", "asset_category": "", "asset_name": "", "asset_step": ""}
		cur_scene_path = cmds.file(q=True, sn=True)  # the current scenepath
		# get_from_scene = False  # a boolean to decide if we need to use the scene path to gather asset info

		# Check if the base asset path is in the scene path.
		if cfg_util.CreatePathFromDict(cfg.project_paths["asset_top_path"]) in cur_scene_path:
			check_path = cfg.project_paths["asset_work_path"]
		else:
			# print("CAN'T PUBLISH A FILE OUT OF THE STRUCTURE!")
			return False

		if cur_scene_path == "":
			self.CollectDumpInfo("GetAssetInfoFromFile", "File not saved. Can't get info from here")
			return False
		# if cmds.objExists("Root_Group"):
		# 	for key in scene_info.keys():
		# 		cur_value = self.CheckAttribute("Root_Group", key)
		# 		if cur_value and not cur_value == "":
		# 			scene_info[key] = cur_value
		# 		# else:
		# 			# print("Missing info: Can't proceed without: %s" % key)
		# 			# self.CollectDumpInfo("GetAssetInfoFromFile", "Missing info: Can't proceed without: %s" % key)
		# else:
		# 	self.CollectDumpInfo("GetAssetInfoFromFile",
		# 							"Can't find Root_Group to check for attributes. Will try to extrapolate from scene path out from scene path")

		collect_dict = cfg.project_paths.copy()
		collect_dict.update(scene_info) #use the info already collected from root

		compare_path = cfg_util.CreatePathFromDict(check_path, collect_dict)
		collect_dict = cfg_util.ComparePartOfPath(cur_scene_path, compare_path)
		if collect_dict:
			scene_info.update(collect_dict)
		else:
			return False
		# if not collect_dict:  # If file works out:
		# 	print("Not the correct type of file to publish!")
		# 	return False


		# for key in scene_info.keys():
		# 	if key in collect_dict:
		# 		scene_info[key] = collect_dict[key]
		# 	else:
		# 		return False
		if "" in scene_info.values():
			logger.info("Missing: INFO: %s" % scene_info)
			return False
		return scene_info
	# def CheckSceneAgainstDict(self,info_dict):
	# 	compare_path = "%s.ma" % cfg_util.CreatePathFromDict(cfg.project_paths["asset_work_path"], info_dict)
	# 	scene_file = cmds.file(q=True,sn=True)
	# 	if scene_file == compare_path:
	# 		return True
	# 	else:
	# 		return scene_file
	###########CHECKS FOR PUBLISH READINESS #############################################

	def CheckSetdressScene(self):
		###  CHECK FOR GROUPS  ###
		if not cmds.objExists('Proxy'):
			logger.debug('Setdress scene is missing Proxy group')
			return False
		if not cmds.objExists('Full'):
			logger.debug('Setdress scene is missing Proxy group')
			return False

		if not cmds.listRelatives('Proxy', c=True):
			logger.debug('Proxy Group is empty')
			return False
		if not cmds.listRelatives('Full', c=True):
			logger.debug('Full Group is empty')
			return False
		return True

	def CheckPublishSet(self):
		if not cmds.objExists(cfg.publish_set):
			logger.debug("NO PublishSet! Nothing will be published without one!")
			return False
		if not cmds.sets(cfg.publish_set, q=True):
			logger.debug("PublishSet EMPTY, please add what you would like to publish")
			return False
		return True


	###################################################################
	############### Config path/Asset functions #######################
	############### Moved to ConfigUtil		    #######################
	###################################################################

	# def ComparePartOfPath(self, scene_path, compare_path, info_dict={}):
	# 	print("COMPARING: %s to %s" % (scene_path,compare_path))
	# 	if not len(scene_path.split("/")) == len(compare_path.split("/")): #check if the two paths are able to be compared
	# 		print("Not equal paths: %s and %s " % (scene_path,compare_path))
	# 		return False
	# 	if "." in scene_path: #remove the extension
	# 		scene_path = scene_path.split(".")[0]
	# 	if "<" in compare_path:
	# 		for parts in compare_path.split("<"):
	# 			if not parts == "":
	# 				if ">" in parts:
	# 					parts_split = parts.split(">")
	# 					cur_key = parts_split[0]
	# 					after = parts_split[1]
	# 					if after == "":
	# 						cur_value = scene_path
	# 						info_dict[cur_key] = cur_value
	# 					else:
	# 						self.CollectDumpInfo("ComparePartOfPath","From ScenePath: %s : %s" % (cur_key, scene_path.split(after)[0]))
	# 						cur_value = scene_path.split(after)[0]
	# 						info_dict[cur_key] = cur_value
	# 						scene_path = after.join(scene_path.split(after)[1:])
	# 				else:
	# 					scene_path = scene_path.split(parts)[1]
	# 	return info_dict

	# def CreatePathFromDict(self, cur_string, path_dict):
	# 	if "<" in cur_string:
	# 		create_path = ""
	# 		for parts in cur_string.split("<"):  # Split up string in with start of VAR <
	# 			if ">" in parts:  # If start part skip
	# 				cur_key = parts.split(">")[0]
	# 				if cur_key in path_dict:
	# 					cur_var = path_dict[cur_key]
	# 					if not cur_var == "":
	# 						cur_var = self.CreatePathFromDict(cur_var, path_dict)
	# 					else:
	# 						cur_var = "<%s>" % parts.split(">")[0]
	# 					create_path = "%s%s%s" % (create_path, cur_var, parts.split(">")[1])
	# 				else:
	# 					create_path = "%s<%s" % (create_path, parts)
	# 			else:
	# 				create_path = "%s%s" % (create_path, parts)
	# 		return create_path
	# 	else:
	# 		return cur_string

	####################################################################
	############### VRAY FUNCTIONS AND GPU/PROXY CREATION  #############
	####################################################################

	def CreateVraySphereOnObject(self,constrain=False):
		current_obj = cmds.ls(sl=True)
		if current_obj:
			current_obj = current_obj[0]
			cur_namespace = ":".join(current_obj.split(":")[0:-1])
			cur_name = "_".join(current_obj.split(":")[0:-1])
			geo_group = "%s:Geo_Group" % cur_namespace
			#get world loc  of current_obj
			current_placement = cmds.xform(current_obj,q=True, translation=True,ws=True)

			# cur_distance = self.FindBoundingBoxAndSetRadius(bounding_group=geo_group,start_loc=current_placement)
			cur_distance = 30
			cur_volume = self.CreateVraySphereFade(cur_name=cur_name,cur_radius=cur_distance)
			if constrain:
				cmds.parentConstraint(current_obj,cur_volume,mo=False)
		else:
			cur_volume = self.CreateVraySphereFade(cur_name="SceneSphere", cur_radius=30)

	def ReturnLocationDifference(self,goal_vec, cur_vec):
		import math
		dist = math.sqrt(((goal_vec[0] - cur_vec[0]) ** 2) + ((goal_vec[1] - cur_vec[1]) ** 2) + ((goal_vec[2] - cur_vec[2]) ** 2))
		return dist

	def FindBoundingBoxAndSetRadius(self, bounding_group,start_loc):
		#TODO Run the frame-range down to figure out if the bounding box needs to be bigger.
		#TODO Check both upper and lower point of bounding box!
		# start_loc = [0, 7.3, 0]
		cur_list = cmds.listRelatives(bounding_group, type="mesh", ad=True, ni=True)
		cur_list = cmds.ls(cur_list, geometry=True, ni=True)
		bbox = cmds.exactWorldBoundingBox(cur_list, ce=True, ii=False)
		bot_distance = self.ReturnLocationDifference(list(bbox)[0:3],start_loc)
		top_distance = self.ReturnLocationDifference(list(bbox)[3:6], start_loc)
		if top_distance>bot_distance:
			cur_distance = top_distance
		else:
			cur_distance = bot_distance
		return cur_distance
		# cmds.setAttr("%s.radius" % base_object, cur_distance * 1.3)

	def CreateVraySphereFade(self,cur_name=None,cur_object=None,cur_radius=None):
		mel.eval("vrayCreateSphereFade")
		set_volume = self.CreateVraySphereFadeVolume()
		sphere_volume = "%s_SphereFade" % cur_name
		sphere_fades = cmds.ls("VRaySphereFade*", type="VRaySphereFade")
		if sphere_fades:
			sphere_transforms = cmds.listRelatives(sphere_fades[0], type="transform", parent=True)
			sphere_volume = cmds.rename(sphere_transforms[0], sphere_volume)
			# sphere_volume = sphere_transforms[0]
			sphere_fade = cmds.listRelatives(sphere_volume, type="VRaySphereFade")[0]
			if cur_radius:
				cmds.setAttr("%s.radius" % sphere_fade, cur_radius*1.2)
			else:
				cmds.setAttr("%s.radius" % sphere_fade, 50)
			sphere_group = cmds.group(sphere_volume,name="%s_Group" % sphere_volume)

			cur_message = cmds.listConnections("%s.settings" % sphere_volume)
			if cur_message:
				if not set_volume in cur_message:
					# pass
					cmds.connect("%s.message" % sphere_volume,"%s.settings" % sphere_volume,f=True)
			return sphere_group
		return None

	def CreateVraySphereFadeVolume(self, fade_volume="KS_SphereRenderVolume"):
		# fade_volume = "KS_SphereRenderVolume"
		if not cmds.objExists(fade_volume):
			fade_volumes = cmds.ls(type="VRaySphereFadeVolume")
			if fade_volumes:
				logger.debug(fade_volumes)
				cmds.rename(fade_volumes[0], fade_volume)
				cmds.setAttr("%s.affectAlpha" % fade_volume, 1)
				cmds.setAttr("%s.emptyColor" % fade_volume, 0, 0, 0, type="double3")
				cmds.setAttr("%s.falloff" % fade_volume, 0.25)
				cmds.defaultNavigation(connectToExisting=True, source=fade_volume, destination='vraySettings.cam_environmentVolume',f=True)
				return fade_volume
			else:
				return False
		return fade_volume

	def SmoothSmoothSet(self,input_list=[]):
		if not input_list:
			my_objs = self.FindObjectsFromSet("Smooth_Set")
		else:
			my_objs = input_list
		if my_objs:
			for obj in my_objs:
				if cmds.objExists(obj):

					if cmds.listRelatives(obj, s=True):
						logger.debug("HEYHEY Object: " % obj)
						cmds.delete(obj, ch=True)
						cmds.polySmooth(obj, mth=0, sdt=2, ovb=1, ofb=3, ofc=0, ost=0, ocr=0, dv=2, bnr=1, c=1, kb=1, ksb=1,
										khe=0, kt=1, kmb=1, suv=1, peh=0, sl=1, dpe=1, ps=0.1, ro=1, ch=0)
					children = cmds.listRelatives(obj, children=True, type="transform",f=True)
					if children:
						self.SmoothSmoothSet(children)

	def CreateSetdressProxySetup(self, asset_info):  # change to asset_info?
		base_path = cfg_util.CreatePathFromDict(cfg.project_paths["asset_base_path"], asset_info)
		gpu_path = cfg_util.CreatePathFromDict(cfg.ref_paths["GPU"], asset_info)
		# gpu_path = '%sCache/Gpu' % (base_asset_path)
		vray_path = cfg_util.CreatePathFromDict(cfg.ref_paths["VrayProxy"], asset_info)
		# vray_path = '%sVrMesh' % (asset_base_path)

		gpu_node = self.createGpuCache(gpu_path, asset_info["asset_name"
		], 'Proxy', replace=True)
		vray_node = self.createVrayProxy(vray_path, mesh_group='Full', previewFaces=1000, deleteNodes=True,
										 crtProxy=True)
		gpu_transform = cmds.listRelatives(gpu_node,parent=True)[0]
		import transferCustomAttributes
		transferCustomAttributes.transferAttributes("Root_Group",gpu_transform)
		# self.ApplyVraySubDiv([vray_node])
		cmds.parent(vray_node, gpu_node)
		self.AddToSet(cfg.publish_set, cmds.listRelatives(gpu_node, p=True))
		self.setVrayProxyDisplay(vray_node)

	def createGpuCache(self, out_path, asset_name, mesh_group, replace=False):

		if cmds.objExists(mesh_group):
			# zero translations
			cmds.makeIdentity(mesh_group, apply=True, s=True)

			# set directory
			# export_dir = '%sCache/Gpu' % (base_asset_path)

			out_folder_path, out_file = os.path.split(out_path)
			# Create directory
			if not os.path.exists(out_folder_path):
				os.makedirs(out_folder_path)

			# String mesh elements
			gpu_sel = ''
			for m in cmds.listRelatives(mesh_group, c=True,f=True):
				gpu_sel = '%s -root %s' % (gpu_sel, m)
			logger.debug('GPU ITEMS : ', gpu_sel)

			# EXPORT GPU
			# command = "-frameRange 1 1 -uvWrite %s -file %s/%s.abc" % (gpu_sel, out_path, asset_name)  # missing size and color
			command = "-frameRange 1 1 -uvWrite %s -file %s" % (gpu_sel, out_path)  # missing size and color
			a = cmds.AbcExport(j=command)
			logger.debug('abc result', a)

			if replace:
				cmds.lockNode(mesh_group, lock=False)
				logger.debug('Mesh group: ' + str(mesh_group))
				logger.debug('Mesh group shape: ' + str(mesh_group + "Shape"))
				if cmds.objExists(mesh_group):
					logger.debug('mesh_group exists')
				if cmds.objExists(mesh_group + "Shape"):
					logger.debug('Mesh_group_shape exists')
				cmds.delete(mesh_group)
				cache_node = cmds.createNode("gpuCache", name=mesh_group + "Shape")
				logger.debug("GPU Shape: %s" % cache_node)
				cmds.setAttr(cache_node + ".cacheFileName", out_path, type="string")

				return cache_node

			return (out_path)

		else:
			logger.debug('NO %s IN SCENE' % (mesh_group))
			return False

	def ApplyVraySubDiv(self, c_list=[], on_off=1):
		for c_obj in c_list:
			get_shape = cmds.listRelatives(c_obj, shapes=True)[0]
			mel.eval('vray addAttributesFromGroup "%s" "vray_subdivision" %s' % (get_shape, on_off))

	def CreateOrAddVraySet(self,set_name="",add_objects=["Geo_Group"]):
		"""This functions creates a vray disps set, that are used to apply subdiv to multi objects."""
		# import maya.mel as mel
		full_name = "%s_SubDivSet" % set_name
		if not cmds.objExists(full_name):
			cmds.createNode("VRayDisplacement", n="%s" % full_name)
			mel.eval('vray addAttributesFromGroup "%s" "vray_subdivision" %s' % (full_name, 1))
		cmds.sets(add_objects, add=full_name)

	def CreateVrayObjectSet(self,set_name="", obj_list=None,selection=True, use_force=True):
		"""This functions creates a vray object set, that are used for applying shadow matte to multiple objects or setting OIDs"""
		sel = cmds.ls(sl=True)
		if not selection:
			cmds.select(clear=True)
		if obj_list and not sel == obj_list:
			cmds.select(obj_list, r=True)
		if not cmds.objExists(set_name):
			obj = mel.eval('vray "objectProperties" "add_single" "VRayObjectProperties" "%s" "force"' % set_name)
			cmds.rename(obj, set_name) #might need a [0]
		if obj_list:
			if use_force:
				cmds.sets(obj_list,edit=True,forceElement=set_name)
			else:
				cmds.sets(obj_list, edit=True, include=set_name)

		# print("OLD SELECTION: %s" % sel)
		# cmds.select(sel)
	
	def SetOIDonObjectSet(self, set_name="", cur_ID=None):
			cmds.setAttr("%s.objectIDEnabled" % set_name, 1)
			cmds.setAttr("%s.objectID" % set_name, cur_ID)
	
	def SetOIDonObjs(self, object_list=None, cur_ID=None):
		if object_list and cur_ID:
			for c_obj in object_list:
				mel.eval('vray addAttributesFromGroup "%s" "vrayObjectID" %s' % (c_obj, 1))
				cmds.setAttr("%s.vrayObjectID" % c_obj, cur_ID)

	def SetVrayObjectSetToBlackMatte(self, set_name=None):
		if cmds.objExists(set_name):
			cmds.setAttr("%s.matteSurface" % set_name, 1)
			cmds.setAttr("%s.shadows" % set_name, 1)
			cmds.setAttr("%s.affectAlpha" % set_name, 1)
			cmds.setAttr("%s.alphaContribution" % set_name, -1)

	def createVrayProxy(self, out_path="", mesh_group='Full', previewFaces=1000, deleteNodes=False, crtProxy=True):

		# export_dir = '%sVrMesh' % (asset_base_path)
		out_folder, out_file = os.path.split(out_path)
		if not os.path.exists(out_folder):
			os.makedirs(out_folder)

		cmds.select(mesh_group, r=True)
		cmds.lockNode(mesh_group, lock=False)
		logger.debug('VRAY ITEMS :', cmds.listRelatives(mesh_group, c=True))
		# Changed name to VRayProxy
		result = cmds.vrayCreateProxy(node='VRayProxy', dir='%s/' % (out_folder), fname=out_file,
									  exportType=1, createProxyNode=crtProxy, existing=False, previewFaces=previewFaces,
									  overwrite=True,
									  vertexColorsOn=True, ignoreHiddenObjects=True, previewType="clustering")
		# result = cmds.vrayCreateProxy(node='Full', dir='%s/' % (out_folder), fname='%s.vrmesh' % (asset_name),
		# 							  exportType=1, createProxyNode=crtProxy, existing=False, previewFaces=previewFaces,
		# 							  overwrite=True,
		# 							  vertexColorsOn=True, ignoreHiddenObjects=True, previewType="clustering")

		vrayNode = None
		if result:
			vrayNode = result[0]

		# if deleteNodes: #Don't need this, create proxy auto deletes what it converts
		# 	cmds.delete(node)

		return vrayNode

	def setVrayProxyDisplay(self, node):

		nodes = node
		if not isinstance(node, list):
			nodes = [node]

		for i in nodes:
			logger.debug('V_NODE : ', i)
			vray_vis = i + ".lodVisibility"
			cmds.setAttr(vray_vis, 0)

	def ReplaceVrayProxyWithMesh(self, refs=None):
		logger.debug("Replacing vray proxies with mesh for publishing as a proxy")
		import maya.mel as mel
		if not refs:
			refs = cmds.file(q=True, r=True)

		for ref in refs:
			if "/Setdress/" in ref: #if there is a setdress proxy
				cur_ns = cmds.referenceQuery(ref, ns=True)[1:] #get namespace
				cmds.file(ref, ir=True) #import the ref
				vmesh = "%s:VRayProxy_vraymesh" % cur_ns
				if cmds.objExists(vmesh):
					mel.eval('vray restoreMesh "%s"' % vmesh)
					vmesh_restored = cmds.listRelatives(cmds.ls(sl=True), parent=True, type="transform")
					vmesh_restored = cmds.rename(vmesh_restored,"%s:TempMesh" % cur_ns)
					cmds.select(vmesh_restored, r=True)
					mel.eval('polyCleanupArgList 4 { "0","1","0","0","0","0","0","0","1","1e-05","1","1e-05","0","1e-05","0","-1","0","0" }')

				else:
					logger.debug("can't find: %s" % vmesh)
					return False
				all_placements = cmds.ls("*%s:Proxy*" % cur_ns, type="transform")
				for p in all_placements:
					p_parent = cmds.listRelatives(p,parent=True,f=True)
					p_obj = cmds.duplicate(vmesh_restored,n="%s_tempMesh" % p)[0]
					self.Align(p, p_obj)
					cmds.setAttr("%s.visibility" % p, 0)
					if p_parent:
						cmds.parent(p_obj, p_parent)
					cmds.delete(p)
				cmds.delete(vmesh_restored)
	###################################################
	############## Yeti Functions            ##########
	###################################################

	def SetYetiNodeToCache(self):
		yeti_nodes = cmds.ls(type="pgYetiMaya")
		for yeti_node in yeti_nodes:
			cmds.setAttr("%s.fileMode" % yeti_node, 1)
			cmds.setAttr("%s.overrideCacheWithInputs" % yeti_node, 1)

	###################################################
	############## General Util and Clean Up ##########
	###################################################
	def GeoNormCons(self,selection=False, normal=True):
		if not selection:
			selection = cmds.ls(sl=True)
		if selection:
			target = selection[-1]
			movers = selection[0:-1]
			for sel in movers:
				gc_del = cmds.geometryConstraint(target, sel, weight=1)
				if normal:
					nc_del = cmds.normalConstraint(target, sel, weight=1, aimVector=[0, 1, 0], upVector=[0, 1, 0],
												   worldUpType="scene")
					cmds.delete(nc_del)
				cmds.delete(gc_del)

	def Align(self,target=None, moving=None):
		if not target and not moving:
			sel = cmds.ls(sl=True)
			target = sel[0]
			moving = sel[1]
		p_delete = cmds.parentConstraint(target, moving, mo=False, n="PO_ToDelete")
		s_delete = cmds.scaleConstraint(target, moving, mo=False, n="SC_ToDelete")
		cmds.delete(p_delete)
		cmds.delete(s_delete)

	def GroupAndParent(self,selection=None):
		if not selection:
			selection = cmds.ls(sl=True)
		for sel in selection:
			temp_grp = cmds.group(empty=True, name="%s_Group" % sel)
			t_con = cmds.parentConstraint(sel, temp_grp, mo=False)
			cmds.delete(t_con)
			cmds.parent(sel, temp_grp)

	def CacheAllArmConstraintsInScene(self):
		obj_list = ["L_Shoulder_Extract_360_Loc_parentConstraint1", "L_Wrist_Forearm_Extract_360_Loc_parentConstraint1",
		 "R_Wrist_ectract_360_loc_parentConstraint1", "R_Upperarm_Twist_Extract_loc_360_orientConstraint1"]
		for cur_obj in obj_list:
			cur_objs = cmds.ls("*::%s" % cur_obj)
			for cur_asset in cur_objs:
				if cmds.getAttr("%s.interpType" % cur_asset)==4:
					logger.debug("Already on Cache: Skipping %s" % cur_asset )
					continue
				if ":" in cur_asset:
					cur_asset = ":".join(cur_asset.split(":")[0:-1])
				logger.debug("Trying to Cache: %s -> %s" % (cur_asset,cur_obj))
				self.CacheArmConstraint(asset=cur_asset,constraint_list=[cur_obj])


	def CacheArmConstraint(self, asset=None, range=None,delete=False,constraint_list=None):
		if not constraint_list:
			constraint_list = ["L_Shoulder_Extract_360_Loc_parentConstraint1", "L_Wrist_Forearm_Extract_360_Loc_parentConstraint1", "R_Wrist_ectract_360_loc_parentConstraint1", "R_Upperarm_Twist_Extract_loc_360_orientConstraint1"]
		#get asset namespace
		if not asset:
			selection = cmds.ls(sl=True)[0]
			if ":" in selection:
				asset = ":".join(selection.split(":")[0:-1])
				logger.debug(asset)
		#get range
		if not range:
			start_range = cmds.playbackOptions(q=True,minTime=True)
			end_range = cmds.playbackOptions(q=True,maxTime=True)
			range =[start_range,end_range]
		#find constraints and apply action
		for con in constraint_list:
			con_obj = cmds.ls("%s*::%s" % (asset,con))
			if con_obj:
				con = con_obj[0]
				if "orientConstraint" in con:
					if delete:
						cmds.orientConstraint(con, e=True,dc=True)
					else:
						cmds.orientConstraint(con, e=True, cc=range)
				else:
					if delete:
						cmds.parentConstraint(con, e=True,dc=True)
					else:
						cmds.parentConstraint(con, e=True, cc=range)

	def SetStringAttribute(self, on_obj="", attr_name="", attr_value="", create=True):
		if not cmds.attributeQuery(attr_name, n=on_obj, ex=True) and create:
			cmds.addAttr(on_obj, longName=attr_name, dt="string")
		cmds.setAttr("%s.%s" % (on_obj, attr_name), attr_value, type="string")

	def CheckAttribute(self, c_obj, c_attr):
		if cmds.attributeQuery(c_attr, node=c_obj, ex=True):
			return_value = cmds.getAttr("%s.%s" % (c_obj, c_attr))
			# if return_value == "":
			# 	return False
			# else:
			return return_value
		else:
			return False

	def CollectDumpInfo(self, c_func, c_info):  # A log collection. Should write out to log instead? Maybe a temp log?
		logger.debug("%s: %s" % (c_func,c_info))
		self.dump_info = "%s\n%s: %s" % (self.dump_info, c_func, c_info)

	def ReturnDumpInfo(self):
		return self.dump_info

	def CheckFileType(self, path):
		if "." in path:
			return ""
		if os.path.exists("%s.ma" % path):
			return ".ma"
		if os.path.exists("%s.mb" % path):
			return ".mb"


	def RemoveUnloadedRefs(self):  # Removes unload refs. Does not work recursively.
		refs = cmds.file(q=True, r=True)
		for c_ref in refs:
			is_load = cmds.referenceQuery(c_ref, isLoaded=True)
			if not is_load:
				ref_file = cmds.referenceQuery(c_ref, f=True)
				# cmds.file(ref_file, rr=True, mergeNamespaceWithRoot=True)
				cmds.file(ref_file, rr=True)

	def SetFrameRate(self): #Create Previz function
		cmds.currentUnit(time="pal", ua=False)

	def DeleteEverythingBesidesPublishSet(self):
		cmds.sets(cmds.ls(assemblies=True, ud=True), n="everything")
		if self.CheckPublishSet():
			delete_list = cmds.sets(cfg.publish_set, sub="everything")
			self.DeleteListAndChildren(delete_list)

	def DeleteListAndChildren(self,delete_list): #a recursive function to delete the given list and all the children
		if delete_list:
			for c_obj in delete_list:
				if cmds.objExists(c_obj):
					logger.debug("Deleting: %s" % c_obj)
					cmds.lockNode(c_obj, lock=False)
					cmds.delete(c_obj)
					# try:
					# 	cmds.delete(c_obj)
					# except:
					# 	print("CAN*T!")
					# 	self.DeleteListAndChildren(cmds.listRelatives(c_obj, c=True, f=True))
					# 	if cmds.objExists(c_obj):
					# 		cmds.delete(c_obj)
				if cmds.objExists(c_obj):
					self.DeleteListAndChildren(cmds.listRelatives(c_obj, c=True, f=True))
					if cmds.objExists(c_obj):
						cmds.delete(c_obj)

	def DeleteImagePlanes(self):  # Anim Publish, Deletes Imageplanes.
		for image_plane in cmds.ls(type="imagePlane"):
			cmds.delete(image_plane)

	def DeleteOldAiExpressions(self):
		logger.debug("Delete old aiPrevis expression")
		a_exp = cmds.ls("*aiPrevis_*", type="expression")
		cmds.delete(a_exp)

	def DeleteDisplayLayers(self):  # Delete display layers
		cur_layers = cmds.ls(type="displayLayer")
		for lay in cur_layers:
			if "defaultLayer" in lay:
				continue
			try:
				find_members = cmds.editDisplayLayerMembers(lay, q=True, fn=True)
				logger.debug("For %s - Found members: %s" % (lay,find_members))
				cmds.delete(lay)
				#clear_old_overrides
				self.SetDisplayOverride(obj_list=find_members)
			except:
				logger.debug("Can't delete %s. Needs to be removed in Ref" % lay)

	def SetDisplayOverride(self,obj_list=None,cur_value=0):

		for cur_obj in obj_list:
			logger.debug("Trying to set display override off on: %s" % cur_obj)
			cmds.setAttr("%s.overrideEnabled"% cur_obj,cur_value)

	def DeleteAnimLayers(self): #Delete anim layers
		anim_layers = cmds.ls(type="animLayer")
		for cur_layer in anim_layers:
			if cmds.objExists(cur_layer):
				cmds.delete(cur_layer)

	def DeleteUnknown(self,also_dag=True):  # Try to delete unknown nodes and plugins
		unknown = cmds.ls(type="unknown")
		if also_dag:
			unknown.extend(cmds.ls(type="unknownDag"))
		for un in unknown:
			if cmds.objExists(un):
				plg_orig = cmds.unknownNode(un, q=True, plugin=True)
				logger.debug("Deleting %s as it is unknown. It came from: %s" % (un, plg_orig))
				cmds.delete(un)
		unplug = cmds.unknownPlugin(q=True, list=True)
		if unplug:
			for p in unplug:
				logger.debug("Removing %s as it is unknown Plugin" % p)
				cmds.unknownPlugin(p, remove=True)

	def DeleteUnusedNodes(self):  # Delete unused nodes. Same as "Delete Unused Nodes" in the hypershader
		logger.debug("Trying to delete unused nodes!")
		mel.eval("MLdeleteUnused;")

	def DeleteVrayRenderInfo(self):  # Delete Render settings added in scene, to avoid complications in Light Scene.
		logger.debug("Trying to delete vray elements")
		res = cmds.ls(type="VRayRenderElement")
		for re in res:
			cmds.delete(re)
		if cmds.objExists("vrayEnvironmentPreviewTm"):
			cmds.delete("vrayEnvironmentPreviewTm")
		if cmds.objExists("vraySettings"):
			cmds.delete("vraySettings")

	def CleanNamespaces(self): #Publish Set: Tries to remove empty namespaces to avoid clutter
		all_ns = cmds.namespaceInfo(listOnlyNamespaces=True)
		for ns in all_ns:
			if not ns == "shared" and cmds.namespaceInfo(ns, ls=True) == None:
				logger.debug("Found empty namespace: %s" % ns)
				cmds.namespace(rm=ns, mnr=True)

	def RemoveNamespaceOfPreviousStep(self,cur_asset_dict=None):
		#Meant to remove the namespaces of the steps. ("Model" namespace in Rig file/"Rig" ns in Shading file)
		if cur_asset_dict:
			all_steps = cfg.ref_order[cur_asset_dict["asset_type"]]
			cur_index= all_steps.index(cur_asset_dict["asset_step"])
			if cur_index >0:
				remove_ns = all_steps[cur_index-1]
				if cmds.namespace(ex=remove_ns):
					cmds.namespace(rm=remove_ns,mnr=True)

	def RemoveArnold(self):  # Try to remove Arnold pluging from scene.
		is_arnold = cmds.pluginInfo("mtoa", q=True, loaded=True)
		logger.debug("Arnold is loaded: %s" % is_arnold)
		if is_arnold:
			ai_path = cmds.pluginInfo("mtoa", q=True, path=True)
			cmds.pluginInfo(ai_path, e=True, writeRequires=False)

			arnold_nodes = cmds.pluginInfo("mtoa", q=True, dn=True)
			arnold_in_scene = cmds.ls(type=arnold_nodes)
			for an in arnold_in_scene:
				if cmds.objExists(an):
					logger.debug("Deleting: %s " % an)
					cmds.delete(an)
			# cmds.unloadPlugin("mtoa", f=True) #force unload of arnold. Has a tendency to make maya a bit unstable
		self.DeleteUnknown()

	def RemoveYetiPlugin(self):
		is_yeti = cmds.pluginInfo("pgYetiMaya", q=True, loaded=True)
		logger.debug("Is Yeti Loaded: %s" % is_yeti)
		if is_yeti:
			yeti_path = cmds.pluginInfo("mtoa", q=True, path=True)
			cmds.pluginInfo(yeti_path, e=True, writeRequires=False)

			yeti_nodes = cmds.pluginInfo("pgYetiMaya", q=True, dn=True)
			yeti_in_scene = cmds.ls(type=yeti_nodes)
			if not yeti_in_scene:
				logger.debug("No yeti nodes in scene, trying to unload plugin")
				cmds.unloadPlugin("pgYetiMaya")
				self.DeleteUnknown()
				cmds.setAttr("defaultRenderGlobals.preMel", "", type="string")
				cmds.setAttr("defaultRenderGlobals.postMel", "", type="string")
		# if not "pgYetiMaya" in cmds.pluginInfo(q=True, pluginsInUse=True):
		# 	cmds.setAttr("defaultRenderGlobals.preMel", "",type="string")
		# 	cmds.setAttr("defaultRenderGlobals.postMel", "",type="string")


	def DeleteRenderLayers(self):  # try to delete default render layer
		cur_layers = cmds.ls(type="renderLayer")
		for lay in cur_layers:
			try:
				cmds.delete(lay)
			except:
				logger.info("Can't delete %s. Needs to be removed in Ref" % lay)

	def RemoveRefs(self, remove_list): #Remove refs by given list.
		for ref in remove_list:
			if cmds.objExists(ref):
				logger.info("Found %s! Trying to remove" % ref)
				ref_file = cmds.referenceQuery(ref, f=True)
				cmds.file(ref_file, rr=True, mergeNamespaceWithRoot=True)

	def RemoveRefsFromAssetPublish(self, remove_list):
		ref_files = cmds.file(q=True, r=True)
		for ref in ref_files:
			for remove in remove_list:
				if remove in ref:
					# cmds.file(ref, rr=True, mergeNamespaceWithRoot=True)
					cmds.file(ref, rr=True, f=True)

	def ImportModuleRefs(self,ref_list=None): #NOT USED YET.
		for cur_ref in ref_list:
			if "/Module/" in cur_ref:
				pass
		pass

	def FindRefsInGroup(self,cur_group="Full"):
		my_childs = cmds.listRelatives("Full", children=True, ad=True)
		my_refs = cmds.ls(my_childs, rn=True)
		list_refs = []
		for cur_ref in my_refs:
			cur_refnode = cmds.referenceQuery(cur_ref, tr=True, rfn=True)
			cur_ref_path = cmds.referenceQuery(cur_refnode, filename=True)
			if not cur_ref_path in list_refs:
				list_refs.append(cur_ref_path)
		return list_refs

	def ImportRefs(self,import_unloaded=False,remove_ns=False): #Import refs. Recursively.
		refs = cmds.file(q=True, r=True)
		for c_ref in refs:
			ns = cmds.file(c_ref, q=True, ns=True)
			if not cmds.referenceQuery(c_ref, il=True): #If ref is unloaded
				if import_unloaded: #load ref if imported_unloaded is true
					cmds.file(c_ref, lr=True)
				else: #Else remove it
					logger.debug("Removing unloaded Ref: %s" % c_ref)
					cmds.file(c_ref,rr=True)
					continue #TODO Check if namespaces still hangs around?
			logger.debug("Importing Ref: %s" % c_ref)
			cmds.file(c_ref, ir=True) #Import reference
		if remove_ns: #Added from Asset Publish. Used to help with sub-assets in assets.
			if cmds.namespace(exists=ns):  # Check if namespace already exists
				cmds.namespace(rm=ns, mnr=True)  # Try to merge it to avoid complications
		if cmds.file(q=True, r=True) != []: #Recursivly check for more refs until none is left.
			self.ImportRefs(import_unloaded,remove_ns)

	def DeleteAnimKeysOnCtrls(self):
		ctrl_objs = cmds.ls("*_Ctrl", type="transform")
		for ctrl in ctrl_objs:
			key_list = cmds.keyframe(ctrl, query=True, name=True)
			if key_list != None:
				for key in key_list:
					try:
						cmds.delete(key)
					except:
						pass

	def CreateOIDSet(self, object_list=None, object_type=None,set_name=None,OID=None,use_force=True):
		selection = False
		if object_type:
			select_all = self.FindAssetTypeInScene(object_type)
		elif object_list:
			select_all = object_list
		else:
			select_all = None
			selection = True
		# if not cmds.objExists(set_name):
		self.CreateVrayObjectSet(set_name=set_name,obj_list=select_all,selection=selection,use_force=use_force)
		self.SetOIDonObjectSet(set_name, OID)

	def FindRootByName(self, name_list=[]):
		return_list = []
		for c_name in name_list:
			cur_objs = cmds.ls("::%s*:Root_Group" % c_name)
			return_list.extend(cur_objs)
		return_list = list(set(return_list))
		return return_list


	def DeleteManagerNodes(self):
		cmds.delete(cmds.ls(type="shapeEditorManager"))
		cmds.delete(cmds.ls(type="poseInterpolatorManager"))

	def AddToSet(self, set_name,selection=None):
		if not selection:
			selection = cmds.ls(sl=True)
		if not cmds.objExists(set_name):
			cmds.sets(n=set_name, empty=True)
		cmds.sets(selection, add=set_name)

	def RemoveFromSet(self, set_name):
		selection = cmds.ls(sl=True)
		cmds.sets(selection, rm=set_name)

	def FindObjectsFromSet(self, set_name):
		if cmds.objExists(set_name):
			set_objs = cmds.sets(set_name, q=True)
			return set_objs
		else:
			return None
	def DeleteOldExpressions(self):
		#Delete aiExpression from old props
		pass

	def DeleteSets(self): #Used to clean away publish set and other work sets
		my_sets = cmds.ls(exactType="objectSet")
		logger.debug(my_sets)
		exclude_list = []
		for obj in my_sets: #go through and try to determine if the set is used behind the scenes (clusters and so on)
			if cmds.listConnections(obj, type="groupId"):
				logger.debug(obj)
				exclude_list.append(obj)
			else:
				if "yetiGroom" in obj or "Guide_Set" in obj:
					logger.debug(obj)
					exclude_list.append(obj)

		my_sets = [i for i in my_sets if i not in exclude_list]
		if my_sets:
			logger.debug(my_sets)
			cmds.lockNode(my_sets, lock=False)
			cmds.delete(my_sets)


	def DeleteAllInSet(self, cur_set):
		s_objs = self.FindObjectsFromSet(cur_set)
		if s_objs:
			for obj in s_objs:
				if cmds.objExists(obj):
					# print("Deleting: %s" % obj)
					cmds.delete(obj)
		# else: #TODO Check if this is needed: #Added from Asset Publish. Deletes Set if its empty
		# 	if cmds.objExists(cur_set):
		# 		cmds.delete(cur_set)

	# def SelectCtrlsFromNamespace(self):
	# 	selection_objects = cmds.ls(sl=True)
	# 	final_selection = []
	# 	for obj in selection_objects:
	# 		cur_namespace = ":".join(obj.split(":")[:-1])
	# 		print("adding ctrls from %s" % cur_namespace)
	#
	# 		new_selection = cmds.ls("%s::*_Ctrl" % cur_namespace, type="transform")
	# 		final_selection += new_selection
	# 	if final_selection:
	# 		cmds.select(final_selection, r=True)

	def SelectCtrlsFromNamespace(self,super_root=False,only_super=False):
		selection_objects = cmds.ls(sl=True)
		final_selection = []
		namespace_check = []
		for obj in selection_objects:
			cur_namespace = ":".join(obj.split(":")[:-1])
			if cur_namespace in namespace_check:
				continue
			else:
				namespace_check.append(cur_namespace)
			logger.debug("adding ctrls from %s" % cur_namespace)

			new_selection = cmds.ls("%s::*_Ctrl" % cur_namespace, type="transform")
			super_root_obj = "%s:SuperRoot_Ctrl" % cur_namespace
			if super_root_obj in new_selection:
				if not super_root and not only_super:
					new_selection.remove(super_root_obj)
				elif only_super:
					final_selection += [super_root_obj]
				else:
					final_selection += new_selection
			else:
				if not only_super:
					final_selection += new_selection
		if final_selection:
			cmds.select(final_selection, r=True)

	def LockGeoGroup(self): #Locks the geo group before publishing
		logger.debug("Trying to lock Geo_Group")
		cur_obj = "|Root_Group|Geo_Group"
		if cmds.objExists(cur_obj): #cmds.objExists("Geo_Group")
			cmds.setAttr("%s.overrideEnabled" % cur_obj, 1)
			cmds.setAttr("%s.overrideDisplayType" % cur_obj, 2)
			# cmds.setAttr("Geo_Group.overrideEnabled", 1)
			# cmds.setAttr("Geo_Group.overrideDisplayType", 2)

	# def CreateSetdressCleanUp(self,file_open=None): #UNUSED. Created a new template instead.
	# 	if file_open:
	# 		self.OpenFile(file_open)
	# 	cmds.group(n='Full', empty=True)
	# 	cmds.group(n='Proxy', empty=True)
	# 	cmds.lockNode(['Full', 'Proxy'], lock=True)
	# 	to_delete_list = []
	# 	to_delete_list.append('Anim_Delete_Set')
	# 	to_delete_list.append('PublishSet')
	# 	to_delete_list.extend(cmds.listRelatives('Root_Group', c=True, f=True))
	# 	cmds.lockNode(to_delete_list, lock=False)
	# 	cmds.delete(to_delete_list)
	# 	self.Saving()


	###################################################
	############## FILE HANDLING ######################
	###################################################

	def SaveTempFile(self):
		import random
		##Save as temp file to check for problems##'
		try:
			if not os.path.exists("C:/Temp"):
				os.mkdir("C:/Temp")
			self.DeleteUnknown()
			self.cur_rand_num = random.randrange(1, 1000)
			temp_path = "C:/Temp/Publish_Temp_%s.ma" % self.cur_rand_num
			self.PrepareForSave(temp_path, ma=True)
			return temp_path
		except():
			return False

		# did_it_publish = self.PublishSteps()
		# try:
		# 	os.remove(self.temp_path)
		# except:
		# 	print("Couldn't remove temp file")
		# return did_it_publish

	def TestAndSave(self, save_path): #Save function, tries to save file, if it succeed, rename and save as final output
		if self.Saving():
			self.PrepareForSave(save_path)
			self.Saving()
			return True
		else:
			# self.OpenFile(self.s_path)
			return False

	def Saving(self): ##SAVING## #TODO Look into if this is even works. Try with a file that would fail to save.(has unknown plugin)
		try:
			cmds.file(save=True)
			return True
		except:
			logger.debug("Not working!")
			return False

	def PrepareForSave(self, cur_path,ma=False): #change filename and set file type to .mb
		logger.debug("Renaming scene to: %s" % cur_path)
		cmds.file(rename=cur_path)
		if ma:
			cmds.file(type="mayaAscii")
		else:
			cmds.file(type="mayaBinary")

	def OpenFile(self, cur_file,compare_path=False):
		if compare_path:
			logger.debug("Currently open file: %s - Target file: %s" % (cmds.file(q=True,sn=True),cur_file))
			if cmds.file(q=True,sn=True) == cur_file:
				return False
		cmds.file(cur_file, open=True, f=True)


	######################################################################################
	###### ASSET PUBLISH FUNCTIONS ########################################################
	######################################################################################

	def LockModuleAttrs(self): #Use this if we need to lock attributes on rig module in publish
		attr_list = ["moduleSize", "armSize",]
		for cur_attr in attr_list:
			cur_obj = cmds.ls("*.%s" % cur_attr,o=True,ln=True)
		pass



	def GeoGroup_Removing_Model(self): #Asset Publish: Try to unparent children of geo_group and then delete it.
		if cmds.objExists("Geo_Group"):
			my_list = cmds.listRelatives("Geo_Group", type="transform")
			if my_list:
				for cur in my_list:
					cmds.parent(cur, world=True)
			cmds.lockNode("Geo_Group", lock=False)
			cmds.delete("Geo_Group")

	def SetDressImport(self):
		logger.debug("Trying to avoid more geo and top groups")
		geo_groups = cmds.ls("Geo_Group", l=True)
		for gg in geo_groups:
			if not gg == "|Geo_Group":
				cmds.rename(gg, "SetDress_Geo_Group")
		top_groups = cmds.ls("Top_Group", l=True)
		for tg in top_groups:
			cmds.rename(tg, "SetDress_Top_Group")

	######################################################################################
	####### ANIM SCENE PUBLISH FUNCTIONS #################################################
	######################################################################################


	def DeleteLightDirection(self): #Animation Publish: Deletes the Light Direction group meant for pre-setting light in previz
		if cmds.objExists("LD_directionalLight"):
			cmds.delete("LD_directionalLight")

	def SetKeyOnPublish(self,key_dict):
		for key in key_dict.keys():
			refs = cmds.ls("%s*:Root_Group" % key)
			for ref in refs:
				ref = ref.split(":")[0]
				for obj in key_dict[key].keys():
					if cmds.objExists("%s:%s" % (ref, obj)):
						self.SetKeyOnAttribute(c_ns=ref,c_object=obj,c_attr=key_dict[key][obj])

	def SetKeyOnAttribute(self, c_ref=None, c_object=None, c_attr=None,c_ns=None): #Animation Publish: Set key on attribute. Special case.
		if not c_ns:
			c_ns = cmds.referenceQuery(c_ref, ns=True)
		if cmds.objExists("%s:%s" % (c_ns, c_object)):
			logger.debug("Trying to set a key on %s:%s.%s" % (c_ns,c_object,c_attr))
			if c_attr:
				cmds.setKeyframe("%s:%s" % (c_ns,c_object), attribute=c_attr, t=1)
			else:
				cmds.setKeyframe("%s:%s" % (c_ns, c_object), t=1)

	def ChangeRefsToRender(self): #Animation Publish: Flip ref to render from anim. Special Cases can be included.
		refs = cmds.file(q=True, r=True)
		for ref_path in refs:
			if "Anim.mb" in ref_path:
				# print(ref_path)
				rot_dict = {}
				if "Leafling" in ref_path: #Example:
					self.SetKeyOnAttribute(ref_path, "root_ctrl", "leafcolor")
				if "/Bubble/" in ref_path:
					self.Bubble_ColorKey(ref_path)
				if "/MilkyWay/" in  ref_path:
					rot_dict = self.GetRotationAxisDict(ref_path)
				# find reference node
				ref_node = cmds.referenceQuery(ref_path, referenceNode=True)
				new_path = "%sRender.mb" % ref_path.split("Anim.mb")[0]
				if os.path.exists(new_path):
					cmds.file(new_path, loadReference=ref_node)
					if rot_dict: #TODO Please educated me in what this does Rune
						for ctrl in rot_dict:
							logger.debug('setting rot order', rot_dict[ctrl])
							cmds.setAttr('%s.rotateOrder'%(ctrl), rot_dict[ctrl])
				else:
					logger.debug("Can't find %s to replace Anim-Ref" % new_path)

	def GetRotationAxisDict(self, ref_path): #Rotation Axis Dict?? Please explain, Rune :D
		ctrl_rot_order = {}
		ref_node = cmds.referenceQuery(ref_path, referenceNode=True)
		name_space = cmds.referenceQuery(ref_node, ns=True)
		ctrls = cmds.ls('%s:*_Ctrl'%(name_space))
		for i in ctrls:
			if not cmds.listConnections('%s.rotateOrder' % (i), s=1, d=0):
				ctrl_rot_order[i] = cmds.getAttr('%s.rotateOrder'%(i))

		return ctrl_rot_order

	def DeleteKeyAndChangeCenter(self, cur_shotname): #Anim Publish: Sets center of interest distance to camera, has to be above 25 or it will affect the light in render!
		my_cam = "%s_Cam" % (cur_shotname) #TODO need current shot as input
		my_cam_shape = cmds.listRelatives(my_cam, shapes=True)[0]
		cmds.camera(my_cam_shape, e=True, lt=False)
		cmds.cutKey(my_cam, cl=True, at="coi")
		cmds.setAttr("%s.centerOfInterest" % my_cam_shape, 50)

	def setVelocityEndKeys(self): #Anim Publish: Make animation overshoot after shot ends so motion blur doesn't get bungled
		# get anim curves
		curves = cmds.ls(typ=("animCurveTL", "animCurveTU", "animCurveTA", "animCurveTT"))

		# find anim shot end
		cTime = cmds.currentTime(q=True)
		shotEnd = cmds.getAttr('%s.endFrame' % (cmds.sequenceManager(lsh=True)[0]))

		# get active curves that are float type
		active_attrs = []
		for crv in curves:
			# filter referenced curves
			if cmds.referenceQuery(crv, isNodeReferenced=True):
				continue

			endKeyTime = cmds.keyframe(crv, q=True)[-1]
			if endKeyTime >= shotEnd:
				attr = cmds.listConnections('%s.output' % (crv), d=True, p=True, scn=True)
				# filter curves without a destination
				if attr:
					# filter curves that are not float values
					if isinstance(cmds.getAttr(attr[0]), float):
						active_attrs.append(attr[0])

		# Set animation keys and tangent
		# print(active_attrs)
		for attr in active_attrs:
			# print attr
			valA = cmds.getAttr(attr, time=shotEnd - 1)
			valB = cmds.getAttr(attr, time=shotEnd)
			newVal = valB + valB - valA
			# print(attr, newVal, shotEnd + 1)
			cmds.setKeyframe(attr.split('.')[0], attribute=attr.split('.')[1], t=shotEnd, insert=True)
			cmds.setKeyframe(attr.split('.')[0], attribute=attr.split('.')[1], t=shotEnd + 1, v=newVal)
			cmds.keyTangent(attr.split('.')[0], attribute=attr.split('.')[1], inTangentType='linear',
							time=(shotEnd + 1, shotEnd + 1))

	######################################################################################
	####### RENDER SUBMIT PUBLISH FUNCTIONS ##############################################
	######################################################################################

	def CreateOnlyBGExceptionSet(self,object_list=None):
		self.AddToSet("OnlyBG_Exception",object_list)

	def OnlyBG(self): #Submit Render Scene
		# Hide all assets except Set and Setdress
		cmds.setAttr("vraySettings.cam_environmentVolumeOn", 0) #turning off sphere render
		all_tops = cmds.ls("Anim:*:Root_Group")
		if cmds.objExists("OnlyBG_Exception"):
			except_list = self.FindObjectsFromSet("OnlyBG_Exception")
			all_tops = [x for x in all_tops if x not in except_list]
		for top in all_tops:
			if cmds.attributeQuery("asset_type", n=top, ex=True):
				c_type = cmds.getAttr("%s.asset_type" % top)
				c_vis = cmds.getAttr("%s.visibility" % top)
				cmds.cutKey(top, attribute='visibility', option="keys")
				#TODO Change this so it doens't set set /setdress to 1, but sets everyhting else to 0 in visibility
				if c_type == "Set" or c_type == "Setdress":
					cmds.setAttr("%s.visibility" % top, c_vis)
					# cmds.setAttr("%s.visibility" % top, 1)
				else:
					cmds.setAttr("%s.visibility" % top, 0)

		if cmds.objExists("OnlyBG_Hide"):
			hide_list = self.FindObjectsFromSet("OnlyBG_Hide")
			for cur_obj in hide_list:
				if cmds.objExists(cur_obj):
					try:
						cmds.cutKey(cur_obj, attribute='visibility', option="keys")
						cmds.setAttr("%s.visibility" % cur_obj, 0)
					except:
						logger.debug("Can't work visibilty for %s" % cur_obj)


	def FindAssetTypeInScene(self, asset_type="Prop"):
		all_tops = cmds.ls("Anim:*:Root_Group")
		return_list = []
		for top in all_tops:
			if cmds.attributeQuery("asset_type", n=top, ex=True):
				c_type = cmds.getAttr("%s.asset_type" % top)
				if c_type == asset_type:
					logger.debug("Found %s -> %s" %(asset_type,top))
					return_list.append(top)

		return return_list

	def update_ref_and_textures(self):
		replace_name = 'Kiwi&Strit_2'
		refs = cmds.file(q=True,r=True)
		for ref_path in refs:
			logger.debug(ref_path)
			ref_node = cmds.referenceQuery(ref_path, referenceNode=True)
			if replace_name in ref_path:
				path_splits = ref_path.split(replace_name)
				new_path = "KiwiStrit2".join(path_splits)
				if "{" in new_path:
					new_path = new_path.split("{")[0]
				if os.path.exists(new_path):
					logger.debug('Replacing %s with %s' %(ref_path,new_path))
					cmds.file(new_path, loadReference=ref_node)
		file_nodes = cmds.ls(type='file')
		for cur_node in file_nodes:
			tex_path = cmds.getAttr('%s.fileTextureName' % (cur_node))
			if replace_name in tex_path:
				path_splits = tex_path.split(replace_name)
				new_tex_path = "KiwiStrit2".join(path_splits)

				if os.path.exists(new_tex_path):
					logger.debug('Replacing %s with %s' %(tex_path,new_tex_path))
					cmds.setAttr('%s.fileTextureName' % (cur_node), new_tex_path, type='string')
		import YetiFunctions as YF
		cur_nodes = YF.GetYetiNodes(from_selection=False)
		for cur in cur_nodes:
			YF.UpdateYetiNode(cur, replace_dict={"Kiwi&Strit_2": "KiwiStrit2"})
# test_path = "P:/930382_Kiwi&Strit_2/Production/"
# update_ref_and_textures([test_path])