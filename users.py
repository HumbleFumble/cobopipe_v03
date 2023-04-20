import os
from Maya_Functions.file_util_functions import saveJson, loadJson
from PySide2 import QtWidgets, QtCore, QtGui
from getConfig import getConfigClass

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


def get_users(key):
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
    users = get_users("animation")
    print(users)
