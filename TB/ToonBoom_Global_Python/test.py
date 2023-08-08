import sys
from Log.CoboLoggers import getLogger

logger = getLogger()

#Extend the environment's path, in order to find the installed Harmony Python module
#we should be able to use os.environ["HarmonyPremium"] + "/python-packages"
sys.path.append( r"C:\Program Files (x86)\Toon Boom Animation\Toon Boom Harmony 22 Premium\win64\bin\python-packages" )


#-----------------------------------------------------------------------------------------------------------------------
def findMisNamed(scene_file, rename):
    from ToonBoom import harmony

    error_dict = {"Guska": {"RENDER_Trin": "RENDER_Guska", "RENDER_Trin_Shadow": "RENDER_Guska_Shadow"},
                  "Harald": {"RENDER_Trin": "RENDER_Harald", "RENDER_Trin_Shadow": "RENDER_Harald_Shadow"}}
    harmony.open_project( scene_file )                                    #Open an offline Harmony project
    session = harmony.session()                                   #Fetch the currently active session of Harmony
    project = session.project
    scene = project.scene
    allnodes = scene.nodes

    result = {"Renamed": [], "Misnamed": []}

    # For each character in error dictionary (keys)
    for character in error_dict.keys():
        # For each wrongly named node (looping over the keys of the nested dict)
        for wrong_name in error_dict[character].keys():
            # Looking to match the node path
            match_node = "Top/" + character + "/" + wrong_name
            # If there is match in the node list
            if allnodes.contains(match_node):
                for node in allnodes:
                    if match_node == node.path and node.type == "WRITE":
                        if rename:
                            if node.name in error_dict[character].keys():
                                node.name = error_dict[character][node.name]
                                result["Renamed"].append(node.path)
                                # project.save_all()
                        else:
                            result["Misnamed"].append(node.path)

    return result

# print(findMisNamed(r"\\dumpap3\production\930462_HOJ_Project\Production\Film\S105\S105_SQ010\S105_SQ010_SH010\S105_SQ010_SH010\Test_H010_V100.xstage", rename=True))


