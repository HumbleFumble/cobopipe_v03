import os.path

import PySide2
from PySide2 import QtWidgets, QtCore, QtGui
import sys
from functools import partial

#TODO use Comp.SetData to save the ignored loaders to avoid clutter
class ChangeLoaders(QtWidgets.QDialog):

    def __init__(self, fusion):
        super(ChangeLoaders, self).__init__()
        if fusion:
            self.__fusion = fusion
            self.comp = self.__fusion.GetCurrentComp()
            self.loader_dict = {}
        else:
            self.__fusion = None
        self.setWindowTitle("Change Loaders")
        self.loaderFrame_dict = {}
        self.ignore_list = []
        self.sortAllLoaders()
        comp_data = self.comp.GetData("loader_ignore_list")
        if comp_data:
            self.ignore_list = list(comp_data.values())
            self.updateSceneData()
        self.createWindow()
        self.updateVisibility()


        # self.setMaximumHeight(400)
        # self.resize(400,400)
    def updateSceneData(self):
        scene_loaders = set(self.loader_dict.keys())

        new_ignore = set(self.ignore_list).intersection(scene_loaders)

        self.ignore_list = list(new_ignore)
        self.comp.SetData("loader_ignore_list",self.ignore_list)

    def sortAllLoaders(self):
        all_loaders = self.comp.GetToolList(False, "Loader").values()
        self.loader_dict = {}
        for loader in all_loaders:
            cur_loader_path = (loader.GetAttrs("TOOLST_Clip_Name")[1]).replace("\\", "/")
            if not cur_loader_path in self.loader_dict.keys():
                self.loader_dict[cur_loader_path] = [loader]
            else:
                self.loader_dict[cur_loader_path].append(loader)


    def changeClip(self, loader_key,new_path):
        for loader in self.loader_dict[loader_key]:
            loader.Clip = new_path
            if list(loader.GetAttrs("TOOLIT_Clip_Length").values())[0] < 2:
                print("Found 1 frame, setting to loop")
                loader.Loop = 1
                loader["GlobalIn"] = 0
                loader.ClipTimeStart = 0
                loader["GlobalIn"] = 1
                loader["GlobalOut"] = 1
            else:
                loader["GlobalIn"] = 1
                loader.ClipTimeStart = 0

    def createWindow(self):

        self.scroll_lay = QtWidgets.QVBoxLayout()
        self.scrollarea = QtWidgets.QScrollArea()
        # self.scrollarea.setMinimumWidth(500)


        self.layout_widget = QtWidgets.QWidget()
        self.layout_top = QtWidgets.QVBoxLayout()
        self.layout_top.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.checkbox_layout = QtWidgets.QHBoxLayout()
        self.ignore_list_checkbox = QtWidgets.QCheckBox("Hide ignored loaders")
        self.ignore_list_checkbox.setChecked(True)
        self.ignore_list_count = QtWidgets.QLabel(f"Hidden Loaders: {len(self.ignore_list)}")
        self.ignore_list_checkbox.stateChanged.connect(self.updateVisibility)
        self.checkbox_layout.addWidget(self.ignore_list_checkbox)
        self.checkbox_layout.addWidget(self.ignore_list_count)

        self.layout_top.addLayout(self.checkbox_layout)
        for k in sorted(self.loader_dict.keys()):
            l = self.loader_dict[k]
            lf = loaderFrame(k,l,self)
            self.layout_top.addWidget(lf)
            self.loaderFrame_dict[k] = lf

        self.layout_widget.setLayout(self.layout_top)

        # self.setLayout(self.layout_top)

        # self.scroll_lay.addWidget(self.layout_widget)


        # self.scrollarea.setWidget(self.scroll_widget)
        # self.scroll_widget.setLayout(self.layout_top)
        # self.scroll_lay.addWidget(self.scrollarea)

        self.scrollarea.setWidget(self.layout_widget)
        self.scroll_lay.addWidget(self.scrollarea)
        self.scrollarea.setWidgetResizable(True)
        # self.scrollarea.setMinimumWidth(self.layout_widget.sizeHint().width())

        self.setLayout(self.scroll_lay)

    def clickBrowse(self,cur_loaderFrame):
        current_text = cur_loaderFrame.loader_key
        comp_path = ""

        if self.__fusion:
            current_comp_path = self.comp.GetAttrs("COMPS_FileName").replace("\\", "/")
            comp_path = os.path.dirname( current_comp_path )
        if os.path.dirname(current_text):
            comp_path = os.path.dirname(current_text)

        fileName = QtWidgets.QFileDialog.getOpenFileName(self,"Pick Input - First frame if stack", comp_path, "Image Files (*.png *.jpg *.bmp *.exr *.mov *.mp4)")[0]

        if fileName:
            # cur_loaderFrame.path_text.setText(fileName)
            self.changeClip(loader_key=cur_loaderFrame.loader_key,new_path=fileName)
            cur_loaderFrame.loader_key = fileName
            cur_loaderFrame.setTextAndTooltip(fileName)
            if current_text in self.ignore_list:
                self.ignore_list.remove(current_text)
                if cur_loaderFrame.ignore_checkbox.isChecked:
                    self.updateIgnoreList(cur_loaderFrame)

    def updateIgnoreList(self,cur_loaderFrame,*args):

        if cur_loaderFrame.ignore_checkbox.isChecked():
            if not cur_loaderFrame.loader_key in self.ignore_list:
                self.ignore_list.append(cur_loaderFrame.loader_key)
        else:
            if cur_loaderFrame.loader_key in self.ignore_list:
                self.ignore_list.remove(cur_loaderFrame.loader_key)
        self.comp.SetData("loader_ignore_list",self.ignore_list)
        self.ignore_list_count.setText(f"Hidden Loaders: {len(self.ignore_list)}")
        self.updateVisibility()
    def updateVisibility(self,*args):
        for i in self.ignore_list:
            if self.ignore_list_checkbox.isChecked():
                # print(self.loaderFrame_dict[i].loader_key)
                self.loaderFrame_dict[i].setVisible(False)
            else:
                self.loaderFrame_dict[i].setVisible(True)
    def pickLoader(self,cur_loaderFrame):
        current_active = self.comp.ActiveTool()
        final_number = 0
        for number,l in enumerate(cur_loaderFrame.loader_list):
            if str(l) == str(current_active):
                if number == (len(cur_loaderFrame.loader_list)-1):
                    final_number = 0
                else:
                    final_number = number + 1
        self.comp.SetActiveTool(cur_loaderFrame.loader_list[final_number])

