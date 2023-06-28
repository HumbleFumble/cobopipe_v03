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
        self.name_layout = QtWidgets.QVBoxLayout()

        ##### NAME SECTION ####
        self.name_pick_layout = QtWidgets.QHBoxLayout()
        self.name_dd = QtWidgets.QComboBox()
        self.name_pick_layout.addWidget(self.name_dd)

        self.name_custom_layout = QtWidgets.QHBoxLayout()
        self.name_edit = QtWidgets.QLineEdit("Custom name here")
        self.name_add_bttn = QtWidgets.QPushButton("+")
        self.name_add_bttn.setToolTip("Click here to add the custom name to the saved options")

        self.name_remove_bttn = QtWidgets.QPushButton("-")
        self.name_remove_bttn.setToolTip("Click here to remove the current selection from the saved options")
        self.name_custom_layout.addWidget(self.name_edit)
        self.name_custom_layout.addWidget(self.name_add_bttn)
        self.name_custom_layout.addWidget(self.name_remove_bttn)



        self.name_inc_dd = QtWidgets.QComboBox()
        self.name_inc_dd.addItems(list(string.ascii_uppercase))
        self.name_pick_layout.addWidget(self.name_inc_dd)

        self.name_inc_layout = QtWidgets.QHBoxLayout()
        self.name_inc_checkbox = QtWidgets.QCheckBox("Auto Increment")
        self.name_inc_checkbox.setToolTip("Auto Increment versions with a letter (A,B,C...)")

        self.name_inc_bttn = QtWidgets.QPushButton("Update increment to the next available")
        self.name_inc_layout.addWidget(self.name_inc_checkbox)
        self.name_inc_layout.addWidget(self.name_inc_bttn)

        self.name_layout.addLayout(self.name_pick_layout)
        self.name_layout.addLayout(self.name_custom_layout)
        self.name_layout.addLayout(self.name_inc_layout)
        # self.name_layout.addWidget()



        self.main_layout.addLayout(self.name_layout)
        self.setLayout(self.main_layout)
        # self.name_overwrite_checkbox = QtWidgets.QCheckBox("Overwrite Version")


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