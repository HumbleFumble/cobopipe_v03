import subprocess
import json
import os
import xml.etree.ElementTree as et

user = os.getlogin()
def SplitLists(computer_name):
    list = []
    for each_dict in app_data:
        if each_dict['PSComputerName'] == computer_name:
            list.append(each_dict)

    return list

def RunPSScript(script_path):
    # Run GetHostInfo_SB.ps1. This script checks which computers are online and outputs to "complist.json"
    process = subprocess.Popen(["pwsh", "C:\\Users\\" + user + script_path])
    process.wait()

RunPSScript("\\VsCodeProjects\\cobopipe_v02-001\\PowerShell\\ScriptBlocks\\GetHostInfo_SB.ps1")


# Run GetHostInfo if there is a change in the list of available computers, for example if a computer had to be turned on
host_info = {}
# Import computers list json file, produced by GetHostInfo_SB.ps1
with open("C:\\Users\\" + user + "\\VsCodeProjects\\cobopipe_v02-001\\PowerShell\\complist.json") as user_file:
    file_contents = user_file.read()
ps_data = json.loads(file_contents)
# Create dictionary with available computers and display the result
for item in ps_data:
    host_info[item["Name"]] = item['WinRMStatus']

# for key, value in host_info.items():
#     print(key, value)

exclude_list = [3, 4, 16, 30]
new_list = []

unavailable_list = []
for i, j in host_info.items():
    if j == "":
        unavailable_list.append(int(i.replace("wsx", "")))

# Convert computers list from the json file (complist.json) to just numbers list
for key in host_info.keys():
    get_number = str(key).replace("wsx", "")
    new_list.append(get_number)

# Create new list without the computers in exclude_list
for number in new_list:
    for exclude_number in exclude_list:
        if int(number) == exclude_number:
            new_list.remove(str(exclude_number))

# Add unavailable computers to exclude list and create final list to update the xml config (Get-InstalledApps2_config.xml)
send_to_ps = ""
for item in unavailable_list:
    if item not in exclude_list:
        exclude_list.append(item)
for i in exclude_list:
    send_to_ps += str(i) + ","

# Import xml file
xmlfile = "C:\\Users\\plp\\VsCodeProjects\\cobopipe_v02-001\\PowerShell\\Get-InstalledApps2_config.xml"
tree = et.parse(xmlfile)
root = tree.getroot()

# Update Get-InstalledApps2_config.xml with the final list and save. This config will be read by the GetInstalledApps2
root[0][0].text = send_to_ps[:-1]
tree.write(xmlfile)

# Check installed apps
RunPSScript("\\VsCodeProjects\\cobopipe_v02-001\\PowerShell\\Get-InstalledApps2.ps1")

with open("C:\\Users\\" + user + "\\VsCodeProjects\\cobopipe_v02-001\\PowerShell\\applist.json") as user_file:
    file_contents = user_file.read()

app_data = json.loads(file_contents)
app_dict = {}

# Get unique computer names
unique = set([i["PSComputerName"] for i in app_data])

# Create dictionary
for computer_name in unique:
    app_dict[computer_name] = SplitLists(computer_name)

# Delete the computer name key from the dictionary
for i in app_dict.values():
    for j in i:
        del j['PSComputerName']

# Print all results
for i, j in app_dict.items():
    print(i, j)
