import sys
import os
from Log.CoboLoggers import getLogger

logger = getLogger()

#Extend the environment's path, in order to find the installed Harmony Python module
#we should be able to use os.environ["HarmonyPremium"] + "/python-packages"
sys.path.append( r"C:\Program Files (x86)\Toon Boom Animation\Toon Boom Harmony 22 Premium\win64\bin\python-packages" )
from ToonBoom import harmony

def disable_glow(file_path):

    
    harmony.open_project(file_path)                                    #Open an offline Harmony project
    session = harmony.session()                                   #Fetch the currently active session of Harmony
    project = session.project
    scene = project.scene
    all_nodes = scene.nodes
    changed = False
    for node in all_nodes:
        if node.name == "Glow":
            node.enabled = False
            changed = True
            print(f'Disabled: {node.path}')

    if changed:
        # Save new version
        path = os.path.splitext(os.path.basename(file_path))
        if 'V' not in path[0]:
            new_version = path[0] + '_V001'
        else:
            ttt = path[0].split('V')
            base_name = ttt[0]
            version = int(ttt[1]) + 1
            version_number = str(version).rjust(3, '0')
            new_version = base_name + 'V' + str(version_number)

        project.save_as_new_version(new_version, True)

    harmony.close_project()
    
if __name__ == "__main__":
    #file_path = 'P:/930462_HOJ_Project/Production/Film/S107/S107_SQ020/S107_SQ020_SH200/S107_SQ020_SH200/S107_SQ020_SH200_V003.xstage'
    # print(sys.argv[1])
    disable_glow(sys.argv[1])
    
    