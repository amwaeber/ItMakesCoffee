from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import os
from PyQt5 import QtWidgets, QtGui, QtCore

import hardware.sensor as sensor
from utility.config import paths


class Experiment(QtWidgets.QWidget):
    update_plt = QtCore.pyqtSignal()  # iv figure signal lane
    # update_sens = QtCore.pyqtSignal()  # sensor readout signal lane

    def __init__(self, parent=None):
        super(Experiment, self).__init__(parent)

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
        grid_sensors = QtWidgets.QGridLayout()

        self.temperature_label = QtWidgets.QLabel("Temperature (C)", self)
        grid_sensors.addWidget(self.temperature_label, 0, 0)
        self.temperature_edit = QtWidgets.QLineEdit('25', self)
        self.temperature_edit.setFixedWidth(60)
        self.temperature_edit.setDisabled(True)
        grid_sensors.addWidget(self.temperature_edit, 0, 1)

        self.diode1_label = QtWidgets.QLabel("Diode 1 (V)", self)
        grid_sensors.addWidget(self.diode1_label, 1, 0)
        self.diode1_edit = QtWidgets.QLineEdit('0.1', self)
        self.diode1_edit.setFixedWidth(60)
        self.diode1_edit.setDisabled(True)
        grid_sensors.addWidget(self.diode1_edit, 1, 1)

        self.diode2_label = QtWidgets.QLabel("Diode 2 (V)", self)
        grid_sensors.addWidget(self.diode2_label, 2, 0)
        self.diode2_edit = QtWidgets.QLineEdit('0.1', self)
        self.diode2_edit.setFixedWidth(60)
        self.diode2_edit.setDisabled(True)
        grid_sensors.addWidget(self.diode2_edit, 2, 1)

        self.diode3_label = QtWidgets.QLabel("Diode 3 (V)", self)
        grid_sensors.addWidget(self.diode3_label, 3, 0)
        self.diode3_edit = QtWidgets.QLineEdit('0.1', self)
        self.diode3_edit.setFixedWidth(60)
        self.diode3_edit.setDisabled(True)
        grid_sensors.addWidget(self.diode3_edit, 3, 1)

        self.diode4_label = QtWidgets.QLabel("Diode 4 (V)", self)
        grid_sensors.addWidget(self.diode4_label, 4, 0)
        self.diode4_edit = QtWidgets.QLineEdit('0.1', self)
        self.diode4_edit.setFixedWidth(60)
        self.diode4_edit.setDisabled(True)
        grid_sensors.addWidget(self.diode4_edit, 4, 1)

        self.sensors_group_box.setLayout(grid_sensors)
        vbox_sensor_col.addWidget(self.sensors_group_box)
        vbox_sensor_col.addStretch(-1)

        hbox_controls = QtWidgets.QHBoxLayout()
        hbox_controls.addStretch(-1)
        self.start_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'start.png')), '')
        self.start_button.clicked.connect(self.start)
        self.start_button.setToolTip('Start Measurement')
        hbox_controls.addWidget(self.start_button)

        self.pause_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'pause.png')), '')
        self.pause_button.clicked.connect(self.folder_dialog)
        self.pause_button.setToolTip('Pause/Unpause')
        hbox_controls.addWidget(self.pause_button)

        self.stop_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'stop.png')), '')
        self.stop_button.clicked.connect(self.stop)
        self.stop_button.setToolTip('Stop Measurement')
        hbox_controls.addWidget(self.stop_button)
        hbox_controls.addStretch(-1)
        vbox_sensor_col.addLayout(hbox_controls)
        hbox_top.addLayout(vbox_sensor_col, 2)
        vbox_total.addLayout(hbox_top, 4)

        hbox_bottom = QtWidgets.QHBoxLayout()
        self.source_group_box = QtWidgets.QGroupBox('Source')
        vbox_source = QtWidgets.QVBoxLayout()
        hbox_sweep = QtWidgets.QHBoxLayout()
        self.sweep_label = QtWidgets.QLabel("Sweep", self)
        hbox_sweep.addWidget(self.sweep_label)
        self.sweep_cb = QtWidgets.QComboBox()
        self.sweep_cb.setFixedWidth(120)
        self.sweep_cb.addItem("Linear")
        self.sweep_cb.addItem("Up-Down")
        self.sweep_cb.addItem("Random")
        hbox_sweep.addWidget(self.sweep_cb)
        hbox_sweep.addStretch(-1)
        vbox_source.addLayout(hbox_sweep)
        vbox_source.addStretch(-1)

        grid_source = QtWidgets.QGridLayout()
        self.start_label = QtWidgets.QLabel("Start (V)", self)
        grid_source.addWidget(self.start_label, 0, 0)
        self.start_edit = QtWidgets.QLineEdit('-0.01', self)
        self.start_edit.setFixedWidth(80)
        grid_source.addWidget(self.start_edit, 0, 1)
        self.end_label = QtWidgets.QLabel("End (V)", self)
        grid_source.addWidget(self.end_label, 0, 2)
        self.end_edit = QtWidgets.QLineEdit('0.7', self)
        self.end_edit.setFixedWidth(80)
        grid_source.addWidget(self.end_edit, 0, 3)
        self.step_label = QtWidgets.QLabel("Step (V)", self)
        grid_source.addWidget(self.step_label, 0, 4)
        self.step_edit = QtWidgets.QLineEdit('0.01', self)  # adjust to update with NSteps
        self.step_edit.setFixedWidth(80)
        grid_source.addWidget(self.step_edit, 0, 5)
        self.nstep_label = QtWidgets.QLabel("# Steps", self)
        grid_source.addWidget(self.nstep_label, 0, 6)
        self.nstep_edit = QtWidgets.QLineEdit('142', self)  # adjust to update with NSteps
        self.nstep_edit.setFixedWidth(80)
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
        vbox_source.addLayout(grid_source)
        self.source_group_box.setLayout(vbox_source)
        hbox_bottom.addWidget(self.source_group_box)

        self.measure_group_box = QtWidgets.QGroupBox('Measure')
        vbox_measure = QtWidgets.QVBoxLayout()

        grid_meas_pars = QtWidgets.QGridLayout()
        self.current_cb = QtWidgets.QCheckBox('Current', self)
        self.current_cb.setChecked(True)
        grid_meas_pars.addWidget(self.current_cb, 0, 0)
        self.voltage_cb = QtWidgets.QCheckBox('Voltage', self)
        self.voltage_cb.setChecked(True)
        grid_meas_pars.addWidget(self.voltage_cb, 0, 1)
        self.power_cb = QtWidgets.QCheckBox('Power', self)
        self.power_cb.setChecked(True)
        grid_meas_pars.addWidget(self.power_cb, 1, 0)
        self.resistance_cb = QtWidgets.QCheckBox('Resistance', self)
        self.resistance_cb.setChecked(True)
        grid_meas_pars.addWidget(self.resistance_cb, 1, 1)
        self.temperature_cb = QtWidgets.QCheckBox('Temperature', self)
        self.temperature_cb.setChecked(True)
        grid_meas_pars.addWidget(self.temperature_cb, 2, 0)
        self.diodes_cb = QtWidgets.QCheckBox('Diodes', self)
        self.diodes_cb.setChecked(True)
        grid_meas_pars.addWidget(self.diodes_cb, 2, 1)
        vbox_measure.addLayout(grid_meas_pars)
        vbox_measure.addStretch(-1)

        hbox_folder = QtWidgets.QHBoxLayout()
        self.folder_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'folder.png')), '')
        self.folder_button.clicked.connect(self.folder_dialog)
        self.folder_button.setToolTip('Choose folder')
        hbox_folder.addWidget(self.folder_button)
        self.folder_edit = QtWidgets.QLineEdit('\\..', self)
        self.folder_edit.setMinimumWidth(180)
        self.folder_edit.setDisabled(True)
        hbox_folder.addWidget(self.folder_edit)
        vbox_measure.addLayout(hbox_folder)
        self.measure_group_box.setLayout(vbox_measure)
        hbox_bottom.addWidget(self.measure_group_box)
        vbox_total.addLayout(hbox_bottom, 1)
        self.setLayout(vbox_total)

        self.start_sensor()

    def sensor_register(self, mes):
        self.sensor_mes = mes
        self.sensor_mes.update.connect(self.update_sensor)

    def update_sensor(self):
        if not self.sensor_mes:
            return
        tval, d1val, d2val, d3val, d4val = self.sensor_mes.get_sensor_latest()
        self.temperature_edit.setText("%.3f" % tval)
        self.diode1_edit.setText("%.3f" % d1val)
        self.diode2_edit.setText("%.3f" % d2val)
        self.diode3_edit.setText("%.3f" % d3val)
        self.diode4_edit.setText("%.3f" % d4val)
        self.sensor_mes.plot(self.iv_canvas.figure, chs=['temp'])
        # self.update_sens.emit()

    def start_sensor(self):
        if hasattr(self, 'sensor_mes') and self.sensor_mes:
            self.sensor_mes.stop()
        self.sensor_mes = sensor.ArduinoSensor(dt=0.25, t=10.0)
        self.sensor_register(self.sensor_mes)
        self.sensor_mes.start(t=10.0)

    def folder_dialog(self):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def pause(self):
        pass
