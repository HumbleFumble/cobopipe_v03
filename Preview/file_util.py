import os
from getConfig import getConfigClass
CC = getConfigClass()

from Log.CoboLoggers import getLogger
logger = getLogger()

def makeTempFile(path):
    file_path, extension = path.split(".")
    temp_path = "%s_ffmpeg_Temp.%s" % (file_path,extension)
    import shutil
    shutil.copy(path,temp_path)
    return temp_path

def isOutdated(source_file, output_file, greaterThan=0):
    source_date = os.path.getmtime(source_file)
    output_date = os.path.getmtime(output_file)
    if output_date < source_date:
        if greaterThan < 0:
            return True
        else:
            difference_in_minutes = (source_date - output_date)/60
            if float(greaterThan) < difference_in_minutes:
                return True
    return False

def previewOutdatedComp(shot):
    """Determines if a shot's comp preview is out of date

    Args:
        shot (str): shotname as string (example 'E01_SQ010_SH010')

    Returns:
        bool: Returns True if outdated
    """
    #print(shot)
    comp_output_folder = CC.get_shot_comp_output_folder(*shot.split('_'))
    if os.listdir(comp_output_folder):
        preview_file = CC.get_shot_comp_preview_file(*shot.split('_'))
        if os.path.exists(preview_file):
            for file in os.listdir(comp_output_folder):
                if file.endswith('.exr'):
                    comp_output_file = os.path.join(comp_output_folder, file).replace(os.sep, '/')
                    break
            if isOutdated(comp_output_file, preview_file):
                return True
        else:
            return True
    return False

def previewOutdatedAnim(shot):
    """Determines if a shot's comp preview is out of date

    Args:
        shot (str): shotname as string (example 'E01_SQ010_SH010')

    Returns:
        bool: Returns True if outdated
    """
    anim_file = CC.get_shot_anim_path(*shot.split('_'))
    preview_file = CC.get_shot_anim_preview_file(*shot.split('_'))
    if os.path.exists(preview_file):
        if isOutdated(anim_file, preview_file, greaterThan=5):
            return True
    else:
        return True
    return False


def isFileLocked(path):
    logger.debug("Check if %s is locked" % path)
    renamed_path = "%s_lockCheck." % path.split(".")[0] + path.split(".")[1]
    print(renamed_path)
    try:
        os.rename(path, renamed_path)
        os.rename(renamed_path, path)
        return False
    except Exception as e:
        if not str(e) == '[Error 32] The process cannot access the file because it is being used by another process':
            print(e)
    return True