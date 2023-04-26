import re
import os

from Log.CoboLoggers import getLogger
logger = getLogger()
# import json
import file_util

class Builder():
    def __init__(self, json_config_file=None):
        # self.base_config = loadSettings(json_config_file)
        self.base_config = file_util.load_json(json_config_file)
        print(json_config_file)
        if self.base_config:
            self.class_file = "%s/ConfigClasses/ConfigClass_%s.py" % (os.path.dirname(os.path.realpath(__file__)), self.base_config["project_name"])
        else:
            logger.critical("CONFIG %s NOT FOUND" % json_config_file)
        # self.CFG_UTIL = ConfigUtilClass(base_config)


    def CreatePathFromDict(self, cur_string, path_dict={}):
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

    def checkForClassFile(self):
        if not os.path.exists(self.class_file):
            self.Build_ConfigClassFile()

    #############################################################
    ################## CREATE CLASS BUILD FUNCTIONS #############
    #############################################################

    def Build_ClassAttributeString(self, cur_dict):
        cur_string = ""
        for cur_key in cur_dict:
            cur_string = '%sself.%s="%s"\n        ' % (cur_string, cur_key, cur_dict[cur_key])
        return cur_string

    def Build_ClassVariableString(self, cur_var):
        cur_string = ""
        for cur_key in cur_var:
            cur_string = '%sself.%s=%s\n        ' % (cur_string, cur_key, cur_var[cur_key])
        return cur_string

    def Build_OldConfigLoad(self):
        if self.base_config["old_project"]:
            old_string = """import getConfig
        self.old = getConfig.getConfigClass("{old_project}",False)
        self.util = getConfig.getJsonConfigUtil("{project}")""".format(project=self.base_config["project_name"],
                                                                   old_project=self.base_config["old_project"])
        else:
            old_string = """import getConfig
        self.old = None
        self.util = getConfig.getJsonConfigUtil("{project}")""".format(
                project=self.base_config["project_name"], old_project=self.base_config["old_project"])
        return old_string

    #     def CreateConfigUtilLoad(self):
    #         config_string = """import Config_{project_name} as cfg
    # {tab}import ConfigUtil
    # {tab}self.util : ConfigUtilClass = ConfigUtil.ConfigUtilClass(cfg)""".format(project_name=self.base_config.project_name,tab="        ")
    #         return config_string
    def Build_ClassAttribute(self,name,value):
        return 'self.%s=%s\n        ' % (name, value)
    def Build_CheckKeyBeforeBuild(self,func,check,args):
        if check in self.base_config.keys():
            return func(args)
        else:
            return ""
    def Build_ClassDict(self,name_key):
        """New and improved BuildClassVaribleString"""
        if name_key in self.base_config.keys():
            return self.Build_ClassVariableString({name_key:self.base_config[name_key]})
        else:
            return ""

    def Build_ConfigClassFile(self):
        """
        Builds the config file into a class with functions to find each key and to make it easier to get paths out.
        :return:
        """
        print(self.base_config)
        logger.info("Building ConfigClass(Json) for %s" % self.base_config["project_name"])
        project_path_attributes = self.Build_ClassAttributeString(self.base_config["project_paths"])
        ref_path_attributes = self.Build_ClassAttributeString(self.base_config["ref_paths"])
        regex_attributes = self.Build_ClassAttributeString(self.base_config["regex_strings"])
        env_var_attributes = self.Build_ClassAttribute("environment_vars",self.base_config["environment_vars"])
        local_env_var_attributes = self.Build_ClassAttribute("local_vars",self.base_config["local_vars"])
        user_attributes = self.Build_ClassVariableString({"users": self.base_config["users"]})
        style_attributes = self.Build_ClassVariableString({"project_style": self.base_config["project_style"]})
        old_class = self.Build_OldConfigLoad()
        ref_order = self.Build_ClassVariableString({"ref_order": self.base_config["ref_order"]})
        ref_steps = self.Build_ClassVariableString({"ref_steps": self.base_config["ref_steps"]})
        ref_paths_func = self.Build_getFunctionByKey("ref_paths", self.base_config["ref_paths"])
        project_settings = self.Build_ClassVariableString({"project_settings": self.base_config["project_settings"]})
        thumbnail_paths_func = self.Build_getFunctionByKey("thumbnail_paths", self.base_config["thumbnail_paths"])
        preview_dict = self.Build_ClassDict("preview_dict")
        get_user_func = self.Build_getUsers()


        class_string = """
from Log.CoboLoggers import getLogger
logger = getLogger()
class ConfigClass():
    def __init__(self):
        self.project_name="{project_name}"
        {class_attributes}
        {ref_path_attributes}
        {regex_attributes}
        {env_var_attributes}
        {local_env_var_attributes}
        {user_attributes}
        {ref_order}
        {ref_steps}
        {project_settings}
        {style_attributes}
        {preview_dict}
        {old_class}


    {ref_paths_func}
    {get_user_func}
    {thumbnail_paths_func}\n""".format(project_name=self.base_config["project_name"],
                                       class_attributes=project_path_attributes,
                                       ref_path_attributes=ref_path_attributes,
                                       regex_attributes=regex_attributes,
                                       user_attributes=user_attributes,
                                       env_var_attributes=env_var_attributes,
                                       local_env_var_attributes=local_env_var_attributes,
                                       project_settings=project_settings, style_attributes=style_attributes,
                                       old_class=old_class, ref_order=ref_order, ref_steps=ref_steps,
                                       ref_paths_func=ref_paths_func, thumbnail_paths_func=thumbnail_paths_func,
                                       preview_dict=preview_dict, get_user_func=get_user_func)
        function_project_paths = self.Build_ConfigClassFunctionsWithoutUtil(self.base_config["project_paths"])
        function_refs_paths = self.Build_ConfigClassFunctionsWithoutUtil(self.base_config["ref_paths"])
        function_thumb_paths = self.Build_ConfigClassFunctionsWithoutUtil(self.base_config["thumbnail_paths"])

        with open(self.class_file, 'w+') as saveFile:
            saveFile.write(class_string + function_project_paths + function_refs_paths + function_thumb_paths)
        saveFile.close()

    def Build_ConfigClassFunctions(self, cur_dict):  # OLD - Uses Config_Util functions
        function_string = ""
        for p_key in sorted(cur_dict.keys()):
            function_name = p_key
            kwords = self.ReturnUnknownKeys(p_key, cur_dict)
            full_string = self.CreatePathFromDict(cur_dict[p_key], cur_dict)
            kwarg_str = ""
            kw_dict = "{"
            if_string = ""
            if kwords:
                for kw in kwords:
                    kwarg_str = kwarg_str + "%s=None," % kw
                    kw_dict = kw_dict + '"%s":%s,' % (kw, kw)
                    if_string = if_string + '        if {kw}==None:\n            raise NameError("Argument Missing: {kw}")\n'.format(
                        kw=kw)

                kw_dict = "%s}" % kw_dict[0:-1]
                function_string = function_string + """
    def get_{function_name}(self,{kwarg_str}):
        func_dict = {kw_dict}
{if_string}
        to_return = cfg_util.CreatePathFromDict("{k_out}",func_dict)
        return to_return\n\n""".format(function_name=function_name, kwarg_str=kwarg_str, kw_dict=kw_dict,
                                       if_string=if_string, k_out=full_string)
            else:
                function_string = function_string + """
    def get_{function_name}(self):
        to_return = cfg_util.CreatePathFromDict("{k_out}")
        return to_return\n\n""".format(function_name=function_name, k_out=full_string)
        return function_string

    def Build_ConfigPathToFormatStyle(self, cur_string):
        cur_string = cur_string.replace("<", "{")
        cur_string = cur_string.replace(">", "}")
        return cur_string

    def Build_getFunctionByKey(self, name, cur_dict):
        """
        returns a function (str) which allows you to get a value of a config-dict with just the key name
        :param name:
        :param cur_dict:
        :return:
        """
        build_string = """def getByKey_{name}(self,call_key=None,**kwords):
        """.format(name=name)
        key_functions_dict = {}
        for call_key in sorted(cur_dict.keys()):
            # call_function = getattr(self,"self.get_{call_key}".format(call_key=call_key))
            build_string = """{build_string}
        if call_key == '{call_key}':
            return self.get_{call_key}(**kwords)""".format(build_string=build_string, call_key=call_key)
        build_string = """{build_string}
        logger.debug("No such key found! This function only takes: {all_keys}")
        return False
        """.format(build_string=build_string, all_keys=str(list(cur_dict.keys())))
        return build_string

    def Build_ConfigClassFunctionsWithoutUtil(self, cur_dict):
        function_string = ""
        for p_key in sorted(cur_dict.keys()):
            function_name = p_key
            kwords = self.ReturnUnknownKeys(p_key, cur_dict)
            full_string = self.CreatePathFromDict(cur_dict[p_key], cur_dict)
            kw_format_string = '"%s".format(' % self.Build_ConfigPathToFormatStyle(full_string)
            kwarg_str = ""
            if_string = ""
            if kwords:
                for kw in kwords:
                    kwarg_str = kwarg_str + "%s=None," % kw
                    kw_format_string = "%s%s=%s," % (kw_format_string, kw, kw)
                    # if_string = if_string + '        if {kw}==None:\n            raise NameError("Argument Missing: {kw}")\n'.format(
                    #     kw=kw)
                    if_string = if_string + '        if {kw}==None:\n            {kw}="<{kw}>"\n            logger.debug("Building path to {function_name}: Argument Missing: {kw}")\n'.format(
                        function_name=function_name,
                        kw=kw)
                kw_format_string = "%s)" % kw_format_string
                function_string = function_string + """
    def get_{function_name}(self,{kwarg_str}**kwargs):
{if_string}
        to_return = {kw_format_string}
        return to_return\n\n""".format(function_name=function_name, kwarg_str=kwarg_str,
                                       kw_format_string=kw_format_string,
                                       if_string=if_string, k_out=full_string)
            else:
                function_string = function_string + """
    def get_{function_name}(self):
        to_return = "{k_out}"
        return to_return\n\n""".format(function_name=function_name, k_out=full_string)
        return function_string

    def Build_getUsers(self):
        if self.base_config['project_paths'].get('users_json'):
            user_json_string = f"""
        import os
        users_json_path = self.users_json.replace('<base_path>', self.base_path)
        folder_path = os.path.dirname(users_json_path)
        
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            
        if not os.path.exists(users_json_path):
            empty_dict = {{}}
            for key in self.users.keys():
                empty_dict[key] = []
            self.util.saveSettings(users_json_path, empty_dict)
        else:
            users_file_dictionary = self.util.loadSettings(users_json_path)
            for key, value in users_file_dictionary.items():
                if type(value) == list:
                    users = users + value\n"""
        else:
            user_json_string = ""
        
        _string = f"""def get_users(self, key=None):
        users = []
        for key, value in self.users.items():
            if type(value) == list:
                users = users + value
        {user_json_string}
        users = sorted(list(set(users)))
        return users
            """

        return _string

# ##TESTING
# def saveSettings(save_location, save_content):
#     with open(save_location, 'w+') as saveFile:
#         json.dump(save_content, saveFile)
#     saveFile.close()

# def loadSettings(load_file):
#     if os.path.isfile(load_file):
#         with open(load_file, 'r') as cur_file:
#             return json.load(cur_file)
#     else:
#         return {}

def FindEpisode(content,ep_reg):
    low_case = content.lower()
    re_compile = re.compile("%s$" % ep_reg)
    if re_compile.search(low_case):
        return True
    else:
        return False



# def _json_object_hook(d):
#     return namedtuple('test', d.keys())(*d.values())
#
# def json2obj(data):
#     return json.loads(data, object_hook=_json_object_hook)

# cfg = json.load(cur_file,object_hook=lambda d: SimpleNamespace(**d))

if __name__ == "__main__":    
    import Configs.ConfigUtil_Json as jcfg
    config_json = "%s/Config_LegoFriends.json" % os.path.dirname(os.path.realpath(__file__))
    b = Builder(config_json)
    b.Build_ConfigClassFile()
    util = jcfg.JsonConfigUtilClass(config_json)

    # import json
    # pass
