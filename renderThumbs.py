import maya.cmds as cmds
import json
import maya.app.renderSetup.views.renderSetupPreferences as prefs
import maya.app.renderSetup.views.renderSetupWindow as rs_wind

ttt = prefs.getUserPresets("arnold")
# Import render settings from json
prefs.loadUserPreset("renderThumbs")

# Create new camera. This function renames the newly created camera. Since by default Maya adds '1' to the name,
# this function will create and rename camera with the intended name (without '1' at the end) 
#---------------------------------------------------------------------------------------------------------------

def makeCamera(cameraName):
    cmds.camera(name = cameraName)
    cmds.rename(cameraName + '1', cameraName)

# Get list of all cameras in the scene and determine which one is selected as renderable in the render settings.
# This is useful if the camera is the desired for rendering the thumbnails
#---------------------------------------------------------------------------------------------------------------

def getRenderableCamera():

    cameras_list = cmds.listCameras()
    camera = ""

    for i in cameras_list:
        if cmds.getAttr(i + '.renderable') == True:
            camera = i
    return camera


# Perhaps add a choice for rendering multiple cameras?

#---------------------------------------------------------------------------------------------------------------
# Set the new camera as renderable and remove the currently assigned

current_cam = getRenderableCamera()
myCamName = 'myCam'

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