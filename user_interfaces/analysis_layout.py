import os
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.Qt import Qt

from utility.config import paths


class AnalysisLayout(QtWidgets.QHBoxLayout):

    def __init__(self, parent=None):
        super(AnalysisLayout, self).__init__(parent)

        self.refresh_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'refresh.png')), '')
        self.refresh_button.clicked.connect(self.load_selection)
        self.refresh_button.setToolTip('Load selected files')
        self.toggle_stats_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'statistics.png')), '')
        self.toggle_stats_button.clicked.connect(self.toggle_table)
        self.toggle_stats_button.setToolTip('Show average / relative values')
        self.save_tables_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'save.png')), '')
        self.save_tables_button.clicked.connect(self.save_tables)
        self.save_tables_button.setToolTip('Save as csv')

        self.statistics_group_box = QtWidgets.QGroupBox('File statistics')

        self.statistics_table = QtWidgets.QTableWidget()
        self.statistics_table.setRowCount(4)
        self.statistics_table.setColumnCount(12)
        self.statistics_table.setItem(0, 0, QtWidgets.QTableWidgetItem("Cell (1,1)"))
        self.statistics_table.setItem(0, 1, QtWidgets.QTableWidgetItem("Cell (1,2)"))
        self.statistics_table.setItem(1, 0, QtWidgets.QTableWidgetItem("Cell (2,1)"))
        self.statistics_table.setItem(1, 1, QtWidgets.QTableWidgetItem("Cell (2,2)"))
        self.statistics_table.setItem(2, 0, QtWidgets.QTableWidgetItem("Cell (3,1)"))
        self.statistics_table.setItem(2, 1, QtWidgets.QTableWidgetItem("Cell (3,2)"))
        self.statistics_table.setItem(3, 0, QtWidgets.QTableWidgetItem("Cell (4,1)"))
        self.statistics_table.setItem(3, 1, QtWidgets.QTableWidgetItem("Cell (4,2)"))

        vbox1 = QtWidgets.QVBoxLayout()
        vbox1.addWidget(self.refresh_button)
        vbox1.addWidget(self.toggle_stats_button)
        vbox1.addWidget(self.save_tables_button)
        vbox1.addStretch(1)
        vbox2 = QtWidgets.QVBoxLayout()
        vbox2.addWidget(self.statistics_table)
        self.statistics_group_box.setLayout(vbox2)
        hbox = QtWidgets.QHBoxLayout()
        hbox.addLayout(vbox1)
        hbox.addWidget(self.statistics_group_box)
        self.addLayout(hbox)

    def load_selection(self):
        # Load file data for selection from folder tab
        # self.files = self.parent().tab3.
        pass

    def save_tables(self):
        # save both average and relative tables
        pass

    def toggle_table(self):
        # switch between showing average data by experiment and relative change vs reference
        pass
