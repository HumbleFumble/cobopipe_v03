import maya.cmds as cmds
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from maya.OpenMayaUI import MQtUtil
from PySide2.QtWidgets import QMainWindow, QWidget
from shiboken2 import wrapInstance
from Log.CoboLoggers import getLogger

logger = getLogger()
import reloadModules as rm

"""
    Launching QWidget inside MayaQWidgetDockableMixin

    objectName = 'AssetBrowserDock'
    windowTitle = 'AssetBrowser'
    if not dockableExists(objectName):
       openDockable(objectName,  windowTitle, QWidgetClass())
"""


def getMayaWindow():
    """Fetches memory pointer to current instance of Maya's main window
    and wraps it in a QWidget instance.

    Returns:
        object: Returns pointer wrapped as QWidget instance.
    """
    pointer = MQtUtil.mainWindow()
    if pointer:
        # Converts memory pointer to type integer. This is Python 3 behavior.
        # To run this in Python 2, convert pointer to type long.
        return wrapInstance(int(pointer), QWidget)


def getWindowInMaya(name):
    """Fetches memory pointer to current instance of specific Maya window based on object name.

    Args:
        name (str): Object name of window to get.

    Returns:
        object: Returns pointer wrapped as QWidget instance.
    """
    pointer = MQtUtil.findWindow(name)
    if pointer:
        # Converts memory pointer to type integer. This is Python 3 behavior.
        # To run this in Python 2, convert pointer to type long.
        return wrapInstance(int(pointer), QWidget)


class MayaDockable(MayaQWidgetDockableMixin, QMainWindow):
    """Custom wrapper container for Qt Window inheriting docking abilities within Maya.

    Args:
        MayaQWidgetDockableMixin (object): Instance of maya.app.general.mayaMixin.MayaQWidgetDockableMixin class.
        QMainWindow (object): Instance of PySide2.QtWidgets.QMainWindow class.
    """

    def __init__(self, objectName, title, centralWidget, parent=getMayaWindow()):
        """Initializing instance of MayaDockable.

        Args:
            objectName (str): Object name.
            title (str): Window title.
            centralWidget (str): QWidget to set as central widget.
            parent (object, optional): Class instance of QWidget. Defaults to getMayaWindow().
        """
        super(MayaDockable, self).__init__(parent)
        self.setObjectName(objectName)
        self.setWindowTitle(title)
        self.setCentralWidget(centralWidget)
        self.beenClosed = False

    def dockCloseEventTriggered(self):
        """Attempting to close all children on close event."""
        for c in self.children():
            try:
                c.close()
            except Exception as e:
                pass
        self.beenClosed = True


def clearDockable(objectName):
    """Trying to delete all traces of the dockable.

    Args:
        objectName (str): Object name of QWidget.
    """
    try:
        if dockableDictionary:
            if objectName in dockableDictionary.keys():
                dockableWidget = dockableDictionary[objectName]
    except:
        pass

    try:
        dockableWidget.close()  # pylint: disable=E0601
        dockableWidget.deleteLater()
    except Exception as e:
        print(e)

    try:
        cmds.deleteUI(objectName)
    except Exception as e:
        print(e)

    try:
        cmds.deleteUI(objectName + "WorkspaceControl")
    except Exception as e:
        print(e)


def dockableExists(objectName):
    """Trying to determine if the window exists.
    If window does not exists, it will attempt to clear any remains left behind.

    Args:
        objectName (str): Object name of QWidget.

    Returns:
        bool: Returns True if window exists. Otherwise False.
    """
    try:
        window = getWindowInMaya(objectName)
    except Exception as e:
        print(e)
        try:
            clearDockable(objectName)
        except Exception as e:
            print(e)

    if window:
        try:
            if dockableDictionary:
                if objectName in dockableDictionary.keys():
                    dockableWidget = dockableDictionary[objectName]

                    if dockableWidget.beenClosed:
                        window = False
                        clearDockable(objectName)
                    else:
                        try:
                            if dockableWidget.isFloating():
                                dockableWidget.raise_()
                            else:
                                dockableWidget.raise_()
                        except Exception as e:
                            print(e)
                else:
                    clearDockable(objectName)
                    window = False
        except:
            clearDockable(objectName)
            window = False

    return window


def runDockable(objectName, title, centralWidget):
    """Creates QMainWindow wrapped in DockableMixin and sets central widget.

    Args:
        objectName (str): Object name of the QWidget object.
        title (str): Window title.
        centralWidget (object): Class instance of QWidget.

    Returns:
        object: Class instance of MayaDockable.
    """
    global dockableDictionary

    # if global variable dockableDictionary does not exist, an empty dockableDictionary is created.
    try:
        if dockableDictionary:
            pass
    except:
        dockableDictionary = {}

    dockableDictionary[objectName] = MayaDockable(objectName, title, centralWidget)
    dockableDictionary[objectName].show(dockable=True)

    return dockableDictionary[objectName]
