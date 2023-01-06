import os
from Configs import ConfigUtil_Json
from importlib import import_module
from Log.CoboLoggers import getLogger
logger = getLogger()


def getConfigFromPath(path):
    """
    get project name based of path
    :param path:
    :return:
    """
    pass

def rebuildConfigClasses():
    """
    Quick way to rebuilding/updating all config classes
    :return:
    """
    config_path = "%s/Configs/" % os.path.dirname(os.path.realpath(__file__))
    configs = os.listdir(config_path)
    for con in configs:
        if "Config_" in con and not ".pyc" in con:
            # temp_config = ConfigUtil.ConfigUtilClass(base_config=import_module("Configs.%s" %con.split(".")[0]))
            # print("%s%s" % (config_path,con.split(".")[0]))
            temp_config = ConfigUtil_Json.JsonConfigUtilClass(base_config="%s%s.json" % (config_path,con.split(".")[0]))
            temp_config.updateConfigClass()

#OLD ORIGINAL
# def getConfig(project_name):
#     cfg = import_module("Configs.Config_%s" % project_name)
#     return cfg
#
#
# def getConfigUtil(project_name):
#     cfg_util = ConfigUtil.ConfigUtilClass(getConfig(project_name))
#     return cfg_util

def getJsonConfigUtil(project_name):
    cfg_util = ConfigUtil_Json.JsonConfigUtilClass(getJsonConfig(project_name))
    return cfg_util

def getJsonConfig(project_name):
    # cfg = import_module("Configs.Config_%s" % project_name)
    # print(__file__)
    # print(os.path.dirname(os.path.realpath(__file__)))
    # print(os.path.abspath(os.path.dirname(os.path.realpath(__file__))))
    cfg_file = "%s/Configs/Config_%s.json" % (os.path.dirname(os.path.realpath(__file__)),project_name)
    # print(cfg_file)
    return cfg_file

def findProjectName(project_name, set_env=True, pick_project=False):
    if project_name:
        if set_env:
            os.environ["BOM_PROJECT_NAME"] = "%s" % project_name
        return project_name
    if pick_project:
        import getConfigWindow
        project_name = getConfigWindow.run()
        if project_name:
            if set_env:
                os.environ["BOM_PROJECT_NAME"] = "%s" % project_name
            return project_name
        else:

            raise NameError("No Project Name given!!")
    if "BOM_PROJECT_NAME" in os.environ:
        if not os.environ["BOM_PROJECT_NAME"] == "":
            logger.debug("Found Project in env: %s" % os.environ["BOM_PROJECT_NAME"])
            return os.environ["BOM_PROJECT_NAME"]

    import getConfigWindow
    project_name = getConfigWindow.run()
    if project_name:
        if set_env:
            os.environ["BOM_PROJECT_NAME"] = "%s" % project_name
        return project_name
    logger.warning("No Project Name given!!")
    raise NameError("No Project Name given!!")


def setOSEnvironment(**env_vars):
    if env_vars:
        for k, v in env_vars:
            os.environ[k] = v


def getConfigClass(project_name=None, set_env=True, pick_project=False):
    project_name = findProjectName(project_name, set_env, pick_project)
    if not os.path.exists("%s/Configs/ConfigClasses/ConfigClass_%s.py" % (os.path.dirname(os.path.realpath(__file__)).replace(os.sep, "/"),  project_name)):
        cfg_util = getJsonConfigUtil(project_name)
        cfg_util.updateConfigClass()
        logger.debug("Creating file, please retry")
    return_module = import_module("Configs.ConfigClasses.ConfigClass_%s" % project_name)
    CC = return_module.ConfigClass()
    logger.debug("returning CC for %s" % project_name)
    return CC

# C:\Users\cg\PycharmProjects\bombay_base_production\Configs\ConfigClass_KiwiStrit3.py
# C:/Users/cg/PycharmProjects/bombay_base_production/Configs/ConfigClass_KiwiStrit3.py


if __name__ == "__main__":
    rebuildConfigClasses()
    # setConsoleLevel(logger,10)
    # rebuildConfigClasses()
    # getConfigClass()
    # getJsonConfigClass()

