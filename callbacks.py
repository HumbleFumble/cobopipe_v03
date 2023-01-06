import maya.cmds as cmds
import maya.OpenMaya as om

import cryptoAttributes
import Maya_Functions.general_util_functions as genUtil
from Log.CoboLoggers import getLogger
logger = getLogger()


# Manages general callbacks created on startup
# Initialized through userSetup.py
class Startup:
    def __init__(self):
        # Checking if Maya is running with UI or not

        mayaState = om.MGlobal.mayaState()
        if mayaState == 0:
            self.maya_interactive = True
            logger.info('Running Maya with UI')
        else:
            self.maya_interactive = False
            logger.info('Running Maya without UI')

        if self.maya_interactive:
            # A list of dictionaries containing arguments to creating callbacks through the SceneCallback class
            self.sceneCallbacksToCreate = [
                {
                    "name": "afterOpen",
                    "callback": "kAfterOpen",
                    "function": self.afterOpen
                 },
                {
                    "name": "beforeSave",
                    "callback": "kBeforeSave",
                    "function": self.beforeSave
                },
            ]

            if self.maya_interactive: # kMayaExiting only working in UI
                self.sceneCallbacksToCreate.append(
                    {
                        "name": "onExit",
                        "callback": "kMayaExiting",
                        "function": self.exit
                    }
                )

            # A list of dictionaries containing arguments to creating callbacks through the SceneCallback class
            self.eventCallbacksToCreate = [
                {
                    "name": "firstIdle",
                    "callback": "idleVeryLow",
                    "function": self.firstIdle
                }
            ]

            self.callbacks = {}
            self.createCallbacks()


    def createCallbacks(self):
        # Creating all Scene callbacks
        for current in self.sceneCallbacksToCreate:
            self.callbacks[current['name']] = SceneCallback(**current)

        # Creating all Event callbacks
        for current in self.eventCallbacksToCreate:
            self.callbacks[current['name']] = EventCallback(**current)


    def removeCallbacks(self): # Removing all callbacks created in this class
        for name, callback in self.callbacks.iteritems():
            callback.remove()


    def firstIdle(self, *args): # Runs first time Maya goes idle
        self.callbacks['firstIdle'].remove() # Removing idle callback to make sure it only runs once
        logger.debug('First idle callback')

        if self.maya_interactive:
            import userSetup
            userSetup.setProjectSettings()

            import ShelfCreator
            ShelfCreator.run(overwrite=False)


    def afterOpen(self, *args): # Runs after opening a file
        logger.debug('After open callback')

        # Add functions here
        if self.maya_interactive:
            import userSetup
            userSetup.setProjectSettings()

        genUtil.virusCheck()
        cryptoAttributes.cryptoAttrCheck()


    def beforeSave(self, *args): # Runs right before saving a file
        logger.debug('Before saving callback')

        # Add functions here
        cryptoAttributes.cryptoAttrCheck()


    def exit(self, *args): # Runs right before Maya closes
        logger.debug('Exit callback')
        # Add functions here

        # Do not remove
        self.removeCallbacks()


# Creates and manages MSceneMessage callbacks
class SceneCallback:
    def __init__(self, name, callback, function):
        '''
        Available callbacks found in getSceneEvents()

        :param name: General name to identify class later if needed
        :param callback: The type of MSceneMessage callback to create
        :param function: The function to run on callback
        '''

        self.callbackTable = getSceneEvents()

        self.name = name
        self.callback = self.callbackTable[callback]
        self.function = function
        self.id = None

        self.create()


    def create(self):
        if self.id:
            print('Callback already exists')
            return False
        else:
            self.id = om.MSceneMessage.addCallback(self.callback, self.function)


    def remove(self):
        if self.id:
            om.MMessage.removeCallback(self.id)
            self.id = None
            return True
        else:
            print('Callback does not exist')


    def getName(self):
        if self.id:
            return self.name()
        else:
            print('Callback does not exist')
            return None


    def getID(self):
        if self.id:
            return self.id
        else:
            print('Callback does not exist')
            return None


    def __del__(self):
        self.remove()


