
###################################################################
############### Config path/Asset functions #######################
###################################################################

import re
import os

from Log.CoboLoggers import getLogger

logger = getLogger()

import json


def loadSettings(load_file):
    if os.path.isfile(load_file):
        with open(load_file, 'r') as cur_file:
            return json.load(cur_file)
    else:
        return {}


class JsonConfigUtilClass():
    def __init__(self, base_config=None):
        self.json_file = base_config
        self.base_config = loadSettings(base_config)
        self.class_file = "%s/ConfigClasses/ConfigClass_%s.py" % (os.path.dirname(os.path.realpath(__file__)), self.base_config["project_name"])
        # self.checkForClassFile()

    # def addToTempDict(self,add={}):
    #    self.temp_dict.update({k:v for k,v in add.items() if v is not None})

    # def checkForClassFile(self):
    #     if not os.path.exists(self.class_file):
    #         self.Build_ConfigClassFile()
    #
    def updateConfigClass(self,check=False):
        if check and os.path.exists(self.class_file):
            logger.info("Check and Found: %s" % self.json_file)
            return True
        from Configs import ConfigClassBuilder
        cfg_build = ConfigClassBuilder.Builder(self.json_file)
        cfg_build.Build_ConfigClassFile()
        return True

    def returnProjectPaths(self):
        return self.base_config["project_paths"]

    def CreatePathFromDict_RE(self, cur_string="", path_dict={}):
        path_dict = path_dict.copy()
        path_dict.update(self.base_config["project_paths"])
        # new_dict = cfg.project_paths.copy()
        # new_dict.update({k: v for k, v in path_dict.items() if v is not None})
        cur_string = self.RecursiveTest(cur_string, path_dict)
        return cur_string

    def RecursiveTest(self, cur_string, cur_dict):
        cur_tags = re.findall(r'\<(.*?)\>', cur_string)
        for cur_tag in cur_tags:
            re_tag = re.compile("<{0}>".format(cur_tag))
            if cur_tag in cur_dict.keys():
                cur_string = re.sub(re_tag, cur_dict[cur_tag], cur_string)
            else:
                print("No Key: %s" % cur_tag)
        if cur_tags:
            return self.RecursiveTest(cur_string, cur_dict)
        else:
            return cur_string

    def replacePathByKeys(self, scene_path, compare_path, replace_dict={}, replace=True):
        # Used for splitting a scene path up, and getting asset info from there. NOT WELL DONE :/
        """
        this is meant to take a file/folder path, a config-path to compare and find keys from, and a dict with asset-info,
        and then try to return a path where the keys related to the config string has been replace in the actual string.
        :return:
        """
        if not len(scene_path.split("/")) == len(
                compare_path.split("/")):  # check if the two paths are able to be compared
            print("Warning: Not equal paths. Errors can occur.\nComparing: %s and %s " % (scene_path, compare_path))
            # return False
        scene_path_dict = {}  # this is where we place the asset keys we find in the scene path.
        if "." in scene_path:  # remove the extension
            scene_path = scene_path.split(".")[0]
        if "." in compare_path:
            compare_path = compare_path.split(".")[0]
        else:  # compare_path.endswith("/"):
            compare_path = compare_path + "/"

        build_path = ""  # the string we turn into our new path, by replacing keys from dict.
        """
        go through compare_path and split it up by keys (<>) and then remove the part before the keys from
        the scene path, so scene path is always just the "unworked" end of the string
        """
        if "<" in compare_path:
            for parts in compare_path.split("<"):
                if not parts == "":
                    if ">" in parts:  # check if the first part of the path is
                        parts_split = parts.split(">")
                        cur_key = parts_split[0]
                        after = parts_split[1]
                        print("SCENE:PATH %s" % scene_path)
                        if not after == "":
                            # print("ComparePartOfPath","From %s: %s : %s" % (scene_path,cur_key, scene_path.split(after)[0]))
                            cur_value = scene_path.split(after)[0]
                            print("Cur Value: %s" % cur_value)
                            print("Cur Key: %s" % cur_key)
                            if cur_key in scene_path_dict.keys():
                                print("Already found: %s" % cur_key)
                                if not scene_path_dict[cur_key] == cur_value:
                                    print("ERROR same key with different values: key:%s Values %s->%s" % (
                                        cur_keOky, scene_path_dict[cur_key], cur_value))
                            scene_path_dict[cur_key] = cur_value

                            if cur_key in replace_dict.keys():
                                build_path = build_path + replace_dict[cur_key] + after
                            else:
                                build_path = build_path + cur_value
                            scene_path = after.join(scene_path.split(after)[1:])
                        else:
                            print("AFTER: %s" % scene_path)
                            cur_value = scene_path
                            scene_path_dict[cur_key] = cur_value
                            build_path = build_path + scene_path
                    else:
                        # The first part of the path, base path and so on.
                        # print("path: %s - parts: %s" % (scene_path,parts))
                        # print(scene_path.split(parts))
                        build_path = build_path + parts
                        scene_path = scene_path.split(parts)[1]
        if scene_path:
            if replace:  # Try to replace by keys from info-dict and replace-dict:
                print("Trying to replace in %s with keys from %s" % (scene_path, replace_dict))
                for r_key in scene_path_dict.keys():
                    if r_key in replace_dict.keys():
                        scene_path = scene_path.replace(scene_path_dict[r_key], replace_dict[r_key])
            build_path = build_path + scene_path
        return build_path, scene_path_dict

    def ComparePartOfPath(self, scene_path, compare_path, info_dict={}):
        # Used for splitting a scene path up, and getting asset info from there. NOT WELL DONE :/
        # print("COMPARING: %s to %s" % (scene_path, compare_path))
        # info_dict.update(cfg.project_paths)

        if not info_dict:
            info_dict = {}
        else:
            logger.debug("ComparePartOfPath: info dict given: %s" % info_dict)

        if not len(scene_path.split("/")) == len(
                compare_path.split("/")):  # check if the two paths are able to be compared
            logger.debug("Not equal paths. Errors can occur. Comparing: %s and %s " % (scene_path, compare_path))
            # return False
        if "." in scene_path:  # remove the extension
            scene_path = scene_path.split(".")[0]
            if "." in compare_path:
                compare_path = compare_path.split(".")[0]
        if "<" in compare_path:
            try:
                for parts in compare_path.split("<"):
                    if not parts == "":
                        if ">" in parts:
                            parts_split = parts.split(">")
                            cur_key = parts_split[0]
                            after = parts_split[1]
                            if after == "":
                                # print("AFTER: %s" % scene_path)
                                cur_value = scene_path
                                info_dict[cur_key] = cur_value
                            else:
                                # print("ComparePartOfPath","From %s: %s : %s" % (scene_path,cur_key, scene_path.split(after)[0]))
                                cur_value = scene_path.split(after)[0]
                                info_dict[cur_key] = cur_value
                                scene_path = after.join(scene_path.split(after)[1:])
                        else:
                            # print("path: %s - parts: %s" % (scene_path, parts))
                            # print(scene_path.split(parts))
                            scene_path = scene_path.split(parts)[1]
            except IndexError as e:
                logger.debug(e)
                logger.debug("Had exception, returning False")
                return False
        logger.debug("Finished with %s" % compare_path)
        return info_dict

    def ReturnUnknownKeys(self, config_key, path_dict={}):
        update_dict = self.base_config["project_paths"].copy()
        update_dict.update({k: v for k, v in path_dict.items() if v is not None})
        return_keys = []
        if config_key in update_dict:
            cur_string = update_dict[config_key]
            cur_string = self.CreatePathFromDict(cur_string, update_dict)
            if "<" in cur_string:
                for parts in cur_string.split("<"):  # Split up string in with start of VAR <
                    if ">" in parts:  # If start part skip
                        cur_key = parts.split(">")[0]
                        if not cur_key in return_keys:
                            return_keys.append(cur_key)
                return return_keys

            else:
                return None

    def GetBasePath(self, path, split_with_path):
        base_path = self.base_config["project_paths"]["base_path"]
        if base_path in path:
            return base_path
        else:
            if base_path in split_with_path:
                splitter = split_with_path.split(base_path)[-1]
                if splitter in path:
                    new_base_path = path.split(splitter)[0]
                    return new_base_path
            if "<base_path>" in split_with_path:
                splitter = split_with_path.split("<base_path>")[-1]
                if splitter in path:
                    new_base_path = path.split(splitter)[0]
                    return new_base_path
            return None

    def CreateDictFromAssetPath(self, path, cfg):
        _dict = {}
        if cfg.project_paths['base_path'] in path:
            cfg_util = JsonConfigUtilClass(cfg)
            _dict["base_path"] = cfg.project_paths['base_path']

            if cfg_util.CreatePathFromDict(cfg.project_paths['asset_top_path'], _dict) in path:
                _dict['asset_top_path'] = cfg_util.CreatePathFromDict(cfg.project_paths['asset_top_path'], _dict)

                values = path.replace(_dict['asset_top_path'], '').split('/')
                while '' in values:
                    values.remove('')
                # values = all the folders after asset_top_path in the given path
                string = cfg.project_paths['asset_base_path']
                for item in ['<asset_top_path>/', '<', '>']:
                    string = string.replace(item, '')
                keys = string.split('/')
                # keys = all the folders with key-names after asset_top_path in the config_path

                for i, key in enumerate(keys):
                    _dict[key] = values[i]

            for key in cfg.project_paths:
                if key not in _dict:
                    project_path = cfg_util.CreatePathFromDict(cfg.project_paths[key], _dict)
                    if '<' not in project_path:
                        _dict[key] = project_path

        else:
            print('Not part of ' + cfg.project_name)

        return _dict

    def CreatePathFromDict(self, cur_string, path_dict={}):  # TODO could make this regex and see how much faster it is?

        # print("dict: %s for %s" % (path_dict,cur_string))
        # path_dict = path_dict.copy()
        # path_dict.update(cfg.project_paths)
        update_dict = self.base_config["project_paths"].copy()
        update_dict.update({k: v for k, v in path_dict.items() if v is not None})

        if "<" in cur_string:
            create_path = ""
            for parts in cur_string.split("<"):  # Split up string in with start of VAR <
                if ">" in parts:  # If start part skip
                    cur_key = parts.split(">")[0]
                    if cur_key in update_dict:
                        cur_var = update_dict[cur_key]
                        if not cur_var == "":
                            cur_var = self.CreatePathFromDict(cur_var, update_dict)
                        else:
                            cur_var = "<%s>" % parts.split(">")[0]
                        create_path = "%s%s%s" % (create_path, cur_var, parts.split(">")[1])
                    else:
                        create_path = "%s<%s" % (create_path, parts)
                else:
                    create_path = "%s%s" % (create_path, parts)
            path_dict = None  # clean up?
            return create_path
        else:
            path_dict = None  # clean up?
            return cur_string

    def loadSettings(self, load_file):
        if os.path.isfile(load_file):
            with open(load_file, 'r') as cur_file:
                return json.load(cur_file)
        else:
            return {}

    def saveSettings(self, save_location, save_content):
        with open(save_location, 'w+') as saveFile:
            json.dump(obj=save_content, fp=saveFile,indent=4, sort_keys=True)
        saveFile.close()

if __name__ == "__main__":
    # import Configs.Config_MiasMagic2 as cfg
    pass

