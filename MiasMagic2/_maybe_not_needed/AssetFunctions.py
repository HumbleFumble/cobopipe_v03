import Config_MiaMagic2 as cfg

try:
    from PySide2 import QtWidgets, QtCore, QtGui
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
import re
import ConfigUtil
cfg_util = ConfigUtil.ConfigUtilClass(cfg)
# import UtilFunctions as UF

# #####  GO TO A GIVEN DEPTH  #####
# basedir = 'P:\\930382_Kiwi&Strit_2\\Production\\Assets\\3D_Assets\\'
# test_name = 'SkisA'
# MAX_DEPTH = 2
# def check_existance(name, assets_dir, depth=2):
#     for root, dirs, files in os.walk(basedir, topdown=True):
#         if root.count(os.sep) - basedir.count(os.sep) == MAX_DEPTH - 1:
#             if dirs:
#                 for d in dirs:
#                     if d == test_name:
#                         print('Name exists : %s'% d)
#                         return True
#         if root.count(os.sep) - basedir.count(os.sep) == MAX_DEPTH:
#             del dirs[:]
#     return False
# if check_existance(test_name, basedir, depth=MAX_DEPTH):
#     print('Match')

def UpdateYetiNode(yeti_node=None): #Update texture paths from old season to new. Could also work for out-of-house path updates?
    if not yeti_node:
        yeti_node = cmds.ls(sl=True)
    if cmds.nodeType(yeti_node)=="transform":
        yeti_node = cmds.listRelatives(yeti_node, type="pgYetiMaya")[0]
    # my_yeti_node = "yetiNode_Grass1Shape"
    if yeti_node and cmds.nodeType(yeti_node)=="pgYetiMaya":
        cmds.setAttr("%s.fileMode" % yeti_node, 0)
        texture_nodes = cmds.pgYetiGraph(yeti_node, listNodes=True,type="texture")
        for cur_node in texture_nodes:
            cur_file = cmds.pgYetiGraph(yeti_node, node=cur_node, param="file_name", getParamValue=True)
            replace_dict = {"O:/TV/KiwiAndStrit/Asset/":"P:/930382_Kiwi&Strit_2/Production/Assets/3D_Assets/","/Texture/":"/03_Texture/"} #TODO HARDCODED!
            for k in replace_dict.keys():
                if k in cur_file:
                    cur_file = cur_file.replace(k,replace_dict[k])
            if os.path.exists(cur_file):
                cmds.pgYetiGraph(yeti_node, node=cur_node, param="file_name", setParamValueString=cur_file)

def ExportGroomSelection(yeti_node_list=None):
    temp_uf = UF.PublishFunctions()
    temp_asset_info = temp_uf.GetAssetInfoFromFile()
    if not yeti_node_list:
        yeti_node_list = cmds.ls(sl=True)
    for yeti_node in yeti_node_list:
        if not cmds.nodeType(yeti_node)=="pgYetiMaya":
            find_yeti = cmds.listRelatives(yeti_node, type="pgYetiMaya")
            if not find_yeti:
                print("%s not a yeti node! Skipping it" % yeti_node)
                continue
            else:
                yeti_node=find_yeti[0]
        node_name = yeti_node
        if "yetiNode_" in yeti_node:
            node_name = node_name.split("yetiNode_")[1]
        if "Shape" in yeti_node:
            node_name = node_name.split("Shape")[0]
        temp_asset_info["yeti_node"] = node_name
        file_path = cfg_util.CreatePathFromDict(cfg.ref_paths["YetiGroom"],temp_asset_info)
        f_folder,f_file = os.path.split(file_path)
        if not os.path.exists(f_folder):
            os.mkdir(f_folder)
        if os.path.exists(file_path):
            history_folder = "%s/_History" % f_folder
            if not os.path.exists(history_folder):
                os.mkdir(history_folder)
            v_num = 0
            for content in os.listdir(history_folder):
                if "%s_V" % f_file.split(".")[0] in content:
                    cur_num = int(content.split("%s_V" % f_file.split(".")[0])[1].split(".")[0])
                    if cur_num > v_num:
                        v_num = cur_num
            v_num = '%03d' % (v_num + 1)
            shutil.move(file_path,"%s/%s_V%s.grm" % (history_folder,f_file.split(".")[0],v_num))

        cmds.setAttr("%s.fileMode" % yeti_node, 0)
        ExportGrooms(yeti_node,file_path)
        cmds.setAttr("%s.cacheFileName" % yeti_node, file_path, type="string")
        cmds.setAttr("%s.fileMode" % yeti_node, 1)
        cmds.setAttr("%s.overrideCacheWithInputs" % yeti_node, 1)

