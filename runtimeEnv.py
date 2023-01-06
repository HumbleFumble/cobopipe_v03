import os

from Log.CoboLoggers import getLogger
logger = getLogger()

def _runtime_env_dict(env_dict={}):
    runtime_env = None
    runtime_env = os.environ.copy()
    for env_key in env_dict:
        if env_key == "PYTHONPATH":
            if "PYTHONPATH" in runtime_env:
                runtime_env['PYTHONPATH'] = "%s;%s" % (runtime_env['PYTHONPATH'], env_dict[env_key])
            else:
                runtime_env[env_key] = env_dict[env_key]
    return runtime_env

def _runtime_environment(python_path="", maya_project="", project_name="",ocio=None):
    '''
    Returns a new environment dictionary for this intepreter, with only the supplied paths
    (and the required maya paths).  Dictionary is independent of machine level settings;
    non maya/python related values are preserved.
    '''
    runtime_env = None
    runtime_env = os.environ.copy()
    # print(runtime_env['PYTHONPATH'])
    if "PYTHONPATH" in runtime_env:
        runtime_env['PYTHONPATH'] = "%s;%s" % (runtime_env['PYTHONPATH'], python_path)
    else:
        runtime_env['PYTHONPATH'] = python_path
    runtime_env['MAYA_PROJECT'] = maya_project
    runtime_env['BOM_PROJECT_NAME'] = project_name
    runtime_env['BOM_PIPE_PATH'] = python_path
    if ocio:
        runtime_env['OCIO'] = ocio
    # runtime_env['PATH'] = ''
    return runtime_env

def getRuntimeEnvFromConfig_OLD(runtime_config=None,local_user=False,ocio=False):
    maya_project = runtime_config.get_base_path()
    project_name = runtime_config.project_name
    python_path = runtime_config.get_python_path()
    # if "OCIO" in runtime_config.__dict__.keys() and ocio:
    #     ocio_path = runtime_config.get_OCIO()
    # else:
    #     ocio_path = None
    if local_user:
        python_path = os.path.dirname(os.path.realpath(__file__))

        #print("picked local user python-path: %s" % python_path)
    run_env = _runtime_environment(python_path=python_path,maya_project=maya_project,project_name=project_name)
    return run_env

def getRuntimeEnvFromConfig(config_class=None,local_user=True):
    config_env_dict = config_class.environment_vars
    #copy the system env
    runtime_env = os.environ.copy()
    #Do the dynamic env vars
    for key in config_class.environment_vars:
        if key in config_class.local_vars and local_user:
            local_dict = {"python_path":"%s" % os.path.dirname(os.path.realpath(__file__))}
            local_path = config_class.util.CreatePathFromDict(config_env_dict[key], local_dict)
            local_path = local_path.replace(os.sep,"/")
            logger.info("Env Var: %s -> %s" % (key, local_path))
            # print(key,local_path)
            to_add = (key,local_path)
        else:
            global_path = config_class.util.CreatePathFromDict(config_env_dict[key])
            # print(key,global_path)
            to_add = (key, global_path)
        if key == "PYTHONPATH":
            if "PYTHONPATH" in runtime_env:
                runtime_env['PYTHONPATH'] = "%s;%s" % (runtime_env['PYTHONPATH'], to_add[1])
            else:
                runtime_env['PYTHONPATH'] = to_add[1]
        runtime_env[to_add[0]] = to_add[1]
    #Do static env vars
    runtime_env['BOM_PROJECT_NAME'] = config_class.project_name
    runtime_env['MAYA_PROJECT'] = config_class.get_base_path()
    if local_user:
        runtime_env['BOM_PIPE_PATH'] = os.path.dirname(os.path.realpath(__file__)).replace(os.sep,"/")
    else:
        runtime_env['BOM_PIPE_PATH'] = config_class.python_path


    logger.debug(runtime_env)
    return runtime_env



if __name__ == "__main__":
    pass


    # from Configs.ConfigClasses.ConfigClass_KiwiStrit3 import ConfigClass
    # CC = ConfigClass()
    # from getConfig import getConfigClass

    # CC = getConfigClass()
    # rt = getRuntimeEnvFromConfig(CC,True)
    # rt = getRuntimeEnvFromConfig(CC)

    #print(rt["PYTHONPATH"])
    #getRuntimeEnvFromConfig(CC)

