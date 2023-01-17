import sys
import maya.cmds as cmds
import json
import maya.app.renderSetup.views.renderSetupPreferences as prefs
import maya.app.renderSetup.views.renderSetupWindow as rs_wind


from PySide2.QtWidgets import QMainWindow, QPushButton, QWidget, QGroupBox, QVBoxLayout, QComboBox, QGridLayout, QLineEdit, QHBoxLayout


class MainWindow(QMainWindow):
    # Get list with all json presets in "C:\Users\plp\Documents\maya\Presets"
    # presets = prefs.getUserPresets("arnold")

    # Import render settings from json

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Render Thumbnails")
        self.cam = 'myCam'

        # Cameras groupbox
        # -----------------------------------------------------------------------------------------------------------
        self.cg_box = QGroupBox("Choose Camera")
        self.cg_box_layout = QVBoxLayout()
        self.cg_combo_box = QComboBox()

        self.cg_box_layout.addWidget(self.cg_combo_box)

        self.cg_box.setLayout(self.cg_box_layout)
        self.cg_combo_box.addItems(cmds.listCameras())
        self.cg_combo_box.currentText()

        # Camera name textbox
        # -----------------------------------------------------------------------------------------------------------
        self.camera_name_textbox = QLineEdit()
        self.camera_name_textbox.setMaximumWidth(100)

        # "Make Camera" button widget
        # -----------------------------------------------------------------------------------------------------------
        self.make_cam_button = QPushButton("Make Camera")
        self.make_cam_button.setCheckable(False)
        self.make_cam_button.clicked.connect(lambda: self.MakeCamera(self.cam))

        # Make camera groupbox
        # -----------------------------------------------------------------------------------------------------------
        self.mc_cam = QGroupBox("Make Camera")
        self.mc_cam_layout = QHBoxLayout()
        self.mc_cam_layout.addWidget(self.camera_name_textbox, 0,0, Qt.AlignCenter())
        self.mc_cam_layout.addWidget(self.make_cam_button, 0,1, Qt.AlignCenterP())


        # "Make Renderable" button widget
        # -----------------------------------------------------------------------------------------------------------
        self.make_rend_button = QPushButton("Make Renderable")
        self.make_rend_button.setCheckable(False)
        self.make_rend_button.clicked.connect(lambda: self.makeCamera(self.cam))

        # Create main layout and add wdgets to it
        # -----------------------------------------------------------------------------------------------------------
        self.main_layout = QGridLayout()
        self.main_layout.addWidget(self.cg_box, 0, 0)
        self.main_layout.addWidget(self.mc_cam_layout, 1,0)

        # Add the main layout to window
        # -----------------------------------------------------------------------------------------------------------
        widget = QWidget()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)

    # Create new camera. This function renames the newly created camera. Since by default Maya adds '1' to the name,
    # this function will create and rename camera with the intended name (without '1' at the end)
    # ---------------------------------------------------------------------------------------------------------------

    def makeCamera(self, camera_name):
        cmds.camera(name=camera_name)
        cmds.rename(camera_name + '1', camera_name)

    # Get list of all cameras in the scene and determine which one is selected as renderable in the render settings.
    # This is useful if the camera is the desired for rendering the thumbnails
    # ---------------------------------------------------------------------------------------------------------------

    def getRenderableCamera(self):

        cameras_list = cmds.listCameras()
        camera = ""

        for i in cameras_list:
            if cmds.getAttr(i + '.renderable') == True:
                camera = i
        return camera

    def makeCameraRenderable(self, myCamName):
        current_cam = self.getRenderableCamera()
        if myCamName != "":
            self.makeCamera(myCamName)
            cmds.setAttr(current_cam + '.renderable', False)
            cmds.setAttr(myCamName + '.renderable', True)
            print("Current renderable camera is " + myCamName)
        elif current_cam != '':
            print("Current renderable camera is " + current_cam)
        else:
            print('No renderable camera is currently selected')


mainWin = MainWindow()
mainWin.show()


# Perhaps add a choice for rendering multiple cameras?

#---------------------------------------------------------------------------------------------------------------
# Set the new camera as renderable and remove the currently assigned

myCamName = ''
current_cam = getRenderableCamera()

if myCamName == '':
    if current_cam == '':
        print("Warning! No renderable camera is currently selected! Please set renderable camera in render settings!")
        
    else:
        print("Current renderable camera is " + current_cam)    
else:
    cmds.setAttr(current_cam + '.renderable', False)
    current_cam = myCamName
    makeCamera(current_cam)
    cmds.setAttr(current_cam + '.renderable', True)
    print("Current renderable camera is " + current_cam) 
    

# Get the currently set resolution, so it can be reset later. This is necessary, since when rendering jpeg or png, if the
# desired resolution is set to different number than the current resolution, arnold will render the first image in the
# originally set resolution, instead of the desired one

current_width = cmds.getAttr('defaultResolution.width')
current_height = cmds.getAttr('defaultResolution.height')

width = 320
height = 180

# Set desired resolution and image format
cmds.setAttr("defaultResolution.width", width)
cmds.setAttr("defaultResolution.height", height)

# Render sequence
cmds.arnoldRender(cam=current_cam, width=width, height=height, seq=None)

# Set back to the original resolution
cmds.setAttr("defaultResolution.width", current_width)
cmds.setAttr("defaultResolution.height", current_height)


# To do:
# Set renderable camera - done (cameras?)
# Choose image type
# Choose resolution
# File render location
# Render settings export?