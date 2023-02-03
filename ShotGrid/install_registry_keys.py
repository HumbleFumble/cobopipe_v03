import os
import shutil
import subprocess

def install():
    file_name = 'ShotGrid_AMI.reg'
    folder = os.path.dirname(__file__)
    file_path = os.path.join(folder, file_name)
    new_file_path = os.path.join(f'C:\\Users\\{os.getlogin()}\\Desktop', file_name)
    shutil.copy(file_path, new_file_path)
    command = f"regedit.exe /S {new_file_path}"
    subprocess.Popen(command, shell=True)
    os.remove(new_file_path)
    print('\n\n > Done\n')

if __name__ == "__main__":
    install()