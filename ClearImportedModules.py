import sys
"""
import ClearImportedModules as CIM
CIM.dropCachedImports("YourScript","NameOfAnotherScriptFile)

import YourScript
reload(YourScript)
YourScript.Run()
"""
def dropCachedImports(*packagesToUnload):
    '''
    prepares maya to re-import
    '''

    def shouldUnload(module):
        for packageToUnload in packagesToUnload:
            if module.startswith(packageToUnload):
                return True
        return False
    # print("Modules loaded!:\n")
    for i in list(sorted(sys.modules.keys())):
        # print(i)
        if shouldUnload(i):
            print("unloading module: ", i)
            del sys.modules[i]