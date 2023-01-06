import os
import re
from getConfig import getConfigClass
CC = getConfigClass()
from Maya_Functions.file_util_functions import saveJson, loadJson

def getComps(episodes):
    _list = []
    for eFolder in os.listdir(CC.get_film_path()):
        if eFolder[0] == 'E' and eFolder[1:].isdigit():
            if int(eFolder[1:]) in episodes:
                # Currently we know the folder is a valid episode within the set range.
                eFolderPath = os.path.join(CC.get_film_path(), eFolder).replace(os.sep, '/')
                for sqFolder in os.listdir(eFolderPath):
                    if sqFolder.split('_')[-1][:2] == 'SQ' and sqFolder.split('_')[-1][2:].isdigit():
                        sqFolderPath = os.path.join(eFolderPath, sqFolder).replace(os.sep, '/')
                        for shFolder in os.listdir(sqFolderPath):
                            if shFolder.split('_')[-1][:2] == 'SH' and shFolder.split('_')[-1][2:].isdigit():
                                shFolderPath = os.path.join(sqFolderPath, shFolder).replace(os.sep, '/')
                                compFolderPath = os.path.join(shFolderPath, '03_Comp').replace(os.sep, '/')
                                if os.path.exists(compFolderPath):
                                    latestCompFile = None
                                    latestVersion = None
                                    for compFile in os.listdir(compFolderPath):
                                        if compFile.endswith('.comp'):
                                            version = compFile.split('_')[-1].replace('.comp', '')
                                            if version:
                                                if version[0] == 'V':
                                                    if version[1:].isdigit():
                                                        if not latestVersion:
                                                            latestVersion = int(version[1:])
                                                            latestCompFile = compFile
                                                        elif int(version[1:]) > latestVersion:
                                                            latestVersion = int(version[1:])
                                                            latestCompFile = compFile
                                    if latestCompFile:
                                        _list.append(os.path.join(compFolderPath, latestCompFile).replace(os.sep, '/'))
    return _list


def getCurrentPasses(compFile):
    passes = []
    with open(compFile, 'r') as comp_file:
        fileContent = comp_file.read()

        # Compiling regex pattern
        regexPattern = re.compile('Filename = "%s.*"' % CC.get_film_path())

        # Finding all matches to compiled regex pattern
        regexResults = regexPattern.findall(fileContent)
        passDirectories = []
        active_pass = ""
        for regexResult in set(regexResults):
            currentPath = regexResult.split('"')[1].replace(os.sep, '/')
            while '//' in currentPath:
                currentPath = currentPath.replace('//', '/')
            if "/Passes/" in currentPath:
                passDirectories.append(currentPath)

        for passDirectory in passDirectories:
            currentPass = passDirectory.split("/Passes/")[1].split("/")[0]
            if currentPass not in passes:
                passes.append(currentPass)

    comp_file.close()
    return passes


def getCutOffDate(passesFolder, currentPasses):
    cutOffDate = None
    for item in os.listdir(passesFolder):
        if item in currentPasses:
            itemPath = os.path.join(passesFolder, item).replace(os.sep, '/')
            lastModifiedList = []
            if os.path.isdir(itemPath):
                currentLastModifiedList = []
                for file in os.listdir(itemPath):
                    filePath = os.path.join(itemPath, file).replace(os.sep, '/')
                    currentLastModifiedList.append(os.path.getmtime(filePath))
                if currentLastModifiedList:
                    lastModifiedList.append(min(currentLastModifiedList))
            if lastModifiedList:
                cutOffDate = min(lastModifiedList)
    return cutOffDate


def getAllFiles(path):
    _list = []
    if os.path.exists(path):
        for item in os.listdir(path):
            currentPath = os.path.join(path, item).replace(os.sep, '/')
            if os.path.isdir(currentPath):
                output = getAllFiles(currentPath)
                for outputFile in output:
                    _list.append(outputFile)
            elif os.path.isfile(currentPath):
                _list.append(currentPath)
        return _list


def getObsoleteFiles(compFile, currentPasses):
    passesFolder = os.path.abspath(os.path.join(os.path.dirname(compFile), '../Passes/')).replace(os.sep, '/')
    cutOffDate = getCutOffDate(passesFolder, currentPasses)
    allFiles = getAllFiles(passesFolder)
    obsoleteFiles = []
    for file in allFiles:
        if cutOffDate:
            if os.path.getmtime(file) < cutOffDate:
                obsoleteFiles.append(file)
    return obsoleteFiles


def createListFile(_list):
    file = os.path.join(CC.get_base_path(), 'Pipeline/obsolete_files_list.json').replace(os.sep, '/')
    saveJson(file, _list)
    return file


def userAgree(_string):
    check = str(input(_string)).lower().strip()
    try:
        if check[0] == 'y':
            return True
        elif check[0] == 'n':
            return False
        else:
            print('Invalid Input')
            return userAgree(_string)
    except Exception as error:
        print("Please enter valid inputs")
        print(error)
        return userAgree(_string)


def nuke(_list):
    folders = []
    for file in _list:
        if os.path.exists(file):
            print('>> Deleting ' + file)
            os.remove(file)
        folder = os.path.dirname(file)
        if folder not in folders:
            folders.append(folder)
    for folder in folders:
        if os.path.exists(folder):
            if os.listdir(folder) == []:
                print('>> Deleting ' + folder)
                os.rmdir(folder)


def run(episodes):
    _list = []
    print('\n>> Finding all compositing files.\n')
    for compFile in getComps(episodes):
        print('>> Finding obsolete files for ' + compFile.split('/')[-1][:-15])
        currentPasses = getCurrentPasses(compFile)
        obsoleteFiles = getObsoleteFiles(compFile, currentPasses)
        _list = _list + obsoleteFiles

    if userAgree('\n>> Save a list of the obsolete files? (Y/N): '):
        print(createListFile(_list))

    if userAgree('\n>> Calculate file-size of obsolete files? (Y/N):'):
        print('\n>> Calculating file-size.')
        size = 0
        for item in _list:
            size = size + os.path.getsize(item)

        sizeConverted = float("{0:.2f}".format(size / (1024 * 1024 * 1024)))
        print('\n>> Collective file-size: ' + str(sizeConverted) + ' GB')

    if userAgree("\n>> Do you want to delete? (Y/N): "):
        print('\n>> Deleting files\n')
        nuke(_list)


if __name__ == '__main__':
    # run([15, 2, 3, 4, 14, 6, 5, 7, 8, 1, 10, 9])
    run([11, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24])