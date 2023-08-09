import os
import zipUtil
import sys
from PySide2 import QtCore, QtWidgets


package_dict = {
    "ffmpeg":["T:/_Executables/ffmpeg/"],
    "python39":["T:/_Software/Python/python-3.9.1-amd64.exe",
                "T:/_Pipeline/cobopipe_v02-001/requirements.txt"],
    "harmony22": ["T:/_Software/Toonboom/HAR22-PRM-win-21617.exe"],
    "harmony-scripts":["T:/_Pipeline/cobopipe_v02-001/TB/Scripting_Hotbars/Toon Boom Harmony Premium/2100-scripts/",
                       "T:/_Pipeline/cobopipe_v02-001/TB/ToonBoom_Global_Scripts/",
                       "T:/_Pipeline/cobopipe_v02-001/TB/ToonBoom_Global_Python/",
                       "T:/_Pipeline/cobopipe_v02-001/Preview/ffmpeg_util.py",
                       "T:/_Pipeline/cobopipe_v02-001/icon/"],
    "mountDriveInterface":["T:/_Pipeline/cobopipe_v02-001/MountDriveInterface.py"],
    "shotBrowser_bat":["T:/_Pipeline/cobopipe_v02-001/BAT_files/ShotBrowser.bat"],
    "space_sniffer":["T:/_Software/SpaceSniffer/spacesniffer_1_3_0_2/"],
    "VPN_Setup":["T:/_Resources/Guides/VPN/EN/",
                 "T:/_Resources/Guides/VPN/EN/Guide Connect to Network Drive.pdf"]
}





class CustomWidget(QtWidgets.QWidget):
    def __init__(self, key, parent=None):
        super(CustomWidget, self).__init__(parent)


        # Layout for the custom widget
        layout = QtWidgets.QHBoxLayout(self)

        # Checkbox
        self.checkbox = QtWidgets.QCheckBox()
        self.checkbox.stateChanged.connect(self.on_checkbox_state_changed)
        layout.addWidget(self.checkbox)

        # Label
        self.label = QtWidgets.QLabel(key)
        layout.setAlignment(QtCore.Qt.AlignLeft)
        layout.addWidget(self.label)
        # self.setStyleSheet("border-bottom: 1px solid gray;")

    def on_checkbox_state_changed(self, state):
        # If this checkbox is clicked, check if there are other selected items and update their checkboxes
        parent_list_widget = self.parent().parent()
        selected_items = parent_list_widget.selectedItems()
        for item in selected_items:
            widget = parent_list_widget.itemWidget(item)
            widget.checkbox.setChecked(state)


class remotePackager(QtWidgets.QWidget):
    def __init__(self):
        super(remotePackager, self).__init__()
        self.start_path = "T:/_Resources/Remote_SoftwarePackages/"
        self.data_dict = package_dict
        self.createUI()
        self.updateList()


    def createUI(self):
        self.setWindowTitle("Remote Packager")
        self.setGeometry(100, 100, 400, 400)

        # Main layout
        layout = QtWidgets.QVBoxLayout(self)

        # List widget
        self.list_widget = QtWidgets.QListWidget()
        layout.addWidget(self.list_widget)
        self.list_widget.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)

        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.setStyleSheet("alternate-background-color: #f10f10f10;")

        # Horizontal layout for line edit and button
        h_layout = QtWidgets.QHBoxLayout()

        # Line edit to display and edit the chosen file path
        self.path_edit = QtWidgets.QLineEdit(self.start_path)
        h_layout.addWidget(self.path_edit)

        # Button to open the file dialog
        self.save_button = QtWidgets.QPushButton("Browse")
        h_layout.addWidget(self.save_button)
        layout.addLayout(h_layout)
        self.save_button.clicked.connect(self.open_save_dialog)

        # Button to gather checked items
        self.gather_button = QtWidgets.QPushButton("Gather Checked Items")
        layout.addWidget(self.gather_button)
        self.gather_button.clicked.connect(self.run_button)
    def updateList(self):
        # Populate the list widget with items from the dictionary
        self.list_widget.clear()
        for key in self.data_dict.keys():
            item = QtWidgets.QListWidgetItem(self.list_widget)
            custom_widget = CustomWidget(key)
            item.setSizeHint(custom_widget.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, custom_widget)
    def gather_file_list(self, list_of_keys=[]):

        source_list = []
        for key in list_of_keys:
            content = self.data_dict[key]
            print(content)
            for c_path in content:
                if os.path.exists(c_path):
                    source_list.append(c_path)
                else:
                    print(f"In {key} -> Can't find {c_path}. Skipping it.")
        if source_list:
            print(source_list)
            return source_list
        else:
            return None

    def run_button(self):
        output_path = self.path_edit.text()
        if not os.path.exists(os.path.split(output_path)[0]):
            print("Folder doesn't exist, please pick an output path that does exist")
            return None
        checked_items = self.gather_checked_items()
        source_list = self.gather_file_list(checked_items)

        if source_list:
            zipUtil.zip_7z(source_list, output_path)


    def gather_checked_items(self):
        checked_items = []
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            widget = self.list_widget.itemWidget(item)
            if widget.checkbox.isChecked():
                checked_items.append(widget.label.text())

        print("Checked items:", checked_items)
        return checked_items
    def open_save_dialog(self):
        options = QtWidgets.QFileDialog.Options()
        my_file_dialog = QtWidgets.QFileDialog()
        my_file_dialog.setDirectory(self.start_path)
        file_name, _ = my_file_dialog.getSaveFileName(self, "Save ZIP File", "", "ZIP Files (*.zip);;All Files (*)",
                                                   options=options)
        # print(file_name)
        if file_name:
            # If the chosen file name doesn't end with .zip, append it
            if not file_name.endswith('.zip'):
                file_name += '.zip'
            self.path_edit.setText(file_name)
            # Here, you can proceed to save your data to the chosen ZIP file
            return file_name
        return None

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = remotePackager()
    window.show()

    sys.exit(app.exec_())
