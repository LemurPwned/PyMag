import sys
from pyqtgraph.Qt import QtGui
from pymag.gui.main_window import UIMainWindow
PYMAG_VERSION = "0.0.1"
if __name__ == "__main__":
    # print(pmg.__version__)
    app = QtGui.QApplication([])
    app.setOrganizationName("PyMag")
    app.setApplicationName(PYMAG_VERSION)
    main_window = UIMainWindow()

    # if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    # QtGui.QApplication.instance().exec_()
    sys.exit(app.exec_())
