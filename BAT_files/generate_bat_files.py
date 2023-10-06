import os
from config import REPOSITORY_DIRECTORY, VERSION


def generate_bat_dict(repository_directory, local=False):
    bat_files_info = {
'fix-p-cores.bat': r"""@echo off
powercfg /powerthrottling disable /path "C:\Program Files\Autodesk\Maya2020\bin\mayabatch.exe"
powercfg /powerthrottling disable /path "C:\Program Files\Autodesk\Maya2020\bin\maya.exe"
EXIT /B 0""",

'install_ffmpeg_python.bat': r"""@echo off
python -m pip install --upgrade pip
pip install ffmpeg_python
EXIT /B 0""",

'Launch_cmd.bat': r'python "' + repository_directory + r'/launchHandler.py" "cmd" ' + str(local),

'Launch_harmony.bat': r'python "' + repository_directory + r'/launchHandler.py" "harmony" ' + str(local),

'Launch_maya.bat': r'python "' + repository_directory + r'/launchHandler.py" "maya" ' + str(local),

'Launch_mayapy.bat': r'python "' + repository_directory + r'/launchHandler.py" "mayapy" ' + str(local),

'Launch_aftereffects.bat': r'python "' + repository_directory + r'/launchHandler.py" "aftereffects" ' + str(local),

'Launch_MountDriveInterface.bat': r'python "' + repository_directory + '/MountDriveInterface.py"',

'New P-drive.bat': r"""net use P: /delete
net use P: \\dumpap3\production""",

'Old P-drive.bat': r"""net use P: /delete
net use P: \\dumpap2\projekter""",

'Pull-repository.bat': r"""T:
cd "T:/_Pipeline/cobopipe_v02-001"
git pull
pause""",

'RenderSubmit.bat': r'python ' + repository_directory + r'/RenderSubmit.py',

'ShotBrowser.bat': r'python ' + repository_directory + r'/ShotBrowser.py',

'update_yeti_env.bat': 'python "' + repository_directory + '/update_yeti_env.py"\nPAUSE',

'updateFFMPEG.bat': 'python "' + repository_directory + '/software_and_hardware/updateFFMPEG.py"\nPAUSE',

'update_harmony_hotbar.bat': r"""@echo off
T:/_Executables/python/Python310/python.exe """ + repository_directory + """/TB/updateHotbar.py
EXIT /B 0""",

'UpdateHarmonyPreferences.bat': 'python ' + repository_directory + '/TB/UpdateHarmonyPreferences.py',

'install_shotgrid_regkey.bat': 'T:/_Executables/python/Python310/python.exe T:/_Pipeline/cobopipe_v02-001/shotgrid/install_registry_keys.py',

'runDeleteThinkBox.bat': f'pwsh -Command "Set-ExecutionPolicy Bypass;& \\\\192.168.0.225/tools/_Pipeline/cobopipe_v02-001/PowerShell/ScriptBlocks/DeleteThinkBoxFolder.ps1"\nPAUSE',

'ReturnAnim.bat': f'python {repository_directory}/ReturnAnim.py'
}
    return bat_files_info


def generate_bat_files(local=False):
    directory = os.path.abspath(os.path.join(__file__, '../../')).replace(os.sep, '/')
    if local:
        destination = os.path.abspath(os.path.join(directory, 'local/BAT_files')).replace(os.sep, '/')
        repository_directory = directory
    else:
        destination = os.path.abspath(os.path.join(directory, 'BAT_files')).replace(os.sep, '/')
        repository_directory = REPOSITORY_DIRECTORY

    if not os.path.exists(destination):
        os.makedirs(destination)

    bat_dict = generate_bat_dict(repository_directory, local=local)
    file_paths = []

    for file_name, content in bat_dict.items():
        file_path = os.path.abspath(os.path.join(destination, file_name)).replace(os.sep, '/')
        if os.path.exists(file_path):
            os.remove(file_path)
            
        with open(file_path, 'w') as f:
            f.write(content)
        f.close()
        file_paths.append(file_path)

    return file_paths


if __name__ == '__main__':
    for local in [True, False]:
        generate_bat_files(local)