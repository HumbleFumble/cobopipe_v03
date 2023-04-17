from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

import os

if os.environ.get("BOM_PIPE_PATH"):
    remote = True
else:
    remote = False

class PreviewPython_UI(QDialog):
    def __init__(self, parent=None):
        super(PreviewPython_UI, self).__init__(parent)
        self.setWindowTitle("Preview")
        self.setObjectName("Preview")
        self.setWindowFlags(self.windowFlags()|Qt.Window|Qt.WindowStaysOnTopHint)
        self.node_list = []
        self.create_ui()
        self.show()


    def create_ui(self):
        self.main_lay = QVBoxLayout()

        self.p_lay = QHBoxLayout()

        self.p_dd = QComboBox()
        self.p_edit = QLineEdit()
        self.p_lay.addWidget(QLabel("Project: "))
        self.p_lay.addWidget(self.p_dd)
        self.p_lay.addWidget(self.p_edit)

        self.u_lay = QHBoxLayout()

        self.u_dd = QComboBox()
        self.u_edit = QLineEdit()
        self.u_lay.addWidget(QLabel("User: "))
        self.u_lay.addWidget(self.u_dd)
        self.u_lay.addWidget(self.u_edit)

        self.slate_check = QCheckBox("Slate")

        self.crop_check = QCheckBox("Crop: ")
        self.crop_edit = QLineEdit("1.1")

        self.options_lay = QHBoxLayout()
        self.options_lay.addWidget(self.slate_check)
        self.options_lay.addWidget(self.crop_check)
        self.options_lay.addWidget(self.crop_edit)

        self.main_lay.addLayout(self.p_lay)
        self.main_lay.addLayout(self.u_lay)
        self.main_lay.addLayout(self.options_lay)
        self.run_bttn = QPushButton("Create Preview")
        self.main_lay.addWidget(self.run_bttn)
        self.setLayout(self.main_lay)
        self.run_bttn.clicked.connect(self.create_preview)

    def create_preview(self):
        pass

if __name__ == '__main__':
    import sys
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    t = PreviewPython_UI()
    t.show()
    app.exec()