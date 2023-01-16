import maya.cmds as cmds
import maya.app.renderSetup.views.renderSetupPreferences as prefs

# Import render settings from json
prefs.loadUserPreset("render_settings")

# Get list of all cameras in the scene and determine which one is selected as renderable in the render settings.
def getRenderableCamera():

    cameras_list = cmds.listCameras()
    camera = ""

    for i in cameras_list:
        if cmds.getAttr(i + '.renderable') == True:
            camera = i
    return camera

cam = getRenderableCamera()

# Get the currently set resolution, so it can be reset later. This is necessary, since when rendering jpeg or png, if the
# desired resolution is set to different number than the current resolution, arnold will render the first image in the
# originally set resolution, instead of the desired one
current_width = cmds.getAttr('defaultResolution.width')
current_height = cmds.getAttr('defaultResolution.height')

width = 320
height = 180

# Set desired resolution
cmds.setAttr("defaultResolution.width", width)
cmds.setAttr("defaultResolution.height", height)

# Render sequence
cmds.arnoldRender(cam=cam, width=width, height=height, seq=None)

# Set back to the original resolution
cmds.setAttr("defaultResolution.width", current_width)
cmds.setAttr("defaultResolution.height", current_height)

# To do:
# Set renderable camera
# Choose image type
# Choose resolution
# File render location
# Render settings export?