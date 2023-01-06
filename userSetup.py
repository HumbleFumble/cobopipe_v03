from Log.CoboLoggers import getLogger
logger = getLogger()

from getConfig import getConfigClass
CC = getConfigClass()

import maya.cmds as cmds
import maya.OpenMaya as om

# Sets project based settings from json file
def setProjectSettings():
    settings = CC.project_settings
    if settings:
        logger.debug('Project settings found')
        if 'fps' in settings.keys():
            if settings['fps']:
                cmds.currentUnit(time=settings['fps'], updateAnimation=True)
                logger.info('FPS set to ' + settings['fps'])
        if 'cmEnabled' in settings.keys():
            if settings['cmEnabled'] == True or settings['cmEnabled'] == False:
                if settings['cmEnabled'] == True:
                    if cmds.colorManagementPrefs(q=True, cmEnabled=True):
                        cmds.colorManagementPrefs(edit=True, cmEnabled=settings['cmEnabled'])
                        logger.info('Color Management has been enabled')
                else:
                    cmds.colorManagementPrefs(edit=True, cmEnabled=settings['cmEnabled'])
                    logger.info('Color Management has been disabled')
        if 'cmViewTransform' in settings.keys():
            if settings['cmViewTransform']:
                if settings['cmViewTransform'] in cmds.colorManagementPrefs(q=True, viewNames=True):
                    cmds.colorManagementPrefs(edit=True, viewTransformName=settings['cmViewTransform'])
                    logger.info('Color Management View Transform has been set to ' + settings['cmViewTransform'])

        if 'cmRenderingSpaceName' in settings.keys():
            if settings['cmRenderingSpaceName']:
                if settings['cmRenderingSpaceName'] in cmds.colorManagementPrefs(q=True, renderingSpaceNames=True):
                    cmds.colorManagementPrefs(edit=True, renderingSpaceName=settings['cmRenderingSpaceName'])
                    logger.info('Color Management RenderSpace has been set to ' + settings['cmRenderingSpaceName'])

        if 'colorManagementEnabledByDefault' in settings.keys():
            cmds.optionVar(iv=['colorManagementEnabledByDefault', settings["colorManagementEnabledByDefault"]])




if __name__ == '__main__':
    import callbacks
    callbacks.Startup()

    # if om.MGlobal.mayaState() == 0:
    #     cmds.evalDeferred("import ShelfCreator; ShelfCreator.run(overwrite=False)")
    #     cmds.evalDeferred("import userSetup; userSetup.setProjectSettings()")


# def createJsonFile():
#     from Maya_Functions.file_util_functions import saveJson, loadJson
#     settings = {'fps': '24fps', 'colorManagementEnabled': True, 'viewColorSpace': 'sRGB gamma'}
#     saveJson('P:/_WFH_Projekter/930486_MiaMagicPlayground_S3-4/4_Production/Pipeline/project_settings.json', settings)