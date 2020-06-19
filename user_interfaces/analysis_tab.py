from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import os
import pandas as pd
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.Qt import Qt

from helper_classes.data_import import Experiment
from helper_classes import data_analysis
from helper_classes.widgets import TreeWidgetItem, ItemSignal
from user_interfaces.multi_dir_dialog import MultiDirDialog
from utility.config import paths
from utility.folder_functions import get_experiment_folders

colors = ['#1e90ff', '#ff0000', '#32cd32', '#ff8c00', '#8a2be2']
line_plot_dict = {'Time': 'Time (s)',
                  'Current': 'Current (A)',
                  'Voltage': 'Voltage (V)',
                  'Power': 'Power (W)',
                  'Temperature': 'Temperature (C)',
                  'Irradiance': 'Irradiance 1 (W/m2)'}
bar_plot_dict = {'Current': 'Short Circuit Current I_sc (A)',
                 'Voltage': 'Open Circuit Voltage V_oc (V)',
                 'Power': 'Maximum Power P_max (W)',
                 'Fill Factor': 'Fill Factor',
                 'Temperature': 'Average Temperature T_avg (C)',
                 'Irradiance': 'Average Irradiance I_1_avg (W/m2)'}
efficiency_plot_dict = {'Current': ['Delta I_sc', r'$\Delta I_{sc}/PV (\%)$'],
                        'Voltage': ['Delta V_oc', r'$\Delta V_{oc}/PV (\%)$'],
                        'Power': ['Delta P_max', r'$\Delta P_{max}/PV (\%)$'],
                        'Fill Factor': ['Delta Fill Factor', r'$\Delta FF/PV (\%)$'],
                        'Temperature': ['Delta T_avg', r'$\Delta T_{avg}/PV (\%)$']}


