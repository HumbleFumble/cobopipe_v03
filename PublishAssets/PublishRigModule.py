try: 
    import maya.cmds as cmds
    import maya.mel as mel
except:
    print("Not in maya")
    pass
import os

from getConfig import getConfigClass
CC = getConfigClass()

#TODO In Create New Asset - have extra file saved in _history folder

class PublishRigModule():
    def __init__(self,asset_info={}, extra={"currently_open_file": False,"LockGeo":False}):
        self.extra = extra
        self.asset_info = asset_info
        print(self.asset_info)
        self.asset_work_file = CC.get_asset_work_file(**self.asset_info)


        output_list = self.asset_info["asset_output"]
        print("OUTPUT LIST: %s" % output_list)

        for c_out in output_list:
            import Maya_Functions.file_util_functions as file_util
            print("Output: %s" % c_out)
            self.asset_info["asset_output"] = c_out
            self.output_file_function = getattr(CC, "get_{asset_output}".format(asset_output =self.asset_info["asset_output"]))
            self.output_file = self.output_file_function(**self.asset_info)

            print(self.output_file)

            file_util.OpenFile(self.asset_work_file, True)
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
        import Maya_Functions.set_util_functions as set_util
        import Maya_Functions.delete_and_clean_up_functions as delete_util
        import Maya_Functions.ref_util_functions as ref_util
        import Maya_Functions.publish_util_functions as publish_util
        import Maya_Functions.file_util_functions as file_util
        print("Publish Steps -RigModule")
        print(self.asset_info)
        if self.asset_info["asset_output"] == "Rig":
            print("Attempting to publish: Model")
            ref_util.RemoveUnloadedRefs()
            ref_util.ImportRefs()
            print("Deleting things!")
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
            delete_util.DeleteVrayRenderInfo() #Clean vray settings and render-elements
            delete_util.DeleteUnusedNodes()
            delete_util.DeleteUnusedKeyframes()
            delete_util.DeleteVraySettings()
            set_util.DeleteSets()
            if not file_util.TestAndSave(self.output_file):
                return False
        return True