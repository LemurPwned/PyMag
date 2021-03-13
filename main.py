import sys
from pyqtgraph.Qt import QtCore, QtGui
from pymag.gui.main_window import UIMainWindow

PYMAG_VERSION = "0.0.1"
if __name__ == "__main__":
    app = QtGui.QApplication([])
    MainWindow = QtGui.QMainWindow()
    QtCore.QCoreApplication.setOrganizationName("PyMag")
    QtCore.QCoreApplication.setApplicationName(PYMAG_VERSION)
    plotter = UIMainWindow()

    # if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    # QtGui.QApplication.instance().exec_()
    sys.exit(app.exec_())
