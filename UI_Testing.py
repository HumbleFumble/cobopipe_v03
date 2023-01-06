from Log.CoboLoggers import getLogger,setFileLevel,setConsoleLevel
# from getConfig import getConfigClass
# CC = getConfigClass()

#TESTING
try:
    import maya.cmds as cmds
    from PySide2 import QtWidgets, QtCore, QtGui
    in_maya = True


except:
    from PySide2 import QtWidgets, QtCore, QtGui
    in_maya = False

if in_maya:
    import MayaDockable
    import reloadModules

class MainWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setObjectName("UI_TEST")
        self.setWindowTitle("UI_TEST")
        self.setWindowFlags(QtCore.Qt.Window)
        self.CreateWindow()
    
    def CreateAction(self,name,menu):
        ##The inside of a menu action with all widgets as variables#
        action_event_widget = QtWidgets.QWidget()
        action_event_widget.setContentsMargins(0,0,0,0)


        action_event_widget_layout = QtWidgets.QHBoxLayout()
        # action_event_widget_layout.setSpacing(0)
        action_event_widget_layout.setContentsMargins(0,0,0,0)

        push_button = QtWidgets.QPushButton("Click Test")
        label = QtWidgets.QLabel("Label Test")
        checkbox_widget = QtWidgets.QCheckBox("Test")
        checkbox_widget.setChecked(True)

        action_event_widget_layout.addWidget(label)
        action_event_widget_layout.addWidget(push_button)
        action_event_widget_layout.addWidget(checkbox_widget)
        action_event_widget.setLayout(action_event_widget_layout)

        checkbox_action = QtWidgets.QWidgetAction(menu)
        checkbox_action.triggered.connect(self.clickity)
        checkbox_action.setText(name)
        checkbox_action.setDefaultWidget(action_event_widget)
        return checkbox_action
        
    def clickity(self):
        print("CLICK!")

    def CreateWindow(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.menu_bar = QtWidgets.QMenuBar()

        self.menu_options = QtWidgets.QMenu("Options", self.menu_bar)
        self.menu_options.setToolTipsVisible(True)
        for a in range(3):
            print(a)
            a_act = self.CreateAction("Action_%s" %a,self.menu_options)
            self.menu_options.addAction(a_act)

        self.menu_bar.addMenu(self.menu_options)
        self.main_layout.addWidget(self.menu_bar)
        #
        self.right_click_widget = QtWidgets.QWidget()
        self.right_click_widget.setMinimumSize(100,100)
        self.right_click_widget.installEventFilter(self)
        self.main_layout.addWidget(self.right_click_widget)

        self.setLayout(self.main_layout)


    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.ContextMenu:
            print(source)

            # menu = self.menu_options
            action = self.menu_options.exec_(event.globalPos())
            if not action == None:
                print("Works??")
                print(action)
        return super(MainWindow, self).eventFilter(source, event)


if not in_maya:

    if __name__ == '__main__':
        print("HEY")
        import sys
        if not QtWidgets.QApplication.instance():
            app = QtWidgets.QApplication(sys.argv)
        else:
            app = QtWidgets.QApplication.instance()
        mainWin = MainWindow()


        mainWin.show()

        sys.exit(app.exec_())