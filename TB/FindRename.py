
import sys
import os
from Log.CoboLoggers import getLogger

logger = getLogger()

#Extend the environment's path, in order to find the installed Harmony Python module
#we should be able to use os.environ["HarmonyPremium"] + "/python-packages"
sys.path.append( r"C:\Program Files (x86)\Toon Boom Animation\Toon Boom Harmony 22 Premium\win64\bin\python-packages" )
import TB.CB_SetupRenderInfo_Python as rs

def get_harmony_project(scene_file):
    from ToonBoom import harmony

    # print("Trying to render out: %s" % scene_file)
    harmony.open_project( scene_file )                                    #Open an offline Harmony project
    session = harmony.session()                                   #Fetch the currently active session of Harmony
    project = session.project
    return project
    #The project that is already loaded.
    # print( "Current Project: %s" % (project.project_path) )



# Rename node. This will only replace a string in the name and not the whole name
def renameNode(old_name, new_name):
    for node in allnodes:
        # path = "TOP/Guska/RENDER_Trin_"
        if old_name in node.path:
            name = node.name
            node.name = name.replace(old_name, new_name)
            print('\n', node)

    # Save scene for the changes to take effect
    # project.save_all()

# Rename files that are named wrongly in Windows Explorer
def renameFile(files, old_name, new_name):
    for filename in files:
        if old_name in filename:
            name = filename.replace(old_string, new_name)
            os.rename(path + '/' + filename, path + '/' + name)
            print('Renaming ' + filename + ' to ' + name)

# Find nodes where the render nodes are named after a character, different from the character, whom the render
# node belongs to
error_dict = {"Guska:":{"RENDER_Trin_Shadow":"RENDER_Guska_Shadow","RENDER_Trin":"Render_Guska"}}

def changeNodeByDict(error_dict,project):
    allnodes = project.scene.nodes
    for node in allnodes:
        for char in error_dict.keys():
            if char in node.parent_group().name and 'RENDER_' in node.name and node.type=="WRITE":
                if node.name in error_dict[char].keys():
                    print("FOUND THIS: %s" % node.name)
                    node.name = error_dict[char][node.name]

def findMisNamed(character_name=None,project=None,fix_now=False):
    allnodes = project.scene.nodes
    return_list = []
    for node in allnodes:
        if character_name in node.path and 'RENDER_' in node.path and node.type=="WRITE":
            if 'RENDER_' + character_name not in node.name:
                print("\"" + character_name + "\"" + " missing in " + node.name)
                if fix_now:
                    pass
                else:
                    return_list.append(node)
    return return_list

def check_scene(scene_path):
    project = get_harmony_project(scene_path)
    char_list = ["Trin","Guska"]
    for char in char_list:
        problem_list = findMisNamed(char,project)
        for p in problem_list:
            logger(f"{scene_path} has issue with: {p.path}")

check_scene(r"\\dumpap3\production\930462_HOJ_Project\Production\Film\S105\S105_SQ010\S105_SQ010_SH010\S105_SQ010_SH010\Test_H010_V100.xstage")

# project = get_harmony_project(r"\\dumpap3\production\930462_HOJ_Project\Production\Film\S105\S105_SQ010\S105_SQ010_SH010\S105_SQ010_SH010\Test_H010_V100.xstage")
# allnodes = project.scene.nodes
#
# old_string = 'RenameME'
# new_string = 'NewName'
# path = "//dumpap3/production/930462_HOJ_Project/Production/Film/S105/S105_SQ020/S105_SQ020_SH100/Passes"
# allfiles = os.listdir(path)
# character_name = 'Guska'
#
# # renameNode(old_string, new_string)
# # renameFile(allfiles, old_string, new_string)
#
# findMisNamed(character_name)