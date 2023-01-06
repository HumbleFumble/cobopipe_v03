import sys
from PySide2.QtWidgets import QMainWindow, QWidget, QSizePolicy, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem
from PySide2.QtGui import QPixmap, QIcon, QIntValidator
from shiboken2 import wrapInstance
import maya.OpenMayaUI as OpenMayaUI
from maya.OpenMayaUI import MQtUtil
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin, MayaQDockWidget
import maya.cmds as cmds
from MayaDockable import *
from Maya_Functions.file_util_functions import generateID


class CalcugatorWidget(QWidget):
    def __init__(self):
        super(CalcugatorWidget, self).__init__()
        self.setObjectName('calcugatorWidget')
        self.setStyleSheet('''
        QLabel {
            font: bold;
        }
        ''')

        self.listItems = {}

        # Settings
        self.controller = 'calcugatorDisplay_Ctrl'
        self.calcLocator = 'calcugatorDisplay_LOC'
        self.textShader = 'rig_calcDisplayTextSG'
        self.prefix = 'calcugatorText'
        minimumLabelWidth = 25

        self.ids = []

        # Creation
        self.mainLayout = QVBoxLayout()

        self.input = InputWidget(minimumLabelWidth)
        self.input.setFixedHeight(50)

        self.listLayout = QVBoxLayout()
        self.listWidget = QListWidget()

        self.buttonLayout = QHBoxLayout()
        self.syncButton = QPushButton('Sync')
        self.syncButton.setStyleSheet('''QPushButton { font: bold; background-color: #55adca; }''')
        self.syncButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.syncButton.setMaximumHeight(25)
        self.deleteButton = QPushButton('Delete')
        self.deleteButton.setStyleSheet('''QPushButton { font: bold; background-color: #d16c6c; }''')
        self.deleteButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.deleteButton.setMaximumHeight(25)

        # Assembly
        self.setLayout(self.mainLayout)

        self.mainLayout.addWidget(self.input)

        self.mainLayout.addLayout(self.listLayout)
        self.listLayout.addWidget(self.listWidget)
        self.listLayout.addLayout(self.buttonLayout)
        self.buttonLayout.addWidget(self.syncButton)
        self.buttonLayout.addWidget(self.deleteButton)

        #self.mainLayout.addStretch(1)

        # Connect
        self.input.addButton.clicked.connect(lambda: self.add())
        self.syncButton.clicked.connect(lambda: self.sync())
        self.deleteButton.clicked.connect(lambda: self.delete())

        self.sync()


    def add(self):
        while True:
            id = generateID()
            if id not in self.ids:
                self.ids.append(id)
                break

        self.startFrame = self.input.startFrameInput.text()
        if self.startFrame:
            self.startFrame = int(self.startFrame)
        else:
            self.startFrame = int(cmds.playbackOptions(query=True, min=True))

        self.endFrame = self.input.endFrameInput.text()
        if self.endFrame:
            self.endFrame = int(self.endFrame)
        else:
            self.endFrame = int(cmds.playbackOptions(query=True, max=True))

        self.textNode = createDisplayText(prefix = self.prefix, suffix = id, text = self.input.textInput.text(), font='Digital-7 Mono') #Mokoko   / Digital-7 Mono
        positionText(self.textNode, locator=self.calcLocator)
        applyShader(self.textNode, self.textShader)
        self.attribute = createTextVisAttr(self.prefix, self.textNode, self.controller)
        key(self.controller, self.attribute, 0, self.startFrame - 1)
        key(self.controller, self.attribute, 1, self.startFrame)
        key(self.controller, self.attribute, 1, self.endFrame)
        key(self.controller, self.attribute, 0, self.endFrame + 1)
        self.addListItem(self.textNode, self.controller, self.attribute)


    def delete(self):
        self.items = self.listWidget.selectedItems()
        if self.items:
            for self.item in self.items:
                cmds.deleteAttr('::' + self.listItems[self.item.text()]['controller'] + '.' + self.listItems[self.item.text()]['attribute'])
                cmds.delete('::' + self.listItems[self.item.text()]['node'])
                self.listWidget.takeItem(self.listWidget.row(self.listItems[self.item.text()]['widget']))


    def addListItem(self, node, controller, attribute):
        self.name = node.replace(self.prefix + '_', '')
        self.item = QListWidgetItem(self.name)
        self.listWidget.addItem(self.item)
        self.listItems[self.name] = {'node': node,
                                     'controller': controller,
                                     'attribute': attribute,
                                     'widget': self.item}

    def sync(self):
        items = []
        for current in range(self.listWidget.count()):
            items.append(self.listWidget.item(current))

        itemNames = []
        for item in items:
            itemNames.append(item.text())

        if cmds.objExists('::' + self.controller):
            self.attributes = cmds.listAttr('::' + self.controller, keyable=True)
            self.attributes.remove('screenOnOff')
            if self.attributes:
                for self.attribute in self.attributes:
                    self.node = self.attribute.replace('text_', self.prefix + '_')
                    try:
                        name = self.node.replace(self.prefix + '_', '')
                    except:
                        name = self.node
                    if cmds.objExists('::' + self.node):
                        if name not in itemNames:
                            self.addListItem(self.node, self.controller, self.attribute)
                    else:
                        if not self.attribute == 'visibility':
                                cmds.deleteAttr('::' + self.controller + '.' + self.attribute)
                        if name in itemNames:
                            self.listWidget.takeItem(self.listWidget.row(items[itemNames.index(name)]))
                            if name[-6:] in self.ids:
                                self.ids.remove(name[-6:])

                for node in cmds.ls('::' + self.prefix + '_*', type='transform'):
                    name = node.replace(self.prefix + '_', '')
                    attributeName = node.replace(self.prefix + '_', 'text_')
                    if attributeName not in self.attributes:
                        cmds.delete('::' + node)
                        if name in itemNames:
                            self.listWidget.takeItem(self.listWidget.row(items[itemNames.index(name)]))
                            if name[-6:] in self.ids:
                                self.ids.remove(name[-6:])

            else:
                for item in items:
                    self.listWidget.takeItem(self.listWidget.row(item))


            for itemName in itemNames:
                if not cmds.ls('::' + self.prefix + '_' + itemName, type='transform'):
                    self.listWidget.takeItem(self.listWidget.row(items[itemNames.index(itemName)]))
                    if itemName[-6:] in self.ids:
                        self.ids.remove(itemName[-6:])


