import shiboken6.Shiboken
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

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
            if not scene_nodes:
                scene_nodes = self.scene.nodes
        node_list = []
        for node in scene_nodes:
            if node.type == "GROUP":
                node_list.extend(self.findReadNodes(cur_node=node))
            if node.type == "READ":
                node_list.append(node)
        return node_list
    def checkAttributes(self,node):
        # Start with the base node's list, and recursively look through each attributelist thereafter.
        # A recursive function to look at all attributes in any attribute list, the node's attributes, or subattributes.
        self.detail_all_attributes(node.attributes, 0)

    def detail_all_attributes(self,attrblist, depth):
        for attrb in attrblist:
            log("%s %s -- %s" % ("  " * depth, attrb.full_keyword, attrb.type))
            if attrb.subattributes:  # If this attribute has further subattributes, detail them too.
                self.detail_all_attributes(attrb.subattributes, depth + 1)
    def reset(self):
        for n in self.scene.nodes:
            if n.type == "READ":
                self.setLineThickness(n,on_off=0,value=0)
    def select_nodes(self,list_of_nodes):
        self.scene.selection.select_none()
        for n in list_of_nodes:
            self.scene.selection.add(n)
    def turn_on_off(self,list_of_nodes=[],on_off=0):
        for n in list_of_nodes:
            self.setLineThickness(node=n,on_off=on_off,value=None)
    def setLineThickness(self,node,on_off=1,value=None,scale_depend=False):
        # TEXTURE_FILTER -- GENERIC_ENUM
        # ADJUST_PENCIL_THICKNESS -- BOOL
        # NORMAL_LINE_ART_THICKNESS -- BOOL
        # ZOOM_INDEPENDENT_LINE_ART_THICKNESS -- GENERIC_ENUM
        # MULT_LINE_ART_THICKNESS -- DOUBLE
        # ADD_LINE_ART_THICKNESS -- DOUBLE
        # MIN_LINE_ART_THICKNESS -- DOUBLE

        node.attributes["ADJUST_PENCIL_THICKNESS"].set_value(-1,on_off)
        if value:
            if scale_depend:
                node.attributes["ZOOM_INDEPENDENT_LINE_ART_THICKNESS"].set_value(-1,1)
            else:
                node.attributes["ZOOM_INDEPENDENT_LINE_ART_THICKNESS"].set_value(-1, 0)
            node.attributes["MULT_LINE_ART_THICKNESS"].set_localvalue(value)


class SetLineThickness_UI(QDialog):
    def __init__(self, parent=None):
        self._ctrl = FrontController()
        super(SetLineThickness_UI, self).__init__(parent)
        self.setWindowTitle("SetLineThickness_UI")
        self.setObjectName("SetLineThickness_UI")
        self.setWindowFlags(self.windowFlags()|Qt.Window|Qt.WindowStaysOnTopHint)
        self.node_list = []
        self.FC = FrontController()
        self.create_ui()
        self.toggle_on_off = 0


    def create_ui(self):
        self.main_lay = QVBoxLayout()
        self.pick_selection_bttn = QPushButton("Set Selection")
        self.set_selection_bttn = QPushButton("Pick Previous Selection")
        self.turn_on_off_bttn = QPushButton("Toggle On/Off")
        self.reset_bttn = QPushButton("Reset all")
        self.bttn_lay = QHBoxLayout()
        self.bttn_lay.addWidget(self.turn_on_off_bttn)
        self.bttn_lay.addWidget(self.reset_bttn)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider_label = QLabel("Value: ")
        self.slider_value = QLineEdit("0.0")
        self.slider_value.setFixedWidth(50)
        self.slider_lay = QHBoxLayout()
        self.slider_lay.addWidget(self.slider_label)
        self.slider_lay.addWidget(self.slider)
        self.slider_lay.addWidget(self.slider_value)
        self.slider.setMaximum(200)

        # self.slider_int = QDoubleValidator()
        # self.slider_value.setValidator(self.slider_int)
        self.slider.valueChanged.connect(self.slider_proc)

        self.slider_value.editingFinished.connect(self.text_proc)


        self.pick_selection_bttn.clicked.connect(self.pickSelection)
        self.set_selection_bttn.clicked.connect(self.setSelection)
        self.reset_bttn.clicked.connect(self.reset_thickness)
        self.turn_on_off_bttn.clicked.connect(self.turn_on_off)
        self.scale_check = QCheckBox("Scale Independent")

        self.main_lay.addWidget(self.pick_selection_bttn)
        self.main_lay.addWidget(self.set_selection_bttn)
        self.main_lay.addLayout(self.slider_lay)
        self.main_lay.addWidget(self.scale_check)
        self.main_lay.addLayout(self.bttn_lay)
        self.scale_check.setChecked(True)
        self.setLayout(self.main_lay)

        

    def pickSelection(self):
        self.node_list = []
        self.node_list = self.FC.findReadNodes()

    def setSelection(self):
        self.FC.select_nodes(self.node_list)

    def reset_thickness(self):
        self.FC.reset()
    def turn_on_off(self): #do selection instead??

        self.FC.turn_on_off(list_of_nodes=self.node_list,on_off=self.toggle_on_off)
        if self.toggle_on_off == 1:
            self.toggle_on_off = 0
        else:
            self.toggle_on_off = 1

    def slider_proc(self):
        v = round(self.slider.value() * 0.1,1)
        self.slider_value.setText(str(v))
        for n in self.node_list:
            self.FC.setLineThickness(node=n,value=v,scale_depend=self.scale_check.isChecked())

    def text_proc(self):
        v = int(round(float(self.slider_value.text()),1)*10)
        self.slider.setValue(v)

def getParentWidget():
    topWidgets = QApplication.topLevelWidgets()
    for tw in topWidgets:
        if isinstance(tw, QMainWindow) and not tw.parentWidget():
            return tw
    return None

def run():
    global my_ui
    my_ui = SetLineThickness_UI(getParentWidget())
    my_ui.resize(300,100)
    my_ui.show()

if __name__ == '__main__':
    import sys
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    run()
    app.exec()