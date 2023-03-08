import json
import os
import xml.etree.ElementTree as et

user = os.getlogin()
with open("C:\\Users\\" + user + "\\VsCodeProjects\\cobopipe_v02-001\\PowerShell\\complist.json") as user_file:
    file_contents = user_file.read()
ps_data = json.loads(file_contents)


host_info = {}
for item in ps_data:
    host_info[item["Name"]] = item['WinRMStatus']

for i, j in host_info.items():
    print(i, j)

delete_list = []
for i, j in host_info.items():
    if j == "":
        delete_list.append(i)

for i in delete_list:
    host_info.pop(i)

for i, j in host_info.items():
    print(i, j)