import os
from PyQt5 import QtWidgets, QtGui

from user_interfaces.table_widget import TableWidget
from utility.config import global_confs
from utility.config import paths


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.init_ui()

    def init_ui(self):

        self.setWindowIcon(QtGui.QIcon(os.path.join(paths['icons'], 'coffee.png')))
        self.setWindowTitle("%s %s" % (global_confs['progname'], global_confs['progversion']))

        self.table_widget = TableWidget(self)  # create multiple document interface widget
        self.setCentralWidget(self.table_widget)
        self.showMaximized()

    def closeEvent(self, *args, **kwargs):
        super(QtWidgets.QMainWindow, self).closeEvent(*args, **kwargs)
        self.table_widget.tab_experiment.stop_sensor()  # disconnect sensor before shutdown