# Creates and manages MEventMessage callbacks
class EventCallback:
    def __init__(self, name, callback, function):
        '''
        Available callbacks found in getEvents()

        :param name: General name to identify class later if needed
        :param callback: The type of MEventMessage callback to create
        :param function: The function to run on callback
        '''

        self.callbackTable = getEvents()
        self.name = name
        self.callback = callback
        self.function = function
        self.id = None

        if self.callback in self.callbackTable:
            self.create()
        else:
            logger.warning('MEventMessage name does not exist')


    def create(self):
        if self.id:
            print('Callback already exists')
            return False
        else:
            self.id = om.MEventMessage.addEventCallback(self.callback, self.function)


    def remove(self):
        if self.id:
            om.MEventMessage.removeCallback(self.id)
            self.id = None
            return True
        else:
            print('Callback does not exist')


    def getName(self):
        if self.id:
            return self.name()
        else:
            print('Callback does not exist')
            return None


    def getID(self):
        if self.id:
            return self.id
        else:
            print('Callback does not exist')
            return None


    def __del__(self):
        self.remove()


# Creates and manages MNodeMessage callbacks
class NodeCallback:
    def __init__(self, name, node, callback, function):
        '''
        Available callbacks found in getNodeEvents()

        :param name: General name to identify class later if needed
        :param node: The targeted node (preferably fullpath)
        :param callback: The type of MNodeMessage callback to create
        :param function: The function to run on callback
        '''

        self.callbackTable = getNodeEvents()
        self.name = name
        self.node = node
        self.callbackTableKey = callback
        self.callback = self.callbackTable[self.callbackTableKey]
        self.function = function
        self.id = None

        if self.callbackTableKey in self.callbackTable.keys():
            print('herp derp')
            self.create()
        else:
            logger.warning('MNodeMessage name does not exist')


    def create(self):
        if self.id:
            print('Callback already exists')
            return False
        else:
            self.selection = om.MSelectionList()
            self.selection.add(self.node)
            self.MObject = om.MObject()
            self.selection.getDependNode(0, self.MObject)
            self.id = self.callback(self.MObject, self.function)


    def remove(self):
        if self.id:
            om.MMessage.removeCallback(self.id)
            self.id = None
            return True
        else:
            print('Callback does not exist')


    def getName(self):
        if self.id:
            return self.name()
        else:
            print('Callback does not exist')
            return None


    def getID(self):
        if self.id:
            return self.id
        else:
            print('Callback does not exist')
            return None


    def __del__(self):
        self.remove()


# Creates and manages MDGCallback callbacks
class MDGCallback:
    def __init__(self, name, callback, function, node_type=None):
        '''
        Available callbacks found in getMDGEvents()

        :param name: General name to identify class later if needed
        :param callback: The type of MDGMessage callback to create
        :param function: The function to run on callback
        :param node_type: Type of node that activates callback (example "dependNode")
        node_type is only relevant to addNodeAddedCallback and addNodeRemovedCallback events
        '''

        self.callbackTable = getMDGEvents()
        self.name = name
        self.callbackTableKey = callback
        self.callback = self.callbackTable[self.callbackTableKey]
        self.function = function
        self.node_type = node_type
        self.id = None

        if self.callbackTableKey in self.callbackTable.keys():
            self.create()
        else:
            logger.warning('MGDMessage name does not exist')


    def create(self):
        if self.id:
            print('Callback already exists')
            return False
        else:
            if self.node_type and self.callback in ['addNodeAddedCallback', 'addNodeRemovedCallback']:
                self.id = self.callback(self.function, self.node_type)
            else:
                self.id = self.callback(self.function)


    def remove(self):
        if self.id:
            om.MMessage.removeCallback(self.id)
            self.id = None
            return True
        else:
            print('Callback does not exist')


    def getName(self):
        if self.id:
            return self.name()
        else:
            print('Callback does not exist')
            return None


    def getID(self):
        if self.id:
            return self.id
        else:
            print('Callback does not exist')
            return None


    def __del__(self):
        self.remove()


