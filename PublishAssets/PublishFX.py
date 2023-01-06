try:
    import maya.cmds as cmds
    import maya.mel as mel
except:
    print("Not in maya")
    pass
import os
from Log.CoboLoggers import getLogger
logger = getLogger()

from getConfig import getConfigClass
CC = getConfigClass()

#IMPORT UTIL FUNCTIONS TO CLEAN WORK FILE - AND SAVE THAT AS PUBLISH
import Maya_Functions.file_util_functions as file_util
import Maya_Functions.delete_and_clean_up_functions as delete_util
import Maya_Functions.ref_util_functions as ref_util
import Maya_Functions.publish_util_functions as publish_util
import Maya_Functions.set_util_functions as set_util
import Maya_Functions.asset_util_functions as asset_util
# import Maya_Functions.vray_util_functions as vray_util

from PublishAssets.PublishMaster import BasePublishClass


class PublishFXClass(BasePublishClass):
    def PublishSteps(self):
        # self.lock_geo = lock_geo
        report_content = {}
        if self.asset_info["asset_output"] == "Anim":
            logger.info("Attempting to publish: Anim")

            # self.UF.RemoveRefs(self.ref_remove_list) #should not need this, instead use a Temp_Group for removal of unwanted WIP objects?
            publish_util.readyPublishReport(info_dict=self.asset_info, current_dict=report_content, ref=True,texture=False)
            ref_util.ImportRefs()
            delete_util.DeleteEverythingBesidesPublishSet()#Need to add the set first
            delete_util.deleteSunAndSky()
            delete_util.DeleteAnimKeysOnCtrls()
            publish_util.SetFrameRate()
            #asset_util.UnlockAndHideRigGroup()
            delete_util.DeleteOldAiExpressions()
            delete_util.DeleteDisplayLayers()
            delete_util.DeleteRenderLayers()
            delete_util.DeleteAnimLayers()
            delete_util.DeleteUnknown()
            delete_util.DeleteUnusedNodes()
            delete_util.DeleteVrayRenderInfo()
            delete_util.DeleteVraySettings()
            set_util.DeleteSets()
            publish_util.ignoreColorspaceRule()
            publish_util.readyPublishReport(info_dict=self.asset_info, current_dict=report_content,ref=False,texture=True, ids=True)
            publish_util.savePublishReport(info_dict=self.asset_info,content=report_content)
            if self.lock_geo:
                asset_util.LockGeoGroup()
            if not file_util.TestAndSave(self.output_file):
                logger.warning("Animation was not published")
                return False
            logger.info("Animation published successfully")

        if self.asset_info["asset_output"] == "Render":
            logger.info("Attempting to publish: Render")
            # self.UF.RemoveRefs(self.ref_remove_list) #should not need this, instead use a Temp_Group for removal of unwanted WIP objects?
            publish_util.readyPublishReport(info_dict=self.asset_info, current_dict=report_content, ref=True,
                                            texture=False)
            ref_util.ImportRefs()
            delete_util.DeleteEverythingBesidesPublishSet()  # Need to add the set first
            delete_util.deleteSunAndSky()
            delete_util.DeleteAnimKeysOnCtrls()
            publish_util.SetFrameRate()
            #asset_util.UnlockAndHideRigGroup()
            delete_util.DeleteOldAiExpressions()
            delete_util.DeleteDisplayLayers()
            delete_util.DeleteRenderLayers()
            delete_util.DeleteAnimLayers()
            delete_util.DeleteUnknown()
            delete_util.DeleteUnusedNodes()
            delete_util.DeleteVrayRenderInfo()
            delete_util.DeleteVraySettings()
            set_util.DeleteSets()
            publish_util.ignoreColorspaceRule()
            publish_util.readyPublishReport(info_dict=self.asset_info, current_dict=report_content,ref=False,texture=True, ids=True)
            publish_util.savePublishReport(info_dict=self.asset_info,content=report_content)
            if self.lock_geo:
                asset_util.LockGeoGroup()
            if not file_util.TestAndSave(self.output_file):
                logger.info("Render was not published")
                return False
            logger.info("Render published successfully")
        return True
"""
class OLD_PublishFXClass():
    def __init__(self,asset_info={}, extra={"currently_open_file":True,"LockGeo":True}):
        self.extra = extra
        self.UF = UF.PublishFunctions()
        self.asset_info = asset_info

        self.asset_info.update(cfg.project_paths)
        if not self.extra["currently_open_file"]:
            self.fx_path = cfg_util.CreatePathFromDict(cfg.project_paths["asset_work_path"], self.asset_info)
            self.fx_path = "%s%s" % (self.fx_path, self.UF.CheckFileType(self.fx_path))
        else:
            self.fx_path = cmds.file(q=True,sn=True)

        output_list = self.asset_info["asset_output"]

        for c_out in output_list:
            self.UF.OpenFile(self.fx_path,True)
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
"""

