import subprocess
import json
import os
import xml.etree.ElementTree as et

user = os.getlogin()


# Run GetHostInfo_SB.ps1 if there is a change in the list of available computers, for example if a computer had to be
# turned on; this can take some time and slow down the script, so it should be run only if there is a change in the
# available computers.
def RunPSScript(script_path, run=None):
    # Run GetHostInfo_SB.ps1. This script checks which computers are online and outputs to "complist.json"
    if run:
        process = subprocess.Popen(["pwsh", "C:\\Users\\" + user + script_path])
        process.wait()
    else:
        pass


RunPSScript("\\VsCodeProjects\\cobopipe_v02-001\\PowerShell\\ScriptBlocks\\GetHostInfo_SB.ps1", run=False)


def SplitLists(computer):
    app_list = []
    for each_dict in app_data:
        if each_dict['PSComputerName'] == computer:
            app_list.append(each_dict)

    return app_list


# Print status for missing or installed
def SortByStatus(missing=None, installed=None):
    new_dict = {}

    for computer_name in unique:
        dict_list = []
        for computer, _value in app_dict.items():
            for each in _value:
                if missing:
                    if each["Status"] == "Missing":
                        if computer == computer_name:
                            dict_list.append(each)
                elif installed:
                    if each["Status"] == "Installed":
                        dict_list.append(each)


        new_dict[computer_name] = dict_list

    return new_dict

# Create a list of computers, in which only computers that are available and not in the exclude list are present
def GetList(exclude_list):
    new_list = []
    unavailable_list = []
    for key, _value in host_info.items():
        if _value == "":
            unavailable_list.append(int(key.replace("wsx", "")))

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
    # This list will be saved in xml file and read by the install script
    send_to_ps = ""
    for _item in unavailable_list:
        if _item not in exclude_list:
            exclude_list.append(_item)
    for i in exclude_list:
        send_to_ps += str(i) + ","

    return send_to_ps


# Import computers list json file, produced by GetHostInfo_SB.ps1
with open("C:\\Users\\" + user + "\\VsCodeProjects\\cobopipe_v02-001\\PowerShell\\complist.json") as user_file:
    file_contents = user_file.read()
ps_data = json.loads(file_contents)

# Create dictionary with available computers and display the result
host_info = {}
for item in ps_data:
    host_info[item["Name"]] = item['WinRMStatus']

exclude_computer_number = [3, 4, 5, 12]


# Import xml file
xmlfile = "C:\\Users\\plp\\VsCodeProjects\\cobopipe_v02-001\\PowerShell\\Get-InstalledApps2_config.xml"
tree = et.parse(xmlfile)
root = tree.getroot()

# Update Get-InstalledApps2_config.xml with the final list and save. This config will be read by the GetInstalledApps2
root[0][0].text = GetList(exclude_computer_number)
tree.write(xmlfile)

print(GetList(exclude_computer_number))

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
for value in app_dict.values():
    for item in value:
        del item['PSComputerName']
        del item['DisplayVersion']

# Print all results
# for computer_name, v in app_dict.items():
#     print(computer_name, v)


result = SortByStatus(missing=True)
for key, value in result.items():
    print(key, value)


with open("C:\\Users\\" + user + "\\VsCodeProjects\\cobopipe_v02-001\\PowerShell\\install_apps.json", "w") as outfile:
    json.dump(result, outfile)