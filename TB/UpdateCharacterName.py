
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
    # Get all nodes
    nodes = project.scene.nodes

    # Get all group nodes
    groupNodes = project.scene.nodes

    # Print all nodes with "RENDER" in the name

    # for node in nodes:
    #     if "RENDER" in node.name:
    #         #print(node.attributes)
    #         print(node.name)
    # Print parent group name and node attributes
    # for node in nodes:
    #     if "RENDER" in node.name:
    #
    #         #print(node.attributes)
    #         print(node.parent_group())

    # Print all nodes that contain "RENDER" in the name
    # for i in groupNodes:
    #     if "RENDER" in i.name:
    #             print(i)


    # render_nodes = []
    # for node in nodes:
    #     if "RENDER" in node.name:
    #         render_nodes.append(node)
    #
    # for i in render_nodes[0].attributes:
    #     print(i)

    # Iterating on the node list with a for-loop
    render_nodes = []
    for node in nodes:  # For loop on the node list.
        if 'Guska' in node.path and "RENDER" in node.path:
            render_nodes.append(node)

    for node in render_nodes:
        name = node.name
        node.name = name.replace('Trin', 'Guska')

    project.save_all()

externalRendering(r"\\dumpap3\production\930462_HOJ_Project\Production\Film\S105\S105_SQ010\S105_SQ010_SH010\S105_SQ010_SH010\Test_H010_V100.xstage")