class loaderFrame(QtWidgets.QFrame):
    def __init__(self, loader_key, loader_list,parent):
        super(loaderFrame, self).__init__()
        # self.setStyleSheet("border: 1px solid black; margin: 0px; padding: 0px;")
        self.parent_class = parent
        self.loader_key = loader_key
        self.loader_list = loader_list
        self.layout = QtWidgets.QHBoxLayout()

        # self.layout.setContentsMargins(0, 0, 0, 0)

        # current_text = os.path.split(self.loader_key)
        # current_dir = os.path.dirname(self.loader_key)

        self.path_text = QtWidgets.QLineEdit()
        self.path_text.setMinimumWidth(450)

        self.setTextAndTooltip(path=self.loader_key)

        self.browse_button = QtWidgets.QPushButton("Browse")

        self.browse_button.clicked.connect(partial(self.parent_class.clickBrowse,self))
        
        self.pick_button = QtWidgets.QPushButton("Pick")
        self.pick_button.clicked.connect(partial(self.parent_class.pickLoader,self))

        self.number_of_loaders = QtWidgets.QLabel(f"Amount: {len(self.loader_list):02}")
        # self.number_of_loaders.setMinimumWidth(60)
        self.ignore_checkbox = QtWidgets.QCheckBox("Ignore")
        if self.loader_key in self.parent_class.ignore_list:
            self.ignore_checkbox.setChecked(True)
        self.ignore_checkbox.stateChanged.connect(partial(self.parent_class.updateIgnoreList, self))
        self.layout.addWidget(self.ignore_checkbox)
        self.layout.addWidget(self.path_text)
        self.layout.addWidget(self.browse_button)
        self.layout.addWidget(self.pick_button)
        self.layout.addWidget(self.number_of_loaders)

        # self.setMinimumWidth(self.path_text.sizeHint().width())
        self.setLayout(self.layout)

    def setTextAndTooltip(self, path):
        # try:
        path_split = path.split("/")
        if len(path_split)>2:

            current_text = "/".join(path_split[-2:])
        else:
            current_text = path_split[-1]

        self.path_text.setText(current_text)
        self.path_text.setToolTip(self.loader_key)


def run(fusion=None):
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    win = ChangeLoaders(fusion=fusion)
    # win.setMaximumHeight(400)
    # win.resize(700, 400)

    # win.show()
    if win.exec_():
        value = win.getValue()
        return value
    return False



if __name__ == "__main__":
    run()