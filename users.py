import os
from Maya_Functions.file_util_functions import saveJson, loadJson
from PySide2 import QtWidgets, QtCore, QtGui
from getConfig import getConfigClass

try:
	import maya.cmds as cmds
	in_maya = True
except:
	in_maya = False

CC = getConfigClass()


class add_user_signals(QtCore.QObject):
    add = QtCore.Signal(str)


class add_user_ui(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(add_user_ui, self).__init__(parent)
        self.setWindowTitle("Add User")
        flags = self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint
        flags = flags | QtCore.Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.add_user_ui_palette()

        self.main_layout = QtWidgets.QHBoxLayout()
        self.input = QtWidgets.QLineEdit()
        self.add_button = QtWidgets.QPushButton("Add")
        self.add_button.setMaximumWidth(50)
        self.main_layout.addWidget(self.input)
        self.main_layout.addWidget(self.add_button)
        self.add_button.clicked.connect(self.add)

        self.setLayout(self.main_layout)

        self.signals = add_user_signals()

    def add(self):
        self.signals.add.emit(self.input.text())
        self.close()

    def add_user_ui_palette(self):
		#TODO setting palette in maya does NOT look great
        if not in_maya:
            magenta = {"R": 142, "G": 45, "B": 197}
            blue = {"R": 50, "G": 50, "B": 255}

            hi_lgt = blue
            palette = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
            palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
            palette.setColor(QtGui.QPalette.Base, QtGui.QColor(40, 40, 40))
            palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
            palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
            palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
            palette.setColor(QtGui.QPalette.Text, QtCore.Qt.lightGray)
            palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
            palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
            palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
            palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(hi_lgt["R"], hi_lgt["G"], hi_lgt["B"]).lighter(100))
            palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.white)
            self.setPalette(palette)
            QtWidgets.QApplication.instance().setStyle('Fusion')


def get_users(key=None):
    if not key:
        config_users = []
        users_json_users = []
        for key, value in CC.users.items():
            config_users = config_users + value
        for key, value in get_users_json().items():
            users_json_users = users_json_users + value
    else:
        key = key.title()
        config_users = CC.users.get(key)
        users_json_users = get_users_json().get(key)
    users = config_users + users_json_users
    users = set(users)
    users = list(users)
    users = sorted(users)
    return users


def add_to_users_json(key, user):
    key = key.title()
    user = user.title()
    users = get_users_json()
    user_list = users.get(key)

    if not type(user_list) == list:
        raise TypeError("Key is not present in users.json")

    if user in user_list:
        raise ValueError(f"{user} is already in the {key} list")

    user_list.append(user)
    users[key] = user_list
    saveJson(CC.get_users_json(), users)


def get_users_json():
    users_json_path = CC.get_users_json()
    folder_path = os.path.dirname(users_json_path)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    if not os.path.exists(users_json_path):
        data = {"Animation": [], "Render": []}
        saveJson(users_json_path, data)
        return data

    return loadJson(users_json_path)


if __name__ == "__main__":
    print(CC.get_users())
