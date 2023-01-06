try:
    import maya.cmds as cmds
    import maya.mel as mel
except:
    print("Not in maya")
    pass
import os
from getConfig import getConfigClass
CC = getConfigClass()
from Log.CoboLoggers import getLogger
logger = getLogger()

#IMPORT UTIL FUNCTIONS TO CLEAN WORK FILE - AND SAVE THAT AS PUBLISH
import Maya_Functions.file_util_functions as file_util
import Maya_Functions.delete_and_clean_up_functions as delete_util
import Maya_Functions.ref_util_functions as ref_util
import Maya_Functions.publish_util_functions as publish_util
import Maya_Functions.set_util_functions as set_util
import Maya_Functions.asset_util_functions as asset_util
import Maya_Functions.vray_util_functions as vray_util
import Maya_Functions.yeti_util_functions as yeti_util

from PublishAssets.PublishMaster import BasePublishClass

class PublishCharClass(BasePublishClass):
    def PublishSteps(self):
        report_content = {}
        if self.asset_info["asset_output"] == "Model":
            logger.info("Attempting to publish: Model")
            ref_util.RemoveUnloadedRefs()
            ref_util.ImportRefs()
            delete_util.CleanNamespaces()
            delete_util.DeleteEverythingBesidesPublishSet()
            delete_util.deleteSunAndSky()
            delete_util.DeleteAnimKeysOnCtrls()
            publish_util.SetFrameRate()
            delete_util.DeleteImagePlanes()
            delete_util.DeleteDisplayLayers()
            delete_util.DeleteRenderLayers()
            delete_util.DeleteAnimLayers()
            delete_util.DeleteUnknown()
            delete_util.DeleteVrayRenderInfo()  # Clean vray settings and render-elements
            delete_util.DeleteUnusedNodes()
            delete_util.DeleteUnusedKeyframes()
            delete_util.DeleteVraySettings()
            publish_util.makeCleanFileForPublishContent(output_file=self.output_file)
            set_util.DeleteSets()
            delete_util.GeoGroup_Removing_Model()
            if not file_util.TestAndSave(self.output_file):
                logger.warning("Model was not published")
                return False
            logger.info("Model published successfully")

        if self.asset_info["asset_output"] == "Rig":
            logger.info("Attempting to publish: Rig")
            ref_util.RemoveUnloadedRefs()
            publish_util.readyPublishReport(info_dict=self.asset_info, current_dict=report_content, ref=True,
                                            texture=False)
            ref_util.ImportRefs()
            delete_util.RemoveNamespaceOfPreviousStep(self.asset_info)
            delete_util.CleanNamespaces()
            set_util.DeleteAllInSet("%s_Delete_Set" % self.asset_info["asset_output"])
            delete_util.deleteSunAndSky()
            delete_util.DeleteEverythingBesidesPublishSet()
            delete_util.DeleteImagePlanes()
            delete_util.DeleteAnimKeysOnCtrls()
            publish_util.SetFrameRate()
            asset_util.UnlockAndHideRigGroup()
            delete_util.DeleteGraphNodes()
            delete_util.DeleteUnknown()
            delete_util.DeleteDisplayLayers()
            delete_util.DeleteRenderLayers()
            delete_util.DeleteAnimLayers()
            delete_util.DeleteVrayRenderInfo()  # Clean vray settings and render-elements
            delete_util.DeleteUnusedNodes()
            delete_util.DeleteUnusedKeyframes()
            delete_util.DeleteVraySettings()
            publish_util.ignoreColorspaceRule()
            publish_util.makeCleanFileForPublishContent(output_file=self.output_file)
            set_util.DeleteSets()
            publish_util.readyPublishReport(info_dict=self.asset_info, current_dict=report_content,ref=False,texture=True, ids=True)
            publish_util.savePublishReport(info_dict=self.asset_info,content=report_content)
            if not file_util.TestAndSave(self.output_file):
                logger.warning("Rig was not published")
                return False
            logger.info("Rig published successfully")

        if self.asset_info["asset_output"] == "Anim":
            logger.info("Attempting to publish: Anim")
            ref_util.RemoveUnloadedRefs()
            publish_util.readyPublishReport(info_dict=self.asset_info, current_dict=report_content, ref=True,
                                            texture=False)
            ref_util.ImportRefs()
            delete_util.RemoveNamespaceOfPreviousStep(self.asset_info)
            delete_util.CleanNamespaces()
            delete_util.DeleteEverythingBesidesPublishSet()
            delete_util.deleteSunAndSky()
            set_util.DeleteAllInSet("%s_Delete_Set" % self.asset_info["asset_output"])
            delete_util.DeleteImagePlanes()
            delete_util.DeleteAnimKeysOnCtrls()
            delete_util.cleanProjectUniques(project_name=CC.project_name,publish_step="Anim")
            publish_util.SetFrameRate()
            asset_util.UnlockAndHideRigGroup()
            delete_util.DeleteGraphNodes()
            delete_util.DeleteUnknown()
            delete_util.DeleteDisplayLayers()
            delete_util.DeleteRenderLayers()
            delete_util.DeleteAnimLayers()
            delete_util.DeleteVrayRenderInfo()  # Clean vray settings and render-elements
            delete_util.DeleteUnusedNodes()
            delete_util.DeleteUnusedKeyframes()
            delete_util.DeleteVraySettings()
            publish_util.ignoreColorspaceRule()
            publish_util.makeCleanFileForPublishContent(output_file=self.output_file)
            set_util.DeleteSets()
            publish_util.readyPublishReport(info_dict=self.asset_info, current_dict=report_content,ref=False, texture=True, ids=True)
            publish_util.savePublishReport(info_dict=self.asset_info,content=report_content)
            if self.lock_geo:
                asset_util.LockGeoGroup()
            if not file_util.TestAndSave(self.output_file):
                logger.warning("Animation was not published")
                return False
            logger.info("Animation published successfully")

        if self.asset_info["asset_output"] == "Render":
            logger.info("Attempting to publish: Render")
            # self.UF.RemoveRefs(self.ref_remove_list)
            ref_util.RemoveUnloadedRefs()
            publish_util.readyPublishReport(info_dict=self.asset_info, current_dict=report_content, ref=True,
                                            texture=False)
            ref_util.ImportRefs()
            delete_util.RemoveNamespaceOfPreviousStep(self.asset_info)
            delete_util.CleanNamespaces()
            delete_util.DeleteEverythingBesidesPublishSet()
            delete_util.deleteSunAndSky()
            set_util.DeleteAllInSet("%s_Delete_Set" % self.asset_info["asset_output"])
            delete_util.DeleteImagePlanes()
            yeti_util.SetYetiNodeToCache()
            delete_util.DeleteAnimKeysOnCtrls()
            publish_util.SetFrameRate()
            asset_util.UnlockAndHideRigGroup()
            delete_util.DeleteGraphNodes()
            delete_util.DeleteUnknown()
            delete_util.DeleteDisplayLayers()
            delete_util.DeleteRenderLayers()
            delete_util.DeleteAnimLayers()
            delete_util.DeleteVrayRenderInfo()  # Clean vray settings and render-elements
            delete_util.DeleteUnusedNodes()
            delete_util.DeleteVraySettings()
            publish_util.ignoreColorspaceRule()
            publish_util.makeCleanFileForPublishContent(output_file=self.output_file)
            # set_util.DeleteSets()
            publish_util.readyPublishReport(info_dict=self.asset_info, current_dict=report_content,ref=False, texture=True, ids=True)
            publish_util.savePublishReport(info_dict=self.asset_info,content=report_content)
            if self.lock_geo:
                asset_util.LockGeoGroup()
            if not file_util.TestAndSave(self.output_file):
                logger.warning("Render was not published")
                return False
            logger.info("Render published successfully")
        return True

"""
class PublishCharClass():
    def __init__(self,asset_info={}, extra={"currently_open_file": False,"LockGeo":True}):
        self.extra = extra
        self.UF = UF.PublishFunctions()
        self.asset_info = asset_info
        self.asset_work_file = CC.asset_work_file(**self.asset_info)


        output_list = self.asset_info["asset_output"]
        print("OUTPUT LIST: %s" % output_list)

        for c_out in output_list:
            import Maya_Functions.file_util_functions as file_util
            file_util.OpenFile(self.asset_work_path,True)
            self.asset_info["asset_output"] = c_out

            self.output_file_function = getattr(CC, "CC.get_{asset_output}".format(asset_output =self.self.asset_info["asset_output"]))
            self.output_file = self.output_file_function(**self.asset_info)


            print(self.output_file)
            temp_path = file_util.SaveTempFile()
            if temp_path:
                did_it_publish = self.PublishSteps()
                try:
                    os.remove(temp_path)
                except:
                    print ("Couldn't remove temp file")
                if not did_it_publish:
                    break

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
"""