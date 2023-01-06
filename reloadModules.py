# Original script by Nick Rodgers
# Source: https://medium.com/@nicholasRodgers/sidestepping-pythons-reload-function-without-restarting-maya-2448bab9476e

import inspect
import sys
import os
import importlib
from os.path import dirname, join

from Log.CoboLoggers import getLogger
logger = getLogger()



# Delete project modules to avoid restarting Autodesk Maya
def resetSession(userPath=None, ignore=[]):
    if userPath is None:
        userPath = os.path.abspath(os.path.join(__file__, ".."))
    userPath = userPath.lower()

    modulesToDelete = []
    # Iterate over all the modules that are currently loaded
    for key, module in sys.modules.items():
        # There's a few modules that are going to complain if you try to query them
        # so I've popped this into a try/except to keep it safe
        try:
            # Use the "inspect" library to get the moduleFilePath that the current module was loaded from
            moduleFilePath = inspect.getfile(module).lower()

            # Don't try and remove the startup script, that will break everything
            if moduleFilePath == __file__.lower():
                continue

            moduleFilePath = moduleFilePath.replace('/', os.sep)

            # If the module's filepath contains the userPath, add it to the list of modules to delete
            if moduleFilePath.startswith(userPath):
                #print(moduleFilePath)
                modulesToDelete.append(key)
                # if moduleFilePath.endswith('.pyc'): TO DELETE
                #     if moduleFilePath not in cleanedIgnore:
                #         filesToDelete.append(moduleFilePath)

        except:
            pass

    # Deleting modules
    logger.info('\n - Cleaning up modules')
    logger.info('________________________________________')
    for module in modulesToDelete:
        if module not in ignore:
            logger.info('|- ' + module)
            del (sys.modules[module])
    logger.info('')

    return modulesToDelete


#########################################

# Use when calling function in Maya
#
# sys.path.append('C:/Users/Mads/Documents/mh_tools')
#
# from mh_fileTools.reloadModules import resetSession
# resetSession()


# # So now you can either put this at the top of your script
# resetSessionForScript(r"C:\MyTool\TheToolIWantToRestart)
#
# # Or just
# resetSessionForScript()
#
# # Personally, I only want this behaviour to be called for me while I'm debugging so I'd probably add it in a condition like
# import getpass
#
# if getpass.getuser() == "nrodgers":
#     resetSessionForScript()

# # Or just for anyone running the tool from an IDE
# if __name__ == "__main__":
#     resetSessionForScript()

def reloadAll(userPath=None, ignore=[]):
    modulesToReload = resetSession(userPath, ignore)
    logger.info('\n - Reimporting modules')
    logger.info('________________________________________')
    for module in modulesToReload:
        if not module in ignore:
            logger.info('|- ' + module)
            importlib.import_module(module)
    logger.info('')
    return modulesToReload

def clearModules(modules):
    modulesToReturn = []
    logger.info('\n - Reimporting modules')
    logger.info('________________________________________')

    for loadedModule in list(sorted(sys.modules.keys())):
        for module in modules:
            if loadedModule.startswith(module):
                modulesToReturn.append(loadedModule)
                logger.info('|- ' + module)
                try:
                    del sys.modules[loadedModule]
                except:
                    pass
    logger.info('')

    return modulesToReturn