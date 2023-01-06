from maya.OpenMayaUI import MQtUtil
from shiboken2 import wrapInstance
from PySide2.QtWidgets import QMainWindow, QWidget
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
import maya.cmds as cmds
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
    pointer = MQtUtil.mainWindow()
    if pointer:
        return wrapInstance(long(pointer), QWidget)


def getWindowInMaya(name):
    pointer = MQtUtil.findWindow(name)
    if pointer:
        return wrapInstance(long(pointer), QWidget)


class MayaDockable(MayaQWidgetDockableMixin, QMainWindow):
    def __init__(self, objectName, title, centralWidget, parent=getMayaWindow()):
        super(MayaDockable, self).__init__(parent)
        self.setObjectName(objectName)
        self.setWindowTitle(title)
        self.setCentralWidget(centralWidget)
        self.beenClosed = False

    def dockCloseEventTriggered(self):
        for c in self.children():
            try:
                c.close()
            except Exception as e:
                pass
                # logger.debug("Tried to close a child of %s" % self.objectName())
        self.beenClosed = True


def clearDockable(objectName):
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
        cmds.deleteUI(objectName + 'WorkspaceControl')
    except Exception as e:
        print(e)

def dockableExists(objectName): # title, centralWidget
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
    """
    Creates Dockable QMainWindow containing passed central widget.

    :param objectName: The name of the QWidget object
    :param title: The window title
    :param centralWidget: The QWidget that will be set as centralWidget
    :return: instance of MayaDock class
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