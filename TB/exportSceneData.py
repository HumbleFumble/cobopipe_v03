import subprocess

def process(scene_path):
    _string = """HarmonyPremium -script "include('T:/_Pipeline/cobopipe_v02-001/TB/ToonBoom_Global_Scripts/CB_ExportSceneData.js');ExportSceneData();" -scene """
    _string = _string + "\"" + scene_path + "\""
    _process = subprocess.Popen(_string)
    output = _process.communicate()

# process("P:/930462_HOJ_Project/Production/Film/S104/S104_SQ070/S104_SQ070_SH170/S104_SQ070_SH170/S104_SQ070_SH170_V001.xstage")