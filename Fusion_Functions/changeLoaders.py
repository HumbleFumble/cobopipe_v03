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
        self.sortAllLoaders()
        self.createWindow()
        # self.setMaximumHeight(400)
        # self.resize(400,400)

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

        # self._scrollAreaWidget = QtWidgets.QScrollArea()
        # self.setLayout(self._scrollAreaWidget)

        # Add tabs
        # self._tabWidget = QtWidgets.QTabWidget()
        # self._tabWidget.addTab(self.createTabOneLayout(), 'Test 1')
        # self._tabWidget.addTab(self.createTabOneLayout(), 'Test 2')
        # self._tabWidget.setTabPosition(QtWidgets.QTabWidget.East)

        self.scroll_lay = QtWidgets.QVBoxLayout()
        self.scrollarea = QtWidgets.QScrollArea()


        #
        # self.scroll_widget = QtWidgets.QWidget()

        self.layout_widget = QtWidgets.QWidget()
        self.layout_top = QtWidgets.QVBoxLayout()

        self.checkbox_layout = QtWidgets.QHBoxLayout()
        self.checkbox = QtWidgets.QCheckBox("Hide ignored loaders")
        self.checkbox.setChecked(True)

        self.checkbox_layout.addWidget(self.checkbox)

        self.layout_top.addLayout(self.checkbox_layout)
        for k,l in self.loader_dict.items():
            self.layout_top.addWidget(loaderFrame(k,l,self))

        self.layout_widget.setLayout(self.layout_top)

        # self.setLayout(self.layout_top)

        # self.scroll_lay.addWidget(self.layout_widget)


        # self.scrollarea.setWidget(self.scroll_widget)
        # self.scroll_widget.setLayout(self.layout_top)
        # self.scroll_lay.addWidget(self.scrollarea)

        self.scrollarea.setWidget(self.layout_widget)
        self.scroll_lay.addWidget(self.scrollarea)
        self.scrollarea.setWidgetResizable(True)
        self.setLayout(self.scroll_lay)

    def clickBrowse(self,cur_loaderFrame):
        current_text = cur_loaderFrame.loader_key.text()
        comp_path = ""

        if self.__fusion:
            current_comp_path = self.comp.GetAttrs("COMPS_FileName").replace("\\", "/")
            comp_path = os.path.dirname( current_comp_path )
        if os.path.dirname(current_text):
            comp_path = os.path.dirname(current_text)

        fileName = QtWidgets.QFileDialog.getOpenFileName(self,"Pick Input - First frame if stack", comp_path, "Image Files (*.png *.jpg *.bmp *.exr *.mov *.mp4)")[0]

        if fileName:
            cur_loaderFrame.path_text.setText(fileName)
            self.changeClip(loader_key=cur_loaderFrame.loader_key,new_path=fileName)
            cur_loaderFrame.loader_key = fileName

            # cur_loaderFrame.


class loaderFrame(QtWidgets.QFrame):
    def __init__(self, loader_key, loader_list,parent):
        super(loaderFrame, self).__init__()
        # self.setStyleSheet("border: 1px solid black; margin: 0px; padding: 0px;")
        self.loader_key = loader_key
        self.loader_list = loader_list
        self.layout = QtWidgets.QHBoxLayout()
        # self.layout.setContentsMargins(0, 0, 0, 0)
        # try:
        #     current_text = "/".join(self.loader_key.split("/")[-3:0])
        # except:
        #     current_text = self.loader_key
        self.path_text = QtWidgets.QLineEdit(self.loader_key)
        self.path_text.setMinimumWidth(250)

        self.browse_button = QtWidgets.QPushButton("Browse")

        self.browse_button.clicked.connect(partial(parent.clickBrowse,self))

        self.ignore_checkbox = QtWidgets.QCheckBox("Ignore")
        self.layout.addWidget(self.path_text)
        self.layout.addWidget(self.browse_button)
        self.layout.addWidget(self.ignore_checkbox)
        self.setLayout(self.layout)

    # def return_line(self):
    #     return self.lineEdit
    #
    # def return_browse(self):
    #     return self.browse_button


def run(fusion=None):
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    win = ChangeLoaders(fusion=fusion)
    # win.setMaximumHeight(400)
    win.resize(400, 100)
    # win.show()
    if win.exec_():
        value = win.getValue()
        return value
    return False



if __name__ == "__main__":
    run()