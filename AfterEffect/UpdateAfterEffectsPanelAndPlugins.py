import os
import re

import shutil

def copy_directory(src_dir, dst_dir, overwrite=False):
    print(f"Copy from {src_dir} to {dst_dir}")
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    for item in os.listdir(src_dir):
        src_item = os.path.join(src_dir, item)
        dst_item = os.path.join(dst_dir, item)

        if os.path.isdir(src_item):
            copy_directory(src_item, dst_item, overwrite)
        else:
            if os.path.exists(dst_item):
                if overwrite:
                    shutil.copy(src_item, dst_item)
                    print(f'Overwritten: {dst_item}')
                else:
                    print(f'Skipped: {dst_item}')
            else:
                shutil.copy(src_item, dst_item)
                print(f'Copied: {dst_item}')


def findLatestAfterEffectsFolder():

    prg_files = os.getenv("programfiles").replace("\\","/")
    adobe_dir = f'{prg_files}/Adobe'
    # Define the directory where Adobe After Effects is typically installed.

    # Check if the directory exists.
    if os.path.isdir(adobe_dir):
        # Get a list of all Adobe After Effects installations.
        ae_installs = [d for d in os.listdir(adobe_dir) if 'Adobe After Effects' in d]

        # Extract the version numbers using regular expressions.
        versions = [re.search(r'\d+', d).group() for d in ae_installs if re.search(r'\d+', d)]

        # Get the highest version.
        highest_version = max(versions)

        print("The highest version of Adobe After Effects installed is:", highest_version)
        return f"{adobe_dir}/Adobe After Effects {highest_version}"
    else:
        print("Adobe directory not found.")
        return None


def CopyToAEFolder():

    ae_dir = findLatestAfterEffectsFolder()
    if ae_dir:
        ae_panel_folder = f"{ae_dir}/Support Files/Scripts/ScriptUI Panels"
        ae_plugin_folder = f"{ae_dir}/Support Files/Plug-ins"
        ae_test = f"{ae_dir}/TEST"
    else:
        return False

    ui_panel_folder = ["T:/_Pipeline/cobopipe_v02-001/AfterEffect/AE_UI_Panel_Calls","T:/_Software/Adobe/After Effects/plugin_packages/FXConsole_ScriptFolder_Part"]
    plugin_folders = ["T:/_Software/Adobe/After Effects/plugin_packages/HOJ_Production_Collection","T:/_Software/Adobe/After Effects/plugin_packages/FXConsole_Plugin_Part"]

    for panel_folder in ui_panel_folder:
        copy_directory(panel_folder,ae_panel_folder,overwrite=True)
    for plug_folder in plugin_folders:
        copy_directory(plug_folder,ae_plugin_folder,overwrite=True)

if __name__ == "__main__":
    CopyToAEFolder()

