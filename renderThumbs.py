
import maya.cmds as cmds

from PySide2.QtWidgets import QMainWindow, QPushButton, QWidget, QGroupBox, QVBoxLayout, QHBoxLayout, QComboBox, \
    QGridLayout, \
    QLineEdit, QLabel, QFileDialog
from PySide2.QtCore import Qt




class MainWindow(QMainWindow):
    # Get list with all json presets in "C:\Users\plp\Documents\maya\Presets"
    # presets = prefs.getUserPresets("arnold")

    # Import render settings from json

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Render Thumbnails")
        self.cam = 'myCam'

        # -----------------------------------------------------------------------------------------------------------
        # Cameras groupbox
        # -----------------------------------------------------------------------------------------------------------
        self.cg_box = QGroupBox("Choose Camera")  # Create groupbox
        self.cg_box_layout = QHBoxLayout()  # Create layout (necessary to display the elements in the groupbox)
        self.cg_combo_box = QComboBox()  # Create combobox (dropdown)
        self.cg_box.setLayout(self.cg_box_layout)  # Set layout to the groupbox

        self.cg_combo_box.addItems(cmds.listCameras())  # Create list to display in the combobox
        self.cg_combo_box.setCurrentText(
            self.getRenderCamera())  # Set the currently displayed camera to the renderable camera

        # "Make renderable" button
        # -----------------------------------------------------------------------------------------------------------
        self.make_cam_button = QPushButton("Set As Renderable")
        self.make_cam_button.setCheckable(False)
        self.make_cam_button.clicked.connect(lambda: self.setRenderCamera())

        # Add dropdown and button to the layout
        # -----------------------------------------------------------------------------------------------------------
        self.cg_box_layout.addWidget(self.cg_combo_box)  # Add the combobox to the layout
        self.cg_box_layout.addWidget(self.make_cam_button)  # Add the button to the layout

        # -----------------------------------------------------------------------------------------------------------
        # Make new camera groupbox
        # -----------------------------------------------------------------------------------------------------------
        self.mnc_box = QGroupBox("Make New Camera")
        self.mnc_box_layout = QHBoxLayout()
        self.mnc_box.setLayout(self.mnc_box_layout)

        # Camera name textbox
        # --------------------------------------------------------------------
        self.camera_name_textbox = QLineEdit()
        self.camera_name_textbox.setMaximumWidth(150)
        self.camera_name_textbox.setAlignment(Qt.AlignLeft)

        # "Make Camera" button
        # --------------------------------------------------------------------
        self.make_cam_button = QPushButton("Make Camera")
        self.make_cam_button.setCheckable(False)
        self.make_cam_button.clicked.connect(lambda: self.MakeCamera(self.camera_name_textbox.text()))

        self.mnc_box_layout.addWidget(self.camera_name_textbox)
        self.mnc_box_layout.addWidget(self.make_cam_button)

        # -----------------------------------------------------------------------------------------------------------
        # Image format groupbox
        # -----------------------------------------------------------------------------------------------------------
        image_format = ['jpeg', 'png', 'tif', 'exr']

        self.if_box = QGroupBox("Image Format")
        self.if_box_layout = QVBoxLayout()
        self.if_combo_box = QComboBox()
        self.if_box.setLayout(self.if_box_layout)
        self.if_combo_box.activated.connect(lambda: self.setImageFormat())
        self.if_box_layout.addWidget(self.if_combo_box)
        self.if_combo_box.addItems(image_format)

        # -----------------------------------------------------------------------------------------------------------
        # Resolution groupbox
        # -----------------------------------------------------------------------------------------------------------

        self.res_box = QGroupBox("Resolution")
        self.res_box_layout = QHBoxLayout()
        self.res_box.setLayout(self.res_box_layout)

        self.width_textbox = QLineEdit()
        self.width_textbox.setMaximumWidth(50)

        self.width_label = QLabel("width")

        self.height_textbox = QLineEdit()
        self.height_textbox.setMaximumWidth(50)

        self.height_label = QLabel("height")

        self.res_box_layout.addWidget(self.width_textbox)
        self.res_box_layout.addWidget(self.width_label)
        self.res_box_layout.addWidget(self.height_textbox)
        self.res_box_layout.addWidget(self.height_label)

        # -----------------------------------------------------------------------------------------------------------
        # Set Directory groupbox
        # -----------------------------------------------------------------------------------------------------------

        self.fd_box = QGroupBox("Render Directory")
        self.fd_box_layout = QHBoxLayout()
        self.fd_box.setLayout(self.fd_box_layout)

        self.fd_button = QPushButton("Browse")
        self.fd_button.setCheckable(False)
        self.fd_button.clicked.connect(lambda: self.setRenderDirectory())

        self.fd_textbox = QLabel()

        self.fd_box_layout.addWidget(self.fd_textbox)
        self.fd_box_layout.addWidget(self.fd_button)

        # -----------------------------------------------------------------------------------------------------------
        # Render button
        # -----------------------------------------------------------------------------------------------------------

        self.rb_box = QGroupBox()
        self.rb_box_layout = QHBoxLayout()
        self.rb_box.setLayout(self.rb_box_layout)

        self.rb_button = QPushButton("Render")
        self.rb_button.setCheckable(False)
        self.rb_button.clicked.connect(lambda: self.renderThumbs())

        self.rb_box_layout.addWidget(self.rb_button)

        # Create main layout and add widgets to it
        # -----------------------------------------------------------------------------------------------------------
        self.main_layout = QGridLayout()
        self.main_layout.addWidget(self.cg_box, 0, 0)
        self.main_layout.addWidget(self.mnc_box, 1, 0)
        self.main_layout.addWidget(self.if_box, 2, 0)
        self.main_layout.addWidget(self.res_box, 3, 0)
        self.main_layout.addWidget(self.fd_box, 4, 0)
        self.main_layout.addWidget(self.rb_box, 5, 0)

        # Add the main layout to window
        # -----------------------------------------------------------------------------------------------------------
        widget = QWidget()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)

    @staticmethod
    def getRenderCamera():

        cameras_list = cmds.listCameras()
        camera = ""

        for i in cameras_list:
            if cmds.getAttr(i + '.renderable'):
                camera = i
        if camera == "":
            camera = cameras_list[0]
            return camera
        else:
            return camera

    def setRenderCamera(self):

        textbox_cam = self.camera_name_textbox.text()
        dropdown_cam = self.cg_combo_box.currentText()

        if textbox_cam != "":
            cmds.setAttr(self.getRenderCamera() + '.renderable', False)
            cmds.setAttr(textbox_cam + '.renderable', True)
        else:
            cmds.setAttr(self.getRenderCamera() + '.renderable', False)
            cmds.setAttr(dropdown_cam + '.renderable', True)

    @staticmethod
    def MakeCamera(camera_name):
        cmds.camera(name=camera_name)
        cmds.rename(camera_name + '1', camera_name)

    def setImageFormat(self):

        cmds.setAttr("defaultArnoldDriver.aiTranslator", self.if_combo_box.currentText(), type="string")

    def setRenderDirectory(self):

        directory = str(QFileDialog.getExistingDirectory(self, "Select Directory")) + "/test"
        cmds.setAttr('defaultRenderGlobals.imageFilePrefix', directory, type="string")
        self.fd_textbox.setText(directory)

    def renderThumbs(self):

        current_width = cmds.getAttr('defaultResolution.width')
        current_height = cmds.getAttr('defaultResolution.height')

        width = int(self.width_textbox.text())
        height = int(self.height_textbox.text())

        cmds.setAttr("defaultResolution.width", width)
        cmds.setAttr("defaultResolution.height", height)

        cmds.arnoldRender(cam=self.getRenderCamera(), width=width, height=height, seq=None)

        cmds.setAttr("defaultResolution.width", current_width)
        cmds.setAttr("defaultResolution.height", current_height)


mainWin = MainWindow()
mainWin.show()

# # To do:
# # Set renderable camera - done (cameras?)
# # Choose image type
# # Choose resolution
# # File render location
# # Render settings export?
