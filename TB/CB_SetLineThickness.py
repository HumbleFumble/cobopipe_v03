import shiboken6.Shiboken
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

import os
import json

try:
    from ToonBoom import harmony
    in_toonboom = True
except Exception as e:
    in_toonboom = False

def log(message):
    if in_toonboom:
        sess = harmony.session()
        sess.log(str(message))
    else:
        print(message)

def tbScene():
    sess = harmony.session()  # Fetch the currently active session of Harmony
    project = sess.project  # The project that is already loaded.
    return project.scene()



class FrontController(QObject):
    def __init__(self):
        super(FrontController, self).__init__()

        if in_toonboom:
            self.sess = harmony.session()
            self.scene = self.sess.project.scene
        else:
            self.sess = None
            self.scene = None
        self.save_dir = "C:/Temp/TB/"


    def findReadNodes(self,cur_node=None):
        if cur_node:
            scene_nodes = cur_node.nodes
        else:
            scene_nodes = self.scene.selection.nodes
        node_list = []
        for node in scene_nodes:
            if node.type == "GROUP":
                node_list.extend(self.findReadNodes(cur_node=node))
            if node.type == "READ":
                node_list.append(node)
        return node_list

    def setLineThickness(self,node,value=None,scale_depend=False):
        node.attributes["TEXT"].set_text_value(value) #Find attribute namez
        node.attributes["TEXT"].set_value(-1,scale_depend)  # Find enum scale attribute namez

class SetLineThickness_UI(QDialog):
    def __init__(self, parent=None):
        self._ctrl = FrontController()
        super(SetLineThickness_UI, self).__init__(parent)
        self.setWindowTitle("SetLineThickness_UI")
        self.setObjectName("SetLineThickness_UI")
        self.setWindowFlags(self.windowFlags()|Qt.Window|Qt.WindowStaysOnTopHint)
        self.node_list = []
        self.create_ui()
    def create_ui(self):
        self.main_lay = QVBoxLayout()
        self.selection_bttn = QPushButton("Set Selection")
        self.turn_off = QPushButton("Turn Off")
        self.reset_bttn = QPushButton("Reset")
        self.bttn_lay = QHBoxLayout()
        self.bttn_lay.addWidget(self.turn_off)
        self.bttn_lay.addWidget(self.reset_bttn)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider_label = QLabel("Value: ")
        self.slider_value = QLineEdit("0.0")
        self.slider_value.setFixedWidth(50)
        self.slider_lay = QHBoxLayout()
        self.slider_lay.addWidget(self.slider_label)
        self.slider_lay.addWidget(self.slider)
        self.slider_lay.addWidget(self.slider_value)


        self.scale_check = QCheckBox("Scale Independent")

        self.main_lay.addWidget(self.selection_bttn)
        self.main_lay.addLayout(self.slider_lay)
        self.main_lay.addWidget(self.scale_check)
        self.main_lay.addLayout(self.bttn_lay)
        self.setLayout(self.main_lay)

        

    def setSelection(self):
        self.node_list = []
        pass
    def reset_thickness(self):
        #get all scene read nodes
        #set to zero
        #turn off adjust line thickness
        pass
    def slider_proc(self):
        pass
    def text_proc(self):
        pass
def getParentWidget():
    topWidgets = QApplication.topLevelWidgets()
    for tw in topWidgets:
        if isinstance(tw, QMainWindow) and not tw.parentWidget():
            return tw
    return None

def run():
    global my_ui
    my_ui = SetLineThickness_UI(getParentWidget())
    my_ui.show()

if __name__ == '__main__':
    import sys
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    run()
    app.exec()