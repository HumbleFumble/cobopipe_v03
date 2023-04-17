import os
import subprocess
from config import REPOSITORY_DIRECTORY
from getConfig import getConfigClass
from runtimeEnv import getRuntimeEnvFromConfig

CC = getConfigClass()
run_env = getRuntimeEnvFromConfig(config_class=CC)


def render(file_path):
    if not os.path.exists(file_path):
        return None
    if not os.path.isfile(file_path):
        return None
    executable = (
        r'"C:\Program Files\Adobe\Adobe After Effects 2023\Support Files\aerender.exe"'
    )
    arguments = ""
    arguments = f'{arguments} -project "{file_path}"'
    arguments = f'{arguments} -comp ".RENDER"'
    arguments = f"{arguments} -v ERRORS_AND_PROGRESS"
    arguments = f"{arguments} -close DO_NOT_SAVE_CHANGES"
    arguments = f"{arguments} -sound OFF"
    command = f"{executable} {arguments}"
    process = subprocess.Popen(command, shell=True, env=run_env)
    stdout, stderr = process.communicate()
    return stdout, stderr


def submit_to_deadline(file_path):
    if not os.path.exists(file_path):
        return None
    if not os.path.isfile(file_path):
        return None

    script_path = (
        REPOSITORY_DIRECTORY + "/AfterEffect/submit_render_to_deadline_externally.jsx"
    )
    executable = r"AfterFX"
    arguments = (
        f"-noui -s \"#include {script_path};Main('{file_path.replace(os.sep, '/')}')\""
    )
    command = f"{executable} {arguments}"
    print(f"\n<COMMAND>\n{command}\n")
    process = subprocess.Popen(command, shell=True, env=run_env)
    stdout, stderr = process.communicate()
    return stdout, stderr


if __name__ == "__main__":
    submit_to_deadline(
        r"P:\930462_HOJ_Project\Production\Film\S107\S107_SQ030\S107_SQ030_SH080\Comp\S107_SQ030_SH080_Comp_V001.aep"
    )
