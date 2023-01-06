import subprocess
import inspect
import sys
import os
import shutil

def copyFFMPEG_To_Desktop():
    server_ffmpeg = "T:/_Executables/ffmpeg"
    desk_folder = os.path.expanduser("~/Desktop/ffmpeg").replace(os.sep, "/")
    if os.path.exists(desk_folder):
        shutil.rmtree(desk_folder)
    shutil.copytree(server_ffmpeg,desk_folder)
    return desk_folder

def copyScriptToDesktop(script_path):
    f,p = os.path.split(script_path)
    dest = os.path.expanduser("~/Desktop/%s" % p).replace(os.sep, "/")
    shutil.copy(script_path,dest)
    print(dest)
    return dest

def removeFromDesktop(remove_list=[]):
    # desk_folder = os.path.expanduser("~/Desktop/ffmpeg").replace(os.sep, "/")
    for r in remove_list:
        if os.path.exists(r):
            if os.path.isdir(r):
                shutil.rmtree(r)
            else:
                os.remove(r)

def exec_powershell_admin(cmd):
    """EXECUTE POWERSHELL IN ADMIN MODE"""
    final_cmd = "$process = start-process powershell " \
                "-PassThru " \
                "-Verb RunAs " \
                "-Wait " \
                "-ArgumentList \"-Command\", \"{cmd}\"".format(cmd=cmd.replace("\"", "\'"))
    process = subprocess.Popen(['powershell', '-Command', final_cmd],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(process.communicate())
    process.wait()

def run():
    desk_folder = copyFFMPEG_To_Desktop()
    script_path = ("%s/updateFFMPEG_CopyAsAdmin.py" % os.path.dirname(os.path.realpath(__file__))).replace(os.sep,"/")
    run_path  = copyScriptToDesktop(script_path)
    t_path = "python %s" % run_path #C:/Users/cg/PycharmProjects/bombay_base_production/software_and_hardware/updateFFMPEG_CopyAsAdmin.py"
    exec_powershell_admin(t_path)
    removeFromDesktop([desk_folder,run_path])
run()
# print()
