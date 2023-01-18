import sys
import maya.cmds as cmds
import json
import maya.app.renderSetup.views.renderSetupPreferences as prefs
import maya.app.renderSetup.views.renderSetupWindow as rs_wind


import maya.cmds as cmds

from PySide2.QtWidgets import QMainWindow, QPushButton, QWidget, QGroupBox, QVBoxLayout, QComboBox, QGridLayout, \
    QLineEdit, QLabel
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
        self.cg_box = QGroupBox("Choose Camera")                        # Create groupbox
        self.cg_box_layout = QVBoxLayout()                              # Create layout (necessary to display the elements in the groupbox)
        self.cg_combo_box = QComboBox()                                 # Create combobox (dropdown)
        self.cg_box.setLayout(self.cg_box_layout)                       # Set layout to the groupbox

        self.cg_combo_box.addItems(cmds.listCameras())                  # Create list to display in the combobox
        self.cg_combo_box.setCurrentText(self.getRenderCamera())        # Set the currently displayed camera to the renderable camera

        # "Make renderable" button
        # -----------------------------------------------------------------------------------------------------------
        self.make_cam_button = QPushButton("Set As Renderable")
        self.make_cam_button.setCheckable(False)
        self.make_cam_button.clicked.connect(lambda: self.setRenderCamera())

        # Add dropdown and button to the layout
        # -----------------------------------------------------------------------------------------------------------
        self.cg_box_layout.addWidget(self.cg_combo_box)                 # Add the combobox to the layout
        self.cg_box_layout.addWidget(self.make_cam_button)              # Add the button to the layout

        # -----------------------------------------------------------------------------------------------------------
        # Make new camera groupbox
        # -----------------------------------------------------------------------------------------------------------
        self.mnc_box = QGroupBox("Make New Camera")
        self.mnc_box_layout = QVBoxLayout()
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

        # -----------------------------------------------------------------------------------------------------------
        # Image format groupbox
        # -----------------------------------------------------------------------------------------------------------
        image_format = ['jpeg', 'png', 'tif', 'exr']

        self.if_box = QGroupBox("Image format")
        self.if_box_layout = QVBoxLayout()
        self.if_combo_box = QComboBox()
        self.if_box.setLayout(self.if_box_layout)
        self.if_combo_box.activated.connect(lambda: self.setImageFormat())
        self.if_box_layout.addWidget(self.if_combo_box)
        self.if_combo_box.addItems(image_format)


        # Create main layout and add widgets to it
        # -----------------------------------------------------------------------------------------------------------
        self.main_layout = QGridLayout()
        self.main_layout.addWidget(self.cg_box, 0, 0)
        self.main_layout.addWidget(self.mnc_box, 1, 0)
        self.main_layout.addWidget(self.if_box, 2, 0)
        

        # Add the main layout to window
        # -----------------------------------------------------------------------------------------------------------
        widget = QWidget()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)


    def getRenderCamera(self):

        cameras_list = cmds.listCameras()
        camera = ""

        for i in cameras_list:
            if cmds.getAttr(i + '.renderable') == True:
                camera = i
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

    def MakeCamera(self, camera_name):
        cmds.camera(name=camera_name)
        cmds.rename(camera_name + '1', camera_name)

    def setImageFormat(self):

        cmds.setAttr("defaultArnoldDriver.aiTranslator", self.if_combo_box.currentText(), type="string")

mainWin = MainWindow()
mainWin.show()


# # Perhaps add a choice for rendering multiple cameras?
  

# # Get the currently set resolution, so it can be reset later. This is necessary, since when rendering jpeg or png, if the
# # desired resolution is set to different number than the current resolution, arnold will render the first image in the
# # originally set resolution, instead of the desired one

# current_width = cmds.getAttr('defaultResolution.width')
# current_height = cmds.getAttr('defaultResolution.height')

# width = 320
# height = 180

# # Set desired resolution and image format
# cmds.setAttr("defaultResolution.width", width)
# cmds.setAttr("defaultResolution.height", height)

# # Render sequence
# cmds.arnoldRender(cam=current_cam, width=width, height=height, seq=None)

# # Set back to the original resolution
# cmds.setAttr("defaultResolution.width", current_width)
# cmds.setAttr("defaultResolution.height", current_height)


# # To do:
# # Set renderable camera - done (cameras?)
# # Choose image type
# # Choose resolution
# # File render location
# # Render settings export?