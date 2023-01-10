import pyshortcuts as sc
import os
import shutil
from config import REPOSITORY_DIRECTORY, VERSION


# First execute generate_bat_files.py


def generate_shortcut_dict(local=False):
    directory = os.path.abspath(os.path.join(__file__, '../../')).replace(os.sep, '/')
    bat_files_path = os.path.abspath(os.path.join(directory, 'BAT_files')).replace(os.sep, '/')

    if local:
        icons_path = os.path.abspath(os.path.join(bat_files_path, 'icons')).replace(os.sep, '/')
    else:
        icons_path = os.path.abspath(os.path.join("%s/BAT_Files/" % REPOSITORY_DIRECTORY, 'icons')).replace(os.sep, '/')
    # print(icons_path)
    if local:
        source = os.path.abspath(os.path.join(directory, 'local/BAT_files')).replace(os.sep, '/')
    else:
        source = bat_files_path
    destination = os.path.abspath(os.path.join(source, 'shortcuts')).replace(os.sep, '/')

    if not os.path.exists(destination):
        os.makedirs(destination)

    icon_dict = {'Launch_maya': 'maya_logo.ico',
                 'Launch_harmony': 'HarmonyPremium.ico',
                 'Launch_aftereffects':'AE_Icon_CPHBOM.ico',
                 'ShotBrowser':'shot_browser_V001.ico'}

    shortcuts_dicts = []
    for item in os.listdir(source):
        if item.lower().endswith('.bat'):
            if local:
                file_path = os.path.abspath(os.path.join(source, item)).replace('/', os.sep)
            else:
                file_path = os.path.abspath(os.path.join(REPOSITORY_DIRECTORY, 'BAT_files/' + item)).replace('/', os.sep)
            base_name = os.path.splitext(item)[0]
            shortcut_name = '_'.join([base_name, VERSION])
            if base_name in icon_dict.keys():
                icon_path = os.path.abspath(os.path.join(icons_path, icon_dict[base_name]))
                print(icon_path)
            else:
                icon_path = ''

            if base_name not in ['Pull-repository']:
                _dict = {
                    "exe": 'C:/Windows/explorer.exe',
                    "flags": '',
                    "cmd": file_path,
                    "name": shortcut_name,
                    "icon": icon_path,
                    "destination": destination
                }

            shortcuts_dicts.append(_dict)
            
    return shortcuts_dicts


def create_shortcut(dictionary):
    final_cmd = ' '.join([dictionary['exe'], dictionary['cmd'], dictionary["flags"]])
    sc.make_shortcut(final_cmd, name=dictionary["name"], icon=dictionary["icon"])
    shortcut_file_name = dictionary["name"] + '.lnk'
    shortcut_path = os.path.abspath(os.path.join(os.environ['USERPROFILE'], 'Desktop', shortcut_file_name)).replace(os.sep, '/')
    destionation_path = os.path.abspath(os.path.join(dictionary['destination'], shortcut_file_name)).replace(os.sep, '/')
    if os.path.exists(destionation_path):
        os.remove(destionation_path)
    shutil.copy2(shortcut_path, destionation_path)
    os.remove(shortcut_path)


if __name__ == '__main__':
    for local in [True, False]:
        shortcut_dicts = generate_shortcut_dict(local)
        for dictionary in shortcut_dicts:
            create_shortcut(dictionary)