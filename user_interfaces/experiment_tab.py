from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import os
from PyQt5 import QtWidgets, QtGui, QtCore

import hardware.keithley as keithley
import hardware.sensor as sensor
from utility import ports
from utility.config import paths


class Experiment(QtWidgets.QWidget):
    update_plt = QtCore.pyqtSignal()  # iv figure signal lane
    update_sensor_plt = QtCore.pyqtSignal()  # sensor calibration plot signal lane

    def __init__(self, parent=None):
        super(Experiment, self).__init__(parent)

        self.directory = paths['last_save']
        self.data_iv = np.zeros((5, 1))

        vbox_total = QtWidgets.QVBoxLayout()
        hbox_top = QtWidgets.QHBoxLayout()
        self.iv_group_box = QtWidgets.QGroupBox('I-V Curve')
        vbox_iv = QtWidgets.QVBoxLayout()
        self.iv_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.iv_canvas.figure.tight_layout(pad=0.3)
        self.update_plt.connect(self.iv_canvas.figure.canvas.draw)
        vbox_iv.addWidget(self.iv_canvas)
        self.iv_group_box.setLayout(vbox_iv)
        hbox_top.addWidget(self.iv_group_box, 5)

        vbox_sensor_col = QtWidgets.QVBoxLayout()
        self.sensors_group_box = QtWidgets.QGroupBox('Sensors')
        vbox_sensors = QtWidgets.QVBoxLayout()
        grid_sensors = QtWidgets.QGridLayout()
        self.temperature_label = QtWidgets.QLabel("Temperature (C)", self)
        grid_sensors.addWidget(self.temperature_label, 0, 0)
        self.temperature_edit = QtWidgets.QLineEdit('25', self)
        self.temperature_edit.setFixedWidth(60)
        self.temperature_edit.setDisabled(True)
        grid_sensors.addWidget(self.temperature_edit, 0, 1)
        self.diode1_label = QtWidgets.QLabel("Diode 1 (W/m2)", self)
        grid_sensors.addWidget(self.diode1_label, 1, 0)
        self.diode1_edit = QtWidgets.QLineEdit('0', self)
        self.diode1_edit.setFixedWidth(60)
        self.diode1_edit.setDisabled(True)
        grid_sensors.addWidget(self.diode1_edit, 1, 1)
        self.diode2_label = QtWidgets.QLabel("Diode 2 (W/m2)", self)
        grid_sensors.addWidget(self.diode2_label, 2, 0)
        self.diode2_edit = QtWidgets.QLineEdit('0', self)
        self.diode2_edit.setFixedWidth(60)
        self.diode2_edit.setDisabled(True)
        grid_sensors.addWidget(self.diode2_edit, 2, 1)
        self.diode3_label = QtWidgets.QLabel("Diode 3 (W/m2)", self)
        grid_sensors.addWidget(self.diode3_label, 3, 0)
        self.diode3_edit = QtWidgets.QLineEdit('0', self)
        self.diode3_edit.setFixedWidth(60)
        self.diode3_edit.setDisabled(True)
        grid_sensors.addWidget(self.diode3_edit, 3, 1)
        self.diode4_label = QtWidgets.QLabel("Diode 4 (W/m2)", self)
        grid_sensors.addWidget(self.diode4_label, 4, 0)
        self.diode4_edit = QtWidgets.QLineEdit('0', self)
        self.diode4_edit.setFixedWidth(60)
        self.diode4_edit.setDisabled(True)
        grid_sensors.addWidget(self.diode4_edit, 4, 1)
        vbox_sensors.addLayout(grid_sensors)
        vbox_sensors.addStretch(-1)

        hbox_sens_plot = QtWidgets.QHBoxLayout()
        self.temp_canvas = FigureCanvas(Figure(figsize=(2, 2)))
        self.temp_canvas.figure.tight_layout(pad=0.3)
        self.update_sensor_plt.connect(self.temp_canvas.figure.canvas.draw)
        hbox_sens_plot.addWidget(self.temp_canvas)
        self.power_canvas = FigureCanvas(Figure(figsize=(2, 2)))
        self.power_canvas.figure.tight_layout(pad=0.3)
        self.update_sensor_plt.connect(self.power_canvas.figure.canvas.draw)
        hbox_sens_plot.addWidget(self.power_canvas)
        vbox_sensors.addLayout(hbox_sens_plot)
        self.sensors_group_box.setLayout(vbox_sensors)
        vbox_sensor_col.addWidget(self.sensors_group_box)

        self.arduino_group_box = QtWidgets.QGroupBox('Sensor Parameters')
        grid_arduino = QtWidgets.QGridLayout()
        self.baud_label = QtWidgets.QLabel("Baud rate", self)
        grid_arduino.addWidget(self.baud_label, 0, 0)
        self.baud_edit = QtWidgets.QLineEdit('38400', self)
        self.baud_edit.setFixedWidth(60)
        self.baud_edit.setDisabled(True)
        grid_arduino.addWidget(self.baud_edit, 0, 1)
        self.datapoints_label = QtWidgets.QLabel("# Data points", self)
        grid_arduino.addWidget(self.datapoints_label, 1, 0)
        self.datapoints_edit = QtWidgets.QLineEdit('100', self)
        self.datapoints_edit.setFixedWidth(60)
        self.datapoints_edit.setDisabled(True)
        grid_arduino.addWidget(self.datapoints_edit, 1, 1)
        self.databytes_label = QtWidgets.QLabel("Data bytes", self)
        grid_arduino.addWidget(self.databytes_label, 2, 0)
        self.databytes_edit = QtWidgets.QLineEdit('2', self)
        self.databytes_edit.setFixedWidth(60)
        self.databytes_edit.setDisabled(True)
        grid_arduino.addWidget(self.databytes_edit, 2, 1)
        self.timeout_label = QtWidgets.QLabel("Timeout (s)", self)
        grid_arduino.addWidget(self.timeout_label, 3, 0)
        self.timeout_edit = QtWidgets.QLineEdit('30', self)
        self.timeout_edit.setFixedWidth(60)
        self.timeout_edit.setDisabled(True)
        grid_arduino.addWidget(self.timeout_edit, 3, 1)
        self.ais_label = QtWidgets.QLabel("Analogue inputs", self)
        grid_arduino.addWidget(self.ais_label, 4, 0)
        self.ais_edit = QtWidgets.QLineEdit('5', self)
        self.ais_edit.setFixedWidth(60)
        self.ais_edit.setDisabled(True)
        grid_arduino.addWidget(self.ais_edit, 4, 1)
        self.query_label = QtWidgets.QLabel("Query period (s)", self)
        grid_arduino.addWidget(self.query_label, 5, 0)
        self.query_edit = QtWidgets.QLineEdit('0.25', self)
        self.query_edit.setFixedWidth(60)
        self.query_edit.setDisabled(True)
        grid_arduino.addWidget(self.query_edit, 5, 1)
        self.arduino_group_box.setLayout(grid_arduino)
        vbox_sensor_col.addWidget(self.arduino_group_box)
        vbox_sensor_col.addStretch(-1)
        hbox_top.addLayout(vbox_sensor_col, 2)
        vbox_total.addLayout(hbox_top, 4)

        hbox_bottom = QtWidgets.QHBoxLayout()
        vbox_bottom_left = QtWidgets.QVBoxLayout()
        self.source_group_box = QtWidgets.QGroupBox('Source')
        vbox_source = QtWidgets.QVBoxLayout()

        grid_source = QtWidgets.QGridLayout()
        self.start_label = QtWidgets.QLabel("Start (V)", self)
        grid_source.addWidget(self.start_label, 0, 0)
        self.start_edit = QtWidgets.QLineEdit('-0.01', self)
        self.start_edit.setFixedWidth(80)
        self.start_edit.textChanged.connect(self.update_steps)
        grid_source.addWidget(self.start_edit, 0, 1)
        self.end_label = QtWidgets.QLabel("End (V)", self)
        grid_source.addWidget(self.end_label, 0, 2)
        self.end_edit = QtWidgets.QLineEdit('0.7', self)
        self.end_edit.setFixedWidth(80)
        self.end_edit.textChanged.connect(self.update_steps)
        grid_source.addWidget(self.end_edit, 0, 3)
        self.step_label = QtWidgets.QLabel("Step (V)", self)
        grid_source.addWidget(self.step_label, 0, 4)
        self.step_edit = QtWidgets.QLineEdit('0.005', self)
        self.step_edit.setFixedWidth(80)
        self.step_edit.setDisabled(True)
        grid_source.addWidget(self.step_edit, 0, 5)
        self.nstep_label = QtWidgets.QLabel("# Steps", self)
        grid_source.addWidget(self.nstep_label, 0, 6)
        self.nstep_edit = QtWidgets.QLineEdit('142', self)
        self.nstep_edit.setFixedWidth(80)
        self.nstep_edit.textChanged.connect(self.update_steps)
        grid_source.addWidget(self.nstep_edit, 0, 7)

        self.ilimit_label = QtWidgets.QLabel("I Limit (A)", self)
        grid_source.addWidget(self.ilimit_label, 1, 0)
        self.ilimit_edit = QtWidgets.QLineEdit('0.5', self)
        self.ilimit_edit.setFixedWidth(80)
        grid_source.addWidget(self.ilimit_edit, 1, 1)
        self.delay_label = QtWidgets.QLabel("Delay (s)", self)
        grid_source.addWidget(self.delay_label, 1, 2)
        self.delay_edit = QtWidgets.QLineEdit('0.025', self)
        self.delay_edit.setFixedWidth(80)
        grid_source.addWidget(self.delay_edit, 1, 3)
        self.reps_label = QtWidgets.QLabel("Repetitions", self)
        grid_source.addWidget(self.reps_label, 1, 4)
        self.reps_edit = QtWidgets.QLineEdit('5', self)
        self.reps_edit.setFixedWidth(80)
        grid_source.addWidget(self.reps_edit, 1, 5)
        self.rep_delay_label = QtWidgets.QLabel("Rep. Delay (s)", self)
        grid_source.addWidget(self.rep_delay_label, 1, 6)
        self.rep_delay_edit = QtWidgets.QLineEdit('2.0', self)
        self.rep_delay_edit.setFixedWidth(80)
        grid_source.addWidget(self.rep_delay_edit, 1, 7)
        self.naverage_label = QtWidgets.QLabel("# Averages", self)
        grid_source.addWidget(self.naverage_label, 1, 8)
        self.naverage_edit = QtWidgets.QLineEdit('5', self)  # adjust to update with NSteps
        self.naverage_edit.setFixedWidth(80)
        grid_source.addWidget(self.naverage_edit, 1, 9)
        vbox_source.addLayout(grid_source)
        self.source_group_box.setLayout(vbox_source)
        vbox_bottom_left.addWidget(self.source_group_box)

        self.ports_group_box = QtWidgets.QGroupBox('Ports')
        hbox_ports = QtWidgets.QHBoxLayout()
        self.sensor_label = QtWidgets.QLabel("Arduino", self)
        hbox_ports.addWidget(self.sensor_label)
        self.sensor_cb = QtWidgets.QComboBox()
        self.sensor_cb.setFixedWidth(120)
        self.sensor_cb.addItem('dummy')
        for port in ports.get_serial_ports():
            self.sensor_cb.addItem(port)
        self.sensor_cb.currentTextChanged.connect(self.sensor_port_changed)
        hbox_ports.addWidget(self.sensor_cb)
        self.source_label = QtWidgets.QLabel("Keithley", self)
        hbox_ports.addWidget(self.source_label)
        self.source_cb = QtWidgets.QComboBox()
        self.source_cb.setFixedWidth(120)
        self.source_cb.addItem('dummy')
        self.source_cb.addItem('GPIB::24')
        hbox_ports.addWidget(self.source_cb)
        hbox_ports.addStretch(-1)
        self.ports_group_box.setLayout(hbox_ports)
        vbox_bottom_left.addWidget(self.ports_group_box)
        vbox_bottom_left.addStretch(-1)

        self.measure_group_box = QtWidgets.QGroupBox('Measure')
        vbox_measure = QtWidgets.QVBoxLayout()
        hbox_folder = QtWidgets.QHBoxLayout()
        self.folder_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'folder.png')), '')
        self.folder_button.clicked.connect(self.folder_dialog)
        self.folder_button.setToolTip('Choose folder')
        hbox_folder.addWidget(self.folder_button)
        self.folder_edit = QtWidgets.QLineEdit(self.directory, self)
        self.folder_edit.setMinimumWidth(180)
        self.folder_edit.setDisabled(True)
        hbox_folder.addWidget(self.folder_edit)
        vbox_measure.addLayout(hbox_folder)
        self.measure_group_box.setLayout(vbox_measure)
        vbox_bottom_left.addWidget(self.measure_group_box)
        hbox_bottom.addLayout(vbox_bottom_left)

        self.controls_group_box = QtWidgets.QGroupBox('Ctrl')
        vbox_controls = QtWidgets.QVBoxLayout()
        vbox_controls.addStretch(-1)
        self.start_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'start.png')), '')
        self.start_button.clicked.connect(self.start)
        self.start_button.setToolTip('Start Measurement')
        vbox_controls.addWidget(self.start_button)
        self.stop_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'stop.png')), '')
        self.stop_button.clicked.connect(self.stop)
        self.stop_button.setToolTip('Stop Measurement')
        vbox_controls.addWidget(self.stop_button)
        vbox_controls.addStretch(-1)
        self.temp_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'temp.png')), '')
        self.temp_button.clicked.connect(self.plot_temp)
        self.temp_button.setToolTip('Plot temperature')
        vbox_controls.addWidget(self.temp_button)
        self.power_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'power.png')), '')
        self.power_button.clicked.connect(self.plot_pow)
        self.power_button.setToolTip('Plot power')
        vbox_controls.addWidget(self.power_button)
        self.controls_group_box.setLayout(vbox_controls)
        hbox_bottom.addWidget(self.controls_group_box)

        self.log_group_box = QtWidgets.QGroupBox('Log')
        grid_log = QtWidgets.QGridLayout()
        self.log_edit = QtWidgets.QTextEdit("Ready to measure...\n", self)
        grid_log.addWidget(self.log_edit, 0, 0)
        self.log_group_box.setLayout(grid_log)
        hbox_bottom.addWidget(self.log_group_box)
        vbox_total.addLayout(hbox_bottom, 1)
        self.setLayout(vbox_total)

        self.data_sensor = np.zeros((int(self.ais_edit.text()), int(self.nstep_edit.text())))
        self.plot_temperature = False
        self.plot_power = False
        self.dummy_plot(self.temp_canvas.figure, chs=['temp'])
        self.dummy_plot(self.power_canvas.figure, chs=['power'])
        self.update_sensor_plt.emit()

        self.sensor_mes = None
        self.start_sensor()

        self.iv_mes = keithley.Keithley(gpib_port='dummy')
        self.iv_register(self.iv_mes)
        self.iv_mes.update.emit(-1)

    def sensor_register(self, mes):
        self.sensor_mes = mes
        self.sensor_mes.update.connect(self.update_sensor)
        self.sensor_mes.to_log.connect(self.logger)

    @QtCore.pyqtSlot()
    def update_sensor(self):
        if not self.sensor_mes:
            return
        tval, d1val, d2val, d3val, d4val = self.sensor_mes.get_sensor_latest()
        self.temperature_edit.setText("%.2f" % tval)
        self.diode1_edit.setText("%02d" % d1val)
        self.diode2_edit.setText("%02d" % d2val)
        self.diode3_edit.setText("%02d" % d3val)
        self.diode4_edit.setText("%02d" % d4val)
        # Could enable plotting permanently as long as port is not dummy
        if self.plot_temperature and not self.sensor_mes.port == 'dummy':
            self.sensor_mes.plot(self.temp_canvas.figure, chs=['temp'])
            self.update_sensor_plt.emit()
        if self.plot_power and not self.sensor_mes.port == 'dummy':
            self.sensor_mes.plot(self.power_canvas.figure, chs=['power'])
            self.update_sensor_plt.emit()

    def start_sensor(self):
        if self.sensor_mes:
            self.sensor_mes.stop()
        self.sensor_mes = sensor.ArduinoSensor(port=str(self.sensor_cb.currentText()),
                                               baud=int(self.baud_edit.text()),
                                               n_data_points=int(self.datapoints_edit.text()),
                                               data_num_bytes=int(self.databytes_edit.text()),
                                               n_ai=int(self.ais_edit.text()),
                                               timeout=float(self.timeout_edit.text()),
                                               query_period=float(self.query_edit.text()))
        self.sensor_register(self.sensor_mes)
        self.sensor_mes.start()

    def stop_sensor(self):
        if self.sensor_mes:
            self.sensor_mes.stop()

    def sensor_port_changed(self):
        self.start_sensor()

    def plot_temp(self):
        if not self.plot_temperature:
            self.plot_temperature = True
        else:
            self.plot_temperature = False
            self.dummy_plot(self.temp_canvas.figure, chs=['temp'])
            self.update_sensor_plt.emit()

    def plot_pow(self):
        if not self.plot_power:
            self.plot_power = True
        else:
            self.plot_power = False
            self.dummy_plot(self.power_canvas.figure, chs=['power'])
            self.update_sensor_plt.emit()

    @staticmethod
    def dummy_plot(target_fig=None, chs=None):
        if chs is None:
            chs = []
        if target_fig is None:
            fig = Figure()
        else:
            fig = target_fig
        fig.clear()
        axis = fig.add_subplot(111)
        if 'temp' in chs:
            axis.set_xlabel("Time (s)")
            axis.set_ylabel("Temperature (C)")
        if 'power' in chs:
            axis.set_xlabel("Time (s)")
            axis.set_ylabel("Illumination (W/m2)")
        xval, yval = range(100), [0] * 100
        axis.plot(xval, yval, lw=1.3)
        return fig

    def folder_dialog(self):
        self.directory = str(QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Directory', paths['last_save']))
        self.folder_edit.setText(self.directory)

    def iv_register(self, mes):
        self.iv_mes = mes
        self.iv_mes.update.connect(self.update_iv)
        self.iv_mes.save.connect(self.save)
        self.iv_mes.to_log.connect(self.logger)

    def start(self):
        if self.iv_mes:
            self.iv_mes.close()
        self.iv_mes = keithley.Keithley(gpib_port=str(self.source_cb.currentText()),
                                        n_data_points=int(self.nstep_edit.text()),
                                        averages=int(self.naverage_edit.text()),
                                        repetitions=int(self.reps_edit.text()),
                                        repetition_delay=float(self.rep_delay_edit.text()),
                                        delay=float(self.delay_edit.text()),
                                        min_voltage=float(self.start_edit.text()),
                                        max_voltage=float(self.end_edit.text()),
                                        compliance_current=float(self.ilimit_edit.text()))
        self.iv_register(self.iv_mes)
        self.data_sensor = np.zeros((int(self.ais_edit.text()), int(self.nstep_edit.text())))
        self.iv_mes.read_keithley_start()

    @QtCore.pyqtSlot(int)
    def update_iv(self, datapoint):
        if not self.iv_mes:
            return
        if datapoint != -1:
            sensor_latest = self.sensor_mes.get_sensor_latest()
            for ai, val in enumerate(sensor_latest):
                self.data_sensor[ai, datapoint] = val
        self.iv_mes.plot(self.iv_canvas.figure)
        self.update_plt.emit()

    def stop(self):  # TODO: implement iv scan pause
        if self.iv_mes:
            self.iv_mes.close()

    @QtCore.pyqtSlot(int)
    def save(self, repetition):
        self.data_iv = self.iv_mes.get_keithley_data()
        self.data_iv['Temperature (C)'] = self.data_sensor[0]
        self.data_iv['Power 1 (W/m2)'] = self.data_sensor[1]
        self.data_iv['Power 2 (W/m2)'] = self.data_sensor[2]
        self.data_iv['Power 3 (W/m2)'] = self.data_sensor[3]
        self.data_iv['Power 4 (W/m2)'] = self.data_sensor[4]
        self.data_iv.to_csv(os.path.join(self.directory, 'IV_Curve_%s.csv' % str(repetition)))

    @QtCore.pyqtSlot(str)
    def logger(self, string):
        self.log_edit.append(string)
        self.log_edit.moveCursor(QtGui.QTextCursor.End)

    @QtCore.pyqtSlot()
    def update_steps(self):
        try:  # capture empty cells, typos etc during data entry
            steps = (float(self.end_edit.text()) - float(self.start_edit.text())) / float(self.nstep_edit.text())
            self.step_edit.setText("%.3f" % steps)
        except (ZeroDivisionError, ValueError):
            pass
