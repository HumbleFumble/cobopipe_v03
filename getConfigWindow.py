from PySide2 import QtWidgets, QtCore, QtGui
import os
import sys
from Maya_Functions.file_util_functions import saveJson, loadJson


class ProjectDialog(QtWidgets.QDialog):
    def __init__(self):
        super(ProjectDialog, self).__init__()
        self.config_path = "%s/Configs/" % os.path.dirname(os.path.realpath(__file__))
        self.user_config_data_path = "C:/Temp/getConfig_data.json"
        self.config_list = []
        self.archivedProjects = []
        self.return_value = False
        self.createWindow()
        self.getConfigList()
        self.getArchivedList()
        self.populateCombo()


    def getConfigList(self):
        configs = os.listdir(self.config_path)
        for con in configs:
            if "Config_" in con and not ".pyc" in con:
                self.config_list.append(con.split("Config_")[-1].split(".")[0])


    def getArchivedList(self):
        from Configs.archivedProjects import list_of_archived_projects
        self.archivedProjects = list_of_archived_projects


    def createWindow(self):
        self.layout_top = QtWidgets.QVBoxLayout(self)
        self.config_combo_layout = QtWidgets.QHBoxLayout()
        self.config_combo = QtWidgets.QComboBox()
        self.config_combo_layout.addWidget(self.config_combo)
        #self.layout_top.addWidget(self.config_combo)

        self.checkbox_layout = QtWidgets.QHBoxLayout()
        self.checkbox = QtWidgets.QCheckBox("Hide archived projects")
        self.checkbox.setChecked(True)
        self.checkbox.stateChanged.connect(lambda: self.populateCombo())
        self.checkbox_layout.addWidget(self.checkbox)

        self.button_layout = QtWidgets.QHBoxLayout()
        self.add_button = QtWidgets.QPushButton("Apply")
        self.add_button.setDefault(True)
        self.button_layout.addWidget(self.add_button)

        self.layout_top.addLayout(self.config_combo_layout)
        self.layout_top.addLayout(self.checkbox_layout)
        self.layout_top.addLayout(self.button_layout)
        self.setLayout(self.layout_top)
        self.add_button.clicked.connect(self.applyClicked)


    def populateCombo(self):
        self.config_combo.clear()
        if not self.checkbox.checkState():
            self.config_combo.addItems(self.config_list)
        else:
            self.activeProjects = []
            for item in self.config_list:
                if item not in self.archivedProjects:
                    self.activeProjects.append(item)
            self.config_combo.addItems(self.activeProjects)
        last_picked = loadJson(self.user_config_data_path)
        if last_picked:
            if "last_picked" in last_picked.keys():
                self.config_combo.setCurrentText(last_picked["last_picked"])


    def applyClicked(self):
        self.return_value = self.config_combo.currentText()
        saveJson(self.user_config_data_path,{"last_picked":self.return_value})
        self.accept()


    def getValue(self):
        return self.return_value


def run():
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    win = ProjectDialog()
    win.resize(400, 100)
    # win.show()
    if win.exec_():
        value = win.getValue()
        return value
    return False


if __name__ == "__main__":
    run()