class InputWidget(QWidget):
    def __init__(self, minimumLabelWidth):
        super(InputWidget, self).__init__()

        self.mainLayout = QVBoxLayout()
        self.mainLayout.setMargin(0)
        self.secondLayout = QHBoxLayout()
        self.inputLayout = QVBoxLayout()

        self.textInputLayout = QHBoxLayout()
        self.textInputLabel = QLabel('Text')
        self.textInputLabel.setMinimumWidth(minimumLabelWidth)
        self.textInput = QLineEdit()

        self.frameInputLayout = QHBoxLayout()
        self.startFrameInputLayout = QHBoxLayout()
        self.startFrameInputLabel = QLabel('Start')
        self.startFrameInputLabel.setMinimumWidth(minimumLabelWidth)
        self.onlyNumbers = QIntValidator()
        self.startFrameInput = QLineEdit()
        self.startFrameInput.setValidator(self.onlyNumbers)
        self.endFrameInputLayout = QHBoxLayout()
        self.endFrameInputLabel = QLabel('End')
        self.endFrameInputLabel.setMinimumWidth(minimumLabelWidth)
        self.endFrameInput = QLineEdit()
        self.endFrameInput.setValidator(self.onlyNumbers)

        self.addButton = QPushButton('Add')
        self.addButton.setMaximumWidth(100)
        self.addButton.setStyleSheet('''QPushButton { font: bold; background-color: #6cd16c; }''')
        self.addButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        #Assembly
        self.setLayout(self.mainLayout)
        self.mainLayout.addLayout(self.secondLayout)
        self.secondLayout.addLayout(self.inputLayout)
        self.secondLayout.addWidget(self.addButton)

        self.inputLayout.addLayout(self.textInputLayout)
        self.inputLayout.addLayout(self.frameInputLayout)

        self.textInputLayout.addWidget(self.textInputLabel)
        self.textInputLayout.addWidget(self.textInput)

        self.frameInputLayout.addLayout(self.startFrameInputLayout)
        self.startFrameInputLayout.addWidget(self.startFrameInputLabel)
        self.startFrameInputLayout.addWidget(self.startFrameInput)
        self.frameInputLayout.addLayout(self.endFrameInputLayout)
        self.endFrameInputLayout.addWidget(self.endFrameInputLabel)
        self.endFrameInputLayout.addWidget(self.endFrameInput)


