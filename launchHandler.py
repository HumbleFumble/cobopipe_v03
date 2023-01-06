import os
import subprocess
import sys
from runtimeEnv import getRuntimeEnvFromConfig
from getConfig import getConfigClass


def launch(app="maya", local_user=True):
    if app == 'maya':
        runMayaFromConfig(local_user=local_user)
    elif app == 'mayapy':
        runMayapyFromConfig(local_user=local_user)
    elif app == 'cmd':
        runCmdFromConfig(local_user=local_user)
    elif app == 'harmony':
        runHarmonyFromConfig(local_user=local_user)
    elif app == 'aftereffects':
        runAEFromConfig(local_user=local_user)

def runAEFromConfig(file_path=None, local_user=False):
    CC = getConfigClass(pick_project=True)
    run_env = getRuntimeEnvFromConfig(config_class=CC, local_user=local_user)
    if not file_path:
        subprocess.Popen('START afterfx.exe -m', shell=True, env=run_env)
def runHarmonyFromConfig(file_path=None,local_user=False):
    CC = getConfigClass(pick_project=True)
    run_env = getRuntimeEnvFromConfig(config_class=CC, local_user=local_user)
    run_env["TOONBOOM_GLOBAL_SCRIPT_LOCATION"] = "%s/TB/ToonBoom_Global_Scripts" % os.path.dirname(os.path.realpath(__file__))
    run_env["BOM_USER"] = ""
    if file_path:
        subprocess.Popen('wstart-wcc.exe HarmonyPremium.exe -scene "%s"' % file_path, shell=True, env=run_env)
    else:
        subprocess.Popen('wstart-wcc.exe HarmonyPremium.exe', shell=True, env=run_env)

def runMayaFromConfig(file_path=None,local_user=False):
    CC = getConfigClass(pick_project=True)
    run_env = getRuntimeEnvFromConfig(config_class=CC, local_user=local_user)
    if not file_path:
        subprocess.Popen('START maya', shell=True, env=run_env)


def runMayapyFromConfig(file_path=None,local_user=False):
    CC = getConfigClass(pick_project=True)
    run_env = getRuntimeEnvFromConfig(config_class=CC, local_user=local_user)
    if not file_path:
        subprocess.Popen('START mayapy', shell=True, env=run_env)


def runCmdFromConfig(file_path=None,local_user=False):
    CC = getConfigClass(pick_project=True)
    run_env = getRuntimeEnvFromConfig(config_class=CC, local_user=local_user)
    if not file_path:
        subprocess.Popen('START cmd', shell=True, env=run_env)

# Test

if __name__ == "__main__":
    if len(sys.argv) > 1:
        args = sys.argv[1:]
        launch(*args)
    else:
        launch()


"""

mayapy.exe -c "import maya.standalone;	maya.standalone.initialize('python');	import maya.cmds as cmds;	import subprocess;    import Maya_Functions.delete_and_clean_up_functions as del_util;    import Maya_Functions.file_util_functions as file_util;    import Maya_Functions.ref_util_functions as ref_util;    import Maya_Functions.publish_util_functions as publish_util;    cmds.file('P:/930383_KiwiStrit3/Production/Film/E90/E90_SQ010/E90_SQ010_SH010/02_Light/E90_SQ010_SH010_Light.ma', open=True, f=True);    del_util.DeleteUnknown();    file_util.PrepareForSave('P:/930383_KiwiStrit3/Production/Film/E90/E90_SQ010/E90_SQ010_SH010/04_Publish/E90_SQ010_SH010_SubmitTesting_Render.ma', ma=True);    ref_util.ImportRefs();    del_util.DeleteDisplayLayers();    del_util.DeleteRenderLayers();    del_util.DeleteUnusedNodes();    del_util.RemoveArnold();    del_util.RemoveYetiPlugin();	print('Not OnlyBG');	print('Now saving file');	cmds.file(save=True);	cmds.quit(f=True);	"

"""