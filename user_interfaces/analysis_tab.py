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
from utility.excel_export import save_to_xlsx
from utility.folders import get_experiment_folders


line_plot_dict = {'Time': 'Time (s)',
                  'Current': 'Current (A)',
                  'Voltage': 'Voltage (V)',
                  'Power': 'Power (W)',
                  'Temperature': 'Temperature (C)',
                  'Irradiance 1': 'Irradiance 1 (W/m2)',
                  'Irradiance 2': 'Irradiance 2 (W/m2)',
                  'Irradiance 3': 'Irradiance 3 (W/m2)',
                  'Irradiance 4': 'Irradiance 4 (W/m2)'}

bar_plot_dict = {'Current': 'Short Circuit Current I_sc (A)',
                 'Voltage': 'Open Circuit Voltage V_oc (V)',
                 'Power': 'Maximum Power P_max (W)',
                 'Fill Factor': 'Fill Factor',
                 'Temperature': 'Average Temperature T_avg (C)',
                 'Irradiance 1': 'Average Irradiance I_1_avg (W/m2)',
                 'Irradiance 2': 'Average Irradiance I_2_avg (W/m2)',
                 'Irradiance 3': 'Average Irradiance I_3_avg (W/m2)',
                 'Irradiance 4': 'Average Irradiance I_4_avg (W/m2)'}

efficiency_plot_dict = {'Current': ['Delta I_sc', r'$\Delta I_{sc}/PV (\%)$'],
                        'Voltage': ['Delta V_oc', r'$\Delta V_{oc}/PV (\%)$'],
                        'Power': ['Delta P_max', r'$\Delta P_{max}/PV (\%)$'],
                        'Fill Factor': ['Delta Fill Factor', r'$\Delta FF/PV (\%)$'],
                        'Temperature': ['Delta T_avg', r'$\Delta T_{avg}/PV (\%)$'],
                        'Irradiance 1': ['Delta I_1_avg', r'$\Delta I_{1, avg}/PV (\%)$'],
                        'Irradiance 2': ['Delta I_2_avg', r'$\Delta I_{2, avg}/PV (\%)$'],
                        'Irradiance 3': ['Delta I_3_avg', r'$\Delta I_{3, avg}/PV (\%)$'],
                        'Irradiance 4': ['Delta I_4_avg', r'$\Delta I_{4, avg}/PV (\%)$']}

