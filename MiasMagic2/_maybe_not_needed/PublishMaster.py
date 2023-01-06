# import ProjectConfig as cfg
import UtilFunctions as UF

import Config_MiaMagic2 as cfg


class ReadyPublish():
    def __init__(self,asset_info={},extra={"currently_open_file":False,"LockGeo":True}):
        self.UF = UF.PublishFunctions()
        self.extra = extra
        try:
            if asset_info:
                self.asset_info = asset_info
            else:
                print("Getting info from file")
                self.asset_info = self.UF.GetAssetInfoFromFile()
            self.CheckPublish()
            #TODO Need a check against what maya file is open.

            if False in self.issue_dict.values():
                print(self.issue_dict)
                print("PROBLEM FOUND!")
        except RuntimeError as e:
            print("What?=??")
            # print(self.UF.ReturnDumpInfo()) #doesn't print. Don't know why.
            print(e)

    def CheckPublish(self):
        self.issue_dict = {}
        if self.asset_info:
            if self.asset_info["asset_type"] == "Prop" or self.asset_info["asset_type"] == "Set":
                print("Prop")
                self.issue_dict["PublishSet"] = self.UF.CheckPublishSet()
            if self.asset_info["asset_type"] == "Setdress":
                print("Setdress")
                self.issue_dict["ProxyGroups"] = self.UF.CheckSetdressScene()
        else:
            self.issue_dict["asset_info"] = False
        return self.issue_dict


    def StartPublish(self):
        if self.asset_info:
            if self.asset_info["asset_type"] == "Prop":
                from PublishAssets import PublishProp
                self.asset_info["asset_output"] = self.GetOutputTypes()
                if self.asset_info["asset_output"]:
                    PublishProp.PublishPropClass(self.asset_info, self.extra)
            if self.asset_info["asset_type"].lower() == "Setdress".lower():
                print("Look at me I'm a setdress")
                from PublishAssets import PublishSetdress
                self.asset_info["asset_output"] = self.GetOutputTypes()
                if self.asset_info["asset_output"]:
                    PublishSetdress.PublishSetdressClass(self.asset_info, self.extra)
            if self.asset_info["asset_type"] == "Set":
                from PublishAssets import PublishSet
                self.asset_info["asset_output"] = self.GetOutputTypes()
                if self.asset_info["asset_output"]:
                    PublishSet.PublishSetClass(self.asset_info, self.extra)
            if self.asset_info["asset_type"] == "Char":
                from PublishAssets import PublishChar
                self.asset_info["asset_output"] = self.GetOutputTypes()
                print(self.asset_info["asset_output"])
                if self.asset_info["asset_output"]:
                    PublishChar.PublishCharClass(self.asset_info, self.extra)


    def GetOutputTypes(self):
        try:
            # outputs = cfg.ref_steps[self.asset_info["asset_type"]][self.asset_info["asset_step"]]
            return cfg.ref_steps[self.asset_info["asset_type"]][self.asset_info["asset_step"]]
        except KeyError:
            print("Wrong asset step(%s) for that type of asset(%s)!" % (self.asset_info["asset_step"],self.asset_info["asset_type"]))
            return False
