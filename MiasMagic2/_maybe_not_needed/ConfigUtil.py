###################################################################
############### Config path/Asset functions #######################
###################################################################

import re
import os

class ConfigUtilClass():
    def __init__(self,base_config=None):
        self.base_config = base_config
        self.temp_dict = {}
        self.class_file = "%s/ConfigClass_%s.py" % (os.path.dirname(os.path.realpath(__file__)),self.base_config.project_name)
        self.checkForClassFile()


    # def addToTempDict(self,add={}):
    #    self.temp_dict.update({k:v for k,v in add.items() if v is not None})
    def checkForClassFile(self):
        if not os.path.exists(self.class_file):
            self.CreateConfigClassFile()

    def updateConfigClass(self):
        self.CreateConfigClassFile()

    def returnProjectPaths(self):
        return self.base_config.project_paths

    def CreatePathFromDict_RE(self,cur_string="", path_dict={}):
        path_dict = path_dict.copy()
        path_dict.update(self.base_config.project_paths)
        # new_dict = cfg.project_paths.copy()
        # new_dict.update({k: v for k, v in path_dict.items() if v is not None})
        cur_string = self.RecursiveTest(cur_string,path_dict)
        return cur_string

    def RecursiveTest(self,cur_string,cur_dict):
        cur_tags = re.findall(r'\<(.*?)\>',cur_string)
        for cur_tag in cur_tags:
            re_tag = re.compile("<{0}>".format(cur_tag))
            if cur_tag in cur_dict.keys():
                cur_string = re.sub(re_tag,cur_dict[cur_tag],cur_string)
            else:
                print("No Key: %s" % cur_tag)
        if cur_tags:
            return self.RecursiveTest(cur_string,cur_dict)
        else:
            return cur_string

    def ComparePartOfPath(self,scene_path, compare_path, info_dict={}): #Used for splitting a scene path up, and getting asset info from there. NOT WELL DONE :/
        # print("COMPARING: %s to %s" % (scene_path, compare_path))
        # info_dict.update(cfg.project_paths)
        if not len(scene_path.split("/")) == len(compare_path.split("/")):  # check if the two paths are able to be compared
            print("Not equal paths: %s and %s " % (scene_path, compare_path))
            return False
        if "." in scene_path:  # remove the extension
            scene_path = scene_path.split(".")[0]
            if "." in compare_path:
                compare_path = compare_path.split(".")[0]
        if "<" in compare_path:
            for parts in compare_path.split("<"):
                if not parts == "":
                    if ">" in parts:
                        parts_split = parts.split(">")
                        cur_key = parts_split[0]
                        after = parts_split[1]
                        if after == "":
                            #print("AFTER: %s" % scene_path)
                            cur_value = scene_path
                            info_dict[cur_key] = cur_value
                        else:
                            # print("ComparePartOfPath","From %s: %s : %s" % (scene_path,cur_key, scene_path.split(after)[0]))
                            cur_value = scene_path.split(after)[0]
                            info_dict[cur_key] = cur_value
                            scene_path = after.join(scene_path.split(after)[1:])
                    else:
                        print("path: %s - parts: %s" % (scene_path,parts))
                        scene_path = scene_path.split(parts)[1]
        return info_dict


    def ReturnUnknownKeys(self, config_key,path_dict={}):
        update_dict = self.base_config.project_paths.copy()
        update_dict.update({k:v for k,v in path_dict.items() if v is not None})
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

    def CreateDictFromAssetPath(self, path, cfg):
        dict = {}
        if cfg.project_paths['base_path'] in path:
            cfg_util = ConfigUtilClass(cfg)
            dict["base_path"] = cfg.project_paths['base_path']

            if cfg_util.CreatePathFromDict(cfg.project_paths['asset_top_path'], dict) in path:
                dict['asset_top_path'] = cfg_util.CreatePathFromDict(cfg.project_paths['asset_top_path'], dict)

                values = path.replace(dict['asset_top_path'], '').split('/')
                while '' in values:
                    values.remove('')

                string = cfg.project_paths['asset_base_path']
                for item in ['<asset_top_path>/', '<', '>']:
                    string = string.replace(item, '')
                keys = string.split('/')

                for i, key in enumerate(keys):
                    dict[key] = values[i]

            for key in cfg.project_paths:
                if key not in dict:
                    project_path = cfg_util.CreatePathFromDict(cfg.project_paths[key], dict)
                    if '<' not in project_path:
                        dict[key] = project_path

        else:
            print('Not part of ' + cfg.project_name)

        return dict


    def CreatePathFromDict(self,cur_string, path_dict={}):  # TODO could make this regex and see how much faster it is?

        # print("dict: %s for %s" % (path_dict,cur_string))
        # path_dict = path_dict.copy()
        # path_dict.update(cfg.project_paths)
        update_dict = self.base_config.project_paths.copy()
        update_dict.update({k:v for k,v in path_dict.items() if v is not None})

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
            path_dict = None #clean up?
            return create_path
        else:
            path_dict = None #clean up?
            return cur_string

    def CreateClassAttributeString(self,cur_dict):
        cur_string = ""
        for cur_key in cur_dict:
            cur_string = '%sself.%s="%s"\n        ' %(cur_string,cur_key,cur_dict[cur_key])
        return cur_string

    def CreateConfigClassFile(self):
        project_path_attributes = self.CreateClassAttributeString(self.base_config.project_paths)
        ref_path_attributes = self.CreateClassAttributeString(self.base_config.ref_paths)
        class_string = """
class ConfigClass():
    def __init__(self):
        self.project_name="{project_name}"
        {class_attributes}
        {ref_path_attributes}\n""".format(project_name=self.base_config.project_name, class_attributes=project_path_attributes,ref_path_attributes=ref_path_attributes)
        function_project_paths = self.CreateConfigClassFunctionsWithoutUtil(self.base_config.project_paths)
        function_refs_paths = self.CreateConfigClassFunctionsWithoutUtil(self.base_config.ref_paths)
        function_thumb_paths = self.CreateConfigClassFunctionsWithoutUtil(self.base_config.thumbnail_paths)
        # dir_path = os.path.dirname(os.path.realpath(__file__))
        # my_file_path = "%s/Test_class.py" % dir_path
        # while(open(self.class_file))
        with open(self.class_file, 'w+') as saveFile:
            saveFile.write(class_string+function_project_paths+function_refs_paths+function_thumb_paths)
        saveFile.close()
        # f = open(my_file_path, "w")
        # f.write(class_string+function_project_paths+function_refs_paths)
        # f.close()


    def CreateConfigClassFunctions(self,cur_dict):#OLD - Uses Config_Util functions
        function_string = ""
        for p_key in cur_dict:
            function_name = p_key
            kwords = self.ReturnUnknownKeys(p_key,cur_dict)
            full_string = self.CreatePathFromDict(cur_dict[p_key],cur_dict)
            kwarg_str = ""
            kw_dict = "{"
            if_string = ""
            if kwords:
                for kw in kwords:
                    kwarg_str = kwarg_str + "%s=None," % kw
                    kw_dict = kw_dict + '"%s":%s,' % (kw,kw)
                    if_string = if_string + '        if {kw}==None:\n            raise NameError("Argument Missing: {kw}")\n'.format(kw=kw)

                kw_dict = "%s}" % kw_dict[0:-1]
                function_string = function_string +"""
    def get_{function_name}(self,{kwarg_str}):
        func_dict = {kw_dict}
{if_string}
        to_return = cfg_util.CreatePathFromDict("{k_out}",func_dict)
        return to_return\n\n""".format(function_name=function_name, kwarg_str=kwarg_str,kw_dict=kw_dict,if_string=if_string,k_out=full_string)
            else:
                function_string = function_string + """
    def get_{function_name}(self):
        to_return = cfg_util.CreatePathFromDict("{k_out}")
        return to_return\n\n""".format(function_name=function_name,k_out=full_string)
        return function_string

    def PathToFormatStyle(self, cur_string):
        cur_string = cur_string.replace("<", "{")
        cur_string = cur_string.replace(">","}")
        return cur_string

    def CreateConfigClassFunctionsWithoutUtil(self, cur_dict):
        function_string = ""
        for p_key in cur_dict:
            function_name = p_key
            kwords = self.ReturnUnknownKeys(p_key, cur_dict)
            full_string = self.CreatePathFromDict(cur_dict[p_key], cur_dict)
            kw_format_string = '"%s".format(' % self.PathToFormatStyle(full_string)
            kwarg_str = ""
            if_string = ""
            if kwords:
                for kw in kwords:
                    kwarg_str = kwarg_str + "%s=None," % kw
                    kw_format_string = "%s%s=%s," % (kw_format_string,kw,kw)
                    if_string = if_string + '        if {kw}==None:\n            raise NameError("Argument Missing: {kw}")\n'.format(
                        kw=kw)
                kw_format_string = "%s)" % kw_format_string
                function_string = function_string + """
    def get_{function_name}(self,{kwarg_str}):
{if_string}
        to_return = {kw_format_string}
        return to_return\n\n""".format(function_name=function_name, kwarg_str=kwarg_str, kw_format_string=kw_format_string,
                                       if_string=if_string, k_out=full_string)
            else:
                function_string = function_string + """
    def get_{function_name}(self):
        to_return = "{k_out}"
        return to_return\n\n""".format(function_name=function_name, k_out=full_string)
        return function_string



if __name__ == "__main__":
    import Config_KiwiStrit3 as cfg
    CU = ConfigUtilClass(cfg)
    CU.updateConfigClass()
# missing_dict = {}
# for cur in CU.base_config.project_paths.keys():
#     missing_keys = CU.ReturnUnknownKeys(cur)
#     if missing_keys:
#         missing_dict[cur] = missing_keys
# print(missing_dict)
# print(CU.ReturnUnknownKeys("shot_anim_path"))