table_header_dict = {'Single': ['Trace', 'Isc (A)', 'Voc (V)', 'Pmax (W)', 'FF', 'Tavg (\u00B0C)',
                                'I\u2081avg (W/m\u00B2)', 'I\u2082avg (W/m\u00B2)', 'I\u2083avg (W/m\u00B2)',
                                'I\u2084avg (W/m\u00B2)'],
                     'Average': ['Experiment', 'Isc (A)', 'Voc (V)', 'Pmax (W)', 'FF', 'Tavg (\u00B0C)',
                                 'I\u2081avg (W/m\u00B2)', 'I\u2082avg (W/m\u00B2)', 'I\u2083avg (W/m\u00B2)',
                                 'I\u2084avg (W/m\u00B2)'],
                     'Efficiency': ['Experiment', '\u0394Isc/PV (%)', '\u0394Voc/PV (%)', '\u0394Pmax/PV (%)',
                                    '\u0394FF/PV (%)', '\u0394Tavg/PV (%)', '\u0394I\u2081avg/PV (%)',
                                    '\u0394I\u2082avg/PV (%)', '\u0394I\u2083avg/PV (%)', '\u0394I\u2084avg/PV (%)']}


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
                          'Scatter': False,
                          'Groups': False}
        self.plot_directory = paths['last_plot_save']

        self.stats_directory = paths['last_stats_save']

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
        self.statistics_table.setColumnCount(10)
        self.statistics_table.setHorizontalHeaderLabels(table_header_dict[self.plot_mode])
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
        self.item_experiment_label = QtWidgets.QLabel("Categorical", self)
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
        self.item_irradiance_x.toggled.connect(lambda: self.irradiance_plot('x', '',
                                                                            self.item_irradiance_x.isChecked()))
        self.plot_mode_xaxis_group.addButton(self.item_irradiance_x)
        grid_plot_items.addWidget(self.item_irradiance_x, 8, 1)
        self.item_irradiance_y1 = QtWidgets.QCheckBox('',)
        self.item_irradiance_y1.toggled.connect(lambda: self.irradiance_plot('y1', '',
                                                                             self.item_irradiance_y1.isChecked()))
        self.plot_mode_yaxis1_group.addButton(self.item_irradiance_y1)
        grid_plot_items.addWidget(self.item_irradiance_y1, 8, 2)
        self.item_irradiance_y2 = QtWidgets.QCheckBox('',)
        self.item_irradiance_y2.toggled.connect(lambda: self.irradiance_plot('y2', '',
                                                                             self.item_irradiance_y2.isChecked()))
        self.plot_mode_yaxis2_group.addButton(self.item_irradiance_y2)
        grid_plot_items.addWidget(self.item_irradiance_y2, 8, 3)

        # X-axis plot category selection
        self.show_categories_label = QtWidgets.QLabel("Category", self)
        grid_plot_items.addWidget(self.show_categories_label, 0, 5)
        self.plot_categories_cb = QtWidgets.QComboBox()
        self.plot_categories_cb.setFixedWidth(120)
        self.plot_categories_cb.addItem('Experiment')
        self.plot_categories_cb.addItem('Film Thickness')
        self.plot_categories_cb.addItem('Film Area')
        self.plot_categories_cb.addItem('Time')
        self.plot_categories_cb.currentTextChanged.connect(self.update_plot)
        grid_plot_items.addWidget(self.plot_categories_cb, 1, 5)

        # Various plot options
        self.plot_show_label = QtWidgets.QLabel('Options', self)
        grid_plot_items.addWidget(self.plot_show_label, 3, 5)
        self.show_avg_label = QtWidgets.QLabel("Show Average", self)
        grid_plot_items.addWidget(self.show_avg_label, 4, 5)
        self.show_avg_cb = QtWidgets.QCheckBox('', )
        self.show_avg_cb.setChecked(True)
        self.show_avg_cb.toggled.connect(lambda: self.change_plot_settings('Average', self.show_avg_cb.isChecked()))
        grid_plot_items.addWidget(self.show_avg_cb, 4, 6)
        self.show_legend_label = QtWidgets.QLabel("Show Legend", self)
        grid_plot_items.addWidget(self.show_legend_label, 5, 5)
        self.show_legend_cb = QtWidgets.QCheckBox('', )
        self.show_legend_cb.setChecked(True)
        self.show_legend_cb.toggled.connect(lambda: self.change_plot_settings('Legend',
                                                                              self.show_legend_cb.isChecked()))
        grid_plot_items.addWidget(self.show_legend_cb, 5, 6)
        self.show_rescale_label = QtWidgets.QLabel("Autoscale Y", self)
        grid_plot_items.addWidget(self.show_rescale_label, 6, 5)
        self.show_rescale_cb = QtWidgets.QCheckBox('', )
        self.show_rescale_cb.setChecked(True)
        self.show_rescale_cb.toggled.connect(lambda: self.change_plot_settings('Rescale',
                                                                               self.show_rescale_cb.isChecked()))
        grid_plot_items.addWidget(self.show_rescale_cb, 6, 6)
        self.show_scatter_label = QtWidgets.QLabel("Plot Scatter", self)  # TODO: Implement scatter plots
        grid_plot_items.addWidget(self.show_scatter_label, 7, 5)
        self.show_scatter_cb = QtWidgets.QCheckBox('', )
        self.show_scatter_cb.toggled.connect(lambda: self.change_plot_settings('Scatter',
                                                                               self.show_scatter_cb.isChecked()))
        grid_plot_items.addWidget(self.show_scatter_cb, 7, 6)
        self.show_groups_label = QtWidgets.QLabel("Plot Groups", self)  # TODO: Implement grouping
        grid_plot_items.addWidget(self.show_groups_label, 8, 5)
        self.show_group_cb = QtWidgets.QCheckBox('', )
        self.show_group_cb.toggled.connect(lambda: self.change_plot_settings('Groups',
                                                                             self.show_group_cb.isChecked()))
        grid_plot_items.addWidget(self.show_group_cb, 8, 6)

        self.plot_mode_rbtn_group = QtWidgets.QButtonGroup()
        self.single_mode_label = QtWidgets.QLabel("Single Mode", self)
        grid_plot_items.addWidget(self.single_mode_label, 0, 8)
        self.single_mode_rbtn = QtWidgets.QRadioButton('')
        self.single_mode_rbtn.setChecked(True)
        self.single_mode_rbtn.toggled.connect(lambda: self.change_plot_mode('Single',
                                                                            self.single_mode_rbtn.isChecked()))
        self.plot_mode_rbtn_group.addButton(self.single_mode_rbtn)
        grid_plot_items.addWidget(self.single_mode_rbtn, 0, 9)
        self.avg_mode_label = QtWidgets.QLabel("Average Mode", self)
        grid_plot_items.addWidget(self.avg_mode_label, 1, 8)
        self.avg_mode_rbtn = QtWidgets.QRadioButton('')
        self.avg_mode_rbtn.toggled.connect(lambda: self.change_plot_mode('Average',
                                                                         self.avg_mode_rbtn.isChecked()))
        self.plot_mode_rbtn_group.addButton(self.avg_mode_rbtn)
        grid_plot_items.addWidget(self.avg_mode_rbtn, 1, 9)
        self.efficiency_mode_label = QtWidgets.QLabel("Efficiency Mode", self)
        grid_plot_items.addWidget(self.efficiency_mode_label, 2, 8)
        self.efficiency_mode_rbtn = QtWidgets.QRadioButton('')
        self.efficiency_mode_rbtn.toggled.connect(lambda: self.change_plot_mode('Efficiency',
                                                                                self.efficiency_mode_rbtn.isChecked()))
        self.plot_mode_rbtn_group.addButton(self.efficiency_mode_rbtn)
        grid_plot_items.addWidget(self.efficiency_mode_rbtn, 2, 9)

        self.diodes_label = QtWidgets.QLabel('Show Diodes', self)
        grid_plot_items.addWidget(self.diodes_label, 4, 8)
        self.show_d1_label = QtWidgets.QLabel("Diode 1", self)
        grid_plot_items.addWidget(self.show_d1_label, 5, 8)
        self.show_d1_cb = QtWidgets.QCheckBox('', )
        self.show_d1_cb.setChecked(True)
        self.show_d1_cb.toggled.connect(lambda: self.irradiance_plot(None, 'Irradiance 1',
                                                                     self.show_d1_cb.isChecked()))
        grid_plot_items.addWidget(self.show_d1_cb, 5, 9)
        self.show_d2_label = QtWidgets.QLabel("Diode 2", self)
        grid_plot_items.addWidget(self.show_d2_label, 6, 8)
        self.show_d2_cb = QtWidgets.QCheckBox('', )
        self.show_d2_cb.setChecked(True)
        self.show_d2_cb.toggled.connect(lambda: self.irradiance_plot(None, 'Irradiance 2',
                                                                     self.show_d2_cb.isChecked()))
        grid_plot_items.addWidget(self.show_d2_cb, 6, 9)
        self.show_d3_label = QtWidgets.QLabel("Diode 3", self)
        grid_plot_items.addWidget(self.show_d3_label, 7, 8)
        self.show_d3_cb = QtWidgets.QCheckBox('', )
        self.show_d3_cb.setChecked(True)
        self.show_d3_cb.toggled.connect(lambda: self.irradiance_plot(None, 'Irradiance 3',
                                                                     self.show_d3_cb.isChecked()))
        grid_plot_items.addWidget(self.show_d3_cb, 7, 9)
        self.show_d4_label = QtWidgets.QLabel("Diode 4", self)
        grid_plot_items.addWidget(self.show_d4_label, 8, 8)
        self.show_d4_cb = QtWidgets.QCheckBox('', )
        self.show_d4_cb.setChecked(True)
        self.show_d4_cb.toggled.connect(lambda: self.irradiance_plot(None, 'Irradiance 4',
                                                                     self.show_d4_cb.isChecked()))
        grid_plot_items.addWidget(self.show_d4_cb, 8, 9)

        hbox_plot_set1.addLayout(grid_plot_items)
        vbox_plot_mode = QtWidgets.QVBoxLayout()
        hbox_plot_set1.addLayout(vbox_plot_mode)
        hbox_plot_set1.addStretch(-1)
        vbox_plot_set.addLayout(hbox_plot_set1)

        hbox_plot_set2 = QtWidgets.QHBoxLayout()
        self.plot_save_folder_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'folder.png')), '')
        self.plot_save_folder_button.clicked.connect(self.folder_dialog)
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

        self.stats_settings_group_box = QtWidgets.QGroupBox('Data Export')
        hbox_data_export = QtWidgets.QHBoxLayout()
        self.stats_save_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'save.png')), '')
        self.stats_save_button.clicked.connect(self.save_stats)
        self.stats_save_button.setToolTip('Save as xlsx')
        hbox_data_export.addWidget(self.stats_save_button)
        self.stats_save_folder_edit = QtWidgets.QLineEdit(self.stats_directory, self)
        self.stats_save_folder_edit.setMinimumWidth(180)
        self.stats_save_folder_edit.setDisabled(True)
        hbox_data_export.addWidget(self.stats_save_folder_edit)
        self.stats_settings_group_box.setLayout(hbox_data_export)
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
        self.analysis_group_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'group.png')), '')
        self.analysis_group_button.clicked.connect(self.group_experiments)
        self.analysis_group_button.setToolTip('Group selected experiments')
        hbox_analysis.addWidget(self.analysis_group_button)
        self.analysis_ungroup_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'ungroup.png')), '')
        self.analysis_ungroup_button.clicked.connect(self.ungroup_experiments)
        self.analysis_ungroup_button.setToolTip('Ungroup selected experiments')
        hbox_analysis.addWidget(self.analysis_ungroup_button)
        hbox_analysis.addStretch(-1)
        vbox_analysis.addLayout(hbox_analysis)
        self.experiment_tree = QtWidgets.QTreeWidget()
        self.experiment_tree.setRootIsDecorated(False)
        self.experiment_tree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.experiment_tree.setHeaderLabels(["Ref", "Plot", "Stat", "Experiment", "Traces", "Film Th.", "Film Area",
                                              "Created"])
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

    def folder_dialog(self):
        self.plot_directory = str(QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Directory',
                                                                             self.plot_directory))
        self.plot_save_folder_edit.setText(self.plot_directory)

    def add_experiments(self):
        multi_dir_dialog = MultiDirDialog()
        multi_dir_dialog.setDirectory(paths['last_save'])
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

    def group_experiments(self):
        pass

    def ungroup_experiments(self):
        pass

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

    def update_experiment_tree(self):
        self.experiment_tree.clear()
        for directory in self.experiment_directories:
            tree_item = TreeWidgetItem(ItemSignal(), self.experiment_tree,
                                       [None, None, None, self.experiments[directory].name,
                                        str(sum(self.experiments[directory].n_traces)),
                                        str(self.experiments[directory].film_thickness),
                                        str(self.experiments[directory].film_area),
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
                self.experiments[directory].store()  # save analysed data in pickle
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
            self.update_stats()

        elif column == 1:  # Plot/Statistics
            if int(item.checkState(column)) == 0:
                self.experiments[experiment].plot = False
            else:
                # set other plot cbs to False if in single-plot mode
                if self.plot_mode == 'Single':
                    iterator = QtWidgets.QTreeWidgetItemIterator(self.experiment_tree)
                    while iterator.value():
                        tree_item = iterator.value()
                        if tree_item != item and int(tree_item.checkState(column)) != 0:
                            tree_item.setCheckState(1, Qt.Unchecked)
                            self.experiments[str(tree_item.toolTip(3))].reference = False
                        iterator += 1
                self.experiments[experiment].plot = True
            self.update_plot()
            self.update_stats()

        elif column == 2:  # Statistics TODO: replace by 'group' indicators?
            if int(item.checkState(column)) == 0:
                self.experiments[experiment].stats = False
            else:
                self.experiments[experiment].stats = True
            # self.update_stats()

    def update_reference(self):
        for experiment in self.experiments.values():
            experiment.update_efficiencies(self.experiments.get(self.reference, None))

    def irradiance_plot(self, axis, item, state):
        if axis is None:  # toggled a 'show diode' checkbox
            for ax, obj in [('x', self.item_irradiance_x), ('y1', self.item_irradiance_y1),
                            ('y2', self.item_irradiance_y2)]:
                if obj.isChecked():
                    self.change_plot_items(ax, item, state)
        else:  # toggled an irradiance axis checkbox
            for it, obj in [('Irradiance 1', self.show_d1_cb), ('Irradiance 2', self.show_d2_cb),
                            ('Irradiance 3', self.show_d3_cb), ('Irradiance 4', self.show_d4_cb)]:
                if obj.isChecked():
                    self.change_plot_items(axis, it, state)

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
            self.update_stats()

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
                plots.format_legend(axis, axis2, self.plot_show['Legend'])
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
                                                     ax=self.get_axis(axis, axis2, item[1]), label=item[0])
                plots.format_legend(axis, axis2, self.plot_show['Legend'])
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
                            categories.insert(0, self.experiments[experiment].
                                              plot_categories[self.plot_categories_cb.currentText()])
                            values.insert(0, self.experiments[experiment].values[item[0]][0])
                            errors.insert(0, self.experiments[experiment].values[item[0]][1])
                            bar_color.insert(0, colors.lighten_color(colors.colors[j % len(colors.colors)], 1.5))
                        else:
                            categories.append(self.experiments[experiment].
                                              plot_categories[self.plot_categories_cb.currentText()])
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
                plots.format_legend(axis, axis2, self.plot_show['Legend'])
                axis.set_xlabel(self.plot_categories_cb.currentText())
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
                                                                           1.75 - 1.5 * i / len(plot_list)),
                                                                       ax=self.get_axis(axis, axis2, item[1]),
                                                                       label=self.experiments[experiment].name)
                plots.format_legend(axis, axis2, self.plot_show['Legend'])
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
                            categories.append(self.experiments[experiment].
                                              plot_categories[self.plot_categories_cb.currentText()])
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
                plots.format_legend(axis, axis2, self.plot_show['Legend'])
                axis.set_xlabel(self.plot_categories_cb.currentText())
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
        stats_list = [experiment for experiment in self.experiment_directories
                      if self.experiments[experiment].plot is True]
        self.statistics_table.setHorizontalHeaderLabels(table_header_dict[self.plot_mode])

        if self.plot_mode == 'Single' and len(stats_list) == 1:
            experiment = self.experiments[stats_list[0]]
            n_data_rows = sum(experiment.n_traces) + 1
            self.statistics_table.setRowCount(n_data_rows)
            for i, trace in enumerate(experiment.traces.values()):
                self.statistics_table.setItem(i, 0, QtWidgets.QTableWidgetItem('Trace %d' % i))
                for j, par in enumerate(bar_plot_dict.values(), 1):
                    self.statistics_table.setItem(i, j, QtWidgets.QTableWidgetItem("%.3f\u00B1%.3f"
                                                                                   % tuple(trace.values[par])))
            self.statistics_table.setItem(n_data_rows - 1, 0, QtWidgets.QTableWidgetItem('Average'))
            for j, par in enumerate(bar_plot_dict.values(), 1):
                self.statistics_table.setItem(n_data_rows - 1, j,
                                              QtWidgets.QTableWidgetItem("%.3f\u00B1%.3f"
                                                                         % tuple(experiment.values[par])))

        elif self.plot_mode == 'Average':
            n_data_rows = len(stats_list)
            self.statistics_table.setRowCount(n_data_rows)
            for i, experiment in enumerate([exp for exp in self.experiments.values() if exp.plot]):
                self.statistics_table.setItem(i, 0, QtWidgets.QTableWidgetItem(experiment.name))
                for j, par in enumerate(bar_plot_dict.values(), 1):
                    self.statistics_table.setItem(i, j,
                                                  QtWidgets.QTableWidgetItem("%.3f\u00B1%.3f"
                                                                             % tuple(experiment.values[par])))

        elif self.plot_mode == 'Efficiency' and self.reference != '' and len(stats_list) >= 1:
            n_data_rows = len(stats_list) - 1
            self.statistics_table.setRowCount(n_data_rows)
            for i, experiment in enumerate([exp for exp in self.experiments.values()
                                            if exp.plot and not exp.reference]):
                self.statistics_table.setItem(i, 0, QtWidgets.QTableWidgetItem(experiment.name))
                for j, par in enumerate(efficiency_plot_dict.values(), 1):
                    self.statistics_table.setItem(i, j,
                                                  QtWidgets.QTableWidgetItem("%.3f\u00B1%.3f"
                                                                             % tuple(experiment.efficiencies[par[0]])))

        else:
            self.statistics_table.setRowCount(4)
        self.statistics_table.resizeColumnsToContents()
        self.statistics_table.resizeRowsToContents()

    def save_stats(self):
        export_filepath = str(QtWidgets.QFileDialog.getSaveFileName(self, 'Save as...', self.stats_directory,
                                                                    "Excel files (*.xlsx)")[0])
        if export_filepath == '':
            return
        if not os.path.basename(export_filepath).endswith('.xlsx'):
            export_filepath = os.path.join(export_filepath, '.xlsx')
        self.stats_directory = os.path.dirname(export_filepath)
        self.stats_save_folder_edit.setText(self.stats_directory)
        save_to_xlsx(self.experiments, export_filepath)

    @staticmethod
    def bool_to_qtchecked(boolean):
        if boolean:
            return Qt.Checked
        else:
            return Qt.Unchecked
