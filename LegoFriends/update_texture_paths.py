import os
import maya.cmds as cmds

def update_texture_paths():
    
    # Define the directory to check
    scene_file_path = cmds.file(query=True, l=True)[0]
    scene_folder_path = os.path.dirname(scene_file_path)
    asset_folder_path = os.path.abspath(scene_folder_path + "/../..")
    tex_folder_path = os.path.abspath(asset_folder_path + "/03_Texture")

    # Get all file nodes
    file_nodes = cmds.ls(type="file")

    print('\n   ... Indexing file nodes ...')

    # Loop through all file nodes
    reference_dictionary = {}
    for file_node in file_nodes:
        # Get the file path from the node
        file_path = cmds.getAttr(file_node + ".fileTextureName")
        if file_path:
            file_name = os.path.basename(file_path)
            if file_name in reference_dictionary.keys():
                reference_dictionary[file_name].append(file_node)
            else:
                reference_dictionary[file_name] = [file_node]

    print('\n   ... Searching through files ...\n')

    # Loop through all files in given directory
    for root, dirs, files in os.walk(tex_folder_path):
        for file in files:
            # Not wasting time on useless files.
            if any(file.endswith(w) for w in ['.tx', '.swatch', '.DS_Store', '.tmp']):
                continue
            
            # Checking if the file is in our index of file nodes
            if not file in reference_dictionary.keys():
                continue
            
            # Updating the texture file path
            for node in reference_dictionary[file]:
                cmds.setAttr(node + ".fileTextureName", os.path.join(root, file), type='string')
                number_of_spaces = 50 - len(node)
                spaces = ' ' * number_of_spaces
                print(' > ' + node + spaces + '  -->  ' + os.path.join(root, file))

    print('\n   ... Done ...\n')

def move_projections_to_face():
    selected_nodes = cmds.ls(sl=True)
    for node in selected_nodes:
        if cmds.nodeType(node) == 'projection':
            continue
        
        place_node = cmds.createNode('place3dTexture')
        cmds.setAttr(f"{place_node}.translateY", 4)
        cmds.connectAttr(f"{place_node}.worldInverseMatrix[0]", f"{node}.placementMatrix")
