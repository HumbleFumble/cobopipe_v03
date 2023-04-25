from PySide6 import QtWidgets, QtCore, QtGui
import os
import sys
# import json
import subprocess
import file_util


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
    def __init__(self, parent=None):
        super(ReturnAnim, self).__init__(parent)
        self.settings_file_path = r"C:\Temp\ReturnAnim\settings.json"
        self.user, self.project = self.get_settings()
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

    def get_settings(self):
        if not os.path.exists(self.settings_file_path):
            os.makedirs(os.path.dirname(self.settings_file_path))
            settings = {"user": None, "project": None}
            # saveJson(self.settings_file_path, settings)
            file_util.save_json(self.settings_file_path, settings)
        else:
            settings = file_util.load_json(self.settings_file_path)
        return settings.get("user"), settings.get("project")

    def set_settings(self, settings):
        # saveJson(self.settings_file_path, settings)
        file_util.save_json(self.settings_file_path, settings)

    def submit(self):
        if not self.user_input.text():
            alert(self, message="Please enter a valid user.")
            return False
        if not self.project_input.text():
            alert(self, message="Please enter a valid project.")
            return False

        self.set_settings(
            {"user": self.user_input.text(), "project": self.project_input.text()}
        )

        selected_file = self.browse_input.text()

        if not os.path.exists(selected_file):
            alert(self, message="Please enter a valid file path.")
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

        popup, msg = alert(self, message="Wait.. Saving new version in a folder.")
        QtWidgets.QApplication.processEvents()
        script_path = r"\\192.168.0.225\tools\_Pipeline\cobopipe_v02-001\TB\CB_increment_folder.py"
        command = (
            f'python "{script_path}" "{harmony_python_packages}" "{selected_file}"'
        )
        
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        
        stdout, stderr = process.communicate()
        stdout = stdout.decode("UTF-8").replace("\r", "")
        stderr = stderr.decode("UTF-8").replace("\r", "")

        file = stdout.split("\n")[-2]
        if not os.path.exists(file):
            msg.setText('Error: Failed to increment version.\nCheck for naming issues or contact a TD.')
            QtWidgets.QApplication.processEvents()
            return False
        
        folder = os.path.dirname(file)
        zip_file = f"{folder}.zip"

        msg.setText("Wait.. File is currently being compressed.")
        QtWidgets.QApplication.processEvents()
        import zipUtil

        if os.path.exists(r"C:\Program Files\7-Zip\7z.exe"):
            zipUtil.zip_7z(folder, zip_file)
        else:
            zipUtil.zip(folder, zip_file)
        msg.setText("Wait.. File is currently being uploaded to FTP.")
        QtWidgets.QApplication.processEvents()
        from getConfig import getConfigClass

        CC = getConfigClass(project_name=self.project_input.text())
        import ftpUtil

        files_objects = [
            {
                "file": zip_file,
                "destination": f"_ANIMATION/{self.user_input.text()}/TO_CB/",
            }
        ]
        try:
            result = ftpUtil.upload(
                files_objects,
                CC.project_settings.get("ftp_local_host"),
                CC.project_settings.get("ftp_username"),
                CC.project_settings.get("ftp_password"),
            )

            os.remove(zip_file)
            if result:
                popup.setWindowTitle("Success")
                msg.setText("File has finished uploading.")
                QtWidgets.QApplication.processEvents()
            else:
                popup.setWindowTitle("Error")
                msg.setText("An error has occurred.\nTry Again or contact a TD.")
                QtWidgets.QApplication.processEvents()
        except Exception as e:
            msg.setText("Error: Failed to upload to FTP.\nTry again or contact a TD.")
            QtWidgets.QApplication.processEvents()
            os.remove(zip_file)


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


# def saveJson(save_location, save_info):
#     with open(save_location, "w+") as saveFile:
#         json.dump(obj=save_info, fp=saveFile, indent=4, sort_keys=True)


# def loadJson(save_location):
#     if os.path.isfile(save_location):
#         with open(save_location, "r") as saveFile:
#             loadedSettings = json.load(saveFile)
#         if loadedSettings:
#             return loadedSettings
#     return None


if __name__ == "__main__":
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    # mainWin = MainUI()
    # mainWin.show()
    window = ReturnAnim()
    window.show()

    app.exec()
