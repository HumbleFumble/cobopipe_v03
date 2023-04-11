import sys
import os
import json
from Log.CoboLoggers import getLogger

logger = getLogger()

#Extend the environment's path, in order to find the installed Harmony Python module
#we should be able to use os.environ["HarmonyPremium"] + "/python-packages"
sys.path.append( r"C:\Program Files (x86)\Toon Boom Animation\Toon Boom Harmony 22 Premium\win64\bin\python-packages" )

def findMisNamed(scene_file, rename=True):
    from ToonBoom import harmony
    error_dict = {"Guska": {"RENDER_Trin": "RENDER_Guska", "RENDER_Trin_Shadow": "RENDER_Guska_Shadow"},
                  "Fenja": {"RENDER_Char": "RENDER_Fenja", "RENDER_Shadow": "RENDER_Fenja_Shadow"},
                  "Knold": {"RENDER_Ull_Skiis": "RENDER_Knold", "RENDER_Ull_Skiis_Shadow": "RENDER_Knold_Shadow"},
                  "Stub":  {"RENDER_Ull_Skiis": "RENDER_Stub", "RENDER_Ull_Skiis_Shadow": "RENDER_Stub_Shadow"}}
    ignore_list = {"alfarim_Rig":["RENDER_Alpharim","RENDER_Alpharim_shadow"],"Huberts_Theaterwagon_prop":["RENDER_HubertsWagon", "RENDER_HubertsWagon_Shadow"],
                   "Hubert_Hat":["RENDER_Hubert", "RENDER_Hubert_shadow"]}
    harmony.open_project( scene_file )                                    #Open an offline Harmony project
    session = harmony.session()                                   #Fetch the currently active session of Harmony
    project = session.project
    scene = project.scene
    allnodes = scene.nodes

    # Save new version with consecutive number
    path = os.path.splitext(os.path.basename(scene_file))
    if 'V' not in path[0]:
        new_version = path[0] + '_V001'
    else:
        ttt = path[0].split('V')
        base_name = ttt[0]
        version = int(ttt[1]) + 1
        version_number = str(version).rjust(3, '0')
        new_version = base_name + 'V' + str(version_number)

    result = {"Shotname": path[0], "Renamed" : [], "Misnamed" : [], "Ignored" : []}

    
    for node in allnodes:
        if 'RENDER_' in node.name and node.type == "WRITE":
            # If the group name is not found in the node name and the node name is not "Top"
            if node.parent_group().name in ignore_list.keys():
                if node.name in ignore_list[node.parent_group().name]:
                    result["Ignored"].append(node.path)
                    continue
            if "_Rig" in node.parent_group().name:
                parent_name = node.parent_group().name.split("_Rig")[0]
            elif "_rig" in node.parent_group().name:
                parent_name = node.parent_group().name.split("_rig")[0]
            else:
                parent_name = node.parent_group().name
            if not parent_name.lower() in node.name.lower() and node.parent_group().name != 'Top':
                check = True

                if node.name in ignore_list:
                    continue

                for key in error_dict.keys():
                    if key in node.path:

                        if rename:
                            if node.name in error_dict[key].keys():
                                node.name = error_dict[key][node.name]
                                result["Renamed"].append(node.path)
                                check = False
                                project.save_as_new_version(new_version, True)
                # Add to misnamed list
                if check:
                    result["Misnamed"].append(node.path)

    
    # Return list with matching results (misnamed nodes)
    json_str = json.dumps(result)
    print(f'<RESULT_START>{json_str}<RESULT_END>')
    return result

# print(findMisNamed(r"P:\930462_HOJ_Project\Production\Film\S105\S105_SQ010\S105_SQ010_SH020\S105_SQ010_SH020\S105_SQ010_SH020_V049.xstage", rename=False))

def renameDone(results):
    for worker, result in results.items():
        print(result)


if __name__ == "__main__":
    findMisNamed(sys.argv[1], rename=sys.argv[2])