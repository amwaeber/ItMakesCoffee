from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot

from user_interfaces.folder_layout import FolderLayout


class TableWidget(QtWidgets.QWidget):

    def __init__(self, parent):
        super(TableWidget, self).__init__(parent)

        self.layout = QtWidgets.QVBoxLayout(self)

        # Initialize tab screen
        self.tabs = QtWidgets.QTabWidget()
        self.tab1 = QtWidgets.QWidget()
        self.tab2 = QtWidgets.QWidget()
        self.tab3 = QtWidgets.QWidget()
        self.tab4 = QtWidgets.QWidget()

        # Add tabs
        self.tabs.addTab(self.tab1, "Experiment")
        self.tabs.addTab(self.tab2, "Analysis")
        self.tabs.addTab(self.tab3, "Folder")
        self.tab3.setLayout(FolderLayout(self))
        self.tabs.addTab(self.tab4, "Calibration")

        # Create first tab
        self.tab1.layout = QtWidgets.QVBoxLayout(self)
        self.pushButton1 = QtWidgets.QPushButton("PyQt5 button")
        self.tab1.layout.addWidget(self.pushButton1)
        self.tab1.setLayout(self.tab1.layout)

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    @pyqtSlot()
    def on_click(self):
        print("\n")
        for currentQTableWidgetItem in self.selectedItems():
            print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())