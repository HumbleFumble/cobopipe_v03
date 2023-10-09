#TODO changed this file to instead of trying to do the import operation, just deals with finding the correct file

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

import os
try:
    from ToonBoom import harmony
    in_toonboom = True
except Exception as e:
    in_toonboom = False

def log(message):
    if in_toonboom:
        sess = harmony.session()
        sess.log(str(message))
    else:
        print(message)

if os.environ.get("BOM_PIPE_PATH"):
    sys.path.append(os.environ["BOM_PIPE_PATH"])
    from getConfig import getConfigClass
    CC = getConfigClass()
    use_config = True
else:
    script_path = os.path.expandvars("%APPDATA%/Toon Boom Animation/Toon Boom Harmony Premium/2200-scripts/")
    sys.path.append(script_path) #Same dir as this script
    use_config = False

class ImportBackgroundDialog(QDialog):
    def __init__(self, parent=None):
        super(ImportBackgroundDialog, self).__init__(parent)
        self.start_folder = ""

    def browseDialog(self):
        find_file = QInputDialog()
        return None
    def FindFileBasedOnName(self,name):
        pass
    def getSearchName(self):
        ok = bool()
        # my_input = QInputDialog()
        text = QInputDialog.getText(self, "Find Background Dir:", "Name of Background: ", QLineEdit.Normal,
        QDir.home().dirName(), ok)
        if (ok and not text.isEmpty()):
            log("New " + text)
def run():
    to_run = ImportBackgroundDialog()
    result = to_run.browseDialog()
    return result

if __name__ == "__main__":
    to_run = ImportBackgroundDialog()
    to_run.getSearchName()