# Creates callback when specified attribute changes
class AttributeCallback:
    def __init__(self, name, node, attribute, function):
        '''
        Creates MNodeMessage.addAttributeChangedCallback for specified attribute

        :param name: General name to identify class later if needed
        :param node: The targeted node (preferably fullpath)
        :param attribute: The targeted attribute
        :param function: The function to run on callback
        '''
        self.name = name
        self.node = node
        self.attribute = attribute
        self.function = function
        self.id = None

        if cmds.attributeQuery(self.attribute, node=self.node, exists=True):
            self.create()
        else:
            logger.warning('MEventMessage name does not exist')

    def create(self):
        if self.id:
            print('Callback already exists')
            return False
        else:
            self.selection = om.MSelectionList()
            self.selection.add(self.node)
            self.MObject = om.MObject()
            self.selection.getDependNode(0, self.MObject)
            self.id = om.MNodeMessage.addAttributeChangedCallback(self.MObject, self.call)


    def call(self, message_type, plug, other_plug, client_data):
        if message_type:
            if not message_type & om.MNodeMessage.kAttributeSet:
                return

            if self.attribute in plug.name():
                self.function()


    def remove(self):
        if self.id:
            om.MEventMessage.removeCallback(self.id)
            self.id = None
            return True
        else:
            print('Callback does not exist')


    def getName(self):
        if self.id:
            return self.name()
        else:
            print('Callback does not exist')
            return None


    def getID(self):
        if self.id:
            return self.id
        else:
            print('Callback does not exist')
            return None


    def __del__(self):
        self.remove()


def getSceneEvents():
    return {
            "kSceneUpdate": om.MSceneMessage.kSceneUpdate,
            "kBeforeNew": om.MSceneMessage.kBeforeNew,
            "kAfterNew": om.MSceneMessage.kAfterNew,
            "kBeforeImport": om.MSceneMessage.kBeforeImport,
            "kAfterImport": om.MSceneMessage.kAfterImport,
            "kBeforeOpen": om.MSceneMessage.kBeforeOpen,
            "kAfterOpen": om.MSceneMessage.kAfterOpen,
            "kBeforeExport": om.MSceneMessage.kBeforeExport,
            "kAfterExport": om.MSceneMessage.kAfterExport,
            "kBeforeSave": om.MSceneMessage.kBeforeSave,
            "kAfterSave": om.MSceneMessage.kAfterSave,
            "kBeforeCreateReference": om.MSceneMessage.kBeforeCreateReference,
            "kAfterCreateReference": om.MSceneMessage.kAfterCreateReference,
            "kBeforeRemoveReference": om.MSceneMessage.kBeforeRemoveReference,
            "kAfterRemoveReference": om.MSceneMessage.kAfterRemoveReference,
            "kBeforeImportReference": om.MSceneMessage.kBeforeImportReference,
            "kAfterImportReference": om.MSceneMessage.kAfterImportReference,
            "kBeforeExportReference": om.MSceneMessage.kBeforeExportReference,
            "kAfterExportReference": om.MSceneMessage.kAfterExportReference,
            "kBeforeUnloadReference": om.MSceneMessage.kBeforeUnloadReference,
            "kAfterUnloadReference": om.MSceneMessage.kAfterUnloadReference,
            "kBeforeLoadReference": om.MSceneMessage.kBeforeLoadReference,
            "kAfterLoadReference": om.MSceneMessage.kAfterLoadReference,
            "kBeforeSoftwareRender": om.MSceneMessage.kBeforeSoftwareRender,
            "kAfterSoftwareRender": om.MSceneMessage.kAfterSoftwareRender,
            "kBeforeSoftwareFrameRender": om.MSceneMessage.kBeforeSoftwareFrameRender,
            "kAfterSoftwareFrameRender": om.MSceneMessage.kAfterSoftwareFrameRender,
            "kSoftwareRenderInterrupted": om.MSceneMessage.kSoftwareRenderInterrupted,
            "kMayaInitialized": om.MSceneMessage.kMayaInitialized,
            "kMayaExiting": om.MSceneMessage.kMayaExiting}