# Functionality
def createDisplayText(prefix, suffix, text=None, locator=None, font=None):
    if not text:
        text = 'ERROR'

    if font:
        groupNode, makeTextNode = cmds.textCurves(name= prefix + '_tmp', text=text, font=font)
    else:
        groupNode, makeTextNode = cmds.textCurves(name= prefix + '_tmp', text=text)

    curves = []
    for node in cmds.listConnections(makeTextNode):
        shapes = cmds.listRelatives(node, shapes=True, fullPath=True)
        if shapes:
            curves.extend(shapes)
    nurbsText = cmds.planarSrf(curves, name= prefix + '_' + text)[0]
    cmds.delete(groupNode)

    dirtyName = nurbsText.replace(prefix, '')
    cleanName = prefix + '_' + dirtyName.replace('_', '') + '_' + suffix

    nurbsText = cmds.rename(cleanName)
    return nurbsText


def positionText(node, locator=None):
    length = cmds.exactWorldBoundingBox(node)[3]
    cmds.setAttr(node + '.translateX', length * -1)
    cmds.xform(node, piv=(0, 0, 0), ws=True)
    cmds.makeIdentity(node, apply=True)

    scaleValue = 0.5
    if locator:
        locator = cmds.ls('::' + locator, long=True)[0]
        if cmds.objExists(locator):
            cmds.parent(node, locator)
            for attribute in ['translate', 'rotate', 'scale']:
                for axis in ['X', 'Y', 'Z']:
                    if attribute == 'scale':
                        value = scaleValue
                    else:
                        value = 0
                    cmds.setAttr(node + '.' + attribute + axis, value)
            cmds.parent(node, world=True)

    cmds.makeIdentity(node, apply=True)
    group = cmds.ls('::calcugatorDisplayText_Group', long=True)
    cmds.parent(node, group)


def createTextVisAttr(prefix, node, controller):
    attributeName = node.replace(prefix + '_', 'text_')
    niceName = attributeName.replace('_', ' ').replace('text', 'Text')
    if not cmds.attributeQuery(attributeName, node='::' + controller, exists=True):
        currentSelection = cmds.ls(sl=True, long=True)
        cmds.select('::' + controller)
        cmds.addAttr(longName=attributeName, niceName=niceName, attributeType='bool', keyable=True)
        cmds.connectAttr('::' + controller + '.' + attributeName, node + '.visibility')
        cmds.select(currentSelection)
    return attributeName


def key(node, attribute, value, frame):
    currentTime = cmds.currentTime(query=True)
    cmds.currentTime(frame)
    cmds.setKeyframe('::' + node, attribute=attribute, value=value)
    cmds.currentTime(currentTime)


def applyShader(node, shader):
    currentSelection = cmds.ls(sl=True, long=True)
    cmds.select(node)
    cmds.sets(e=True, forceElement='::' + shader)
    cmds.select(currentSelection)


def run():
    objectName = 'calcugator_mainWindow'
    if not dockableExists(objectName):
       runDockable(objectName,  'Calcugator Text', CalcugatorWidget())
