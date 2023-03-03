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

def getParentWidget():
    topWidgets = QApplication.topLevelWidgets()
    for tw in topWidgets:
        if isinstance(tw, QMainWindow) and not tw.parentWidget():
            return tw
    return None

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

def run():
    global my_ui
# my_ui = SelectionPreset_UI(getParentWidget())

if __name__ == '__main__':
    import sys
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    run()
    app.exec()