def ExportGrooms(yeti_node=None,file_path=None):
    #Must be the shape node itself can't be transform
    if not yeti_node:
        yeti_node = cmds.ls(sl=True)[0]
    if cmds.nodeType(yeti_node)=="transform":
        yeti_node = cmds.listRelatives(yeti_node, type="pgYetiMaya")[0]

    cmds.pgYetiCommand(yeti_node,exportGroom=file_path) #".GRM" at the end I think


class UpdateAssetFile():
    def __init__(self, asset_info={}):
        self.log_file = "c:/Temp/Prop_Log.txt"
        self.UF = UF.PublishFunctions()
        if asset_info:
            self.asset_info = asset_info
        else:
            self.asset_info = self.UF.GetAssetInfoFromFile()
        if self.asset_info:
            self.asset_base = cfg_util.CreatePathFromDict(cfg.project_paths["asset_base_path"], self.asset_info)
            self.asset_ref_folder = cfg_util.CreatePathFromDict(cfg.project_paths["asset_ref_folder"], self.asset_info)
            self.asset_work_folder = cfg_util.CreatePathFromDict(cfg.project_paths["asset_work_folder"], self.asset_info)
        else:
            print("Can't find asset!")

    def Run(self):
        print("RUNNING CLEAN UP!")
        if self.asset_info["asset_type"] == "Prop":
            # self.CleanProp()
            self.SetBaseProjectPath()
        if self.asset_info["asset_type"] == "Setdress":
            # self.CleanSetDress()
            self.SetBaseProjectPath()
        if self.asset_info["asset_type"] == "Set":
            self.CleanSet()
            pass
        if self.asset_info["asset_type"] == "Char":
            self.CleanChar()
            pass
    def SetBaseProjectPath(self):
        print("Set Base Project Path!")
        self.asset_info["asset_step"] = "Base"

        work_file = "%s.ma" % cfg_util.CreatePathFromDict(cfg.project_paths["asset_work_path"],self.asset_info)
        print(work_file)
        if os.path.exists(work_file):
            self.UF.SaveLog(cfg.project_paths["update_log_path"], "Started on: %s" % (self.asset_info["asset_name"]))
            cmds.file(work_file, open=True, f=True, prompt=False)
            self.UF.DeleteUnknown(also_dag=True)
            self.UF.DeleteUnusedNodes()
            try:
                cmds.file(type="mayaAscii")
                cmds.file(rename=cfg_util.CreatePathFromDict(cfg.project_paths["asset_work_path"], self.asset_info))
                cmds.file(save=True, f=True)
            except:
                print("Can't find %s/%s" %(self.asset_info["asset_category"],self.asset_info["asset_name"]))
                return False

            import IncSave
            IncSave.incrementalSave()
            self.UF.update_ref_and_textures()
            cmds.file(save=True, f=True)

            from PublishAssets import PublishMaster
            ready = PublishMaster.ReadyPublish(asset_info=self.asset_info)
            ready.StartPublish()


    def CleanChar(self): #Only works for currently open scene. (one asset step)
        # self.UF.SaveLog(cfg.project_paths["update_log_path"], "--- UPDATE: %s -----" % self.asset_info["asset_name"])
        # self.asset_info["asset_step"] = "Base"
        # steps = ["Model","Rig","Shading"]
        # # work_content = self.GetContentAndCreateHistory(self.asset_work_folder)
        # # set_file = "%s/%s.ma" % (self.asset_work_folder, self.asset_info["asset_name"])
        # ref_content = self.GetContentAndCreateHistory(self.asset_ref_folder)
        # for cur in ref_content:
        #     print("Ref: %s/%s" % (self.asset_ref_folder, cur))
        #     shutil.move("%s/%s" % (self.asset_ref_folder, cur), "%s/_History/ORIG_%s" % (self.asset_ref_folder, cur))
        #
        # for step in steps:
        #     self.asset_info["asset_step"] = step
            # set_file = "%s/%s.ma" % (self.asset_work_folder, self.asset_info["asset_name"])
        #set_file = cfg_util.CreatePathFromDict(cfg.project_paths["asset_work_path"],self.asset_info)

        # move refs into "_History" folder
        # if os.path.exists(set_file):
        #     #open rig file
        #     cmds.file(set_file, open = True, f = True,prompt=False)
        if self.asset_info["asset_step"] =="Model":
            if cmds.objExists("Root_Group"):
                delete_objs = cmds.listRelatives("Root_Group", children=True, ad=True, f=True)
                delete_objs.append("Root_Group")
                cmds.lockNode(delete_objs, lock=False)
                cmds.delete(delete_objs)
            if not cmds.objExists("Geo_Group"):
                cmds.group(n="Geo_Group", empty=True)

            add_and_lock = ['PublishSet']
            for c_set in add_and_lock:
                if not cmds.objExists(c_set):
                    cmds.sets(n=c_set, empty=True)
                cmds.lockNode(c_set,lock=True)
            cmds.sets("Geo_Group", add="PublishSet")

        if self.asset_info["asset_step"] == "Rig":
            #Add and remove sets:
            unlock_and_remove= ["Anim_Set","Model_Set","Render_Set"]
            add_and_lock = ['Anim_Delete_Set',"Rig_Delete_Set",'PublishSet']
            add_to_publish_set = ["Root_Group"]
            for r_set in unlock_and_remove:
                if cmds.objExists(r_set):
                    cmds.lockNode(r_set, lock=False)
                    cmds.delete(r_set)
            for c_set in add_and_lock:
                if not cmds.objExists(c_set):
                    cmds.sets(n=c_set, empty=True)
                cmds.lockNode(c_set,lock=True)
            cmds.sets(add_to_publish_set, add="PublishSet")

            self.CleanRootGroup(self.asset_info)

        if self.asset_info["asset_step"] == "Shading":
            if cmds.objExists(":Root_Group"):
                delete_objs = cmds.listRelatives(":Root_Group", children=True, ad=True, f=True)
                delete_objs.append(":Root_Group")
                cmds.lockNode(delete_objs, lock=False)
                cmds.delete(delete_objs)

            unlock_and_remove = ["Anim_Set", "Model_Set", "Render_Set"]
            add_and_lock = ['PublishSet']
            add_to_publish_set = ["Rig:Root_Group"]
            for r_set in unlock_and_remove:
                if cmds.objExists(r_set):
                    cmds.lockNode(r_set, lock=False)
                    cmds.delete(r_set)
            for c_set in add_and_lock:
                if not cmds.objExists(c_set):
                    cmds.sets(n=c_set, empty=True)
                cmds.lockNode(c_set, lock=True)
            cmds.sets(add_to_publish_set, add="PublishSet")
            yeti_nodes = cmds.ls(type="pgYetiMaya")
            for yn in yeti_nodes:
                cmds.setAttr("%s.fileMode" % yn,0)
                UpdateYetiNode(yn)

            #TODO export all yeti groom or maybe just selection?

        from KS_AssetUpdate import TransferModel
        TM = TransferModel()
        TM.update_textures()
        TM.update_refs()

            #self.UF.DeleteUnknown(also_dag=True)
            #self.UF.DeleteUnusedNodes()

            # #SAVE FILE
            # try:
            #     cmds.file(type="mayaAscii")
            #     cmds.file(rename=cfg_util.CreatePathFromDict(cfg.project_paths["asset_work_path"], self.asset_info))
            #     cmds.file(save=True, f=True)
            # except Exception as c_e:
            #     print("Can't change fileformat?")
            #     self.UF.SaveLog(cfg.project_paths["update_log_path"],"Can't save as ascii!: %s" % (c_e))
            #     return False



            #publish the asset
            # import PublishMaster
            # ready = PublishMaster.ReadyPublish(asset_info=self.asset_info)
            # ready.StartPublish()

        # Move work files - old content into the history folder
        # for cur_w in work_content:
        #     if not cur_w == "_History" or ".maya" in cur_w:
        #         shutil.move("%s/%s" % (self.asset_work_folder, cur_w),
        #                     "%s/_History/ORIG_%s" % (self.asset_work_folder, cur_w))

        # else:
        #     self.UF.SaveLog(cfg.project_paths["update_log_path"], "Asset skipped! Can't find %s_Rig.mb!" % (self.asset_info["asset_name"]))



    def CleanSet(self):
        # self.UF.SaveLog(cfg.project_paths["update_log_path"], "--- UPDATE: %s -----" % self.asset_info["asset_name"])
        # self.asset_info["asset_step"] = "Base"
        # work_content = self.GetContentAndCreateHistory(self.asset_work_folder)
        # set_file = "%s/%s.ma" % (self.asset_work_folder, self.asset_info["asset_name"])
        # if os.path.exists(set_file):
        #     #open rig file
        #     cmds.file(set_file, open = True, f = True,prompt=False)

        #Add and remove sets:
        unlock_and_remove= ["Anim_Set","Model_Set","Render_Set"]
        add_and_lock = ['PublishSet']
        add_to_publish_set = ["Root_Group"]
        for r_set in unlock_and_remove:
            if cmds.objExists(r_set):
                cmds.lockNode(r_set, lock=False)
                cmds.delete(r_set)
        for c_set in add_and_lock:
            if not cmds.objExists(c_set):
                cmds.sets(n=c_set, empty=True)
            cmds.lockNode(c_set,lock=True)
        cmds.sets(add_to_publish_set, add="PublishSet")

        self.CleanRootGroup(self.asset_info)

        from KS_AssetUpdate import TransferModel
        TM = TransferModel()
        TM.update_textures()
        TM.update_refs()

            # self.UF.DeleteUnknown(also_dag=True)
            # self.UF.DeleteUnusedNodes()

        # #SAVE FILE
        # try:
        #     cmds.file(type="mayaAscii")
        #     cmds.file(rename=cfg_util.CreatePathFromDict(cfg.project_paths["asset_work_path"], self.asset_info))
        #     cmds.file(save=True, f=True)
        # except Exception as c_e:
        #     print("Can't change fileformat?")
        #     self.UF.SaveLog(cfg.project_paths["update_log_path"],"Can't save as ascii!: %s" % (c_e))
        #     return False

        # move refs into "_History" folder
        # ref_content = self.GetContentAndCreateHistory(self.asset_ref_folder)
        # for cur in ref_content:
        #     print("Ref: %s/%s" % (self.asset_ref_folder,cur))
        #     shutil.move("%s/%s" %(self.asset_ref_folder,cur),"%s/_History/ORIG_%s" %(self.asset_ref_folder,cur))

            # # Move work files - old content into the history folder
            # for cur_w in work_content:
            #     if not cur_w == "_History" or ".maya" in cur_w:
            #         shutil.move("%s/%s" %(self.asset_work_folder,cur_w),"%s/_History/ORIG_%s" %(self.asset_work_folder,cur_w))

            # old_cache_folders = ["VrMesh", "Cache"]
            # asset_history = "%s/_History/" % self.asset_base
            # if not os.path.exists(asset_history):
            #     os.mkdir(asset_history)
            # for c_f in old_cache_folders:
            #     c_path = "%s/%s" % (self.asset_base,c_f)
            #     if os.path.exists(c_path):
            #         shutil.move(c_path, "%s/%s" % (asset_history,c_f))

            # #publish the asset
            # import PublishMaster
            # ready = PublishMaster.ReadyPublish(asset_info=self.asset_info)
            # ready.StartPublish()


        # else:
        #     self.UF.SaveLog(cfg.project_paths["update_log_path"], "Asset skipped! Can't find %s_Rig.mb!" % (self.asset_info["asset_name"]))

    def CleanSetDress(self):
        self.UF.SaveLog(cfg.project_paths["update_log_path"], "--- UPDATE: %s -----" % self.asset_info["asset_name"])
        self.asset_info["asset_step"] = "Base"
        work_content = self.GetContentAndCreateHistory(self.asset_work_folder)
        setdress_file = "%s/%s_Model.mb" % (self.asset_work_folder, self.asset_info["asset_name"])
        if os.path.exists(setdress_file):
            #open rig file
            cmds.file(setdress_file, open = True, f = True,prompt=False)

            #Add and remove sets:
            unlock_and_remove= ["Anim_Set","Model_Set","Render_Set"]
            for r_set in unlock_and_remove:
                if cmds.objExists(r_set):
                    cmds.lockNode(r_set, lock=False)
                    cmds.delete(r_set)
            self.CleanRootGroup(self.asset_info)

            from KS_AssetUpdate import TransferModel
            TM = TransferModel()
            TM.update_textures()
            TM.update_refs()

            self.UF.DeleteUnknown(also_dag=True)
            self.UF.DeleteUnusedNodes()

            #SAVE FILE
            try:
                cmds.file(type="mayaAscii")
                cmds.file(rename=cfg_util.CreatePathFromDict(cfg.project_paths["asset_work_path"], self.asset_info))
                cmds.file(save=True, f=True)
            except Exception as c_e:
                print("Can't change fileformat?")
                self.UF.SaveLog(cfg.project_paths["update_log_path"],"Can't save as ascii!: %s" % (c_e))
                return False

            # move refs into "_History" folder
            ref_content = self.GetContentAndCreateHistory(self.asset_ref_folder)
            for cur in ref_content:
                print("Ref: %s/%s" % (self.asset_ref_folder,cur))
                shutil.move("%s/%s" %(self.asset_ref_folder,cur),"%s/_History/ORIG_%s" %(self.asset_ref_folder,cur))

            # Move work files - old content into the history folder
            for cur_w in work_content:
                if not cur_w == "_History" or ".maya" in cur_w:
                    shutil.move("%s/%s" %(self.asset_work_folder,cur_w),"%s/_History/ORIG_%s" %(self.asset_work_folder,cur_w))

            old_cache_folders = ["VrMesh", "Cache"]
            asset_history = "%s/_History/" % self.asset_base
            if not os.path.exists(asset_history):
                os.mkdir(asset_history)
            for c_f in old_cache_folders:
                c_path = "%s/%s" % (self.asset_base,c_f)
                if os.path.exists(c_path):
                    shutil.move(c_path, "%s/%s" % (asset_history,c_f))

            #publish the asset
            from PublishAssets import PublishMaster
            ready = PublishMaster.ReadyPublish(asset_info=self.asset_info)
            ready.StartPublish()


        else:
            self.UF.SaveLog(cfg.project_paths["update_log_path"], "Asset skipped! Can't find %s_Rig.mb!" % (self.asset_info["asset_name"]))

    def CleanProp(self):
        print(self.asset_info)
        self.UF.SaveLog(cfg.project_paths["update_log_path"], "--- UPDATE: %s -----" % self.asset_info["asset_name"])
        self.asset_info["asset_step"]="Base"

        #make list of content in work folder
        work_content = os.listdir(self.asset_work_folder)
        if not "_History" in work_content:
            os.mkdir("%s/_History" % self.asset_work_folder)

        prop_file = "%s/%s_Rig.mb" % (self.asset_work_folder, self.asset_info["asset_name"])
        if os.path.exists(prop_file):
            #open rig file
            cmds.file(prop_file, open = True, f = True,prompt=False)

            #Add and remove sets:
            unlock_and_remove= ["Anim_Set","Model_Set","Render_Set"]
            add_and_lock = ['Anim_Delete_Set','PublishSet']
            add_to_publish_set = ["Root_Group"]
            for r_set in unlock_and_remove:
                if cmds.objExists(r_set):
                    cmds.lockNode(r_set, lock=False)
                    cmds.delete(r_set)
            for c_set in add_and_lock:
                if not cmds.objExists(c_set):
                    cmds.sets(n=c_set, empty=True)
                cmds.lockNode(c_set,lock=True)
            cmds.sets(add_to_publish_set, add="PublishSet")

            #unlock/break connection/remove old root attributes
            c_obj = "|Root_Group"
            attr_order = ["asset_type", "asset_category", "asset_name"]

            c_root = "|Root_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl|Root_Ctrl_Group|Root_Ctrl"
            c_obj_super = "|Root_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl"

            for c_at in ["scaleX", "scaleY", "scaleZ"]:
                cmds.setAttr("%s.%s" % (c_root, c_at), e=True, k=True, l=False)
                cmds.setAttr("%s.%s" % (c_obj_super, c_at), e=True, k=True, l=False)

            # cmds.setAttr("%s.__________Extra" % c_root, l=False)
            # cmds.deleteAttr(c_root, at="__________Extra")
            cmds.deleteAttr(c_root, at="smooth")

            if cmds.objExists(c_obj):  # Clean up Root_Group
                self.UF.DeleteOldRootAttributes()
                for my_attr in attr_order:
                    self.UF.SetStringAttribute(c_obj, my_attr, self.asset_info[my_attr])

            # update texture paths
            from KS_AssetUpdate import TransferModel
            TM = TransferModel()
            TM.update_textures()
            TM.update_refs()
            self.UF.DeleteUnknown()
            self.UF.DeleteUnusedNodes()
            # If ctrls are needed, then run replace ctrl script here: Otherwise delete the old nodes:
            # old_ai_shapes = cmds.ls(type="unknownDag")
            # for old in old_ai_shapes:
            #     cmds.delete(old)
            #SAVE FILE

            try:
                cmds.file(type="mayaAscii")
                cmds.file(rename=cfg_util.CreatePathFromDict(cfg.project_paths["asset_work_path"], self.asset_info))
                cmds.file(save=True, f=True)
            except Exception as c_e:
                print("Can't change fileformat?")
                self.UF.SaveLog(cfg.project_paths["update_log_path"],"Can't save as ascii!: %s" % (c_e))
                return False

            # move refs into "_History" folder
            ref_content = os.listdir(self.asset_ref_folder)
            if not "_History" in ref_content:
                os.mkdir("%s/_History" % self.asset_ref_folder)
            for cur in ref_content:
                if not cur =="_History" or ".maya" in cur:
                    print("Ref: %s/%s" % (self.asset_ref_folder,cur))
                    shutil.move("%s/%s" %(self.asset_ref_folder,cur),"%s/_History/ORIG_%s" %(self.asset_ref_folder,cur))

            # Move work files - old content into the history folder
            for cur_w in work_content:
                if not cur_w == "_History" or ".maya" in cur_w:
                    shutil.move("%s/%s" %(self.asset_work_folder,cur_w),"%s/_History/ORIG_%s" %(self.asset_work_folder,cur_w))

            #publish the asset
            from PublishAssets import PublishMaster
            ready = PublishMaster.ReadyPublish(asset_info=self.asset_info)
            ready.StartPublish()
        else:
            self.UF.SaveLog(cfg.project_paths["update_log_path"], "Asset skipped! Can't find %s_Rig.mb!" % (self.asset_info["asset_name"]))

    def CleanRootGroup(self,cur_asset_info):
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
            if cmds.attributeQuery("smooth", n=c_root, ex=True):
                cmds.deleteAttr(c_root, at="smooth")

        if cmds.objExists(c_obj):  # Clean up Root_Group
            self.UF.DeleteOldRootAttributes()
            for my_attr in attr_order:
                self.UF.SetStringAttribute(c_obj, my_attr, cur_asset_info[my_attr])

    def GetContentAndCreateHistory(self, cur_folder):
        work_content = os.listdir(cur_folder)
        if not "_History" in work_content:
            os.mkdir("%s/_History" % cur_folder)
        if "_History" in work_content:
            work_content.remove("_History")
        return work_content




    # def CreateSetdressCleanUp(self, file_open=None):  # UNUSED. Created a new template instead.
    #     # if file_open:
    #     #     self.UF.OpenFile(file_open)
    #     cmds.file(file_open, open=True, f=True)
    #     cmds.group(n='Full', empty=True)
    #     cmds.group(n='Proxy', empty=True)
    #     cmds.lockNode(['Full', 'Proxy'], lock=True)
    #     to_delete_list = []
    #     to_delete_list.append('Anim_Delete_Set')
    #     to_delete_list.append('PublishSet')
    #     to_delete_list.extend(cmds.listRelatives('Root_Group', c=True, f=True))
    #     cmds.lockNode(to_delete_list, lock=False)
    #     cmds.delete(to_delete_list)
    #     self.UF.Saving()

    def Overall(self):
        pass
        #Overall. Create Light asset type. Used for skydomes and lights?
        #Do we want to place in an approval light and a size relation? Or should that just be a import function ppl can chose to use?

        #Delete unused files - logs and asset text file.
        # For setdress move and rename vrayproxy and gpu.abc to the ref folder. In the file, correct the pathing to each.

        #open file

        #run update steps depending on what asset type we have open:
        #create and lock PublishSet and Anim_Delete_Set
        #Add Root_Group to PublishSet and Render_Group to Anim_Delete_Set
        #Delete old attributes on Root_Group and place new ones (only in base and rig files)
        #Change texture paths(mostly already done)
        #Change ref input for Char assets/Shading step. Might need to have a look at the files so nothing breaks.
        #Run clean up functions (delete unknown / delete unused nodes)
        #Save as MA file - Set/Setdress/Prop uses <asset_name>_Base.ma | Char uses <asset_name>_model/rig/shading.ma
        #move mb file into history folder and rename it to _orig.mb
        #Move and rename the old publish files in a "_History" folder in the ref folder as "_orig".
        #Publish the file.


