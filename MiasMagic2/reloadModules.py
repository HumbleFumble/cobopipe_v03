# Original script by Nick Rodgers
# Source: https://medium.com/@nicholasRodgers/sidestepping-pythons-reload-function-without-restarting-maya-2448bab9476e

import inspect
import sys
import os
from os.path import dirname, join


# Delete project modules to avoid restarting Autodesk Maya
def resetSession(userPath=None):
    if userPath is None:
        userPath = os.path.abspath(os.path.join(__file__, ".."))
    userPath = userPath.lower()

    modulesToDelete = []
    # Iterate over all the modules that are currently loaded
    for key, module in sys.modules.iteritems():
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

        except:
            pass

    # Deleting modules
    print('\n - Cleaning up modules')
    print('________________________________________')
    for module in modulesToDelete:
        print('|- ' + module)
        del (sys.modules[module])
    print('')

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