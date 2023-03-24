from PySide2 import QtWidgets, QtCore, QtGui


# from getConfig import getConfigClass
# CC = getConfigClass()
#
# from runtimeEnv import getRuntimeEnvFromConfig
# run_env = getRuntimeEnvFromConfig(config_class=CC)

class Controller:
    def __init__(self):
        super(Controller, self).__init__()



class MainUI(QtWidgets.QWidget):

    def __init__(self, parent=None,user=None,project=None,info=None):
        self.ctrl = Controller()
        super(MainUI, self).__init__(parent,user,project,info)
        self.project = project
        self.user = user
        self.BuildUI()
        self.preset_changed()
        self.preset_dict = {"Shot-Anim":{"FTP":"get_anim_shot"},"Shot-Comp":"get_shot_comp_folder"}

    def BuildUI(self):
        self.main_lay = QtWidgets.QVBoxLayout()

        self.context_lay = QtWidgets.QHBoxLayout()

        self.user_text = QtWidgets.QLineEdit() #This should have all users as easy options when you start typing?
        self.context_lay.addWidget(QtWidgets.QLabel("User: "))
        self.context_lay.addWidget(self.user_text)

        self.context_lay.addSpacing(25)
        self.project_combo = QtWidgets.QComboBox()
        self.context_lay.addWidget(QtWidgets.QLabel("Project: "))
        self.context_lay.addWidget(self.project_combo)


        self.preset_lay = QtWidgets.QHBoxLayout()
        self.context_combo = QtWidgets.QComboBox() #This should say Shot-Anim/Shot-Comp/BG
        self.context_combo.addItems(["Shot-Anim","Shot-Comp","Background"])
        self.preset_lay.addWidget(QtWidgets.QLabel("Context: "))
        self.preset_lay.addWidget(self.context_combo)

        self.preset_combo = QtWidgets.QComboBox()  # This should preset where to look for things, like ftp or shot
        self.preset_combo.addItems(["From FTP: Unpack Zip",
                                     "From FTP: Move File",
                                     "From Project: Zip File",
                                     "From Project: Move File",
                                    "Custom"])
        self.preset_lay.addWidget(QtWidgets.QLabel("Preset: "))
        self.preset_lay.addWidget(self.preset_combo)

        # self.main_lay.addSpacerItem()
        self.line = QtWidgets.QFrame()
        self.line.setFrameShape(QtWidgets.QFrame.HLine)


        self.from_lay = QtWidgets.QHBoxLayout()

        self.from_path_line = QtWidgets.QLineEdit("")
        self.from_browse_bttn = QtWidgets.QPushButton("Browse")
        self.from_lay.addWidget(QtWidgets.QLabel("File Source: "))
        self.from_lay.addWidget(self.from_path_line)
        self.from_lay.addWidget(self.from_browse_bttn)

        self.to_lay = QtWidgets.QHBoxLayout()

        self.to_path_line = QtWidgets.QLineEdit("")
        self.to_browse_bttn = QtWidgets.QPushButton("Browse")
        self.to_lay.addWidget(QtWidgets.QLabel("File Destination: "))
        self.to_lay.addWidget(self.to_path_line)
        self.to_lay.addWidget(self.to_browse_bttn)

        self.options_lay = QtWidgets.QHBoxLayout()
        self.overwrite_check = QtWidgets.QCheckBox("Overwrite")
        self.zip_check = QtWidgets.QCheckBox("Zip Source")
        self.unpack_check = QtWidgets.QCheckBox("Unpack Destination")
        self.create_history_check = QtWidgets.QCheckBox("Place Destination in _History folder")
        self.options_lay.addWidget(self.overwrite_check)
        self.options_lay.addWidget(self.zip_check)
        self.options_lay.addWidget(self.unpack_check)
        self.options_lay.addWidget(self.create_history_check)


        self.run_bttn = QtWidgets.QPushButton("RUN")


        self.main_lay.addLayout(self.context_lay)
        self.main_lay.addLayout(self.preset_lay)
        self.main_lay.addWidget(self.line)
        self.main_lay.addLayout(self.from_lay)
        self.main_lay.addLayout(self.to_lay)
        self.main_lay.addLayout(self.options_lay)
        self.main_lay.addWidget(self.run_bttn)

        self.setLayout(self.main_lay)
        self.preset_combo.currentTextChanged.connect(self.preset_changed)


    def preset_changed(self):
        state = self.preset_combo.currentText()
        if state == "From FTP: Unpack Zip":
            self.zip_check.setChecked(False)
            self.unpack_check.setChecked(True)
        if state == "From FTP: Move File":
            self.unpack_check.setChecked(False)
            self.zip_check.setChecked(False)
        if state == "From Project: Zip File":
            self.zip_check.setChecked(True)
            self.unpack_check.setChecked(False)
        if state == "From Project: Move File":
            self.unpack_check.setChecked(False)
            self.zip_check.setChecked(False)




if __name__ == '__main__':

    import sys

    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    mainWin = MainUI()
    mainWin.show()

    app.exec_()