class CreateAsset():
    def __init__(self, asset_info={}):
        #Get asset info?
        #Get template path - Done -
        #Get destination path - Done -
        #Check if path exists / Check if asset name is unique
        #Check on asset step? Should be set in publish? What functions use is it?
        # import UtilFunctions as UF
        # self.UF = UF.PublishFunctions()

        self.reg_dict = {}
        self.ref_dict = {}

        #TODO This could be changed. No reason to have this if statement
        if asset_info: #If asset_info is not given, can't create new asset :/ No reason to check for it.
            self.asset_info = asset_info
        else:
            self.asset_info = {"asset_type":"", "asset_category":"","asset_name":"","asset_step":""}
            return

        # self.asset_info.update(cfg.project_paths)
        self.asset_base = cfg_util.CreatePathFromDict(cfg.project_paths["asset_base_path"], self.asset_info)


    def Run(self):
        # TODO RUN check to see if asset already exists?
        if os.path.exists(self.asset_base):
            print("Asset folder already exists! -> %s"% self.asset_base)
            return False

        if self.asset_info["asset_type"].lower() == "setdress":
            self.template_path = "%s/Setdress_Template_Folder" % cfg.project_paths["template_path"]
            self.template_path = cfg_util.CreatePathFromDict(self.template_path)
            self.MakeRefPaths()
            self.CreateRegexDict()

            self.CopyTemplateAndReplace()
            # FOR NOW SKIP THIS. Instead we have more template folders to copy.
            self.asset_info["asset_step"] = "Base"
            #TODO - NOT OPTIMAL WORKFLOW! -Shouldn't open file if in maya? Unless asked for. Make MayaPy work :(
            # Don't need to clean up anymore because I've made separate asset template folders.
            # if in_maya:
            #     work_path = "%s.ma" % self.UF.CreatePathFromDict(cfg.project_paths["asset_work_path"], self.asset_info)
            #     self.UF.CreateSetdressCleanUp(file_open=work_path)
            # else:
            #     print("Can't access file :/")
            #     #TODO MAKE MAYAPY WORK!! WTF? VRAY ISSUE? Could port the whole command to mel, and use mayabatch.exe, but it seems like a weird work-around
            #     # self.RunMayaPySetdressCleanUp("%s.ma" % self.UF.CreatePathFromDict(cfg.project_paths["asset_work_path"], self.asset_info), "mayaAscii")

        elif self.asset_info["asset_type"] == "Set" or self.asset_info["asset_type"] == "Prop":
            self.template_path = "%s/Set_Template_Folder" % cfg.project_paths["template_path"]
            self.template_path = cfg_util.CreatePathFromDict(self.template_path,cfg.project_paths)
            self.MakeRefPaths()
            self.CreateRegexDict()

            self.CopyTemplateAndReplace()
        elif self.asset_info["asset_type"] == "Char":

            self.template_path = "%s/Char_Template_Folder" % cfg.project_paths["template_path"]
            self.template_path = cfg_util.CreatePathFromDict(self.template_path,cfg.project_paths)
            if os.path.exists(self.template_path):
                self.MakeRefPaths()
                self.CreateRegexDict()
                self.CopyTemplateAndReplace()

            # TODO Make a way to define what asset_step is currently going on?



    def CopyTemplateAndReplace(self):

        shutil.copytree(self.template_path, self.asset_base)
        # work_path = self.UF.CreatePathFromDict(cfg.project_paths["asset_work_path"], self.asset_info)
        for dirpath, dirnames, files in os.walk(self.asset_base):
            for c_file in files:
                if "Template" in c_file:
                    file_path = os.path.join(dirpath,c_file)
                    correct_path = file_path.replace("Template", self.asset_info["asset_name"])
                    # print("renaming: %s to %s" % (file_path, correct_path))
                    os.rename(file_path,correct_path)
                    if correct_path.endswith(".ma"):

                        self.ReplaceInMAFile(correct_path)

    def MakeRefPaths(self):
        for c_ref in cfg.ref_paths:
            self.asset_info["asset_step"]= c_ref
            my_regex = r"(((?<=\").:.*\/Template.*)(%s).*(?=\"))" % c_ref # (((?<=\").:.*\/Templates.*)(Model).*(?=\"))
            #regex (?<=\")<find " but don't include it>.:.*\/Templates.*<if symbol then : then as many chars until you hit /Templates
            # then run as many symbols until you hit Model then again until you find " but dont include it
            #Basically <"X:.../Templates...Model..."> but don't include the start and end ".
            asset_ref = cfg_util.CreatePathFromDict(cfg.ref_paths[c_ref], self.asset_info)
            # temp_ref = asset_ref.replace(self.asset_base,self.template_path)
            # self.ref_dict[temp_ref] = asset_ref
            self.ref_dict[my_regex] = asset_ref



    def CreateRegexDict(self):
        replace_dict = {"ReplaceName":self.asset_info["asset_name"],
                        "ReplaceType":self.asset_info["asset_type"],
                        "ReplaceCategory":self.asset_info["asset_category"]}
        replace_dict.update(self.ref_dict)
        for key in replace_dict.keys():
            if not replace_dict[key] == "":
                # print("Replace key: %s : %s |" % (key, replace_dict[key]))
                self.reg_dict[re.compile(key)] = replace_dict[key]


    def ReplaceInMAFile(self, cur_path):

        #(((? <= \").:.*/Templates.*)(?=\")) regex for finding template ref paths in ma files
        print("opening and running regex on file: %s" % cur_path)
        cur_file = open(cur_path, "r")
        cur_content = cur_file.read()
        cur_file.close()
        for key in self.reg_dict.keys():
            # print("running regex: %s on %s" % (self.reg_dict[key], cur_path))
            cur_content = re.sub(key,self.reg_dict[key],cur_content)
        temp = open(cur_path, "w")
        temp.write(cur_content)
        temp.close()


