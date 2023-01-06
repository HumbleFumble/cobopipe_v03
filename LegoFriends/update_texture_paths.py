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
            if not any(file.endswith(w) for w in ['.tx', '.swatch', '.DS_Store', '.tmp']):
                # Checking if the file is in our index of file nodes
                if file in reference_dictionary.keys():
                    # Updating the texture file path
                    for node in reference_dictionary[file]:
                        cmds.setAttr(node + ".fileTextureName", os.path.join(root, file), type='string')
                        number_of_spaces = 50 - len(node)
                        spaces = ' ' * number_of_spaces
                        print(' > ' + node + spaces + '  -->  ' + os.path.join(root, file))