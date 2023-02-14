
import sys
import os

#Extend the environment's path, in order to find the installed Harmony Python module
#we should be able to use os.environ["HarmonyPremium"] + "/python-packages"
sys.path.append( r"C:\Program Files (x86)\Toon Boom Animation\Toon Boom Harmony 22 Premium\win64\bin\python-packages" )
import TB.CB_SetupRenderInfo_Python as rs

def externalRendering(scene_file):
    from ToonBoom import harmony

    # print("Trying to render out: %s" % scene_file)
    harmony.open_project( scene_file )                                    #Open an offline Harmony project
    session = harmony.session()                                   #Fetch the currently active session of Harmony
    project = session.project
    return project
    #The project that is already loaded.
    # print( "Current Project: %s" % (project.project_path) )

project = externalRendering(r"\\dumpap3\production\930462_HOJ_Project\Production\Film\S105\S105_SQ010\S105_SQ010_SH010\S105_SQ010_SH010\Test_H010_V100.xstage")
allnodes = project.scene.nodes

old_string = 'RenameME'
new_string = 'NewName'
path = "//dumpap3/production/930462_HOJ_Project/Production/Film/S105/S105_SQ020/S105_SQ020_SH100/Passes"
allfiles = os.listdir(path)
character_name = 'Guska'

# Rename node. This will only replace a string in the name and not the whole name
def renameNode(old_name, new_name):
    for node in allnodes:
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
def findMisNamed(character_name):
    for node in allnodes:
        if character_name in node.path and 'RENDER_' in node.path:
            if 'RENDER_' + character_name not in node.name:
             print("\"" + character_name + "\"" + " missing in " + node.name)



# renameNode(old_string, new_string)
# renameFile(allfiles, old_string, new_string)

findMisNamed(character_name)