class CreateExtraFiles():
    def __init__(self, asset_info):
        self.asset_info = asset_info

    def CreateBlendshapeFile(self):
        #Create a blendshape file. Should have a ref of model. Maybe also some blendshape groups/sets from mmcb? And a PublishSet
        pass

    def LoadBlendshapeIntoScene(self):
        #Import or reference blendshape ref into rig scene
        pass

    def CreateGroomFile(self):
        #Create a groom file. Should ref in model or rig? Doesn't need publish set.
        pass

    def ImportGroom(self):
        #Optional. Should create a yeti node and set the input to groom-file and load in the groom file.
        pass


#
# def TestRegex(cur_path,cur_content):
#
#     #(((? <= \").:.*/Templates.*)(?=\")) regex for finding template ref paths in ma files
#     # print("opening and running regex on file: %s" % cur_path)
#     # cur_file = open(cur_path, "r")
#     # cur_content = cur_file.read()
#     # cur_file.close()
#
#     my_regex = r"(((?<=\").:.*\/Template.*)(%s).*(?=\"))" % "Rig"
#     s_gex = re.compile(my_regex,re.MULTILINE)
#     print(re.search(s_gex,cur_content))
#     # for key in self.reg_dict.keys():
#     #     # print("running regex: %s on %s" % (self.reg_dict[key], cur_path))
#     #     cur_content = re.sub(key,self.reg_dict[key],cur_content)
#     # temp = open(cur_path, "w")
#     # temp.write(cur_content)
#     # temp.close()

#     def RunMayaPySetdressCleanUp(self, file_path, file_type): #Not currently in use. Also didn't work.
#         script_content = """import maya.standalone
# maya.standalone.initialize('python')
# import maya.cmds as cmds
# import UtilFunctions as UF
# cmds.file('%s', open=True,f=True)
# c = UF.PublishFunctions()
# c.CreateSetdressCleanUp()
# cmds.file(type='%s')
# cmds.file(save=True)
# cmds.quit(f=True)""" % (file_path, file_type)
#         script_content = ";".join(script_content.split("\n"))
#         base_command = 'mayapy.exe -c "%s"' % (script_content)
#         print(base_command)
#         subprocess.Popen(base_command, shell=False, universal_newlines=True)
#
# CreateAsset(asset_info={"asset_type": "Setdress", "asset_category": "Stone", "asset_name": "FlintstoneB","asset_step": ""})
