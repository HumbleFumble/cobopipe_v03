from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *



class PreviewPython_UI(QDialog):
    def __init__(self, parent=None):
        super(PreviewPython_UI, self).__init__(parent)
        self.setWindowTitle("SetLineThickness_UI")
        self.setObjectName("SetLineThickness_UI")
        self.setWindowFlags(self.windowFlags()|Qt.Window|Qt.WindowStaysOnTopHint)
        self.node_list = []
        self.create_ui()
        self.toggle_on_off = 0


    def create_ui(self):
        self.main_lay = QVBoxLayout()

        # project dropdown and text?
        # Find projects if there is a config. Otherwise go to custom? which equals Text ?
        #
        # user dropdown and text?
        #
        # Options
        # slate checkbox
        # crop + crop edit that toggles along with checkboxes. Auto sets with project
        # In-house/remote?
        # Sound?




        self.pick_selection_bttn = QPushButton("Set Selection")
        self.set_selection_bttn = QPushButton("Pick Previous Selection")
        self.turn_on_off_bttn = QPushButton("Toggle On/Off")
        self.reset_bttn = QPushButton("Reset all")
        self.bttn_lay = QHBoxLayout()
        self.bttn_lay.addWidget(self.turn_on_off_bttn)
        self.bttn_lay.addWidget(self.reset_bttn)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider_label = QLabel("Value: ")
        self.slider_value = QLineEdit("0.0")
        self.slider_value.setFixedWidth(50)
        self.slider_lay = QHBoxLayout()
        self.slider_lay.addWidget(self.slider_label)
        self.slider_lay.addWidget(self.slider)
        self.slider_lay.addWidget(self.slider_value)
        self.slider.setMaximum(200)

        # self.slider_int = QDoubleValidator()
        # self.slider_value.setValidator(self.slider_int)
        self.slider.valueChanged.connect(self.slider_proc)

        self.slider_value.editingFinished.connect(self.text_proc)


        self.pick_selection_bttn.clicked.connect(self.pickSelection)
        self.set_selection_bttn.clicked.connect(self.setSelection)
        self.reset_bttn.clicked.connect(self.reset_thickness)
        self.turn_on_off_bttn.clicked.connect(self.turn_on_off)
        self.scale_check = QCheckBox("Scale Independent")

        self.main_lay.addWidget(self.pick_selection_bttn)
        self.main_lay.addWidget(self.set_selection_bttn)
        self.main_lay.addLayout(self.slider_lay)
        self.main_lay.addWidget(self.scale_check)
        self.main_lay.addLayout(self.bttn_lay)
        self.scale_check.setChecked(True)
        self.setLayout(self.main_lay)