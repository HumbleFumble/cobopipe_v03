from PySide6 import QtWidgets, QtCore, QtGui
import os
import sys
import subprocess


# from getConfig import getConfigClass
# CC = getConfigClass()
#
# from runtimeEnv import getRuntimeEnvFromConfig
# run_env = getRuntimeEnvFromConfig(config_class=CC)


class Controller:
    def __init__(self):
        super(Controller, self).__init__()


class MainUI(QtWidgets.QWidget):
    def __init__(self, parent=None, user=None, project=None):
        self.ctrl = Controller()
        super(MainUI, self).__init__(parent)
        self.project = project
        self.user = user
        self.BuildUI()
        self.preset_changed()

    def BuildUI(self):
        self.main_lay = QtWidgets.QVBoxLayout()

        self.context_lay = QtWidgets.QHBoxLayout()

        self.user_text = (
            QtWidgets.QLineEdit()
        )  # This should have all users as easy options when you start typing?
        self.context_lay.addWidget(QtWidgets.QLabel("User: "))
        self.context_lay.addWidget(self.user_text)

        self.context_lay.addSpacing(25)
        self.project_combo = QtWidgets.QComboBox()
        self.context_lay.addWidget(QtWidgets.QLabel("Project: "))
        self.context_lay.addWidget(self.project_combo)

        self.preset_lay = QtWidgets.QHBoxLayout()
        self.context_combo = (
            QtWidgets.QComboBox()
        )  # This should say Shot-Anim/Shot-Comp/BG
        self.context_combo.addItems(["Shot-Anim", "Shot-Comp", "Background"])
        self.preset_lay.addWidget(QtWidgets.QLabel("Context: "))
        self.preset_lay.addWidget(self.context_combo)

        self.preset_combo = (
            QtWidgets.QComboBox()
        )  # This should preset where to look for things, like ftp or shot
        self.preset_combo.addItems(
            [
                "From FTP: Unpack Zip",
                "From FTP: Move File",
                "From Project: Zip File",
                "From Project: Move File",
                "Custom",
            ]
        )
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
        self.create_history_check = QtWidgets.QCheckBox(
            "Place Destination in _History folder"
        )
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


