from PySide2 import QtWidgets, QtCore, QtGui

class MainWindow():
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

    def create_ui(self):
        # layout
        # file browser

        #preset combo?? Like "Transfer from FTP" or ""
        #Explaining label ? Like FTP location should be "drive/project/User/TO_CB/Episode/sequence/Shot"
        #this should be connected to the shotbrowser??
        #file browser + label + line edit for source



        #file browser + label + line for destination


        #bttn for transfer
        pass



if __name__ == '__main__':
    import sys

    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    mainWin = MainWindow()
    mainWin.show()

    app.exec_()