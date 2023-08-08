import os
import zipUtil
import sys
from PySide2 import QtCore, QtWidgets


package_dict = {
    "ffmpeg":["T:/_Executables/ffmpeg"],
    "python39":["T:/_Software/Python/python-3.9.1-amd64.exe"],
    "harmony22": ["T:/_Software/Toonboom/HAR22-PRM-win-21617.exe"],
    "harmony-scripts":["T:/_Pipeline/cobopipe_v02-001/TB/Scripting_Hotbars/Toon Boom Harmony Premium/2100-scripts"]
}




class CustomWidget(QtWidgets.QWidget):
    def __init__(self, key, parent=None):
        super(CustomWidget, self).__init__(parent)


        # Layout for the custom widget
        layout = QtWidgets.QHBoxLayout(self)

        # Checkbox
        self.checkbox = QtWidgets.QCheckBox()
        layout.addWidget(self.checkbox)

        # Label
        self.label = QtWidgets.QLabel(key)
        layout.setAlignment(QtCore.Qt.AlignLeft)
        layout.addWidget(self.label)
        # self.setStyleSheet("border-bottom: 1px solid gray;")


class remotePackager(QtWidgets.QWidget):
    def __init__(self):
        super(remotePackager, self).__init__()
        self.createUI()
        self.data_dict = package_dict
        self.updateList()
    def createUI(self):
        self.setWindowTitle("Remote Packager")
        self.setGeometry(100, 100, 300, 400)

        # Main layout
        layout = QtWidgets.QVBoxLayout(self)

        # List widget
        self.list_widget = QtWidgets.QListWidget()
        layout.addWidget(self.list_widget)

        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.setStyleSheet("alternate-background-color: #f10f10f10;")

        # Horizontal layout for line edit and button
        h_layout = QtWidgets.QHBoxLayout()

        # Line edit to display and edit the chosen file path
        self.path_edit = QtWidgets.QLineEdit()
        h_layout.addWidget(self.path_edit)

        # Button to open the file dialog
        self.save_button = QtWidgets.QPushButton("Browse")
        h_layout.addWidget(self.save_button)
        layout.addLayout(h_layout)
        self.save_button.clicked.connect(self.open_save_dialog)

        # Button to gather checked items
        self.gather_button = QtWidgets.QPushButton("Gather Checked Items")
        layout.addWidget(self.gather_button)
        self.gather_button.clicked.connect(self.gather_checked_items)
    def updateList(self):
        # Populate the list widget with items from the dictionary
        self.list_widget.clear()
        for key in self.data_dict.keys():
            item = QtWidgets.QListWidgetItem(self.list_widget)
            custom_widget = CustomWidget(key)
            item.setSizeHint(custom_widget.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, custom_widget)
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
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save ZIP File", "", "ZIP Files (*.zip);;All Files (*)",
                                                   options=options)
        print(file_name)
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

    data_dict = {
        "Item1": "Value1",
        "Item2": "Value2",
        "Item3": "Value3",
        "Item4": "Value4",
    }

    window = remotePackager()
    window.show()

    sys.exit(app.exec_())


# class RemotePackager():
#     def __init__(self):
#         pass


