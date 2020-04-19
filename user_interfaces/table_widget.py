from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot

from user_interfaces.analysis_layout import Analysis
from user_interfaces.folder_layout import Folders


class TableWidget(QtWidgets.QWidget):

    def __init__(self, parent):
        super(TableWidget, self).__init__(parent)

        self.layout = QtWidgets.QVBoxLayout(self)

        # Initialize tab screen
        self.tabs = QtWidgets.QTabWidget()

        self.tab_experiment = QtWidgets.QWidget()
        self.tabs.addTab(self.tab_experiment, "Experiment")

        self.tab_analysis = Analysis(self)
        self.tabs.addTab(self.tab_analysis, "Analysis")

        self.tab_folders = Folders(self)
        self.tabs.addTab(self.tab_folders, "Folder")

        self.tab_calibration = QtWidgets.QWidget()
        self.tabs.addTab(self.tab_calibration, "Calibration")

        # Connect signals
        self.tab_analysis.get_file_paths.connect(self.tab_folders.get_ticked_paths)
        self.tab_folders.file_paths.connect(self.tab_analysis.set_paths)

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
