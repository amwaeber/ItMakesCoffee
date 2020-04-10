import os
from PyQt5 import QtWidgets, QtGui

from utility.config import global_confs
from utility.config import paths


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.init_ui()

    def init_ui(self):

        self.resize(800, 600)
        self.showMaximized()
        self.setWindowIcon(QtGui.QIcon(os.path.join(paths['icons'], 'coffee.png')))
        self.setWindowTitle("%s %s" % (global_confs['progname'], global_confs['progversion']))

        self.mdi = QtWidgets.QMdiArea()  # create multiple document interface widget
        self.setCentralWidget(self.mdi)
