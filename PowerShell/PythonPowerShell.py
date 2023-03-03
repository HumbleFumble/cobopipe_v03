import subprocess
import json

# Using RUN
# prun = subprocess.run(['powershell', 'get-date'], stdout=subprocess.PIPE)
#
# print(p.stdout.decode())

# process = subprocess.Popen(["pwsh", 'C:/Users/plp/Desktop/PowerShell/getprogram.ps1'], stdout=subprocess.PIPE, stdin= subprocess.PIPE, text=True)
# process.communicate()
# stdout = process.stdout
# stdin = process.stdin
#
# # data = json.loads(stdout.read())
#
# print(stdout.read())

# encoding='cp1252'
# process = subprocess.Popen(["powershell", "C:\\Users\\plp\\Desktop\\PowerShell\\getprogram.ps1"], stdout=subprocess.PIPE, stdin=subprocess.PIPE, text=True)

#
# data = process.stdout

process = subprocess.Popen(["pwsh", "C:\\Users\\plp\\Desktop\\PowerShell\\getprogram.ps1"])
process.wait()

with open("C:\\Users\\plp\\Desktop\\PowerShell\\applist.json") as user_file:
  file_contents = user_file.read()
data = json.loads(file_contents)
user_file.close()

dict = {}

# for i in data:
#     dict[i['PSComputerName']] = None
# for i in data:
#     if i['PSComputerName'] in dict.keys():
#         for j in i:
#             i = j

# for i in data:
#     dict[i['PSComputerName']] = i
#     del [i['PSComputerName']]
#
# for i, j in dict.items():
#         print(i, j)

# def makeList(list, item):
#     temp = []
#     for i in list:
#         if i["PSComputerName"] == list2:
#             temp.append(i)
#     return temp
#
# makeList(unique, 'wsx22')

# Get unique names in the data to use as keys
unique = set([i["PSComputerName"] for i in data])

# Sort all entries in 'data' - create list of dictionaries for each computer name
def makeList(computer_name):
    temp_list = []
    for entry in data:
        if entry["PSComputerName"] == computer_name:
            temp_list.append(entry)
    return temp_list

for i in unique:
    dicts = makeList(i)
    dict[i] = dicts

# for i in dict["wsx2"]:
#     print(i['DisplayName'], i['DisplayVersion'])

for i, j in dict.items():
    print(i,j)