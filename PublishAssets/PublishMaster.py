import logging
import os
from getConfig import getConfigClass
from Log.CoboLoggers import getLogger
logger = getLogger()

try:
    import maya.cmds as cmds
    in_maya = True
except:
    in_maya = False

CC = getConfigClass(set_env=False)

# IMPORT UTIL FUNCTIONS TO CLEAN WORK FILE - AND SAVE THAT AS PUBLISH
import Maya_Functions.file_util_functions as file_util


# import Maya_Functions.delete_and_clean_up_functions as delete_util
# import Maya_Functions.ref_util_functions as ref_util
# import Maya_Functions.publish_util_functions as publish_util
# import Maya_Functions.set_util_functions as set_util
# import Maya_Functions.asset_util_functions as asset_util
# import Maya_Functions.vray_util_functions as vray_util


# TODO Implement Logging!


class ReadyPublish:
    def __init__(self, asset_info={}, currently_open_file=False, lock_geo=True):
        # if logger:
        #     logger = getLogger(str(self.__class__).split(".")[-1].replace("'>", ""), console_level=logging.DEBUG)
        # else:
        #     logger = getLogger(str(self.__class__).split(".")[-1].replace("'>", ""))
        logger.info("Initializing")
        self.maya_py_cmd = ""
        self.issue_dict = {}
        self.currently_open_file = currently_open_file
        self.lock_geo = lock_geo
        if asset_info:
            logger.info("****Initialized with asset info")
            self.asset_info = asset_info
        else:
            logger.warning("****Initialized without asset info")
            if in_maya:
                logger.warning("********Getting asset info from file")
                from Maya_Functions.asset_util_functions import GetAssetInfoFromFile
                # TODO Need a check against what maya file is open.
                self.asset_info = GetAssetInfoFromFile()
                self.CheckPublish()
                if False in self.issue_dict.values():
                    logger.warning("************Problem found. issue_dict=" + str(self.issue_dict))
            else:
                logger.critical("********Illegal state, asset_info=" + self.asset_info + " in_maya=" + in_maya)
                raise ValueError("Missing asset_info dict with asset values!")
        self.CreateMayaPyCmd()

    def CreateMayaPyCmd(self):
        script_content = """import maya.standalone
            maya.standalone.initialize('python')
            import maya.cmds as cmds
            import PublishAssets.PublishMaster as PublishMaster 
            pub = PublishMaster.ReadyPublish(asset_info={asset_dict})
            pub.StartPublish()""".format(asset_dict=self.asset_info)
        script_content = ";".join(script_content.split("\n"))
        base_command = 'mayapy.exe -c "%s"' % (script_content)
        logger.info("Created mayapy command: " + base_command)
        self.maya_py_cmd = base_command

    def StartPublishInMayaPy(self):
        import subprocess
        print(self.maya_py_cmd)
        cp = subprocess.Popen(self.maya_py_cmd, shell=False, universal_newlines=True, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
        # output = cp.communicate()[0]
        print(cp.communicate()[0])
        return cp.communicate()

    def CheckPublish(self):
        from Maya_Functions.publish_util_functions import CheckPublishSet, CheckSetdressScene
        self.issue_dict = {}
        if self.asset_info:
            if self.asset_info["asset_type"] == "Prop" or self.asset_info["asset_type"] == "Set":
                self.issue_dict["PublishSet"] = CheckPublishSet()
            if self.asset_info["asset_type"] == "Setdress":
                self.issue_dict["ProxyGroups"] = CheckSetdressScene()
        else:
            self.issue_dict["asset_info"] = False
        return self.issue_dict

    def StartPublish(self):
        if self.asset_info:
            if self.asset_info["asset_type"] == "Prop":
                import PublishProp
                self.asset_info["asset_output"] = self.GetOutputTypes()
                if self.asset_info["asset_output"]:
                    asset_class = PublishProp.PublishPropClass(self.asset_info, self.lock_geo)
                    return asset_class.runPublish()

            if self.asset_info["asset_type"] == "Setdress":
                import PublishSetdress
                self.asset_info["asset_output"] = self.GetOutputTypes()
                if self.asset_info["asset_output"]:
                    asset_class = PublishSetdress.PublishSetdressClass(self.asset_info, self.lock_geo)
                    return asset_class.runPublish()
            if self.asset_info["asset_type"] == "Set":
                import PublishSet
                self.asset_info["asset_output"] = self.GetOutputTypes()
                if self.asset_info["asset_output"]:
                    asset_class = PublishSet.PublishSetClass(self.asset_info, self.lock_geo)
                    return asset_class.runPublish()
            if self.asset_info["asset_type"] == "Char":
                import PublishChar
                self.asset_info["asset_output"] = self.GetOutputTypes()
                print(self.asset_info["asset_output"])
                if self.asset_info["asset_output"]:
                    asset_class = PublishChar.PublishCharClass(self.asset_info, self.lock_geo)
                    return asset_class.runPublish()
            if self.asset_info["asset_type"] == "RigModule":
                import PublishRigModule
                self.asset_info["asset_output"] = self.GetOutputTypes()
                print("Output_list=%s" % self.asset_info["asset_output"])
                if self.asset_info["asset_output"]:
                    asset_class = PublishRigModule.PublishRigModule(self.asset_info, self.lock_geo)
                    return asset_class.runPublish()
            if self.asset_info["asset_type"] == "FX":
                import PublishFX
                self.asset_info["asset_output"] = self.GetOutputTypes()
                if self.asset_info["asset_output"]:
                    asset_class = PublishFX.PublishFXClass(self.asset_info, self.lock_geo)
                    return asset_class.runPublish()

    def GetOutputTypes(self):
        try:
            # outputs = cfg.ref_steps[self.asset_info["asset_type"]][self.asset_info["asset_step"]]
            return CC.ref_steps[self.asset_info["asset_type"]][self.asset_info["asset_step"]]
        except KeyError:
            print("Wrong asset step(%s) for that type of asset(%s)!" % (
            self.asset_info["asset_step"], self.asset_info["asset_type"]))
            return False


class BasePublishClass:
    """
    asset_info = a dict that contains keys that hold the asset id, such as:
        asset_name,
        asset_category,
        asset_type,
        asset_step
    """

    def __init__(self, asset_info={}, lock_geo=False):
        # if logger:
        #     logger = getLogger(str(self.__class__).split(".")[-1].replace("'>", ""), console_level=logging.DEBUG)
        # else:
        #     logger = getLogger(str(self.__class__).split(".")[-1].replace("'>", ""))
        logger.info("Initializing")
        self.lock_geo = lock_geo
        self.asset_info = asset_info
        self.asset_work_file = CC.get_asset_work_file(**self.asset_info)

    def runPublish(self):
        did_it_publish = True
        output_list = self.asset_info["asset_output"]
        logger.info("Publishing: asset_dict=" + str(self.asset_info) + ", output_list=" + str(output_list))
        for c_out in output_list:  # Go over each output needed when publishing and run the steps needed.
            logger.info("****Currently handling: " + c_out)
            self.asset_info["asset_output"] = c_out
            # TODO Find output paths smarter than making use of getattr
            self.output_file_function = getattr(CC, "get_{asset_output}".format(
                asset_output=self.asset_info["asset_output"]))
            self.output_file = self.output_file_function(**self.asset_info)

            file_util.OpenFile(cur_file=self.asset_work_file, compare_path=True)
            temp_path = file_util.SaveTempFile()
            if temp_path:
                did_it_publish = self.PublishSteps()
                try:
                    os.remove(temp_path)
                    logger.info("********Temporary path removed")
                except:
                    logger.warning("********Couldn't remove temporary path: " + temp_path)
                if not did_it_publish:
                    logger.critical("************The element ( " + c_out + " ) did not publish correctly")
                    break
        if did_it_publish:
            logger.info("Publish of ( " + self.asset_info["asset_name"] + " ) complete")
            return True
        else:
            logger.info("Publish of ( " + self.asset_info["asset_name"] + " ) cancelled")
            return False


    def PublishSteps(self):
        """
        Replace this function with the steps needed for each output type possible for the type of asset.
        :return: True or False, depending on if the publish was succesfull
        """
        print("Attempting to publish: %s" % self.asset_info["asset_output"])
        return True
