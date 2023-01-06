try: 
    import maya.cmds as cmds
    import maya.mel as mel
except:
    pass
import os

import Config_MiaMagic2 as cfg
import ConfigUtil
import Config_MiaMagic as old_cfg
cfg_util = ConfigUtil.ConfigUtilClass(cfg)
# import ConfigUtil as cfg_util
# import ProjectConfig as cfg
# import UtilFunctions as UF
# import ConfigUtil

#TODO In Create New Asset - have extra file saved in _history folder

class PublishCharClass():
    def __init__(self,asset_info={}, extra={"currently_open_file": False,"LockGeo":True}):
        self.extra = extra
        self.UF = UF.PublishFunctions()
        self.asset_info = asset_info

        self.asset_info.update(cfg.project_paths)
        # if not self.extra["currently_open_file"]:
        self.asset_work_path = cfg_util.CreatePathFromDict(cfg.project_paths["asset_work_path"], self.asset_info)
        self.asset_work_path = "%s%s" % (self.asset_work_path, self.UF.CheckFileType(self.asset_work_path))
        # else:
        #     self.asset_work_path = cmds.file(q=True, sn=True)

        output_list = self.asset_info["asset_output"]
        print("OUTPUT LIST: %s" % output_list)
        # for c_out in output_list:
        #     self.UF.OpenFile(self.asset_work_path, True)
        #     self.asset_info["asset_output"] = c_out
        #     self.output_file = cfg.ref_paths[self.asset_info["asset_output"]]
        #     self.output_file = cfg_util.CreatePathFromDict(self.output_file, self.asset_info)
        #     print(self.output_file)
        #     if not self.RunPublish():
        #         break
        for c_out in output_list:
            self.UF.OpenFile(self.asset_work_path,True)
            self.asset_info["asset_output"] = c_out
            self.output_file = cfg.ref_paths[self.asset_info["asset_output"]]
            self.output_file = cfg_util.CreatePathFromDict(self.output_file, self.asset_info)
            print(self.output_file)
            temp_path = self.UF.SaveTempFile()
            if temp_path:
                did_it_publish = self.PublishSteps()
                try:
                    os.remove(temp_path)
                except:
                    print ("Couldn't remove temp file")
                if not did_it_publish:
                    break


    # def RunPublish(self):
    #     ##Save as temp file to check for problems##'
    #     # if self.extra["open"]:
    #     #     self.UF.OpenFile(self.prop_path)
    #     if not os.path.exists("C:/Temp"):
    #         os.mkdir("C:/Temp")
    #     self.cur_rand_num = random.randrange(1,1000)
    #     self.temp_path = "C:/Temp/Publish_Temp_%s.mb" % self.cur_rand_num
    #     self.UF.PrepareForSave(self.temp_path)
    #     did_it_publish = self.PublishSteps()
    #     try:
    #         os.remove(self.temp_path)
    #     except:
    #         print("Couldn't remove temp file")
    #     return did_it_publish

    def PublishSteps(self):

        if self.asset_info["asset_output"] == "Model":
            print("Attempting to publish: Model")
            self.UF.RemoveUnloadedRefs()
            self.UF.ImportRefs()
            self.UF.CleanNamespaces()
            self.UF.DeleteEverythingBesidesPublishSet()
            self.UF.DeleteAnimKeysOnCtrls()
            self.UF.SetFrameRate()
            self.UF.DeleteImagePlanes()
            self.UF.DeleteDisplayLayers()
            self.UF.DeleteRenderLayers()
            self.UF.DeleteAnimLayers()
            self.UF.DeleteUnknown()
            self.UF.DeleteVrayRenderInfo() #Clean vray settings and render-elements
            self.UF.DeleteUnusedNodes()
            self.UF.DeleteSets()
            self.UF.GeoGroup_Removing_Model()
            if not self.UF.TestAndSave(self.output_file):
                return False


        if self.asset_info["asset_output"] == "Rig":
            print("Attempting to publish: Rig")
            self.UF.RemoveUnloadedRefs()
            self.UF.ImportRefs()
            self.UF.RemoveNamespaceOfPreviousStep(self.asset_info)
            self.UF.CleanNamespaces()
            self.UF.DeleteAllInSet("%s_Delete_Set" % self.asset_info["asset_output"])
            self.UF.DeleteEverythingBesidesPublishSet()
            self.UF.DeleteImagePlanes()
            self.UF.DeleteAnimKeysOnCtrls()
            self.UF.SetFrameRate()
            self.UF.UnlockAndHideRigGroup()
            self.UF.DeleteUnknown()
            self.UF.DeleteDisplayLayers()
            self.UF.DeleteRenderLayers()
            self.UF.DeleteAnimLayers()
            self.UF.DeleteVrayRenderInfo()  # Clean vray settings and render-elements
            self.UF.DeleteUnusedNodes()
            self.UF.DeleteSets()
            if not self.UF.TestAndSave(self.output_file):
                return False
            print("RIG PUBLISHED!")

        if self.asset_info["asset_output"] == "Anim":
            print("Attempting to publish: Anim")
            self.UF.RemoveUnloadedRefs()
            self.UF.ImportRefs()
            self.UF.RemoveNamespaceOfPreviousStep(self.asset_info)
            self.UF.CleanNamespaces()
            self.UF.DeleteEverythingBesidesPublishSet()
            self.UF.DeleteAllInSet("%s_Delete_Set" % self.asset_info["asset_output"])
            self.UF.DeleteImagePlanes()
            self.UF.DeleteAnimKeysOnCtrls()
            self.UF.SetFrameRate()
            self.UF.UnlockAndHideRigGroup()
            self.UF.DeleteUnknown()
            self.UF.DeleteDisplayLayers()
            self.UF.DeleteRenderLayers()
            self.UF.DeleteAnimLayers()
            self.UF.DeleteVrayRenderInfo()  # Clean vray settings and render-elements
            self.UF.DeleteUnusedNodes()
            self.UF.DeleteSets()
            if self.extra["LockGeo"]:
                self.UF.LockGeoGroup()
            if not self.UF.TestAndSave(self.output_file):
                return False
            print("ANIM PUBLISHED!")

        if self.asset_info["asset_output"] == "Render":
            print("Attempting to publish: Render")
            # self.UF.RemoveRefs(self.ref_remove_list)
            self.UF.RemoveUnloadedRefs()
            self.UF.ImportRefs()
            self.UF.RemoveNamespaceOfPreviousStep(self.asset_info)
            # cmds.namespace(rm="Rig", mnr=True) #Delete the rig namespace for the root group. Could be avoided by not having a namespace on rig ref?
            self.UF.CleanNamespaces()
            self.UF.DeleteEverythingBesidesPublishSet()
            self.UF.DeleteAllInSet("%s_Delete_Set" % self.asset_info["asset_output"])
            self.UF.DeleteImagePlanes()
            self.UF.SetYetiNodeToCache()
            self.UF.DeleteAnimKeysOnCtrls()
            self.UF.SetFrameRate()
            self.UF.DeleteUnknown()
            self.UF.DeleteDisplayLayers()
            self.UF.DeleteRenderLayers()
            self.UF.DeleteAnimLayers()
            self.UF.DeleteVrayRenderInfo()  # Clean vray settings and render-elements
            self.UF.DeleteUnusedNodes()
            self.UF.DeleteSets()
            if self.extra["LockGeo"]: #Do we want that on render versions??
                self.UF.LockGeoGroup()
            if not self.UF.TestAndSave(self.output_file):
                return False
        return True