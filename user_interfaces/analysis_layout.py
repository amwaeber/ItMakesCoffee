import os
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.Qt import Qt


class AnalysisLayout(QtWidgets.QHBoxLayout):

    def __init__(self, parent=None):
        super(AnalysisLayout, self).__init__(parent)

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
        vbox1.addWidget(self.statistics_table)
        self.statistics_group_box.setLayout(vbox1)
        self.addWidget(self.statistics_group_box)

        # self.files = self.parent().tab3.