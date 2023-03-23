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

    def __init__(self, parent=None):
        self.ctrl = Controller()
        super(MainUI, self).__init__(parent)
        self.BuildUI()

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

        self.context_combo = QtWidgets.QComboBox() #This should say Shot-Anim/Shot-Comp/BG
        self.context_combo.addItems(["Shot-Anim","Shot-Comp","Background"])

        self.preset_combo = QtWidgets.QComboBox()  # This should preset where to look for things, like ftp or shot
        self.preset_combo.addItems(["From FTP: Unpack Zip",
                                         "From FTP: Move File",
                                         "From Project: Zip File",
                                         "From Project: Move File"])
        self.from_browse_bttn = QtWidgets.QPushButton("Browse")
        self.from_path_line = QtWidgets.QLineEdit("")


        self.main_lay.addLayout(self.context_lay)
        self.main_lay.addWidget(self.context_combo)
        self.main_lay.addWidget(self.preset_combo)

        self.main_lay.addWidget(self.from_path_line)
        self.main_lay.addWidget(self.from_browse_bttn)
        self.setLayout(self.main_lay)





if __name__ == '__main__':

    import sys

    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    mainWin = MainUI()
    mainWin.show()

    app.exec_()
