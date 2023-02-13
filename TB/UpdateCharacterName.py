
import sys

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
    #The project that is already loaded.
    # print( "Current Project: %s" % (project.project_path) )
    '''
    shot_name = "_SH010"
    rename_node = []
    nodes = project.scene.nodes
    for node in nodes:
        if node.type == "WRITE":
            if "RENDER_" in node.name and shot_name not in node.name:
                rename_node.append(node.name)

    print(rename_node)

    '''
    rename_node = []
    nodes = project.scene.nodes
    for node in nodes:
        if "RENDER" in node.name:
            print(node.attributes)
            print(node.parent_group())
    print(rename_node)
externalRendering(r"P:\930462_HOJ_Project\Production\Film\S105\S105_SQ010\S105_SQ010_SH010\S105_SQ010_SH010\Test_H010_V100.xstage")