class Analysis(QtWidgets.QWidget):
    update_plt = QtCore.pyqtSignal()  # figure signal lane

    def __init__(self, parent=None):
        super(Analysis, self).__init__(parent)

        self.plot_directory = paths['last_save']
        self.stats_directory = paths['last_save']
        self.experiment_directories = list()
        self.experiments = {}
        self.reference = ''

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
                       'Fill Factor', r'$\sigma$', 'Temperature', r'$\sigma$', 'Irradiance', r'$\sigma$']
        self.statistics_table.setHorizontalHeaderLabels(col_headers)
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
        self.xaxis_cb.addItem('Temperature')
        self.xaxis_cb.addItem('Irradiance')
        self.xaxis_cb.currentTextChanged.connect(self.update_plot)
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
        self.yaxis_cb.addItem('Irradiance')
        self.yaxis_cb.currentTextChanged.connect(self.update_plot)
        hbox_plot_set1.addWidget(self.yaxis_cb)
        self.plot_mode_label = QtWidgets.QLabel('Mode', self)
        hbox_plot_set1.addWidget(self.plot_mode_label)
        self.plot_mode_cb = QtWidgets.QComboBox()
        self.plot_mode_cb.setFixedWidth(120)
        self.plot_mode_cb.addItem('Single')
        self.plot_mode_cb.addItem('Average')
        self.plot_mode_cb.addItem('Efficiency')
        self.plot_mode_cb.currentTextChanged.connect(self.update_plot)
        hbox_plot_set1.addWidget(self.plot_mode_cb)
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
        self.stats_mode_cb.currentTextChanged.connect(self.update_stats)
        hbox_stats_set1.addWidget(self.stats_mode_cb)
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

        self.analysis_group_box = QtWidgets.QGroupBox('Experiment data')
        vbox_analysis = QtWidgets.QVBoxLayout()
        hbox_analysis = QtWidgets.QHBoxLayout()
        self.analysis_add_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'plus.png')), '')
        self.analysis_add_button.clicked.connect(self.add_experiments)
        self.analysis_add_button.setToolTip('Add experiment folders')
        hbox_analysis.addWidget(self.analysis_add_button)
        self.analysis_remove_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'minus.png')), '')
        self.analysis_remove_button.clicked.connect(self.remove_experiments)
        self.analysis_remove_button.setToolTip('Remove experiment folders')
        hbox_analysis.addWidget(self.analysis_remove_button)
        self.analysis_select_all_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'select_all.png')), '')
        self.analysis_select_all_button.clicked.connect(lambda: self.change_selection('all'))
        self.analysis_select_all_button.setToolTip('Select all experiments')
        hbox_analysis.addWidget(self.analysis_select_all_button)
        self.analysis_select_none_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'select_none.png')), '')
        self.analysis_select_none_button.clicked.connect(lambda: self.change_selection('none'))
        self.analysis_select_none_button.setToolTip('Unselect all experiments')
        hbox_analysis.addWidget(self.analysis_select_none_button)
        hbox_analysis.addStretch(-1)
        vbox_analysis.addLayout(hbox_analysis)
        self.experiment_tree = QtWidgets.QTreeWidget()
        self.experiment_tree.setRootIsDecorated(False)
        self.experiment_tree.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.experiment_tree.setHeaderLabels(["Ref", "Plot", "Stat", "Experiment", "Traces", "Created"])
        self.experiment_tree.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        vbox_analysis.addWidget(self.experiment_tree)
        self.analysis_group_box.setLayout(vbox_analysis)
        vbox_right.addWidget(self.analysis_group_box)
        hbox_total.addLayout(vbox_right, 3)
        self.setLayout(hbox_total)

        self.update_plot()
        self.update_stats()

    def folder_dialog(self, origin):
        if origin == 'plot':
            self.plot_directory = str(QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Directory',
                                                                                 paths['last_save']))
            self.plot_save_folder_edit.setText(self.plot_directory)
        elif origin == 'stats':
            self.stats_directory = str(QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Directory',
                                                                                  paths['last_save']))
            self.stats_save_folder_edit.setText(self.stats_directory)

    def add_experiments(self):
        multi_dir_dialog = MultiDirDialog()
        multi_dir_dialog.setDirectory(paths['last_data'])
        multi_dir_dialog.show()
        multi_dir_dialog.exec_()
        self.experiment_directories.extend(get_experiment_folders(multi_dir_dialog.selectedFiles()))
        self.experiment_directories = list(set(self.experiment_directories))
        self.update_experiment_data()
        self.update_experiment_tree()

    def remove_experiments(self):
        for item in self.experiment_tree.selectedItems():
            self.experiment_directories = [entry for entry in self.experiment_directories
                                           if not (item.toolTip(3) == entry)]
        self.update_experiment_data()
        self.update_experiment_tree()
        self.update_reference()
        self.update_plot()
        self.update_stats()

    def change_selection(self, select):
        iterator = QtWidgets.QTreeWidgetItemIterator(self.experiment_tree)
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        while iterator.value():
            tree_item = iterator.value()
            if modifiers == QtCore.Qt.ControlModifier:  # Affecting plots
                if select == 'all':
                    tree_item.setCheckState(1, Qt.Checked)
                    self.experiments[str(tree_item.toolTip(3))].plot = True
                elif select == 'none':
                    tree_item.setCheckState(1, Qt.Unchecked)
                    self.experiments[str(tree_item.toolTip(3))].plot = False
            elif modifiers == (QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier):  # affecting statistics
                if select == 'all':
                    tree_item.setCheckState(2, Qt.Checked)
                    self.experiments[str(tree_item.toolTip(3))].stats = True
                elif select == 'none':
                    tree_item.setCheckState(2, Qt.Unchecked)
                    self.experiments[str(tree_item.toolTip(3))].stats = False
            else:
                if select == 'all':
                    tree_item.setSelected(True)
                elif select == 'none':
                    tree_item.setSelected(False)
            iterator += 1

    def update_experiment_tree(self):
        self.experiment_tree.clear()
        for directory in self.experiment_directories:
            tree_item = TreeWidgetItem(ItemSignal(), self.experiment_tree,
                                       [None, None, None, self.experiments[directory].name,
                                        str(self.experiments[directory].n_traces),
                                        str(self.experiments[directory].time)])
            tree_item.setToolTip(3, directory)
            tree_item.setCheckState(0, self.bool_to_qtchecked(self.experiments[directory].reference))
            tree_item.setCheckState(1, self.bool_to_qtchecked(self.experiments[directory].plot))
            tree_item.setCheckState(2, self.bool_to_qtchecked(self.experiments[directory].stats))
            tree_item.signal.itemChecked.connect(self.checkbox_changed)
        self.experiment_tree.sortByColumn(3, Qt.AscendingOrder)

    def update_experiment_data(self):
        directories = self.experiment_directories
        for directory in directories:
            if directory not in self.experiments.keys():
                self.experiments[directory] = Experiment(directory)
        for directory in list(self.experiments.keys()):
            if directory not in directories:
                self.experiments.pop(directory, None)

    @QtCore.pyqtSlot(object, int)
    def checkbox_changed(self, item, column):
        experiment = str(item.toolTip(3))
        if column == 0:  # Reference
            if int(item.checkState(column)) == 0:
                self.experiments[experiment].reference = False
                if self.reference == experiment:
                    self.reference = ''
            else:
                self.experiments[experiment].reference = True
                self.reference = experiment
                # set other reference cbs to False so only one reference at any time
                iterator = QtWidgets.QTreeWidgetItemIterator(self.experiment_tree)
                while iterator.value():
                    tree_item = iterator.value()
                    if tree_item != item and int(tree_item.checkState(column)) != 0:
                        tree_item.setCheckState(0, Qt.Unchecked)
                        self.experiments[str(tree_item.toolTip(3))].reference = False
                    iterator += 1
            self.update_reference()
            self.update_plot()  # to update effects reference switch has on plot

        elif column == 1:  # Plot
            if int(item.checkState(column)) == 0:
                self.experiments[experiment].plot = False
            else:
                self.experiments[experiment].plot = True
                # set other plot cbs to False if in single-plot mode
                if self.plot_mode_cb.currentText() == 'Single':
                    iterator = QtWidgets.QTreeWidgetItemIterator(self.experiment_tree)
                    while iterator.value():
                        tree_item = iterator.value()
                        if tree_item != item and int(tree_item.checkState(column)) != 0:
                            tree_item.setCheckState(1, Qt.Unchecked)
                            self.experiments[str(tree_item.toolTip(3))].reference = False
                        iterator += 1
            self.update_plot()

        elif column == 2:  # Statistics
            if int(item.checkState(column)) == 0:
                self.experiments[experiment].stats = False
            else:
                self.experiments[experiment].stats = True
            self.update_stats()

    def update_reference(self):
        for experiment in self.experiments.values():
            experiment.update_efficiencies(self.experiments.get(self.reference, None))

    def update_plot(self):
        plot_list = [key for key, experiment in self.experiments.items() if experiment.plot is True]
        self.plot_canvas.figure.clear()
        axis = self.plot_canvas.figure.add_subplot(111)
        if self.plot_mode_cb.currentText() == 'Single' and len(plot_list) == 1:
            experiment = self.experiments[plot_list[0]]
            axis.set_title(experiment.name)
            if self.xaxis_cb.currentText() == 'Categorical':
                try:
                    y_data = bar_plot_dict[self.yaxis_cb.currentText()]
                except KeyError:
                    return
                categories, values, errors, bar_color = list(), list(), list(), list()
                for i, trace in enumerate(experiment.traces.values()):
                    categories.append('Trace %d' % i)
                    values.append(trace.values[y_data][0])
                    errors.append(trace.values[y_data][1])
                    bar_color.append(colors[0])
                categories.append('Average')
                values.append(experiment.values[y_data][0])
                errors.append(experiment.values[y_data][1])
                bar_color.append(colors[1])
                low, high = min(values), max(values)
                axis.set_ylim([min([(low-0.5*(high-low)), low-0.0005]), max([(high+0.5*(high-low)), high+0.0005])])
                axis.bar(categories, values, yerr=errors, color=bar_color,
                         error_kw=dict(ecolor='black', elinewidth=1, capsize=3))
                axis.set_xlabel("")
                axis.set_ylabel(y_data)
            else:
                try:
                    x_data = line_plot_dict[self.xaxis_cb.currentText()]
                    y_data = line_plot_dict[self.yaxis_cb.currentText()]
                except KeyError:
                    return
                for i, trace in enumerate(experiment.traces.values()):
                    trace.data.plot(kind='line', x=x_data, y=y_data, color=colors[i % len(colors)], lw=1, ax=axis,
                                    label='Trace %d' % i)
                experiment.average_data.plot(kind='line', x=x_data, y=y_data, color='#000000', lw=2, ax=axis,
                                             label='Average')
                axis.set_xlabel(x_data)
                axis.set_ylabel(y_data)
        elif self.plot_mode_cb.currentText() == 'Average':
            axis.set_title('Averages')
            if self.xaxis_cb.currentText() == 'Categorical':
                try:
                    y_data = bar_plot_dict[self.yaxis_cb.currentText()]
                except KeyError:
                    return
                categories, values, errors, bar_color = list(), list(), list(), list()
                for i, experiment in enumerate(plot_list):
                    if self.experiments[experiment].reference:
                        categories.insert(0, self.experiments[experiment].name)
                        values.insert(0, self.experiments[experiment].values[y_data][0])
                        errors.insert(0, self.experiments[experiment].values[y_data][1])
                        bar_color.insert(0, colors[1])
                    else:
                        categories.append(self.experiments[experiment].name)
                        values.append(self.experiments[experiment].values[y_data][0])
                        errors.append(self.experiments[experiment].values[y_data][1])
                        bar_color.append(colors[0])
                for k, cat in enumerate(categories):  # add line breaks in experiment labels
                    categories[k] = ''.join([elem + '\n' if i % 2 == 0 else elem + ' '
                                             for i, elem in enumerate(cat.split(' '))][0:-1]) + cat.split(' ')[-1]
                try:
                    low, high = min(values), max(values)
                except ValueError:  # if no experiment selected
                    low, high = 0, 0.0005
                axis.set_ylim([min([(low-0.5*(high-low)), low-0.0005]), max([(high+0.5*(high-low)), high+0.0005])])
                axis.bar(categories, values, yerr=errors, color=bar_color,
                         error_kw=dict(ecolor='black', elinewidth=1, capsize=3))
                axis.set_xlabel("")
                axis.set_ylabel(y_data)
            else:
                try:
                    x_data = line_plot_dict[self.xaxis_cb.currentText()]
                    y_data = line_plot_dict[self.yaxis_cb.currentText()]
                except KeyError:
                    return
                for i, experiment in enumerate(plot_list):
                    self.experiments[experiment].average_data.plot(kind='line', x=x_data, y=y_data,
                                                                   color=colors[i % len(colors)], lw=1, ax=axis,
                                                                   label=self.experiments[experiment].name)
                axis.set_xlabel(x_data)
                axis.set_ylabel(y_data)
        elif self.plot_mode_cb.currentText() == 'Efficiency':
            axis.set_title('Relative efficiency vs reference')
            if self.xaxis_cb.currentText() == 'Categorical' and self.reference != '' and len(plot_list) >= 2:
                try:
                    y_data = efficiency_plot_dict[self.yaxis_cb.currentText()]
                except KeyError:
                    return
                categories, values, errors, bar_color = list(), list(), list(), list()
                for i, experiment in enumerate(plot_list):
                    if self.experiments[experiment].reference is False:
                        categories.append(self.experiments[experiment].name)
                        values.append(self.experiments[experiment].efficiencies[y_data[0]][0])
                        errors.append(self.experiments[experiment].efficiencies[y_data[0]][1])
                        bar_color.append(colors[0])
                for k, cat in enumerate(categories):  # add line breaks in experiment labels
                    categories[k] = ''.join([elem + '\n' if i % 2 == 0 else elem + ' '
                                             for i, elem in enumerate(cat.split(' '))][0:-1]) + cat.split(' ')[-1]
                try:
                    low, high = min(values), max(values)
                except ValueError:  # if no experiment selected
                    low, high = 0, 0.0005
                axis.set_ylim([min([(low-0.5*(high-low)), low-0.0005]), max([(high+0.5*(high-low)), high+0.0005])])
                axis.bar(categories, values, yerr=errors, color=bar_color,
                         error_kw=dict(ecolor='black', elinewidth=1, capsize=3))
                axis.set_xlabel("")
                axis.set_ylabel(y_data[1])
            else:
                pass
        else:
            self.plot_canvas.figure.clear()
            axis = self.plot_canvas.figure.add_subplot(111)
            axis.set_xlabel(self.xaxis_cb.currentText())
            axis.set_ylabel(self.yaxis_cb.currentText())
            axis.plot([], [], color=colors[0], lw=1)
        self.update_plt.emit()

    def clipboard(self):
        pixmap = QtWidgets.QWidget.grab(self.plot_canvas)
        QtWidgets.QApplication.clipboard().setPixmap(pixmap)

    def save_plot(self):
        # save current plot
        pass

    def update_stats(self):
        pass
        # if self.table_select == 'default':  # TODO: sort table settings
        #     for n in range(self.statistics_table.columnCount()):
        #         for m in range(4):  # add a fix to catch reset to default
        #             entry = QtWidgets.QTableWidgetItem('-')
        #             self.statistics_table.setItem(m, n, entry)
        # elif self.stats_mode_cb.currentText() == 'Average':
        #     df = pd.concat([self.reference_averaged, self.selection_averaged])
        #     for m in range(len(df.index)):  # capture shorter subsequent datasets
        #         if m >= self.statistics_table.rowCount():
        #             self.statistics_table.insertRow(m)
        #         for n in range(len(df.columns)):
        #             entry = QtWidgets.QTableWidgetItem('123')
        #             self.statistics_table.setItem(m, n, entry)
        # elif self.stats_mode_cb.currentText() == 'Efficiency':
        #     df = self.selection_efficiency
        #     pass
        # self.statistics_table.resizeColumnsToContents()
        # self.statistics_table.resizeRowsToContents()

    def save_stats(self):
        # save both average and relative tables
        pass

    @staticmethod
    def bool_to_qtchecked(boolean):
        if boolean:
            return Qt.Checked
        else:
            return Qt.Unchecked
