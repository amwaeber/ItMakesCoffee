from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import os
import pandas as pd
from PyQt5 import QtWidgets, QtGui, QtCore

from helper_classes.csv_import import CsvFile
from helper_classes import data_analysis
from utility.config import paths
import utility.folder_functions as folder_functions


class Analysis(QtWidgets.QWidget):
    update_plt = QtCore.pyqtSignal()  # iv figure signal lane
    get_file_paths = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(Analysis, self).__init__(parent)

        self.plot_directory = paths['last_save']
        self.stats_directory = paths['last_save']
        self.reference_directory = None

        self.reference_files = list()
        self.reference_data = list()
        self.reference_averaged = pd.DataFrame()
        self.selection_files = list()
        self.selection_data = list()
        self.selection_averaged = pd.DataFrame()
        self.selection_efficiency = pd.DataFrame()
        self.table_select = 'default'

        hbox_total = QtWidgets.QHBoxLayout()
        vbox_left = QtWidgets.QVBoxLayout()
        self.plot_group_box = QtWidgets.QGroupBox('Graphs')
        vbox_plot = QtWidgets.QVBoxLayout()
        self.plot_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.plot_canvas.figure.tight_layout(pad=0.3)
        self.update_plt.connect(self.plot_canvas.figure.canvas.draw)
        vbox_plot.addWidget(self.plot_canvas)
        self.plot_group_box.setLayout(vbox_plot)
        vbox_left.addWidget(self.plot_group_box, 5)

        self.statistics_group_box = QtWidgets.QGroupBox('Statistics')
        vbox_table = QtWidgets.QVBoxLayout()
        self.statistics_table = QtWidgets.QTableWidget()
        self.statistics_table.setRowCount(4)
        self.statistics_table.setColumnCount(14)
        col_headers = ['Experiment', 'Time', 'Max. Power', r'$\sigma$', 'V_oc', r'$\sigma$', 'I_sc', r'$\sigma$',
                       'Fill Factor', r'$\sigma$', 'Temperature', r'$\sigma$', 'Illumination', r'$\sigma$']
        self.statistics_table.setHorizontalHeaderLabels(col_headers)
        self.update_stats()
        vbox_table.addWidget(self.statistics_table)
        self.statistics_group_box.setLayout(vbox_table)
        vbox_left.addWidget(self.statistics_group_box, 2)
        hbox_total.addLayout(vbox_left, 5)

        vbox_right = QtWidgets.QVBoxLayout()
        self.plot_settings_group_box = QtWidgets.QGroupBox('Plot Settings')
        vbox_plot_set = QtWidgets.QVBoxLayout()
        hbox_plot_set1 = QtWidgets.QHBoxLayout()
        self.xaxis_label = QtWidgets.QLabel('X-Axis', self)
        hbox_plot_set1.addWidget(self.xaxis_label)
        self.xaxis_cb = QtWidgets.QComboBox()
        self.xaxis_cb.setFixedWidth(120)
        self.xaxis_cb.addItem('Categorical')
        self.xaxis_cb.addItem('Time')
        self.xaxis_cb.addItem('Current')
        self.xaxis_cb.addItem('Voltage')
        self.xaxis_cb.addItem('Power')
        self.xaxis_cb.addItem('Fill Factor')
        self.xaxis_cb.addItem('Temperature')
        self.xaxis_cb.addItem('Illumination')
        hbox_plot_set1.addWidget(self.xaxis_cb)
        self.yaxis_label = QtWidgets.QLabel('Y-Axis', self)
        hbox_plot_set1.addWidget(self.yaxis_label)
        self.yaxis_cb = QtWidgets.QComboBox()
        self.yaxis_cb.setFixedWidth(120)
        self.yaxis_cb.addItem('Time')
        self.yaxis_cb.addItem('Current')
        self.yaxis_cb.addItem('Voltage')
        self.yaxis_cb.addItem('Power')
        self.yaxis_cb.addItem('Fill Factor')
        self.yaxis_cb.addItem('Temperature')
        self.yaxis_cb.addItem('Illumination')
        hbox_plot_set1.addWidget(self.yaxis_cb)
        self.plot_mode_label = QtWidgets.QLabel('Mode', self)
        hbox_plot_set1.addWidget(self.plot_mode_label)
        self.plot_mode_cb = QtWidgets.QComboBox()
        self.plot_mode_cb.setFixedWidth(120)
        self.plot_mode_cb.addItem('Average')
        self.plot_mode_cb.addItem('Efficiency')
        hbox_plot_set1.addWidget(self.plot_mode_cb)
        self.plot_update_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'refresh.png')), '')
        self.plot_update_button.clicked.connect(self.update_plot)
        self.plot_update_button.setToolTip('Update plot')
        hbox_plot_set1.addWidget(self.plot_update_button)
        hbox_plot_set1.addStretch(-1)
        vbox_plot_set.addLayout(hbox_plot_set1)

        hbox_plot_set2 = QtWidgets.QHBoxLayout()
        self.plot_save_folder_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'folder.png')), '')
        self.plot_save_folder_button.clicked.connect(lambda: self.folder_dialog('plot'))
        self.plot_save_folder_button.setToolTip('Choose folder')
        hbox_plot_set2.addWidget(self.plot_save_folder_button)
        self.plot_save_folder_edit = QtWidgets.QLineEdit(self.plot_directory, self)
        self.plot_save_folder_edit.setMinimumWidth(180)
        self.plot_save_folder_edit.setDisabled(True)
        hbox_plot_set2.addWidget(self.plot_save_folder_edit)
        self.plot_save_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'save.png')), '')
        self.plot_save_button.clicked.connect(self.save_plot)
        self.plot_save_button.setToolTip('Save plot')
        hbox_plot_set2.addWidget(self.plot_save_button)
        self.clipboard_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'clipboard.png')), '')
        self.clipboard_button.clicked.connect(self.clipboard)
        self.clipboard_button.setToolTip('Save plot to clipboard')
        hbox_plot_set2.addWidget(self.clipboard_button)
        vbox_plot_set.addLayout(hbox_plot_set2)
        self.plot_settings_group_box.setLayout(vbox_plot_set)
        vbox_right.addWidget(self.plot_settings_group_box)

        self.stats_settings_group_box = QtWidgets.QGroupBox('Statistics Settings')
        vbox_stats_set = QtWidgets.QVBoxLayout()
        hbox_stats_set1 = QtWidgets.QHBoxLayout()
        self.stats_mode_label = QtWidgets.QLabel('Mode', self)
        hbox_stats_set1.addWidget(self.stats_mode_label)
        self.stats_mode_cb = QtWidgets.QComboBox()
        self.stats_mode_cb.setFixedWidth(120)
        self.stats_mode_cb.addItem('Average')
        self.stats_mode_cb.addItem('Efficiency')
        self.stats_mode_cb.currentTextChanged.connect(self.stats_mode_changed)
        hbox_stats_set1.addWidget(self.stats_mode_cb)
        self.stats_update_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'refresh.png')), '')
        self.stats_update_button.clicked.connect(self.load_selection)
        self.stats_update_button.setToolTip('Update statistics')
        hbox_stats_set1.addWidget(self.stats_update_button)
        hbox_stats_set1.addStretch(-1)
        vbox_stats_set.addLayout(hbox_stats_set1)

        hbox_stats_set2 = QtWidgets.QHBoxLayout()
        self.stats_save_folder_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'folder.png')), '')
        self.stats_save_folder_button.clicked.connect(lambda: self.folder_dialog('stats'))
        self.stats_save_folder_button.setToolTip('Choose folder')
        hbox_stats_set2.addWidget(self.stats_save_folder_button)
        self.stats_save_folder_edit = QtWidgets.QLineEdit(self.stats_directory, self)
        self.stats_save_folder_edit.setMinimumWidth(180)
        self.stats_save_folder_edit.setDisabled(True)
        hbox_stats_set2.addWidget(self.stats_save_folder_edit)
        self.stats_save_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'save.png')), '')
        self.stats_save_button.clicked.connect(self.save_stats)
        self.stats_save_button.setToolTip('Save as csv')
        hbox_stats_set2.addWidget(self.stats_save_button)
        vbox_stats_set.addLayout(hbox_stats_set2)
        self.stats_settings_group_box.setLayout(vbox_stats_set)
        vbox_right.addWidget(self.stats_settings_group_box)

        self.reference_group_box = QtWidgets.QGroupBox('Reference data')
        vbox_reference = QtWidgets.QVBoxLayout()
        hbox_reference = QtWidgets.QHBoxLayout()
        self.reference_folder_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'folder.png')), '')
        self.reference_folder_button.clicked.connect(lambda: self.folder_dialog('reference'))
        self.reference_folder_button.setToolTip('Choose reference folder')
        hbox_reference.addWidget(self.reference_folder_button)
        hbox_reference.addStretch(-1)
        vbox_reference.addLayout(hbox_reference)
        self.reference_tree = QtWidgets.QTreeWidget()
        self.reference_tree.setRootIsDecorated(False)
        self.reference_tree.setHeaderLabels(["Experiment", "CSV Files", "Created"])
        self.reference_tree.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        vbox_reference.addWidget(self.reference_tree)
        self.reference_group_box.setLayout(vbox_reference)
        vbox_right.addWidget(self.reference_group_box)

        self.analysis_group_box = QtWidgets.QGroupBox('Analysis data')
        vbox_analysis = QtWidgets.QVBoxLayout()
        hbox_analysis = QtWidgets.QHBoxLayout()
        self.analysis_add_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'plus.png')), '')
        self.analysis_add_button.clicked.connect(self.add_analysis_folders)
        self.analysis_add_button.setToolTip('Add analysis folder')
        hbox_analysis.addWidget(self.analysis_add_button)
        self.analysis_remove_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'minus.png')), '')
        self.analysis_remove_button.clicked.connect(self.remove_analysis_folders)
        self.analysis_remove_button.setToolTip('Remove analysis folder')
        hbox_analysis.addWidget(self.analysis_remove_button)
        hbox_analysis.addStretch(-1)
        vbox_analysis.addLayout(hbox_analysis)
        self.analysis_tree = QtWidgets.QTreeWidget()
        self.analysis_tree.setRootIsDecorated(False)
        self.analysis_tree.setHeaderLabels(["Experiment", "CSV Files", "Created"])
        self.analysis_tree.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        vbox_analysis.addWidget(self.analysis_tree)
        self.analysis_group_box.setLayout(vbox_analysis)
        vbox_right.addWidget(self.analysis_group_box)
        hbox_total.addLayout(vbox_right, 3)
        self.setLayout(hbox_total)

        self.update_plot()

    def folder_dialog(self, origin):
        if origin == 'plot':
            self.plot_directory = str(QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Directory',
                                                                                 paths['last_save']))
            self.plot_save_folder_edit.setText(self.plot_directory)
        elif origin == 'stats':
            self.stats_directory = str(QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Directory',
                                                                                  paths['last_save']))
            self.stats_save_folder_edit.setText(self.stats_directory)
        elif origin == 'reference':
            self.reference_directory = str(QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Directory',
                                                                                      paths['last_data']))
            self.update_reference()

    def add_analysis_folders(self):
        pass

    def remove_analysis_folders(self):
        pass

    def update_reference(self):
        if self.reference_directory:
            self.reference_tree.clear()
            basename = os.path.basename(self.reference_directory)
            QtWidgets.QTreeWidgetItem(self.reference_tree,
                                      [basename,
                                       str(folder_functions.get_number_of_csv(self.reference_directory)),
                                       str(folder_functions.get_datetime(self.reference_directory))])

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
        self.update_stats()

    def save_stats(self):
        # save both average and relative tables
        pass

    def save_plot(self):
        # save current plot
        pass

    def clipboard(self):
        pixmap = QtWidgets.QWidget.grab(self.plot_canvas)
        QtWidgets.QApplication.clipboard().setPixmap(pixmap)

    @QtCore.pyqtSlot(list, list)
    def set_paths(self, reference_path, selection_path):
        self.reference_files = reference_path
        self.selection_files = selection_path

    def stats_mode_changed(self):
        self.update_stats()

    def update_data(self):
        self.reference_averaged = data_analysis.average_results(self.reference_data)
        self.selection_averaged = data_analysis.average_results(self.selection_data)
        self.selection_efficiency = data_analysis.efficiency_results(self.selection_averaged, self.reference_averaged)

    def update_plot(self):
        self.plot_canvas.figure.clear()
        axis = self.plot_canvas.figure.add_subplot(111)
        axis.set_xlabel(self.xaxis_cb.currentText())
        axis.set_ylabel(self.yaxis_cb.currentText())
        xval, yval = range(100), [0] * 100
        axis.plot(xval, yval, lw=1.3)
        self.update_plt.emit()

    def update_stats(self):
        if self.table_select == 'default':  # TODO: sort table settings
            for n in range(self.statistics_table.columnCount()):
                for m in range(4):  # add a fix to catch reset to default
                    entry = QtWidgets.QTableWidgetItem('-')
                    self.statistics_table.setItem(m, n, entry)
        elif self.stats_mode_cb.currentText() == 'Average':
            df = pd.concat([self.reference_averaged, self.selection_averaged])
            for m in range(len(df.index)):  # capture shorter subsequent datasets
                if m >= self.statistics_table.rowCount():
                    self.statistics_table.insertRow(m)
                for n in range(len(df.columns)):
                    entry = QtWidgets.QTableWidgetItem('123')
                    self.statistics_table.setItem(m, n, entry)
        elif self.stats_mode_cb.currentText() == 'Efficiency':
            df = self.selection_efficiency
            pass
        self.statistics_table.resizeColumnsToContents()
        self.statistics_table.resizeRowsToContents()
