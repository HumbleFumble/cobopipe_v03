#TODO changed this file to instead of trying to do the import operation, just deals with finding the correct file
#
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

import os
import sys
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
        self.start_folder = "P:/930462_HOJ_Project/Production/Asset/Environment/"
        self.file_folder = self.start_folder
        self.setWindowTitle("Import Background")




    def dialogWindow(self):
        self.main_layout = QVBoxLayout()
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("Search from this Folder: "))
        self.search_dir_text = QLineEdit(self.start_folder)
        self.search_dir_bttn = QPushButton("Browse")
        self.search_dir_bttn.clicked.connect(self.browse_folder)
        dir_layout.addWidget(self.search_dir_text)
        dir_layout.addWidget(self.search_dir_bttn)

        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("Name To Search For: "))
        self.search_filename_text = QLineEdit("")
        self.search_filename_bttn = QPushButton("Search!")
        self.search_filename_bttn.clicked.connect(self.find_bttn_call)
        file_layout.addWidget(self.search_filename_text)
        file_layout.addWidget(self.search_filename_bttn)

        final_layout = QHBoxLayout()
        final_layout.addWidget(QLabel("Final Path: "))
        self.final_path_text = QLineEdit("")
        self.final_path_bttn = QPushButton("Browse")
        final_layout.addWidget(self.final_path_text)
        final_layout.addWidget(self.final_path_bttn)
        self.final_path_bttn.clicked.connect(self.final_path_bttn_call)

        self.import_button = QPushButton("Import Background")
        self.main_layout.addLayout(dir_layout)
        self.main_layout.addLayout(file_layout)
        self.main_layout.addLayout(final_layout)
        self.main_layout.addWidget(self.import_button)
        self.setLayout(self.main_layout)

        self.resize(700,150)
        self.show()


    # def browseDialog(self):
    #     find_file = QInputDialog()
    #     return None
    # def FindFileBasedOnName(self,name):
    #     self.find_files()
    #     pass
    def find_bttn_call(self):
        dir_name = self.search_dir_text.text()
        filename = self.search_filename_text.text()
        ff = None
        if filename and dir_name:
            if os.path.exists(dir_name):
                if os.path.isdir(dir_name):
                    ff = self.find_files(names=[filename],base_path=dir_name)
        if ff:
            final = self.browse_file(start_folder=os.path.dirname(ff[0]))
            if final:
                self.final_path_text.setText(final)

        else:
            log("No files found with that name")
    def final_path_bttn_call(self):
        file = self.browse_file(start_folder=self.start_folder)
        if file:
            self.final_path_text.setText(file)
        else:
            log("No file picked")

    # def getSearchName(self):
    #     my_input = QInputDialog()
    #     text = QInputDialog.getText(my_input, "Find Background Dir:", "Name of Background: ", QLineEdit.Normal,
    #     "")
    #     log(text)
    #     if (text[1] and text[0]):
    #         log("New " + text[0])
    #         return text[0]
    #     else:
    #         return False
    def browse_file(self, start_folder=""):
        fdia = QFileDialog.getOpenFileName(parent=self, caption="Pick File", dir=start_folder,
                                            filter="PSD Files (*.psd)")
        if fdia:
            return fdia[0]
        else:
            return False

    def browse_folder(self):
        fdia = QFileDialog.getExistingDirectory(parent=self, caption="Pick Folder",dir=self.search_dir_text.text())
        print(fdia)
        if fdia:
            self.search_dir_text.setText(fdia)
    def find_files(self, names=[], base_path=""):
        return_list = []
        for root, folder, files in os.walk(base_path):
            for cur_file in files:
                if any(name.lower() in cur_file.lower() for name in names):
                    if "anim" in root.lower():
                        file_path = (
                            os.path.join(root, cur_file)
                            .replace(os.sep, "/")
                            .replace("//", "\\\\")
                        )
                        return_list.append(file_path)
        return return_list


def run():
    to_run = ImportBackgroundDialog()
    result = to_run.dialogWindow()
    return result

if __name__ == '__main__':
    import sys
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    # t = PreviewPython_UI()
    # t.show()
    # app.exec()
    to_run = ImportBackgroundDialog()
    to_run.dialogWindow()
    app.exec()
    # to_run.getSearchName()