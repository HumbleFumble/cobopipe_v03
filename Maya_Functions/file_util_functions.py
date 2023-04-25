import os
import string
import random
from datetime import datetime


from Log.CoboLoggers import getLogger
logger = getLogger()
###################################################
############## FILE HANDLING ######################
###################################################


def getMayaFileType(file_path):
    maya_exten = file_path.split(".")[-1]
    if maya_exten == "ma":
        return "mayaAscii"
    else:
        return "mayaBinary"


def saveFile(save_location, save_info, overwrite=True):
    if overwrite:
        with open(save_location, 'w+') as saveFile:
            saveFile.write("%s\n" % (save_info))
    else:
        with open(save_location, 'a+') as saveFile:
            saveFile.write("%s\n" % (save_info))


def makeFolder(cur_path):
    cur_folder = os.path.dirname(cur_path)
    if os.path.exists(cur_folder):
        return True
    else:
        logger.warning("couldn't find folder. Creating it: %s" % cur_folder)
        os.makedirs(cur_folder)


# def saveJson(save_location, save_info):
#     import json
#     with open(save_location, 'w+') as saveFile:
#         json.dump(obj=save_info, fp=saveFile,indent=4, sort_keys=True)
#     saveFile.close()


# def loadJson(save_location):
#     import json
#     if os.path.isfile(save_location):
#         with open(save_location, 'r') as saveFile:
#             loadedSettings = json.load(saveFile)
#         if loadedSettings:
#             return loadedSettings
#     else:
#         logger.warning("not a file")
#     return None


def generateID(size=6, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

# def SaveJson(save_location, save_info):
#     with open(save_location, 'w+') as saveFile:
#         saveFile.write("%s\n" % (save_info))
#
# def LoadJson(save_location, save_info):
#     with open(save_location, 'w+') as saveFile:
#         saveFile.write("%s\n" % (save_info))


def createDirectory(directory):
    currentPath = ''
    for folder in directory.split('/'):
        if folder:
            currentPath = currentPath + folder + '/'
            if not os.path.exists(currentPath):
                os.mkdir(currentPath)


def SaveTempFile():
    import maya.cmds as cmds
    from Maya_Functions.delete_and_clean_up_functions import DeleteUnknown
    import random
    ##Save as temp file to check for problems##'
    try:
        if not os.path.exists("C:/Temp"):
            os.mkdir("C:/Temp")
        DeleteUnknown()
        cur_rand_num = random.randrange(1, 1000)
        temp_path = "C:/Temp/Publish_Temp_%s.ma" % cur_rand_num
        PrepareForSave(temp_path, ma=True)
        return temp_path
    except():
        return False


def TestAndSave(save_path): #Save function, tries to save file, if it succeed, rename and save as final output
    if Saving():
        PrepareForSave(save_path)
        Saving()
        return True
    else:
        # OpenFile(s_path)
        return False


def Saving(): ##SAVING## #TODO Look into if this even works. Try with a file that would fail to save.(has unknown plugin)
    import maya.cmds as cmds
    if not cmds.file(q=True,sn=True):
        print("NO SCENE NAME; SKIPPING SAVE")
        return True
    try:
        cmds.file(save=True)
        return True
    except:
        logger.warning("Not working!")
        return False


def PrepareForSave(cur_path,ma=False): #change filename and set file type to .mb
    import maya.cmds as cmds
    logger.info("Renaming scene to: %s" % cur_path)
    cmds.file(rename=cur_path)
    if ma:
        cmds.file(type="mayaAscii")
    else:
        cmds.file(type="mayaBinary")


def OpenFile(cur_file,compare_path=False):
    import maya.cmds as cmds
    if compare_path:
        logger.info("Currently open file: %s - Target file: %s" % (cmds.file(q=True,sn=True),cur_file))
        if cmds.file(q=True,sn=True) == cur_file:
            return False
    cmds.file(cur_file, open=True, f=True)

def runCmdsInMayaPy(content=""):
    from getConfig import getConfigClass
    CC = getConfigClass()
    from runtimeEnv import getRuntimeEnvFromConfig
    cur_run = getRuntimeEnvFromConfig(CC, True)
    import subprocess
    script_content = """import maya.standalone
maya.standalone.initialize('python')
import maya.cmds as cmds
import maya.mel as mel
{content}
""".format(content=content)
    script_content = ";".join(script_content.split("\n"))
    base_command = 'mayapy.exe -c "%s"' % (script_content)
    logger.info(base_command) #logger.info(base_command)
    p = subprocess.Popen(base_command, shell=False, universal_newlines=True,env=cur_run,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    s,e = p.communicate()
    print(s,e)

def runRemoveVirusInMayaPy(cur_file):
    # runRemoveVirusInMayaPy("P:/930383_KiwiStrit3/Production/Film/E06/E06_SQ010/E06_SQ010_SH020/01_Animation/E06_SQ010_SH020_Animation.ma")
    content="""import Maya_Functions.general_util_functions as gen_util
gen_util.openAndCleanFile('{cur_file}')""".format(cur_file=cur_file)
    runCmdsInMayaPy(content)


def publishOutdated(workFile=None, publishFile=None,time_difference=300):
    """
    Checks if work-file has been modified later than 5 minutes
    after the publish-file has been last modified

    :param workFile: Path to the work file
    :param publishFile:  Path to the publish file
    :return: Boolean
    """

    # Getting timestamp and converting it to datetime-object for both files
    workFileTimestamp = os.path.getmtime(workFile)
    workFileTime = datetime.fromtimestamp(round(workFileTimestamp))

    publishFileTimestamp = os.path.getmtime(publishFile)
    publishFileTime = datetime.fromtimestamp(round(publishFileTimestamp))

    # Calculating time difference
    timeDifference = workFileTime - publishFileTime

    # Converting time difference to an integer of seconds
    timeDifferenceInSeconds = int(timeDifference.total_seconds())

    # Checking if difference is more than 300 positive seconds
    if timeDifferenceInSeconds > time_difference:
        return timeDifference
    else:
        return False

def createFolderFromTemplate(destination=None,template_folder="3D_Shot_Template",create_folder=True):
    import shutil
    from getConfig import getConfigClass
    CC = getConfigClass()

    if not os.path.exists(destination):
        if create_folder:
            print(f'path: {destination}')
            #os.makedirs(destination)
        else:
            return False

    to_copy_path = "%s/%s" % (CC.get_template_path(),template_folder)
    if(os.path.exists(to_copy_path)):
        to_copy = os.listdir(to_copy_path)
        for content in to_copy:
            s_path = "%s/%s" % (to_copy_path, content)
            d_path = "%s/%s" % (destination, content)
            if os.path.isdir(s_path):
                if not os.path.exists(d_path):
                    shutil.copytree(s_path, d_path)
                    logger.info("COPYING: %s" % content)
    else:
        logger.warning("Can't find template folder: %s" % to_copy_path)
        return False
    return True

if __name__ == '__main__':
    makeFolder('W:/930507_Lego_Friends/Production/Pipeline/PublishReports/Film/E99/E99_SQ010')

    # publishOutdated('P:/930383_KiwiStrit3/Production/Film/E02/E02_SQ020/E02_SQ020_SH010/01_Animation/E02_SQ020_SH010_Animation.ma',
    #                 'P:/930383_KiwiStrit3/Production/Film/E02/E02_SQ020/E02_SQ020_SH010/04_Publish/E02_SQ020_SH010_AnimRef.mb')