import os
import pandas as pd
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.Qt import Qt

from helper_classes.csv_import import CsvFile
from helper_classes import data_analysis
from utility.config import paths


class Analysis(QtWidgets.QWidget):
    get_file_paths = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(Analysis, self).__init__(parent)

        self.reference_files = list()
        self.reference_data = list()
        self.reference_averaged = pd.DataFrame()
        self.selection_files = list()
        self.selection_data = list()
        self.selection_averaged = pd.DataFrame()
        self.selection_efficiency = pd.DataFrame()
        self.table_select = 'default'

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
        self.setLayout(hbox)

    def load_selection(self):
        # Load file data for selection from folder tab
        self.get_file_paths.emit()
        for file in self.reference_files:
            csv = CsvFile()
            csv.load_file(file)
            self.reference_data.append(csv)
        for file in self.selection_files:
            csv = CsvFile()
            csv.load_file(file)
            self.selection_data.append(csv)
        self.update_data()
        self.table_select = 'averaged'
        self.update_tables()

    def save_tables(self):
        # save both average and relative tables
        pass

    @QtCore.pyqtSlot(list, list)
    def set_paths(self, reference_path, selection_path):
        self.reference_files = reference_path
        self.selection_files = selection_path

    def toggle_table(self):
        if self.table_select == 'averaged':
            self.table_select = 'efficiency'
            self.update_tables()
        elif self.table_select == 'efficiency':
            self.table_select = 'averaged'
            self.update_tables()

    def update_data(self):
        self.reference_averaged = data_analysis.average_results(self.reference_data)
        self.selection_averaged = data_analysis.average_results(self.selection_data)
        self.selection_efficiency = data_analysis.efficiency_results(self.selection_averaged, self.reference_averaged)

    def update_tables(self):
        if self.table_select == 'default':
            # add tables here
            pass
        elif self.table_select == 'averaged':
            pass
        elif self.table_select == 'efficiency':
            pass
