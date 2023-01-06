try:
    import maya.cmds as cmds
    import maya.mel as mel
except:
    pass
import os
import Config_MiaMagic2 as cfg
import ConfigUtil
cfg_util = ConfigUtil.ConfigUtilClass(cfg)
# import ConfigUtil as cfg_util
# import ProjectConfig as cfg
import UtilFunctions as UF


# import ConfigUtil as cfg_util


class PublishPropClass():
    def __init__(self,asset_info={}, extra={"currently_open_file":True,"LockGeo":True}):
        self.extra = extra
        self.UF = UF.PublishFunctions()
        self.asset_info = asset_info

        self.asset_info.update(cfg.project_paths)
        if not self.extra["currently_open_file"]:
            self.prop_path = cfg_util.CreatePathFromDict(cfg.project_paths["asset_work_path"], self.asset_info)
            self.prop_path = "%s%s" % (self.prop_path, self.UF.CheckFileType(self.prop_path))
        else:
            self.prop_path = cmds.file(q=True,sn=True)

        output_list = self.asset_info["asset_output"]

        for c_out in output_list:
            self.UF.OpenFile(self.prop_path,True)
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

    def PublishSteps(self):
        if self.asset_info["asset_output"] == "Anim":
            print("Attempting to publish: Anim")

            # self.UF.RemoveRefs(self.ref_remove_list) #should not need this, instead use a Temp_Group for removal of unwanted WIP objects?
            self.UF.ImportRefs()
            self.UF.DeleteEverythingBesidesPublishSet()#Need to add the set first
            self.UF.DeleteAnimKeysOnCtrls()
            self.UF.SetFrameRate()
            self.UF.UnlockAndHideRigGroup()
            self.UF.DeleteOldAiExpressions()
            self.UF.DeleteDisplayLayers()
            self.UF.DeleteRenderLayers()
            self.UF.DeleteAnimLayers()
            # self.UF.RemoveArnold() #Not sure how much we need to do this
            self.UF.DeleteUnknown()
            self.UF.DeleteUnusedNodes()
            self.UF.DeleteSets()
            if self.extra["LockGeo"]:
                self.UF.LockGeoGroup()
            if not self.UF.TestAndSave(self.output_file):
                return False

        if self.asset_info["asset_output"] == "Render":
            print("Attempting to publish: Render")
            # self.UF.DeleteUnknown()
            # self.UF.RemoveRefs(self.ref_remove_list) #should not need this, instead use a Temp_Group for removal of unwanted WIP objects?
            self.UF.ImportRefs()
            self.UF.DeleteEverythingBesidesPublishSet()#Need to add the set first
            self.UF.DeleteAnimKeysOnCtrls()
            self.UF.UnlockAndHideRigGroup()
            self.UF.SetFrameRate()
            self.UF.DeleteDisplayLayers()
            self.UF.DeleteRenderLayers()
            self.UF.DeleteAnimLayers()
            # self.UF.RemoveArnold() #Not sure how much we need to do this
            self.UF.DeleteUnknown()
            self.UF.DeleteUnusedNodes()
            self.UF.DeleteSets()
            if self.extra["LockGeo"]:
                self.UF.LockGeoGroup()
            if not self.UF.TestAndSave(self.output_file):
                return False
        return True


