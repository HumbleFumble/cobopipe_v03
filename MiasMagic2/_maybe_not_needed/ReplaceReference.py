import maya.cmds as cmds
import os
#TODO PICK REFERNCE FROM AB2. Replace the current selection if it is a ref with that.


def ReplaceProxy():
	import maya.mel as mel
	refs = cmds.file(q=True, r=True)
	for ref in refs:
		if "/Setdress/" in ref:
			cur_ns = cmds.referenceQuery(ref, ns=True)[1:]
			look_for_vrmesh = "%s:VRayProxy_vraymesh" % cur_ns
			all_placements = cmds.ls("*%s:Proxy*" % cur_ns, type="transform")

	# mel.eval('vray restoreMesh "FernLeafA:VRayProxy_vraymesh"')

def ReplaceRefWith(asset_path, asset_name):
	selection = cmds.ls(sl=True)
	ref_list = CheckForReference(selection)
	for c_ref in ref_list:
		if "_Anim" in c_ref:
			new_ref_path = "%s/02_Ref/%s_Anim.mb" % (asset_path, asset_name)
		else:
			new_ref_path = "%s/02_Ref/%s_Render.mb" % (asset_path, asset_name)

		if os.path.exists(new_ref_path):
			goal_ns = cmds.referenceQuery(c_ref, ns=True)
			goal_super = "%s:SuperRoot_Ctrl" % goal_ns
			if c_ref:
				# Importing new ref
				new_ref = ImportRefs(new_ref_path, asset_name)
				cur_ns = cmds.referenceQuery(new_ref, ns=True)
				new_super = "%s:SuperRoot_Ctrl" % cur_ns
				#Aligning new ref to the old
				Align(goal_super, new_super)
				#Removing the old ref
				RemoveRefs(c_ref)

def Align(goal, moving):
	p_delete = cmds.parentConstraint(goal,moving, mo=False, n="PO_ToDelete")
	s_delete = cmds.scaleConstraint(goal, moving, mo=False, n="SC_ToDelete")
	cmds.delete(p_delete)
	cmds.delete(s_delete)

def ImportRefs(import_path, asset_name):
	new_ref = cmds.file(import_path, r=True, type="mayaBinary", loadReferenceDepth="all", mergeNamespacesOnClash=False, namespace=asset_name, options="v=0")
	return new_ref

def CheckForReference(obj_list):
	# selection = cmds.ls(sl = True)
	return_list = []
	for obj in obj_list:
		refcheck = cmds.referenceQuery(obj, inr = True)
		if (refcheck == 1):

			ref_filepath = cmds.referenceQuery(obj, f = True)
			if not ref_filepath in return_list:
				return_list.append(ref_filepath)

	return return_list

def RemoveRefs(ref):
	cmds.file(ref, rr=True, mergeNamespaceWithRoot=True)

# ReplaceRefWith("P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Assets/3D_Assets/Setdress/Trees/BirchTreeA/02_Ref/BirchTreeA_Anim.mb","BirchTreeA")