class ReturnAnim(QtWidgets.QWidget):
    def __init__(self, parent=None, user=None, project=None):
        super(ReturnAnim, self).__init__(parent)
        self.user = user
        self.project = project
        self.build_ui()

    def build_ui(self):
        self.setWindowTitle("ReturnAnim")

        # CREATING
        self.main_layout = QtWidgets.QVBoxLayout()
        self.settings_layout = QtWidgets.QHBoxLayout()
        self.browse_layout = QtWidgets.QHBoxLayout()
        self.submit_layout = QtWidgets.QHBoxLayout()

        self.user_layout = QtWidgets.QHBoxLayout()
        self.user_label = QtWidgets.QLabel("User:")
        self.user_label.setMinimumWidth(40)
        self.user_label.setMaximumWidth(40)
        self.user_input = QtWidgets.QLineEdit()
        self.user_input.insert(self.user)

        self.project_layout = QtWidgets.QHBoxLayout()
        self.project_label = QtWidgets.QLabel("Project:")
        self.project_label.setMinimumWidth(40)
        self.project_input = QtWidgets.QLineEdit()
        self.project_input.insert(self.project)

        self.browse_label = QtWidgets.QLabel("File:")
        self.browse_label.setMinimumWidth(40)
        self.browse_input = QtWidgets.QLineEdit()
        self.browse_button = QtWidgets.QPushButton("Browse")

        self.submit_button = QtWidgets.QPushButton("Submit")
        self.submit_button.setMinimumWidth(120)
        self.submit_button.setMaximumWidth(120)
        self.submit_button.setMinimumHeight(40)

        # ASSEMBLING
        self.main_layout.addLayout(self.settings_layout)
        self.main_layout.addLayout(self.browse_layout)
        self.main_layout.addStretch()
        self.main_layout.addLayout(self.submit_layout)

        self.settings_layout.addLayout(self.user_layout)
        self.settings_layout.addSpacerItem(QtWidgets.QSpacerItem(50, 0))
        self.settings_layout.addLayout(self.project_layout)

        self.user_layout.addWidget(self.user_label)
        self.user_layout.addWidget(self.user_input)

        self.project_layout.addWidget(self.project_label)
        self.project_layout.addWidget(self.project_input)

        self.browse_layout.addWidget(self.browse_label)
        self.browse_layout.addWidget(self.browse_input)
        self.browse_layout.addWidget(self.browse_button)

        self.submit_layout.addWidget(self.submit_button)

        # CONNECTING
        self.browse_button.clicked.connect(
            lambda: self.browse_input.insert(
                QtWidgets.QFileDialog.getOpenFileName(
                    parent=self, caption="Select File", filter="XSTAGE File (*.xstage)"
                )[0]
            )
        )
        self.submit_button.clicked.connect(self.submit)

        self.setLayout(self.main_layout)

    def submit(self):
        if not self.user_input.text():
            alert(self, message="Please enter a valid user.")
            return False
        if not self.project_input.text():
            alert(self, message="Please enter a valid project.")
            return False

        file = self.browse_input.text()

        # python "C:\Users\mha\Projects\cobopipe_v02-001\TB\CB_increment_folder.py" "C:\Program Files (x86)\Toon Boom Animation\Toon Boom Harmony 22 Premium\win64\bin\python-packages" "P:\930462_HOJ_Project\Production\Film\S107\S107_SQ010\S107_SQ010_SH010\S107_SQ010_SH010_V002\S107_SQ010_SH010_V002.xstage"
        
        if not os.path.exists(file):
            alert(self, message='Please enter a valid file path.')
            return False

        harmonypremium = (
            subprocess.check_output(["where", "harmonypremium.exe"])
            .decode("UTF-8")
            .replace("\n", "")
            .replace("\r", "")
        )

        if not os.path.exists(harmonypremium):
            alert(self, message="Cannot find Harmony Premium executable.")
            return False

        harmony_python_packages = os.path.join(
            os.path.dirname(harmonypremium), "python-packages"
        )

        subprocess.Run(f'python "" "{}" "{}"')

        from getConfig import getConfigClass

        CC = getConfigClass(project_name=self.project_input.text())
        folder = os.path.dirname(file)
        zip_file = f"{folder}.zip"

        popup, msg = alert(self, message='Wait.. File is currently being compressed.')
        import zipUtil
        zipUtil.zip(folder, zip_file)
        msg.setText('Wait.. File is currently being uploaded to FTP.')
        QtWidgets.QApplication.processEvents()
        import ftpUtil
        files_objects = [
            {
                "file": zip_file,
                "destination": f"_ANIMATION/{self.user_input.text()}/TO_CB/",
            }
        ]
        result = ftpUtil.upload(
            files_objects,
            CC.project_settings.get("ftp_local_host"),
            CC.project_settings.get("ftp_username"),
            CC.project_settings.get("ftp_password"),
        )
        if result:
            popup.setWindowTitle('Success')
            msg.setText('File has finished uploading.')
            QtWidgets.QApplication.processEvents()
        else:
            popup.setWindowTitle('Error')
            msg.setText('An error has occurred.\nTry Again or contact a TD.')
            QtWidgets.QApplication.processEvents()


def alert(parent, title="Alert", message=""):
    popup = Popup(parent, title)
    popup.resize(300, 50)
    alert_layout = QtWidgets.QVBoxLayout()
    msg = QtWidgets.QLabel(message)
    msg.setAlignment(QtCore.Qt.AlignCenter)
    popup.setLayout(alert_layout)
    alert_layout.addWidget(msg)
    popup.show()
    return popup, msg


class Popup(QtWidgets.QDialog):
    def __init__(self, parent=None, title="Popup"):
        super(Popup, self).__init__(parent)
        self.setWindowTitle(title)
        flags = self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint
        flags = flags | QtCore.Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)


if __name__ == "__main__":
    import sys

    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    # mainWin = MainUI()
    # mainWin.show()
    window = ReturnAnim(user="Mads", project="Hoj")
    window.show()

    app.exec()
