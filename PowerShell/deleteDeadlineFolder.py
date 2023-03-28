import subprocess
import os
import sys

user = os.getlogin()
script_path = "C:\\Users\\" + user + "\\VsCodeProjects\\cobopipe_v02-001\\PowerShell\\ScriptBlocks\\DeleteThinkBoxFolder.ps1"
computer_name = "wsx3"
process = subprocess.Popen(["pwsh", script_path, " -ComputerName ", computer_name] )
process.wait()

# p = subprocess.Popen(["powershell.exe",
#               "C:\\Users\\USER\\Desktop\\helloworld.ps1"],
#               stdout=sys.stdout)
# p.communicate()