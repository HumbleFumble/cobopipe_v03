try:
    import maya.cmds as cmds
    import maya.mel as mel
except:
    print("Not in maya")
    pass
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
import Maya_Functions.attr_util_functions as attr_util

from PublishAssets.PublishMaster import BasePublishClass

class PublishSetdressClass(BasePublishClass):
    def PublishSteps(self):
        report_content = {}
        if not CC.project_name == "MiasMagic2":
            if self.asset_info["asset_output"] == "Render":
                self.asset_info["asset_output"] = "Proxy"
        if self.asset_info["asset_output"] == "Proxy":
            publish_util.FindAndGroupFullAndProxyGroup()
            logger.info("SETDRESS PUBLISH! %s" % self.asset_info["asset_output"])
            publish_util.readyPublishReport(info_dict=self.asset_info,current_dict=report_content,ref=True,texture=False)
            vray_util.ReplaceVrayProxyWithMesh(ref_util.FindRefsInGroup())
            ref_util.ImportRefs()
            publish_util.SmoothSmoothSet()  # Use mesh smooth on everything in the set "SmoothSet"
            publish_util.ignoreColorspaceRule()
            #delete_util.optimizeScene()
            delete_util.DeleteUnknown()
            set_util.RemoveFromSet(set_name="PublishSet",selection=set_util.FindObjectsFromSet("PublishSet"))
            delete_util.DeleteDisplayLayers()
            delete_util.deleteSunAndSky()
            if not asset_util.CreateSetdressProxySetup(self.asset_info):
                cmds.warning("Setdress was not published. Couldn't make vray-node. Probably in use/rendering.")
                logger.warning("Setdress was not published. Couldn't make vray-node. Probably in use/rendering.")
                return False
            delete_util.DeleteEverythingBesidesPublishSet()
            delete_util.DeleteVrayRenderInfo()
            publish_util.SetFrameRate()
            delete_util.DeleteRenderLayers()
            delete_util.DeleteAnimLayers()
            delete_util.DeleteGraphNodes()
            delete_util.DeleteUnusedKeyframes()
            delete_util.DeleteUnusedNodes()
            delete_util.DeleteVraySettings()
            publish_util.makeCleanFileForPublishContent(output_file=self.output_file)
            set_util.DeleteSets()
            publish_util.readyPublishReport(info_dict=self.asset_info, current_dict=report_content,ref=False,texture=True, ids=True)
            publish_util.savePublishReport(info_dict=self.asset_info,content=report_content)
            if not file_util.TestAndSave(self.output_file):
                logger.warning("Setdress was not published")
                return False
            logger.info("Setdress published successfully")

        if self.asset_info["asset_output"] == "Render":
            logger.info("Attempting to publish: Render")
            # self.UF.RemoveRefs(self.ref_remove_list) #should not need this, instead use a Temp_Group for removal of unwanted WIP objects?
            publish_util.readyPublishReport(info_dict=self.asset_info, current_dict=report_content, ref=True,texture=False)
            ref_util.ImportRefs()
            publish_util.createRenderSubDivSet()
            delete_util.DeleteEverythingBesidesPublishSet()  # Need to add the set first
            delete_util.deleteSunAndSky()
            delete_util.DeleteAnimKeysOnCtrls()
            publish_util.SetFrameRate()
            asset_util.UnlockAndHideRigGroup()
            set_util.DeleteAllInSet("%s_Delete_Set" % self.asset_info["asset_output"])
            delete_util.DeleteOldAiExpressions()
            delete_util.DeleteDisplayLayers()
            delete_util.DeleteRenderLayers()
            delete_util.DeleteAnimLayers()
            delete_util.DeleteGraphNodes()
            delete_util.DeleteUnknown()
            delete_util.DeleteUnusedNodes()
            delete_util.DeleteUnusedKeyframes()
            delete_util.DeleteVrayRenderInfo()
            delete_util.DeleteVraySettings()
            publish_util.ignoreColorspaceRule()
            publish_util.makeCleanFileForPublishContent(output_file=self.output_file)
            set_util.DeleteSets()
            publish_util.readyPublishReport(info_dict=self.asset_info, current_dict=report_content,ref=False,texture=True, ids=True)
            publish_util.savePublishReport(info_dict=self.asset_info,content=report_content)
            if self.lock_geo:
                asset_util.LockGeoGroup()
            if not file_util.TestAndSave(self.output_file):
                logger.warning("Render was not published")
                return False
            logger.info("Render published successfully")

        if self.asset_info["asset_output"] == "Ingest":
            logger.info("Attempting to publish: Ingest")
            # self.UF.RemoveRefs(self.ref_remove_list) #should not need this, instead use a Temp_Group for removal of unwanted WIP objects?
            publish_util.readyPublishReport(info_dict=self.asset_info, current_dict=report_content, ref=True,texture=False)
            ref_util.ImportRefs()
            attr_util.copyOID('|Root_Group', '|Root_Group|Geo_Group')
            delete_util.DeleteEverythingBesidesPublishSet()  # Need to add the set first
            delete_util.deleteSunAndSky()
            delete_util.DeleteAnimKeysOnCtrls()
            publish_util.SetFrameRate()
            asset_util.UnlockAndHideRigGroup()
            publish_util.deleteRenderSubDivSet()
            set_util.DeleteAllInSet("%s_Delete_Set" % self.asset_info["asset_output"])
            delete_util.DeleteOldAiExpressions()
            delete_util.DeleteDisplayLayers()
            delete_util.DeleteRenderLayers()
            delete_util.DeleteAnimLayers()
            delete_util.DeleteGraphNodes()
            delete_util.DeleteUnknown()
            delete_util.DeleteUnusedNodes()
            delete_util.DeleteUnusedKeyframes()
            delete_util.DeleteVrayRenderInfo()
            publish_util.ignoreColorspaceRule()
            publish_util.makeCleanFileForPublishContent(output_file=self.output_file)
            set_util.DeleteSets()
            publish_util.removeRootGroup()
            publish_util.readyPublishReport(info_dict=self.asset_info, current_dict=report_content,ref=False,texture=True, ids=True)
            publish_util.savePublishReport(info_dict=self.asset_info,content=report_content)
            if not file_util.TestAndSave(self.output_file):
                logger.warning("Ingest was not published")
                return False
            logger.info("Ingest published successfully")
        return True