import sys
import os
import re

def increment_tb_folder(file):
    if not os.path.exists(file):
        return False
    
    harmony.open_project(file)
    session = harmony.session()
    project = session.project
    #scene = project.scene
    folder = project.project_path 
    print(folder.split('/')[-1].split('_')[-1])
    if re.match('V\d\d\d', folder.split('/')[-1].split('_')[-1]):
        print(folder)
    else:
        print('FUCK')


if __name__ == '__main__':
    sys.path.append(sys.argv[1])
    from ToonBoom import harmony
    increment_tb_folder(sys.argv[2])