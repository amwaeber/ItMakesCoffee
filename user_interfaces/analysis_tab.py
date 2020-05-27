import os
import pandas as pd
from PyQt5 import QtWidgets, QtGui, QtCore

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
            QtGui.QIcon(os.path.join(paths['icons'], 'stats_avg.png')), '')
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
        col_headers = ['Experiment', 'Time', 'Max. Power', r'$\sigma$', 'V_oc', r'$\sigma$',
                       'I_sc', r'$\sigma$', 'Fill Factor', r'$\sigma$', 'Temperature', r'$\sigma$']
        self.statistics_table.setHorizontalHeaderLabels(col_headers)
        self.update_tables()

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
            for n in range(self.statistics_table.columnCount()):
                for m in range(4):  # add a fix to catch reset to default
                    entry = QtWidgets.QTableWidgetItem('-')
                    self.statistics_table.setItem(m, n, entry)
        elif self.table_select == 'averaged':
            df = pd.concat([self.reference_averaged, self.selection_averaged])
            for m in range(len(df.index)):  # capture shorter subsequent datasets
                if m >= self.statistics_table.rowCount():
                    self.statistics_table.insertRow(m)
                for n in range(len(df.columns)):
                    entry = QtWidgets.QTableWidgetItem('123')
                    self.statistics_table.setItem(m, n, entry)
        elif self.table_select == 'efficiency':
            df = self.selection_efficiency
            pass
        self.statistics_table.resizeColumnsToContents()
        self.statistics_table.resizeRowsToContents()
