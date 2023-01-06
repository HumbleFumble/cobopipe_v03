import sys
import os
import shutil
from subprocess import Popen, PIPE

""" This is a script to update the hotbar in Toon Boom Harmony

@echo off
T:/_Executables/python/Python310/python.exe T:/_Pipeline/cobopipe_v02-001/TB/updateHotbar.py
EXIT /B 0

"""  


def moveFilesInFolder(source, target):
    if os.path.exists(source):
        if os.path.isdir(source):
            for item in os.listdir(source):
                _sourceItem = os.path.abspath(os.path.join(source, item))
                _targetItem = os.path.abspath(os.path.join(target, item))
                if os.path.isdir(_sourceItem):
                    moveFilesInFolder(_sourceItem, _targetItem)
                elif os.path.isfile(_sourceItem):
                    if not os.path.exists(target):
                        os.makedirs(target)
                    if os.path.exists(_targetItem):
                        os.remove(_targetItem)
                    shutil.copyfile(_sourceItem, _targetItem)


def extendButtonlist(source, target):
    with open(source, 'r') as f:
        sourceData = f.read()
    sourceLines = sourceData.split('\n')
    
    with open(target, 'r') as f:
        targetData = f.read()
    targetLines = targetData.split('\n')
    
    linesToRemove = []
    for _line in targetLines:
        if "file=\"CB_" in _line:
            linesToRemove.append(_line)
            
    for i in linesToRemove:
        targetLines.remove(i)

    if '<Scripts>' in targetLines:
        index = targetLines.index('<Scripts>') + 1
    else:
        index = 2
        
    sourceLines.reverse()
    for currentLine in sourceLines:
        if currentLine not in targetLines:
            targetLines.insert(index, currentLine)

    with open(target, 'w') as f:
        f.write('\n'.join(targetLines))


def run(username):
    blacklist = ['bomadm']

    sourcePath = os.path.abspath(os.path.join(__file__, '../Scripting_Hotbars/Toon Boom Harmony Premium/2100-scripts'))

    proc = Popen("HarmonyPremium -v", stdout=PIPE, stderr=PIPE)
    stdout, stderr = proc.communicate()
    version = str(stderr).split(' version ')[-1].split(' build ')[0].replace('.', '')
    version = version[0:-1] + '0'
    print(f"Running on version {version}")

    if version:
        if username not in blacklist:
            targetPath = os.path.abspath("C:/Users/" + username + "/AppData/Roaming/Toon Boom Animation/Toon Boom Harmony Premium/"+ version + "-scripts")
            if not os.path.exists(targetPath):
                os.makedirs(targetPath)
            if os.path.exists(sourcePath) and os.path.exists(targetPath):
                _sourceItems = os.listdir(sourcePath)
                for item in _sourceItems:
                    _sourceItemPath = os.path.abspath(os.path.join(sourcePath, item))
                    _targetItemPath = os.path.abspath(os.path.join(targetPath, item))
                    if item not in ['buttonlist.xml']:
                        if os.path.isfile(_sourceItemPath):
                            if os.path.exists(_targetItemPath):
                                os.remove(_targetItemPath)
                            shutil.copyfile(_sourceItemPath, _targetItemPath)
                        elif os.path.isdir(_sourceItemPath):
                            moveFilesInFolder(_sourceItemPath, _targetItemPath)
                    elif item == 'buttonlist.xml':
                        if not os.path.exists(_targetItemPath):
                            shutil.copyfile(_sourceItemPath, _targetItemPath)
                        else:
                            extendButtonlist(_sourceItemPath, _targetItemPath)
                            
                print('\n>> Hotbar updated on ' + username + ' <<\n')
                
            else:
                print('\n>> Harmony not installed, skipping ' + username + ' <<\n')


if __name__ == '__main__':
    _users = ['freelance', 'mmcb', 'hojprod', 'borsteprod', 'mha']
    print(sys.argv[1:])
    if len(sys.argv) > 1:
        if 'all' in sys.argv[1:]:
            for username in _users:
                try:
                    run(username.lower())
                except Exception as e:
                    print(e)
                
        else:
            for arg in sys.argv[1:]:
                try:
                    run(arg.lower())
                except Exception as e:
                    print(e)
    else:
        if os.getlogin().lower() == 'royalrender':
            for username in _users:
                try:
                    run(username.lower())
                except Exception as e:
                    print(e)
        else:
            try:
                run(os.getlogin().lower())
            except Exception as e:
                    print(e)