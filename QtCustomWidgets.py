from PySide2 import QtWidgets, QtCore, QtGui


class Popup(QtWidgets.QDialog):
    def __init__(self, parent=None, title='Popup'):
        super(Popup, self).__init__(parent)
        self.setWindowTitle(title)
        flags = self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint
        flags = flags | QtCore.Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)


def confirmPopup(parent=None, title='Popup', label='Is this a placeholder?'):
    """     
    if confirmPopup(self, title='Question', label='Would you bite into Schrodingers burrito?'):
        print('Accepted')
    else:
        print('Rejected')
    """
    dlg = QtWidgets.QMessageBox(parent)
    dlg.setWindowTitle(title)
    dlg.setText(label)
    dlg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
    dlg.setIcon(QtWidgets.QMessageBox.Question)
    button = dlg.exec_()

    if button == QtWidgets.QMessageBox.Yes:
        return True
    else:
        return False

    

if __name__ == '__main__':
    import sys
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()

    
    mainWin = Popup()
    mainWin.show()

    sys.exit(app.exec_())