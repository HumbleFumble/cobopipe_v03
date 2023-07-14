from PySide2 import QtWidgets, QtCore, QtGui
import string

class MainWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setObjectName("RenderSubmit")
        self.setWindowTitle("RenderSubmit")
        self.setWindowFlags(QtCore.Qt.Window)
        self.createBaseUI()

    def createBaseUI(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.PresetUI())
        self.main_layout.addWidget(self.NameUI())
        self.setLayout(self.main_layout)

    def NameUI(self):
        self.name_group = QtWidgets.QGroupBox("Name Settings")
        self.name_layout = QtWidgets.QVBoxLayout()

        ##### NAME SECTION ####
        self.name_pick_layout = QtWidgets.QHBoxLayout()
        # self.name_pick_layout.addWidget(self.name_dd)

        #Don't need a dropdown, just update the edit field along with preset
        self.name_edit = QtWidgets.QLineEdit("")
        self.name_edit.setPlaceholderText("Custom name here")
        self.name_add_bttn = QtWidgets.QPushButton("+")
        self.name_add_bttn.setToolTip("Click here to add the custom name to the saved options")

        self.name_remove_bttn = QtWidgets.QPushButton("-")
        self.name_remove_bttn.setToolTip("Click here to remove the current selection from the saved options")

        self.name_pick_layout.addWidget(self.name_edit)

        self.name_inc_layout = QtWidgets.QHBoxLayout()
        self.name_inc_radio = QtWidgets.QRadioButton("Auto Increment")
        self.name_inc_radio.setToolTip("Auto Increment versions with a letter (A,B,C...)")
        self.no_verion_radio = QtWidgets.QRadioButton("Don't Add Letter")
        self.overwrite_latest_radio = QtWidgets.QRadioButton("Overwrite Latest")

        # self.name_inc_bttn = QtWidgets.QPushButton("Update increment to the next available")

        self.name_inc_layout.addWidget(self.name_inc_radio)
        self.name_inc_layout.addWidget(self.overwrite_latest_radio)
        self.name_inc_layout.addWidget(self.no_verion_radio)
        self.name_inc_radio.setChecked(True)

        self.name_radio_group = QtWidgets.QButtonGroup(self)

        self.name_radio_group.addButton(self.name_inc_radio)
        self.name_radio_group.addButton(self.overwrite_latest_radio)
        self.name_radio_group.addButton(self.no_verion_radio)

        self.name_layout.addLayout(self.name_pick_layout)
        self.name_layout.addLayout(self.name_inc_layout)

        self.name_group.setLayout(self.name_layout)
        return self.name_group

    def PresetUI(self):
        # PRESET SETTINGS
        self.preset_group = QtWidgets.QGroupBox("Preset Settings")
        self.preset_layout = QtWidgets.QVBoxLayout()
        self.preset_dd_layout = QtWidgets.QHBoxLayout()

        self.preset_dd = QtWidgets.QComboBox()
        self.preset_create_button = QtWidgets.QPushButton("+")
        # self.preset_create_button.clicked.connect(self.CreateNewPreset)
        self.preset_create_button.setMaximumWidth(30)
        self.preset_delete_button = QtWidgets.QPushButton("-")
        # self.preset_delete_button.clicked.connect(self.DeleteCurrentPreset)
        self.preset_delete_button.setMaximumWidth(30)
        self.preset_button_layout = QtWidgets.QHBoxLayout()

        self.pick_preset_buton = QtWidgets.QPushButton("Pick Preset")
        # self.pick_preset_buton.clicked.connect(self.PickPreset)
        self.appy_preset_button = QtWidgets.QPushButton("Apply Preset")
        # self.appy_preset_button.clicked.connect(self.ApplyPresetCall)

        self.save_preset_button = QtWidgets.QPushButton("Save Preset")
        # self.save_preset_button.clicked.connect(self.SavePresetCall)

        self.preset_group.setLayout(self.preset_layout)
        self.preset_layout.addLayout(self.preset_dd_layout)
        self.preset_dd_layout.addWidget(self.preset_dd)
        self.preset_dd_layout.addWidget(self.preset_dd)
        self.preset_dd_layout.addWidget(self.preset_create_button)
        self.preset_dd_layout.addWidget(self.preset_delete_button)
        self.preset_layout.addLayout(self.preset_button_layout)
        self.preset_button_layout.addWidget(self.pick_preset_buton)
        self.preset_button_layout.addWidget(self.save_preset_button)

        self.preset_layout.addWidget(self.appy_preset_button)
        return self.preset_group

if __name__ == '__main__':
    import sys
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    mainWin = MainWindow()

    # # mainWin.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    # # mainWin.setFixedSize(584, 662)
    # # mainWin.resize(584, 662)
    # # print(QtWidgets.qApp.topLevelWidgets())

    mainWin.show()

    sys.exit(app.exec_())