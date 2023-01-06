from PySide2 import QtWidgets, QtCore, QtGui

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mainWin = QtWidgets.QWidget()
    mainWin.show()
    # mainWin.copyAsset()
    sys.exit(app.exec_())
