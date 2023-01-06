# Python file
# from PythonQt.QtGui import *
# from PythonQt.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

def uiMessage():
    messageLog.trace(input.text)
    input.text = ""


def createUI():
    global myUI  # this needs to be global otherwise as soon as the function is over, the created UI will be destroy
    global input  # this needs to be global since we access it from another function
    messageLog.trace("RUNNING")
    messageLog.trace(pythonManager.appWidget())

    myUI = QWidget()
    # myUI.setParent(pythonManager.appWidget)  # without this line, the UI we create will not be closed when harmony is closing.
    myUI.setWindowFlags(Qt.Window)  # this line allow the UI to be in it's own window

    box = QVBoxLayout(myUI)
    input = QLineEdit(myUI)
    box.addWidget(input)

    push1 = QPushButton(myUI)
    push1.text = 'Send text to messageLog'
    push1.clicked.connect(uiMessage)
    box.addWidget(push1)

    push2 = QPushButton(myUI)
    push2.text = 'this button is not connected'
    box.addWidget(push2)

    check = QCheckBox(myUI)
    check.text = 'Does nothing'
    box.addWidget(check)

    myUI.show()

def TestManager():
    messageLog.trace(pythonManager.__dict__)
    messageLog.trace(dir(pythonManager))
    if not QApplication.instance():
        messageLog.trace("Can't find")
    else:
        messageLog.trace("found")
    messageLog.trace(pythonManager.appWidget)