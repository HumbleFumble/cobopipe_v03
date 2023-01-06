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
# import Maya_Functions.vray_util_functions as vray_util

from PublishAssets.PublishMaster import BasePublishClass

class PublishSetClass(BasePublishClass):
    def PublishSteps(self):
        # self.lock_geo = lock_geo
        report_content = {}
        if self.asset_info["asset_output"] == "Anim" or self.asset_info["asset_output"] == "Render":
            logger.info("Attempting to publish: Anim")
            delete_util.DeleteUnknown()
            ref_util.RemoveUnloadedRefs()
            if CC.project_name == 'MiasMagic2':
                ref_util.instanceScene()
                # ref_util.removeProxyShaderIssueEdits()
            publish_util.readyPublishReport(info_dict=self.asset_info, current_dict=report_content, ref=True,texture=False)

            ref_util.ImportRefs()
            delete_util.CleanNamespaces()
            delete_util.deleteSunAndSky()
            delete_util.DeleteEverythingBesidesPublishSet()#Need to add the set first
            set_util.DeleteAllInSet("%s_Delete_Set" % self.asset_info["asset_output"])
            delete_util.cleanProjectUniques(project_name=CC.project_name, publish_step=self.asset_info["asset_output"])
            delete_util.DeleteAnimKeysOnCtrls()
            publish_util.SetFrameRate()
            delete_util.DeleteDisplayLayers()
            delete_util.DeleteGraphNodes()
            delete_util.DeleteUnknown()
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
            if self.lock_geo:
                asset_util.LockGeoGroup()
            if not file_util.TestAndSave(self.output_file):
                logger.warning("Animation was not published")
                return False
            logger.info("Animation published successfully")
        return True

