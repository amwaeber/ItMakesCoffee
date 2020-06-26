from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import os
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.Qt import Qt

import utility.colors as colors
import utility.plots as plots
from utility.data_import import Experiment
from utility.widgets import TreeWidgetItem, ItemSignal
from user_interfaces.multi_dir_dialog import MultiDirDialog
from utility.config import paths
from utility.folders import get_experiment_folders


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

        self.experiment_directories = list()
        self.experiments = {}
        self.reference = ''

        self.plot_x = 'Experiment'
        self.plot_y = [['Power', 'y1']]
        self.plot_mode = 'Single'
        self.plot_show = {'Average': True,
                          'Legend': True,
                          'Rescale': True,
                          'Scatter': False}
        self.plot_directory = paths['last_save']

        self.table_select = 'default'
        self.stats_directory = paths['last_save']

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
        grid_plot_items = QtWidgets.QGridLayout()
        grid_plot_items.setHorizontalSpacing(20)
        grid_plot_items.setColumnMinimumWidth(4, 60)
        grid_plot_items.setColumnMinimumWidth(7, 60)
        self.plot_mode_xaxis_group = QtWidgets.QButtonGroup()
        self.plot_mode_yaxis1_group = QtWidgets.QButtonGroup()
        self.plot_mode_yaxis1_group.setExclusive(False)
        self.plot_mode_yaxis2_group = QtWidgets.QButtonGroup()
        self.plot_mode_yaxis2_group.setExclusive(False)
        self.xaxis_label = QtWidgets.QLabel("X", self)
        grid_plot_items.addWidget(self.xaxis_label, 0, 1)
        self.yaxis1_label = QtWidgets.QLabel("Y1", self)
        grid_plot_items.addWidget(self.yaxis1_label, 0, 2)
        self.yaxis2_label = QtWidgets.QLabel("Y2", self)
        grid_plot_items.addWidget(self.yaxis2_label, 0, 3)
        self.item_experiment_label = QtWidgets.QLabel("Experiment", self)
        grid_plot_items.addWidget(self.item_experiment_label, 1, 0)
        self.item_experiment_x = QtWidgets.QCheckBox('',)
        self.item_experiment_x.setChecked(True)
        self.item_experiment_x.toggled.connect(lambda: self.change_plot_items('x', 'Experiment',
                                                                              self.item_experiment_x.isChecked()))
        self.plot_mode_xaxis_group.addButton(self.item_experiment_x)
        grid_plot_items.addWidget(self.item_experiment_x, 1, 1)
        self.item_experiment_y1 = QtWidgets.QCheckBox('',)
        self.item_experiment_y1.setEnabled(False)
        self.plot_mode_yaxis1_group.addButton(self.item_experiment_y1)
        grid_plot_items.addWidget(self.item_experiment_y1, 1, 2)
        self.item_experiment_y2 = QtWidgets.QCheckBox('',)
        self.item_experiment_y2.setEnabled(False)
        self.plot_mode_yaxis2_group.addButton(self.item_experiment_y2)
        grid_plot_items.addWidget(self.item_experiment_y2, 1, 3)
        self.item_time_label = QtWidgets.QLabel("Time", self)
        grid_plot_items.addWidget(self.item_time_label, 2, 0)
        self.item_time_x = QtWidgets.QCheckBox('',)
        self.item_time_x.toggled.connect(lambda: self.change_plot_items('x', 'Time', self.item_time_x.isChecked()))
        self.plot_mode_xaxis_group.addButton(self.item_time_x)
        grid_plot_items.addWidget(self.item_time_x, 2, 1)
        self.item_time_y1 = QtWidgets.QCheckBox('',)
        self.item_time_y1.toggled.connect(lambda: self.change_plot_items('y1', 'Time', self.item_time_y1.isChecked()))
        self.plot_mode_yaxis1_group.addButton(self.item_time_y1)
        grid_plot_items.addWidget(self.item_time_y1, 2, 2)
        self.item_time_y2 = QtWidgets.QCheckBox('',)
        self.item_time_y2.toggled.connect(lambda: self.change_plot_items('y2', 'Time', self.item_time_y2.isChecked()))
        self.plot_mode_yaxis2_group.addButton(self.item_time_y2)
        grid_plot_items.addWidget(self.item_time_y2, 2, 3)
        self.item_current_label = QtWidgets.QLabel("Current/Isc", self)
        grid_plot_items.addWidget(self.item_current_label, 3, 0)
        self.item_current_x = QtWidgets.QCheckBox('',)
        self.item_current_x.toggled.connect(lambda: self.change_plot_items('x', 'Current',
                                                                           self.item_current_x.isChecked()))
        self.plot_mode_xaxis_group.addButton(self.item_current_x)
        grid_plot_items.addWidget(self.item_current_x, 3, 1)
        self.item_current_y1 = QtWidgets.QCheckBox('',)
        self.item_current_y1.toggled.connect(lambda: self.change_plot_items('y1', 'Current',
                                                                            self.item_current_y1.isChecked()))
        self.plot_mode_yaxis1_group.addButton(self.item_current_y1)
        grid_plot_items.addWidget(self.item_current_y1, 3, 2)
        self.item_current_y2 = QtWidgets.QCheckBox('',)
        self.item_current_y2.toggled.connect(lambda: self.change_plot_items('y2', 'Current',
                                                                            self.item_current_y2.isChecked()))
        self.plot_mode_yaxis2_group.addButton(self.item_current_y2)
        grid_plot_items.addWidget(self.item_current_y2, 3, 3)
        self.item_voltage_label = QtWidgets.QLabel("Voltage/Voc", self)
        grid_plot_items.addWidget(self.item_voltage_label, 4, 0)
        self.item_voltage_x = QtWidgets.QCheckBox('',)
        self.item_voltage_x.toggled.connect(lambda: self.change_plot_items('x', 'Voltage',
                                                                           self.item_voltage_x.isChecked()))
        self.plot_mode_xaxis_group.addButton(self.item_voltage_x)
        grid_plot_items.addWidget(self.item_voltage_x, 4, 1)
        self.item_voltage_y1 = QtWidgets.QCheckBox('',)
        self.item_voltage_y1.toggled.connect(lambda: self.change_plot_items('y1', 'Voltage',
                                                                            self.item_voltage_y1.isChecked()))
        self.plot_mode_yaxis1_group.addButton(self.item_voltage_y1)
        grid_plot_items.addWidget(self.item_voltage_y1, 4, 2)
        self.item_voltage_y2 = QtWidgets.QCheckBox('',)
        self.item_voltage_y2.toggled.connect(lambda: self.change_plot_items('y2', 'Voltage',
                                                                            self.item_voltage_y2.isChecked()))
        self.plot_mode_yaxis2_group.addButton(self.item_voltage_y2)
        grid_plot_items.addWidget(self.item_voltage_y2, 4, 3)
        self.item_power_label = QtWidgets.QLabel("Power/Pmax", self)
        grid_plot_items.addWidget(self.item_power_label, 5, 0)
        self.item_power_x = QtWidgets.QCheckBox('',)
        self.item_power_x.toggled.connect(lambda: self.change_plot_items('x', 'Power',
                                                                         self.item_power_x.isChecked()))
        self.plot_mode_xaxis_group.addButton(self.item_power_x)
        grid_plot_items.addWidget(self.item_power_x, 5, 1)
        self.item_power_y1 = QtWidgets.QCheckBox('',)
        self.item_power_y1.setChecked(True)
        self.item_power_y1.toggled.connect(lambda: self.change_plot_items('y1', 'Power',
                                                                          self.item_power_y1.isChecked()))
        self.plot_mode_yaxis1_group.addButton(self.item_power_y1)
        grid_plot_items.addWidget(self.item_power_y1, 5, 2)
        self.item_power_y2 = QtWidgets.QCheckBox('',)
        self.item_power_y2.toggled.connect(lambda: self.change_plot_items('y2', 'Power',
                                                                          self.item_power_y2.isChecked()))
        self.plot_mode_yaxis2_group.addButton(self.item_power_y2)
        grid_plot_items.addWidget(self.item_power_y2, 5, 3)
        self.item_fill_label = QtWidgets.QLabel("Fill Factor", self)
        grid_plot_items.addWidget(self.item_fill_label, 6, 0)
        self.item_fill_x = QtWidgets.QCheckBox('',)
        self.item_fill_x.toggled.connect(lambda: self.change_plot_items('x', 'Fill Factor',
                                                                        self.item_fill_x.isChecked()))
        self.plot_mode_xaxis_group.addButton(self.item_fill_x)
        grid_plot_items.addWidget(self.item_fill_x, 6, 1)
        self.item_fill_y1 = QtWidgets.QCheckBox('',)
        self.item_fill_y1.toggled.connect(lambda: self.change_plot_items('y1', 'Fill Factor',
                                                                         self.item_fill_y1.isChecked()))
        self.plot_mode_yaxis1_group.addButton(self.item_fill_y1)
        grid_plot_items.addWidget(self.item_fill_y1, 6, 2)
        self.item_fill_y2 = QtWidgets.QCheckBox('',)
        self.item_fill_y2.toggled.connect(lambda: self.change_plot_items('y2', 'Fill Factor',
                                                                         self.item_fill_y2.isChecked()))
        self.plot_mode_yaxis2_group.addButton(self.item_fill_y2)
        grid_plot_items.addWidget(self.item_fill_y2, 6, 3)
        self.item_temperature_label = QtWidgets.QLabel("Temperature/Tavg", self)
        grid_plot_items.addWidget(self.item_temperature_label, 7, 0)
        self.item_temperature_x = QtWidgets.QCheckBox('',)
        self.item_temperature_x.toggled.connect(lambda: self.change_plot_items('x', 'Temperature',
                                                                               self.item_temperature_x.isChecked()))
        self.plot_mode_xaxis_group.addButton(self.item_temperature_x)
        grid_plot_items.addWidget(self.item_temperature_x, 7, 1)
        self.item_temperature_y1 = QtWidgets.QCheckBox('',)
        self.item_temperature_y1.toggled.connect(lambda: self.change_plot_items('y1', 'Temperature',
                                                                                self.item_temperature_y1.isChecked()))
        self.plot_mode_yaxis1_group.addButton(self.item_temperature_y1)
        grid_plot_items.addWidget(self.item_temperature_y1, 7, 2)
        self.item_temperature_y2 = QtWidgets.QCheckBox('',)
        self.item_temperature_y2.toggled.connect(lambda: self.change_plot_items('y2', 'Temperature',
                                                                                self.item_temperature_y2.isChecked()))
        self.plot_mode_yaxis2_group.addButton(self.item_temperature_y2)
        grid_plot_items.addWidget(self.item_temperature_y2, 7, 3)
        self.item_irradiance_label = QtWidgets.QLabel("Irradiance/Iavg", self)
        grid_plot_items.addWidget(self.item_irradiance_label, 8, 0)
        self.item_irradiance_x = QtWidgets.QCheckBox('',)
        self.item_irradiance_x.toggled.connect(lambda: self.change_plot_items('x', 'Irradiance',
                                                                              self.item_irradiance_x.isChecked()))
        self.plot_mode_xaxis_group.addButton(self.item_irradiance_x)
        grid_plot_items.addWidget(self.item_irradiance_x, 8, 1)
        self.item_irradiance_y1 = QtWidgets.QCheckBox('',)
        self.item_irradiance_y1.toggled.connect(lambda: self.change_plot_items('y1', 'Irradiance',
                                                                               self.item_irradiance_y1.isChecked()))
        self.plot_mode_yaxis1_group.addButton(self.item_irradiance_y1)
        grid_plot_items.addWidget(self.item_irradiance_y1, 8, 2)
        self.item_irradiance_y2 = QtWidgets.QCheckBox('',)
        self.item_irradiance_y2.toggled.connect(lambda: self.change_plot_items('y2', 'Irradiance',
                                                                               self.item_irradiance_y2.isChecked()))
        self.plot_mode_yaxis2_group.addButton(self.item_irradiance_y2)
        grid_plot_items.addWidget(self.item_irradiance_y2, 8, 3)

        self.plot_show_label = QtWidgets.QLabel('Show', self)
        grid_plot_items.addWidget(self.plot_show_label, 0, 5)
        self.show_avg_label = QtWidgets.QLabel("Average Lines", self)
        grid_plot_items.addWidget(self.show_avg_label, 1, 5)
        self.show_avg_cb = QtWidgets.QCheckBox('', )
        self.show_avg_cb.setChecked(True)
        self.show_avg_cb.toggled.connect(lambda: self.change_plot_settings('Average', self.show_avg_cb.isChecked()))
        grid_plot_items.addWidget(self.show_avg_cb, 1, 6)
        self.show_legend_label = QtWidgets.QLabel("Legend", self)
        grid_plot_items.addWidget(self.show_legend_label, 2, 5)
        self.show_legend_cb = QtWidgets.QCheckBox('', )
        self.show_legend_cb.setChecked(True)
        self.show_legend_cb.toggled.connect(lambda: self.change_plot_settings('Legend',
                                                                              self.show_legend_cb.isChecked()))
        grid_plot_items.addWidget(self.show_legend_cb, 2, 6)
        self.show_rescale_label = QtWidgets.QLabel("Rescale", self)
        grid_plot_items.addWidget(self.show_rescale_label, 3, 5)
        self.show_rescale_cb = QtWidgets.QCheckBox('', )
        self.show_rescale_cb.setChecked(True)
        self.show_rescale_cb.toggled.connect(lambda: self.change_plot_settings('Rescale',
                                                                               self.show_rescale_cb.isChecked()))
        grid_plot_items.addWidget(self.show_rescale_cb, 3, 6)
        self.show_scatter_label = QtWidgets.QLabel("Scatter", self)
        grid_plot_items.addWidget(self.show_scatter_label, 4, 5)
        self.show_scatter_cb = QtWidgets.QCheckBox('', )
        self.show_scatter_cb.toggled.connect(lambda: self.change_plot_settings('Scatter',
                                                                               self.show_scatter_cb.isChecked()))
        grid_plot_items.addWidget(self.show_scatter_cb, 4, 6)

        self.plot_mode_label = QtWidgets.QLabel('Mode', self)
        grid_plot_items.addWidget(self.plot_mode_label, 0, 8)
        self.plot_mode_rbtn_group = QtWidgets.QButtonGroup()
        self.single_mode_label = QtWidgets.QLabel("Single", self)
        grid_plot_items.addWidget(self.single_mode_label, 1, 8)
        self.single_mode_rbtn = QtWidgets.QRadioButton('')
        self.single_mode_rbtn.setChecked(True)
        self.single_mode_rbtn.toggled.connect(lambda: self.change_plot_mode('Single',
                                                                            self.single_mode_rbtn.isChecked()))
        self.plot_mode_rbtn_group.addButton(self.single_mode_rbtn)
        grid_plot_items.addWidget(self.single_mode_rbtn, 1, 9)
        self.avg_mode_label = QtWidgets.QLabel("Average", self)
        grid_plot_items.addWidget(self.avg_mode_label, 2, 8)
        self.avg_mode_rbtn = QtWidgets.QRadioButton('')
        self.avg_mode_rbtn.toggled.connect(lambda: self.change_plot_mode('Average',
                                                                         self.avg_mode_rbtn.isChecked()))
        self.plot_mode_rbtn_group.addButton(self.avg_mode_rbtn)
        grid_plot_items.addWidget(self.avg_mode_rbtn, 2, 9)
        self.efficiency_mode_label = QtWidgets.QLabel("Efficiency", self)
        grid_plot_items.addWidget(self.efficiency_mode_label, 3, 8)
        self.efficiency_mode_rbtn = QtWidgets.QRadioButton('')
        self.efficiency_mode_rbtn.toggled.connect(lambda: self.change_plot_mode('Efficiency',
                                                                                self.efficiency_mode_rbtn.isChecked()))
        self.plot_mode_rbtn_group.addButton(self.efficiency_mode_rbtn)
        grid_plot_items.addWidget(self.efficiency_mode_rbtn, 3, 9)
        hbox_plot_set1.addLayout(grid_plot_items)
        vbox_plot_mode = QtWidgets.QVBoxLayout()
        hbox_plot_set1.addLayout(vbox_plot_mode)
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
        self.analysis_move_up_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'move_up.png')), '')
        self.analysis_move_up_button.clicked.connect(lambda: self.change_order('up'))
        self.analysis_move_up_button.setToolTip('Move selected up')
        hbox_analysis.addWidget(self.analysis_move_up_button)
        self.analysis_move_down_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'move_down.png')), '')
        self.analysis_move_down_button.clicked.connect(lambda: self.change_order('down'))
        self.analysis_move_down_button.setToolTip('Move selected down')
        hbox_analysis.addWidget(self.analysis_move_down_button)
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
        self.experiment_tree.setSortingEnabled(True)
        self.experiment_tree.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.experiment_tree.header().sectionClicked.connect(lambda: self.change_order('header'))
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
        if self.reference:
            self.update_reference()  # apply reference to new experiments too

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

    def change_order(self, origin=None):
        if origin == 'header':
            self.experiment_directories = []
            iterator = QtWidgets.QTreeWidgetItemIterator(self.experiment_tree)
            while iterator.value():
                tree_item = iterator.value()
                self.experiment_directories.append(str(tree_item.toolTip(3)))
                iterator += 1
        elif len(self.experiment_tree.selectedItems()) == 1:
            self.experiment_tree.header().setSortIndicator(-1, Qt.AscendingOrder)
            item = self.experiment_tree.selectedItems()[0]
            row = self.experiment_tree.selectedIndexes()[0].row()
            if origin == 'up' and row > 0:
                self.experiment_tree.takeTopLevelItem(row)
                self.experiment_tree.insertTopLevelItem(row - 1, item)
                self.experiment_tree.setCurrentItem(item)
                self.experiment_directories.insert(row - 1, self.experiment_directories.pop(row))
            elif origin == 'down' and row < len(self.experiment_directories) - 1:
                self.experiment_tree.takeTopLevelItem(row)
                self.experiment_tree.insertTopLevelItem(row + 1, item)
                self.experiment_tree.setCurrentItem(item)
                self.experiment_directories.insert(row + 1, self.experiment_directories.pop(row))
        self.update_plot()
        self.update_stats()

    def update_experiment_tree(self):
        self.experiment_tree.clear()
        for directory in self.experiment_directories:
            tree_item = TreeWidgetItem(ItemSignal(), self.experiment_tree,
                                       [None, None, None, self.experiments[directory].name,
                                        str(sum(self.experiments[directory].n_traces)),
                                        str(self.experiments[directory].time)])
            tree_item.setToolTip(3, directory)
            tree_item.setCheckState(0, self.bool_to_qtchecked(self.experiments[directory].reference))
            tree_item.setCheckState(1, self.bool_to_qtchecked(self.experiments[directory].plot))
            tree_item.setCheckState(2, self.bool_to_qtchecked(self.experiments[directory].stats))
            tree_item.signal.itemChecked.connect(self.tree_checkbox_changed)

    def update_experiment_data(self):
        directories = self.experiment_directories
        for directory in directories:
            if directory not in self.experiments.keys():
                self.experiments[directory] = Experiment(directory)
        for directory in list(self.experiments.keys()):
            if directory not in directories:
                self.experiments.pop(directory, None)

    @QtCore.pyqtSlot(object, int)
    def tree_checkbox_changed(self, item, column):
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
                if self.plot_mode == 'Single':
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

    def change_plot_items(self, axis, item, state):
        if axis == 'x' and state:
            self.plot_x = item
        elif axis == 'y1' or axis == 'y2':
            if state:
                self.plot_y.append([item, axis])
            else:
                self.plot_y.remove([item, axis])
        self.update_plot()

    def change_plot_settings(self, setting, state):
        self.plot_show[setting] = state
        self.update_plot()

    def change_plot_mode(self, mode, state):
        if state:
            self.plot_mode = mode
            # Set defaults and parameters
            if mode == 'Single':
                self.show_avg_cb.setEnabled(True)
                self.show_rescale_cb.setChecked(True)
            elif mode == 'Average':
                self.show_avg_cb.setEnabled(False)
                self.show_rescale_cb.setChecked(True)
            elif mode == 'Efficiency':
                self.show_avg_cb.setEnabled(False)
                self.show_rescale_cb.setChecked(False)
            self.update_plot()

    def update_plot(self):
        plot_list = [experiment for experiment in self.experiment_directories
                     if self.experiments[experiment].plot is True]
        self.plot_canvas.figure.clear()
        axis = self.plot_canvas.figure.add_subplot(111)
        axis2 = axis.twinx()
        axis2.yaxis.tick_right()
        axis2.yaxis.set_label_position("right")
        if self.plot_mode == 'Single' and len(plot_list) == 1:
            experiment = self.experiments[plot_list[0]]
            axis.set_title(experiment.name)
            if self.plot_x == 'Experiment':
                y_data = list()
                for item in self.plot_y:
                    try:
                        y_data.append([bar_plot_dict[item[0]], item[1]])
                    except KeyError:
                        pass
                ny = len(y_data)
                for j, item in enumerate(y_data):
                    categories, values, errors, bar_color = list(), list(), list(), list()
                    for i, trace in enumerate(experiment.traces.values()):
                        categories.append('Trace %d' % i)
                        values.append(trace.values[item[0]][0])
                        errors.append(trace.values[item[0]][1])
                        bar_color.append(colors.colors[j % len(colors.colors)])
                    if self.plot_show['Average']:
                        categories.append('Average')
                        values.append(experiment.values[item[0]][0])
                        errors.append(experiment.values[item[0]][1])
                        bar_color.append(colors.lighten_color(colors.colors[j % len(colors.colors)], 1.5))
                    index = [k + j * 0.8 / ny for k in range(len(values))]
                    if j == 0:
                        axis.set_xticks([k + 0.4 * (ny - 1) / ny for k in range(len(values))])
                        axis.set_xticklabels(tuple(categories))
                    if item[1] == 'y1':
                        axis.bar(index, values, yerr=errors, width=0.8/ny, color=bar_color,
                                 error_kw=dict(ecolor='black', elinewidth=1, capsize=3), label=y_data[j][0])
                    elif item[1] == 'y2':
                        axis2.bar(index, values, yerr=errors, width=0.8 / ny, color=bar_color,
                                  error_kw=dict(ecolor='black', elinewidth=1, capsize=3), label=y_data[j][0])
                plots.format_yaxis(axis, axis2, self.plot_show['Rescale'])
                axis.set_xlabel("")
                axis.set_ylabel(" /\n".join([item[0] for item in y_data if item[1] == 'y1']))
                axis2.set_ylabel(" /\n".join([item[0] for item in y_data if item[1] == 'y2']))
            else:
                try:
                    x_data = line_plot_dict[self.plot_x]
                except KeyError:
                    return
                y_data = list()
                for item in self.plot_y:
                    try:
                        y_data.append([line_plot_dict[item[0]], item[1]])
                    except KeyError:
                        pass
                for j, item in enumerate(y_data):
                    for i, trace in enumerate(experiment.traces.values()):
                        trace.data.plot(kind='line', x=x_data, y=item[0], lw=1, ls='--',
                                        color=colors.lighten_color(colors.colors[j % len(colors.colors)],
                                                                   1 - 0.6 * i / sum(experiment.n_traces)),
                                        ax=self.get_axis(axis, axis2, item[1]), label='Trace %d' % i)
                    if self.plot_show['Average']:
                        experiment.average_data.plot(kind='line', x=x_data, y=item[0], lw=2,
                                                     color=colors.lighten_color(colors.colors[j % len(colors.colors)],
                                                                                1.5),
                                                     ax=self.get_axis(axis, axis2, item[1]), label='Average')
                axis.set_xlabel(x_data)
                axis.set_ylabel(" /\n".join([item[0] for item in y_data if item[1] == 'y1']))
                axis2.set_ylabel(" /\n".join([item[0] for item in y_data if item[1] == 'y2']))
        elif self.plot_mode == 'Average':
            axis.set_title('Averages')
            if self.plot_x == 'Experiment':
                y_data = list()
                for item in self.plot_y:
                    try:
                        y_data.append([bar_plot_dict[item[0]], item[1]])
                    except KeyError:
                        pass
                ny = len(y_data)
                for j, item in enumerate(y_data):
                    categories, values, errors, bar_color = list(), list(), list(), list()
                    for i, experiment in enumerate(plot_list):
                        if self.experiments[experiment].reference:  # TODO: check why not updated
                            categories.insert(0, self.experiments[experiment].name)
                            values.insert(0, self.experiments[experiment].values[item[0]][0])
                            errors.insert(0, self.experiments[experiment].values[item[0]][1])
                            bar_color.insert(0, colors.lighten_color(colors.colors[j % len(colors.colors)], 1.5))
                        else:
                            categories.append(self.experiments[experiment].name)
                            values.append(self.experiments[experiment].values[item[0]][0])
                            errors.append(self.experiments[experiment].values[item[0]][1])
                            bar_color.append(colors.colors[j % len(colors.colors)])
                    index = [k + j * 0.8 / ny for k in range(len(values))]
                    if j == 0:
                        for k, cat in enumerate(categories):  # add line breaks in experiment labels
                            categories[k] = ''.join([elem + '\n' if i % 2 == 0 else
                                                     elem + ' ' for i, elem in enumerate(cat.split(' '))][0:-1]) + \
                                            cat.split(' ')[-1]
                        axis.set_xticks([k + 0.4 * (ny - 1) / ny for k in range(len(values))])
                        axis.set_xticklabels(tuple(categories))
                    if item[1] == 'y1':
                        axis.bar(index, values, yerr=errors, width=0.8/ny, color=bar_color,
                                 error_kw=dict(ecolor='black', elinewidth=1, capsize=3), label=y_data[j][0])
                    elif item[1] == 'y2':
                        axis2.bar(index, values, yerr=errors, width=0.8 / ny, color=bar_color,
                                  error_kw=dict(ecolor='black', elinewidth=1, capsize=3), label=y_data[j][0])
                plots.format_yaxis(axis, axis2, self.plot_show['Rescale'])
                axis.set_xlabel("")
                axis.set_ylabel(" /\n".join([item[0] for item in y_data if item[1] == 'y1']))
                axis2.set_ylabel(" /\n".join([item[0] for item in y_data if item[1] == 'y2']))
            else:
                try:
                    x_data = line_plot_dict[self.plot_x]
                except KeyError:
                    return
                y_data = list()
                for item in self.plot_y:
                    try:
                        y_data.append([line_plot_dict[item[0]], item[1]])
                    except KeyError:
                        pass
                for j, item in enumerate(y_data):
                    for i, experiment in enumerate(plot_list):
                        self.experiments[experiment].average_data.plot(kind='line', x=x_data, y=item[0], lw=1,
                                                                       color=colors.lighten_color(
                                                                           colors.colors[j % len(colors.colors)],
                                                                           2 - 1.8 * i / len(plot_list)),
                                                                       ax=self.get_axis(axis, axis2, item[1]),
                                                                       label=self.experiments[experiment].name)
                axis.set_xlabel(x_data)
                axis.set_ylabel(" /\n".join([item[0] for item in y_data if item[1] == 'y1']))
                axis2.set_ylabel(" /\n".join([item[0] for item in y_data if item[1] == 'y2']))
        elif self.plot_mode == 'Efficiency':
            axis.set_title('Relative efficiency vs reference')
            if self.plot_x == 'Experiment' and self.reference != '' and len(plot_list) >= 1:
                y_data = list()
                for item in self.plot_y:
                    try:
                        y_data.append([efficiency_plot_dict[item[0]], item[1]])
                    except KeyError:
                        pass
                ny = len(y_data)
                for j, item in enumerate(y_data):
                    categories, values, errors, bar_color = list(), list(), list(), list()
                    for i, experiment in enumerate(plot_list):
                        if self.experiments[experiment].reference is False:
                            categories.append(self.experiments[experiment].name)
                            values.append(self.experiments[experiment].efficiencies[item[0][0]][0])
                            errors.append(self.experiments[experiment].efficiencies[item[0][0]][1])
                            bar_color.append(colors.colors[j % len(colors.colors)])
                    index = [k + j * 0.8 / ny for k in range(len(values))]
                    if j == 0:
                        for k, cat in enumerate(categories):  # add line breaks in experiment labels
                            categories[k] = ''.join([elem + '\n' if i % 2 == 0 else elem + ' '
                                                     for i, elem in enumerate(cat.split(' '))][0:-1]) + \
                                            cat.split(' ')[-1]
                        axis.set_xticks([k + 0.4 * (ny - 1) / ny for k in range(len(values))])
                        axis.set_xticklabels(tuple(categories))
                    if item[1] == 'y1':
                        axis.bar(index, values, yerr=errors, width=0.8/ny, color=bar_color,
                                 error_kw=dict(ecolor='black', elinewidth=1, capsize=3), label=y_data[j][0][1])
                    elif item[1] == 'y2':
                        axis2.bar(index, values, yerr=errors, width=0.8 / ny, color=bar_color,
                                  error_kw=dict(ecolor='black', elinewidth=1, capsize=3), label=y_data[j][0][1])
                plots.format_yaxis(axis, axis2, self.plot_show['Rescale'])
                axis.set_xlabel("")
                axis.set_ylabel(" /\n".join([item[0][1] for item in y_data if item[1] == 'y1']))
                axis2.set_ylabel(" /\n".join([item[0][1] for item in y_data if item[1] == 'y2']))
            else:
                pass
        else:
            axis.set_xlabel(self.plot_x)
            axis.set_ylabel(" /\n".join([item[0] for item in self.plot_y if item[1] == 'y1']))
            axis2.set_ylabel(" /\n".join([item[0] for item in self.plot_y if item[1] == 'y2']))
        self.update_plt.emit()

    @staticmethod
    def get_axis(ax1, ax2, string='y1'):
        if string == 'y1':
            return ax1
        elif string == 'y2':
            return ax2
        else:
            raise ValueError

    def clipboard(self):
        pixmap = QtWidgets.QWidget.grab(self.plot_canvas)
        QtWidgets.QApplication.clipboard().setPixmap(pixmap)

    def save_plot(self):
        i = 0
        path = os.path.join(self.plot_directory, '%s_%s_%s_%d.png' % (self.plot_x,
                                                                      "_".join([item[0] for item in self.plot_y]),
                                                                      self.plot_mode, i))
        while os.path.isfile(path):
            i += 1
            path = os.path.join(self.plot_directory, '%s_%s_%s_%d.png' % (self.plot_x,
                                                                          "_".join([item[0] for item in self.plot_y]),
                                                                          self.plot_mode, i))
        self.plot_canvas.figure.savefig(path)

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