def getEvents():
    return [
            "dbTraceChanged",
            "resourceLimitStateChange",
            "linearUnitChanged",
            "timeUnitChanged",
            "angularUnitChanged",
            "Undo",
            "undoSupressed",
            "Redo",
            "quitApplication",
            "idleHigh",
            "idle",
            "idleVeryLow",
            "RecentCommandChanged",
            "ToolChanged",
            "PostToolChanged",
            "ToolDirtyChanged",
            "ToolSettingsChanged",
            "tabletModeChanged",
            "DisplayRGBColorChanged",
            "customEvaluatorChanged",
            "serialExecutorFallback",
            "timeChanged",
            "currentContainerChange",
            "animLayerRebuild",
            "animLayerRefresh",
            "animLayerAnimationChanged",
            "animLayerLockChanged",
            "animLayerBaseLockChanged",
            "animLayerGhostChanged",
            "cteEventKeyingTargetForClipChanged",
            "cteEventKeyingTargetForLayerChanged",
            "cteEventKeyingTargetForInvalidChanged",
            "teClipAdded",
            "teClipModified",
            "teClipRemoved",
            "teCompositionAdded",
            "teCompositionRemoved",
            "teCompositionActiveChanged",
            "teCompositionNameChanged",
            "teMuteChanged",
            "cameraChange",
            "cameraDisplayAttributesChange",
            "SelectionChanged",
            "PreSelectionChangedTriggered",
            "LiveListChanged",
            "ActiveViewChanged",
            "SelectModeChanged",
            "SelectTypeChanged",
            "SelectPreferenceChanged",
            "DisplayPreferenceChanged",
            "DagObjectCreated",
            "transformLockChange",
            "renderLayerManagerChange",
            "renderLayerChange",
            "displayLayerManagerChange",
            "displayLayerAdded",
            "displayLayerDeleted",
            "displayLayerVisibilityChanged",
            "displayLayerChange",
            "renderPassChange",
            "renderPassSetChange",
            "renderPassSetMembershipChange",
            "passContributionMapChange",
            "DisplayColorChanged",
            "lightLinkingChanged",
            "lightLinkingChangedNonSG",
            "UvTileProxyDirtyChangeTrigger",
            "preferredRendererChanged",
            "polyTopoSymmetryValidChanged",
            "SceneSegmentChanged",
            "PostSceneSegmentChanged",
            "SequencerActiveShotChanged",
            "SoundNodeAdded",
            "SoundNodeRemoved",
            "ColorIndexChanged",
            "deleteAll",
            "NameChanged",
            "symmetricModellingOptionsChanged",
            "softSelectOptionsChanged",
            "SetModified",
            "xformConstraintOptionsChanged",
            "metadataVisualStatusChanged",
            "undoXformCmd",
            "redoXformCmd",
            "freezeOptionsChanged",
            "linearToleranceChanged",
            "angularToleranceChanged",
            "nurbsToPolygonsPrefsChanged",
            "nurbsCurveRebuildPrefsChanged",
            "constructionHistoryChanged",
            "threadCountChanged",
            "SceneSaved",
            "NewSceneOpened",
            "SceneOpened",
            "SceneImported",
            "PreFileNewOrOpened",
            "PreFileNew",
            "PreFileOpened",
            "PostSceneRead",
            "renderSetupAutoSave",
            "workspaceChanged",
            "PolyUVSetChanged",
            "PolyUVSetDeleted",
            "selectionConstraintsChanged",
            "nurbsToSubdivPrefsChanged",
            "startColorPerVertexTool",
            "stopColorPerVertexTool",
            "start3dPaintTool",
            "stop3dPaintTool",
            "DragRelease",
            "ModelPanelSetFocus",
            "modelEditorChanged",
            "MenuModeChanged",
            "gridDisplayChanged",
            "interactionStyleChanged",
            "axisAtOriginChanged",
            "CurveRGBColorChanged",
            "SelectPriorityChanged",
            "snapModeChanged",
            "texWindowEditorImageBaseColorChanged",
            "texWindowEditorCheckerDensityChanged",
            "texWindowEditorCheckerDisplayChanged",
            "texWindowEditorDisplaySolidMapChanged",
            "texWindowEditorShowup",
            "texWindowEditorClose",
            "activeHandleChanged",
            "ChannelBoxLabelSelected",
            "colorMgtOCIORulesEnabledChanged",
            "colorMgtUserPrefsChanged",
            "RenderSetupSelectionChanged",
            "colorMgtEnabledChanged",
            "colorMgtConfigFileEnableChanged",
            "colorMgtConfigFilePathChanged",
            "colorMgtConfigChanged",
            "colorMgtWorkingSpaceChanged",
            "colorMgtPrefsViewTransformChanged",
            "colorMgtPrefsReloaded",
            "colorMgtOutputChanged",
            "colorMgtPlayblastOutputChanged",
            "colorMgtRefreshed",
            "selectionPipelineChanged",
            "glFrameTrigger",
            "graphEditorChanged",
            "graphEditorParamCurveSelected",
            "graphEditorOutlinerHighlightChanged",
            "graphEditorOutlinerListChanged",
            "currentSoundNodeChanged",
            "EditModeChanged",
            "playbackRangeAboutToChange",
            "playbackSpeedChanged",
            "playbackModeChanged",
            "playbackRangeSliderChanged",
            "playbackByChanged",
            "playbackRangeChanged",
            "profilerSelectionChanged",
            "RenderViewCameraChanged",
            "texScaleContextOptionsChanged",
            "texRotateContextOptionsChanged",
            "texMoveContextOptionsChanged",
            "polyCutUVSteadyStrokeChanged",
            "polyCutUVEventTexEditorCheckerDisplayChanged",
            "polyCutUVShowTextureBordersChanged",
            "polyCutUVShowUVShellColoringChanged",
            "shapeEditorTreeviewSelectionChanged",
            "poseEditorTreeviewSelectionChanged",
            "sculptMeshCacheBlendShapeListChanged",
            "sculptMeshCacheCloneSourceChanged",
            "RebuildUIValues",
            "cacheDestroyed",
            "cachingPreferencesChanged",
            "cachingSafeModeChanged",
            "cachingEvaluationModeChanged",
            "teTrackAdded",
            "teTrackRemoved",
            "teTrackNameChanged",
            "teTrackModified",
            "cteEventClipEditModeChanged",
            "teEditorPrefsChanged"
    ]


def getNodeEvents():
    return {
            "addAttributeChangedCallback": om.MNodeMessage.addAttributeChangedCallback,
            "addAttributeAddedOrRemovedCallback": om.MNodeMessage.addAttributeAddedOrRemovedCallback,
            "addNodeDirtyPlugCallback": om.MNodeMessage.addNodeDirtyPlugCallback,
            "addNodePreRemovalCallback": om.MNodeMessage.addNodePreRemovalCallback,
            "addNodeDestroyedCallback": om.MNodeMessage.addNodeDestroyedCallback,
            "addKeyableChangeOverride": om.MNodeMessage.addKeyableChangeOverride,
    }


def getMDGEvents():
    return {
            "addTimeChangeCallback": om.MDGMessage.addTimeChangeCallback,
            "addForceUpdateCallback": om.MDGMessage.addForceUpdateCallback,
            "addNodeRemovedCallback": om.MDGMessage.addNodeRemovedCallback,
            "addConnectionCallback": om.MDGMessage.addConnectionCallback,
            "addPreConnectionCallback": om.MDGMessage.addPreConnectionCallback
    }