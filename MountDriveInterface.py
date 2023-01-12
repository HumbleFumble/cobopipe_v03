import string

from PySide2 import QtWidgets, QtCore, QtGui
import subprocess
import os
path = r"\\192.168.0.235\projekter"
letter = "p"
user = r"CPHBOM\freelance"
password = "freelance"


def mapDrive(path="",letter="",user=None,password=None, force=True):

    # Disconnect anything on letter
    if force:
        subprocess.call('net use %s: /del /Y' % letter, shell=True)
    else:
        subprocess.call('net use %s: /del' % letter, shell=True)

    # Connect to shared drive, use drive letter given
    if user and password:
        subprocess.call('net use %s: %s /user:%s %s' % (letter, path, user,password), shell=True)
    else:
        subprocess.call('net use %s: %s' % (letter, path), shell=True)

#mapDrive(path, letter,user,password)

class DriveDialog(QtWidgets.QDialog):
    def __init__(self):
        super(DriveDialog, self).__init__()
        """
        Get user? add CPHBOM\ infront?
        Get password?
        Ask for them at beginning?
        Save passwords as Hash5 cryptation?
        List of drives available?
        Check for os type?
        """
        self.user = os.getlogin()
        self.password = ""
        self.drive_dict = {}
        self.drive_dict["production"] = {"letter":"p","win_path":r"\\192.168.0.225\production",
                                         "info":"The production drive on our new server"}
        self.drive_dict["projekter"] = {"letter":"p","win_path":r"\\192.168.0.235\projekter",
                                         "info":"The old 'p-drive', home of all our old productions"}
        self.drive_dict["ftp-prod"] = {"letter":"v","win_path":r"\\192.168.0.225\ftpprod",
                                         "info":"The production drive on our new server"}
        self.drive_dict["WFH"] = {"letter":"w","win_path":r"\\192.168.0.225\WFH",
                                         "info":"Work for Hire projects, access is limited for each project"}
        self.drive_dict["udvikling"] = {"letter": "u", "win_path": r"\\192.168.0.225\udvikling",
                                  "info": "The place for everything not ready for production"}
        self.createWindow()
        self.populate()

    def askForUserPass(self):
        self.d = LoginForm()
        if self.d.exec_():
            print("yeah")
        else:
            print("nay")


    def populate(self):
        self.preset_combo.addItems(sorted(self.drive_dict.keys()))
        for s in string.ascii_uppercase:
            self.letter_edit.addItem("%s:" % s)
            # print("%s:" % s)
        self.preset_combo.currentTextChanged.connect(self.setPreset)
        self.setPreset()
    def createWindow(self):
        self.layout_top = QtWidgets.QVBoxLayout(self)

        self.user_lay = QtWidgets.QHBoxLayout()
        self.user_label_info = QtWidgets.QLabel("User: ")
        self.user_label = QtWidgets.QLabel(self.user)
        self.user_checkbox = QtWidgets.QCheckBox("Use current")
        self.user_checkbox.setChecked(True)
        self.user_lay.addWidget(self.user_label_info)
        self.user_lay.addWidget(self.user_label)
        self.user_lay.addWidget(self.user_checkbox)
        self.layout_top.addLayout(self.user_lay)


        self.preset_combo_layout = QtWidgets.QHBoxLayout()
        self.preset_combo = QtWidgets.QComboBox()
        self.preset_combo_layout.addWidget(self.preset_combo)

        self.label_lay = QtWidgets.QHBoxLayout()
        self.input_lay = QtWidgets.QHBoxLayout()

        self.letter_label = QtWidgets.QLabel("Drive: ")
        self.letter_label.setFixedWidth(50)
        # self.letter_edit = QtWidgets.QLineEdit()
        self.letter_edit = QtWidgets.QComboBox()
        self.letter_edit.setFixedWidth(50)
        # self.letter_validator = QtGui.QValidator()
        # self.letter_validator = QtGui.QRegularExpressionValidator(QtCore.QRegularExpression("[a-zA-Z]"))
        # self.letter_edit.setValidator(self.letter_validator)

        self.path_label = QtWidgets.QLabel("Server Address: ")

        self.path_edit = QtWidgets.QLineEdit()
        self.path_edit.setMinimumWidth(300)
        self.input_lay.addWidget(self.letter_edit)
        self.input_lay.addWidget(self.path_edit)
        
        self.label_lay.addWidget(self.letter_label)
        self.label_lay.addWidget(self.path_label)
        
        self.layout_top.addLayout(self.preset_combo_layout)
        self.layout_top.addLayout(self.label_lay)
        self.layout_top.addLayout(self.input_lay)

        self.connect_bttn = QtWidgets.QPushButton("Connect")
        self.connect_bttn.clicked.connect(self.connectDrive)
        self.layout_top.addWidget(self.connect_bttn)
    def setPreset(self):
        current = self.preset_combo.currentText()
        self.letter_edit.setCurrentText("%s:" % self.drive_dict[current]["letter"].upper())
        self.path_edit.setText(self.drive_dict[current]["win_path"])

    def connectDrive(self):
        letter = self.letter_edit.currentText()[0]
        path = self.path_edit.text()

        result = mapDrive(letter=letter,path=path)

class LoginForm(QtWidgets.QDialog):
    def __init__(self):
        super(LoginForm, self).__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Login Form")
        self.setGeometry(50, 50, 500, 300)
        self.btn = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        # Create text boxes
        self.username_textbox = QtWidgets.QLineEdit()
        self.password_textbox = QtWidgets.QLineEdit()
        self.password_textbox.setEchoMode(QtWidgets.QLineEdit.Password)

        # # Create labels
        # self.username_label = QtWidgets.QLabel("Username:")
        # self.password_label = QtWidgets.QLabel("Password:")

        # Create layout
        self.f_layout = QtWidgets.QFormLayout()
        # self.layout.addRow(self.username_label, self.username_textbox)
        # self.layout.addRow(self.password_label, self.password_textbox)
        self.f_layout.addRow("Username", self.username_textbox)
        self.f_layout.addRow("Password", self.password_textbox)
        self.setLayout(self.f_layout)

        # Show window
        self.btn_group = QtWidgets.QDialogButtonBox(self.btn)
        self.f_layout.addWidget(self.btn_group)


if __name__ == "__main__":
    import sys
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    win = DriveDialog()
    win.show()

    app.exec_()