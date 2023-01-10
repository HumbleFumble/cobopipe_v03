import sys
import os
import subprocess
#Extend the environment's path, in order to find the installed Harmony Python module
sys.path.append( r"C:/Program Files (x86)/Toon Boom Animation/Toon Boom Harmony 22 Premium/win64/bin/python-packages" )
# sys.path.append( "C:/Users/cg/PycharmProjects/cobopipe_v02-001/" )

from ToonBoom import harmony

from getConfig import getConfigClass
CC = getConfigClass()

def log(message):
    sess = harmony.session()
    sess.log(str(message))

def runDirect(scene_path):
    harmony.open_project(scene_path)
    current_session = harmony.session()  # Fetch the currently active session of Harmony
    project = current_session.project
    run()
    project.save_all()
def run():
    current_session = harmony.session()  # Fetch the currently active session of Harmony
    project = current_session.project
    passes_folder = findPassesFolder()
    for node in project.scene.nodes:
        if(node.type == "WRITE" and "RENDER_" in node.name):
            setRenderNodePaths(node,passes_folder)


def setRenderNodePaths(node,passes_folder):
    print("setting path for %s" % node.name)
    subfix = node.name.split("RENDER_")[1]
    full_name = "%s/%s_" % (passes_folder,subfix)
    node.attributes["DRAWING_NAME"].set_text_value(1,full_name)
    if "tb_number_padding" in CC.project_settings:
        node.attributes["LEADING_ZEROS"].set_text_value(1, CC.project_settings["tb_number_padding"])
    if "tb_output_format" in CC.project_settings:
        node.attributes["DRAWING_TYPE"].set_text_value(1, CC.project_settings["tb_output_format"])

def findPassesFolder():
    sess = harmony.session()  # Fetch the currently active session of Harmony
    project = sess.project  # The project that is already loaded.
    scene_dir = project.project_path
    passes_dir = "%s/Passes/" % "/".join(scene_dir.split("/")[0:-1])
    if not os.path.exists(passes_dir):
        os.mkdir(passes_dir)
    return passes_dir

if __name__ == "__main__":
    runDirect(sys.argv[1])
# python "C:/Users/cg/PycharmProjects/cobopipe_v02-001/TB/CB_SetupRenderInfo_Python.py" "P:/930462_HOJ_Project/Production/Film/S104/S104_SQ010/S104_SQ010_SH010/S104_SQ010_SH010/S104_SQ010_SH010_V007.xstage"