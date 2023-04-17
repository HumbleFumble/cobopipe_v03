import sys
import os
import re

def increment_tb_folder(file):
    if not os.path.exists(file):
        return False
    
    harmony.open_project(file)
    session = harmony.session()
    project = session.project
    scene = project.scene
    folder = project.project_path
    current_folder_version = folder.split('/')[-1].split('_')[-1]
    current_version = project.version_name.split('_')[-1]
    if re.match('V\d\d\d', current_version):
        new_version = int(current_version[1:]) + 1
        new_version = f'V{new_version:03}'
    else:
        new_version = 'V001'
        
    if re.match('V\d\d\d', current_folder_version):
        folder = folder.replace(current_folder_version, new_version)
        # new_version = int(cur_version.replace('V', '')) + 1 # Convert to integer and increment.
        # new_version = f'V{new_version:03}' # Convert to string, adding V and padding.
        # folder = folder.replace(cur_version, new_version)
    else:
        folder = f'{folder}_{new_version}'

    if os.path.exists(folder):
        return False
    
    project.save_as(folder)
    new_file = folder.split('/')[-1] + '.xstage'
    new_path = f'{folder}/{new_file}'
    return new_path


if __name__ == '__main__':
    sys.path.append(sys.argv[1])
    from ToonBoom import harmony
    result = increment_tb_folder(sys.argv[2])
    print(result)