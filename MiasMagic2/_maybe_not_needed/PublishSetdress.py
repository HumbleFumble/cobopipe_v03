try:
    import maya.cmds as cmds
    import maya.mel as mel
except:
    pass
import os

# import ProjectConfig as cfg
import UtilFunctions as UF
# import ConfigUtil as cfg_util

import Config_MiaMagic2 as cfg
# import Config_MiaMagic as old_cfg
import ConfigUtil
cfg_util = ConfigUtil.ConfigUtilClass(cfg)

class PublishSetdressClass():
    def __init__(self,asset_info={}, extra={"currently_open_file":True,"LockGeo":True}):
        self.extra = extra
        self.UF = UF.PublishFunctions()
        self.asset_info = asset_info

        self.asset_info.update(cfg.project_paths)
        if not self.extra["currently_open_file"]:
            self.asset_work_path = cfg_util.CreatePathFromDict(cfg.project_paths["asset_work_path"], self.asset_info)

            self.asset_work_path = "%s%s" % (self.asset_work_path, self.UF.CheckFileType(self.asset_work_path))
        else:
            self.asset_work_path = cmds.file(q=True,sn=True)

        output_list = self.asset_info["asset_output"]

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


    def PublishSteps(self):
        print("Attempting to publish: Render")
        self.UF.ReplaceVrayProxyWithMesh(self.UF.FindRefsInGroup())
        self.UF.SmoothSmoothSet() #Use mesh smooth on everything in the set "SmoothSet"
        self.UF.ImportRefs()
        self.UF.DeleteUnknown()
        self.UF.CreateSetdressProxySetup(self.asset_info)

        self.UF.DeleteEverythingBesidesPublishSet()
        self.UF.SetFrameRate()
        self.UF.DeleteDisplayLayers()
        self.UF.DeleteRenderLayers()
        self.UF.DeleteAnimLayers()
        # self.UF.RemoveArnold()
        self.UF.DeleteUnusedNodes()
        self.UF.DeleteSets()
        if not self.UF.TestAndSave(self.output_file):
            return False
        return True