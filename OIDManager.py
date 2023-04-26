

try:
    from PySide2 import QtWidgets, QtCore, QtGui
    import maya.cmds as cmds
    in_maya = True
except:
    from PySide2 import QtWidgets, QtCore, QtGui
    in_maya = False
# import json
import file_util
import os
import shutil

from getConfig import getConfigClass
CC = getConfigClass()

class MainWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        pass

    def CreateWindow(self):
        pass

class OID_Functions(object):
    def __init__(self):
        super(OID_Functions, self).__init__()
        # if not CC.OD_set_rules == "":
        self.save_dict_file = CC.get_OID_set_rules() #cfg_util.CreatePathFromDict(cfg.project_paths["OID_set_rules"])
        # self.rule_rep = self.LoadSettings(self.save_dict_file)
        self.rule_rep = file_util.load_json(self.save_dict_file)
        self.info_dict = {}
        # self.SetAssetDictFromScene()
        # self.rule_rep = {}

    def SetAssetDictFromScene(self):
        self.info_dict = {}
        scene_path = cmds.file(q=True, sn=True)
        if scene_path:
            light_scene = CC.get_shot_light_file() #cfg_util.CreatePathFromDict(cfg.project_paths["shot_light_file"])
            self.info_dict = CC.util.ComparePartOfPath(os.path.split(scene_path)[0], os.path.split(light_scene)[0],self.info_dict)
            print(self.info_dict)
            if not self.info_dict:
                print("Not a Light Scene. Not making OID sets")
                return False
            return True



    def SaveDict(self):
        # self.rule_rep = {"E14": {"24": ["BiggestTreeA", "LadderA"]}, "E26_SQ020": {"25": ["LadderA", "BathTubA"]}}
        file_path = self.save_dict_file
        #Make a save of the old cache just in case:
        f_folder,f_file = os.path.split(file_path)
        if not os.path.exists(f_folder):
            os.mkdir(f_folder)
        if os.path.exists(file_path):
            history_folder = "%s/_History" % f_folder
            if not os.path.exists(history_folder):
                os.mkdir(history_folder)
            v_num = 0
            for content in os.listdir(history_folder):
                if "%s_V" % f_file.split(".")[0] in content:
                    cur_num = int(content.split("%s_V" % f_file.split(".")[0])[1].split(".")[0])
                    if cur_num > v_num:
                        v_num = cur_num
            v_num = '%03d' % (v_num + 1)
            shutil.move(file_path,"%s/%s_V%s.%s" % (history_folder,f_file.split(".")[0],v_num,f_file.split(".")[1]))

        # self.SaveSettings(self.save_dict_file, self.rule_rep)
        file_util.save_json(self.save_dict_file, self.rule_rep)

    def AddRule(self, temp_rule_dict,replace=False):
        print("Adding:\n%s\nTO\n%s" % (temp_rule_dict,self.rule_rep))
        if not self.rule_rep:
            self.rule_rep = temp_rule_dict
            return
        self.merge(self.rule_rep,temp_rule_dict,update=replace)

    def merge(self,a, b, path=None, update=True):
        "http://stackoverflow.com/questions/7204805/python-dictionaries-of-dictionaries-merge"
        "merges b into a"
        if path is None: path = []
        for key in b:
            if key in a:
                if isinstance(a[key], dict) and isinstance(b[key], dict):
                    self.merge(a[key], b[key], path + [str(key)], update=update)
                elif a[key] == b[key]:
                    pass  # same leaf value
                elif isinstance(a[key], list) and isinstance(b[key], list):
                    if update:
                        a[key] = b[key]
                    else:
                        a[key] = list(set(a[key] + b[key]))
                    # for idx, val in enumerate(b[key]):
                    #     a[key][idx] = self.merge(a[key][idx], b[key][idx], path + [str(key), str(idx)], update=update)
                elif update:
                    a[key] = b[key]
                else:
                    raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
            else:
                a[key] = b[key]
        print("FINAL FINAL: %s" % a)
        return a

    def RunKeysThroughDict(self, c_key):
        if c_key in self.rule_rep:
            for cur_oid in sorted(self.rule_rep[c_key]):
                for c_obj in self.rule_rep[c_key][cur_oid]:
                    for oid_key in self.object_oid_list.keys():
                        if c_obj in self.object_oid_list[oid_key]:
                            self.object_oid_list[oid_key].remove(c_obj)
                if not cur_oid in self.object_oid_list.keys():
                    self.object_oid_list[cur_oid] = self.rule_rep[c_key][cur_oid]
                else:
                    self.object_oid_list[cur_oid].extend(self.rule_rep[c_key][cur_oid])

    def DefineObjectsForScene(self):
        print("Rules: %s" % self.rule_rep)
        self.object_oid_list = {}

        ep_key = self.info_dict["episode_name"]
        sq_key = "%s_%s" % (self.info_dict["episode_name"], self.info_dict["seq_name"])
        shot_key = "%s_%s" % (sq_key, self.info_dict["shot_name"])

        self.RunKeysThroughDict(ep_key)
        self.RunKeysThroughDict(sq_key)
        self.RunKeysThroughDict(shot_key)
        print("For %s OIDs should be: %s" % (shot_key,self.object_oid_list))
        self.CreateSetFromKey()

    def CreateSetFromKey(self):
        import Maya_Functions.asset_util_functions as asset_util
        import Maya_Functions.set_util_functions as set_util
        for c_OID in self.object_oid_list.keys():
            if self.object_oid_list[c_OID]:
                scene_objects = asset_util.FindRootByName(self.object_oid_list[c_OID])
                if scene_objects:
                    set_util.CreateOIDSet(object_list=scene_objects,set_name="SpecialOID%s" % c_OID, OID=int(c_OID))

    def CreateRulesFromPublishData(self,scope=None,shot_list=None):
        OID_start_range = 29
        flat_list = []
        for v in shot_list.values():
            flat_list.extend(v)
        used_props = set(flat_list)
        counted = dict((i, flat_list.count(i)) for i in used_props)
        most_use_list = list(reversed(sorted(counted.items(), key=lambda x: x[1])))
        final_dict = {scope:{}}
        for n in range(0,len(most_use_list)):
            n_k =n+OID_start_range
            el = most_use_list[n][0]
            final_dict[scope][n_k]=[el]
        print("NEW RULE: %s" % final_dict)
        self.AddRule(final_dict)
        self.SaveDict()

    def CreateSmartRulesFromPublishData(self,scope=None,shot_list=None):
        list_of_sets = []
        for cur_shot in shot_list.values():
            list_of_sets.append(set(cur_shot))
        # all_assets = set()
        # for v in shot_list.values():
        #     all_assets |= set(v)
        flat_list = []
        for v in shot_list.values():
            flat_list.extend(v)
        all_assets = set(flat_list)

        # Make a dict of all the props in order of the most used one.
        counted = dict((i, flat_list.count(i)) for i in all_assets)
        most_use_list = list(reversed(sorted(counted.items(), key=lambda x: x[1])))

        # Make a dict of asset as keys, with a value thats a list of all other assets they don't share shots with.
        final_dict = {}
        for asset in all_assets:
            asset_set = {asset}
            for shot_set in list_of_sets:
                if asset in shot_set:
                    asset_set |= shot_set
            result = all_assets.difference(asset_set)
            final_dict[asset] = result

        # Go through and eliminate all the re-occurences of the assets, in lists.
        final_list = []
        clean_dict = final_dict.copy()
        ignore_list = []

        for k, v in most_use_list:
            if not k in ignore_list:
                temp_list = [k]
                clean_dict, ignore_list = self.updateCleanDict(clean_dict, k, ignore_list)
                loop_list = []  # list(temp_dict[k])
                for in_p, in_u in most_use_list:
                    if in_p in clean_dict[k]:
                        loop_list.append(in_p)
                for i, asset in enumerate(loop_list):
                    if not asset in ignore_list:
                        clear = True
                        for item in temp_list[1:]:
                            if asset in final_dict[item]:
                                clear = False
                        if clear:
                            temp_list.append(asset)
                            clean_dict, ignore_list = self.updateCleanDict(clean_dict, asset, ignore_list)
                print(temp_list)
                final_list.append(temp_list)
        OID_start_range = 29
        final_dict = {scope: {}}
        for n in range(0,len(final_list)):
            n_k =str(n+OID_start_range)
            # el = most_use_list[n][0]
            final_dict[scope][n_k]=final_list[n]
        print("NEW RULE: %s" % final_dict)
        self.AddRule(final_dict)
        self.SaveDict()

    def updateCleanDict(self,dictionary, key, ignore_list):
        ignore_list.append(key)

        for k, v in dictionary.items():
            if not k in ignore_list:
                dictionary[k] -= set(key)
                # print("remove %s from %s" %(key,v))
        return dictionary, ignore_list

    # def SaveSettings(self, save_location, save_info):
    #     with open(save_location, 'w+') as saveFile:
    #         json.dump(obj=save_info, fp=saveFile,indent=4, sort_keys=True)
    #     saveFile.close()

    # def LoadSettings(self, save_location):
    #     if os.path.isfile(save_location):
    #         with open(save_location, 'r') as saveFile:
    #             loadedSettings = json.load(saveFile)

    #         # if 'selected node' in loadedSettings.keys():
    #         if loadedSettings:
    #             return loadedSettings
    #     else:
    #         print("not a file")
    #     return None


def _maya_main_window():
    """Return Maya's main window"""
    for obj in QtWidgets.QApplication.topLevelWidgets():
        if obj.objectName() == 'MayaWindow':
            return obj
    raise RuntimeError('Could not find MayaWindow instance')


# def Run():
#     mainWin = MainWindow(parent=_maya_main_window())
#     # mainWin.resize(500, 500)
#     # mainWin.show()
#     # mainWin.raise_()


if not in_maya:
    if __name__ == '__main__':
        import sys
        if not QtWidgets.QApplication.instance():
            app = QtWidgets.QApplication(sys.argv)
        else:
            app = QtWidgets.QApplication.instance()
        mainWin = OID_Functions()
        mainWin.CreateRulesFromPublishData()
        # mainWin.DefineObjectsForScene()
        # mainWin.AddRule({"E14":{"24":["BinocularsA"]}})
        # mainWin.SaveDict()
        # mainWin.DefineObjectsForScene()
        # mainWin.SaveDict()
        # mainWin.resize(584, 662)
        # mainWin.show()
        sys.exit(app.exec_())
