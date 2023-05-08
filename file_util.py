import os
import json
from Log.CoboLoggers import getLogger

logger = getLogger()


def create_folder(path):
    path = os.path.dirname(path)
    
    if not os.path.exists(path):
        return os.makedirs(path)
    
    return False


def save_json(save_location, save_info):
    with open(save_location, "w+") as saveFile:
        json.dump(obj=save_info, fp=saveFile, indent=4, sort_keys=True)
    saveFile.close()


def load_json(save_location):
    if os.path.isfile(save_location):
        with open(save_location, "r") as saveFile:
            loadedSettings = json.load(saveFile)
        if loadedSettings:
            return loadedSettings
    else:
        logger.debug("not a file: %s" % save_location)
    return None