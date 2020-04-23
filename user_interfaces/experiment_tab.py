from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import os
from PyQt5 import QtWidgets, QtGui, QtCore

import hardware.sensor as sensor
from utility.config import paths


class Experiment(QtWidgets.QWidget):
    update_plt = QtCore.pyqtSignal()

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
        vbox_sensors = QtWidgets.QVBoxLayout()

        hbox_temp = QtWidgets.QHBoxLayout()
        self.temperature_label = QtWidgets.QLabel("Temperature (C)", self)
        hbox_temp.addWidget(self.temperature_label)
        self.temperature_edit = QtWidgets.QLineEdit('25', self)
        self.temperature_edit.setFixedWidth(60)
        self.temperature_edit.setDisabled(True)
        hbox_temp.addWidget(self.temperature_edit)
        vbox_sensors.addLayout(hbox_temp)

        hbox_diode1 = QtWidgets.QHBoxLayout()
        self.diode1_label = QtWidgets.QLabel("Diode 1 (V)", self)
        hbox_diode1.addWidget(self.diode1_label)
        self.diode1_edit = QtWidgets.QLineEdit('0.1', self)
        self.diode1_edit.setFixedWidth(60)
        self.diode1_edit.setDisabled(True)
        hbox_diode1.addWidget(self.diode1_edit)
        vbox_sensors.addLayout(hbox_diode1)

        hbox_diode2 = QtWidgets.QHBoxLayout()
        self.diode2_label = QtWidgets.QLabel("Diode 2 (V)", self)
        hbox_diode2.addWidget(self.diode2_label)
        self.diode2_edit = QtWidgets.QLineEdit('0.1', self)
        self.diode2_edit.setFixedWidth(60)
        self.diode2_edit.setDisabled(True)
        hbox_diode2.addWidget(self.diode2_edit)
        vbox_sensors.addLayout(hbox_diode2)

        hbox_diode3 = QtWidgets.QHBoxLayout()
        self.diode3_label = QtWidgets.QLabel("Diode 3 (V)", self)
        hbox_diode3.addWidget(self.diode3_label)
        self.diode3_edit = QtWidgets.QLineEdit('0.1', self)
        self.diode3_edit.setFixedWidth(60)
        self.diode3_edit.setDisabled(True)
        hbox_diode3.addWidget(self.diode3_edit)
        vbox_sensors.addLayout(hbox_diode3)

        hbox_diode4 = QtWidgets.QHBoxLayout()
        self.diode4_label = QtWidgets.QLabel("Diode 4 (V)", self)
        hbox_diode4.addWidget(self.diode4_label)
        self.diode4_edit = QtWidgets.QLineEdit('0.1', self)
        self.diode4_edit.setFixedWidth(60)
        self.diode4_edit.setDisabled(True)
        hbox_diode4.addWidget(self.diode4_edit)
        vbox_sensors.addLayout(hbox_diode4)
        self.sensors_group_box.setLayout(vbox_sensors)
        vbox_sensor_col.addWidget(self.sensors_group_box)
        vbox_sensor_col.addStretch(1)

        hbox_controls = QtWidgets.QHBoxLayout()
        hbox_controls.addStretch(1)
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
        hbox_controls.addStretch(1)
        vbox_sensor_col.addLayout(hbox_controls)
        hbox_top.addLayout(vbox_sensor_col, 2)
        vbox_total.addLayout(hbox_top, 3)


        hbox_bottom = QtWidgets.QHBoxLayout()
        self.source_group_box = QtWidgets.QGroupBox('Source')
        hbox_source = QtWidgets.QHBoxLayout()
        vbox1_source = QtWidgets.QVBoxLayout()
        hbox_sweep = QtWidgets.QHBoxLayout()
        self.sweep_label = QtWidgets.QLabel("Sweep", self)
        hbox_sweep.addWidget(self.sweep_label)
        self.sweep_cb = QtWidgets.QComboBox()
        self.sweep_cb.setFixedWidth(120)
        self.sweep_cb.addItem("Linear")
        self.sweep_cb.addItem("Up-Down")
        self.sweep_cb.addItem("Random")
        hbox_sweep.addWidget(self.sweep_cb)
        vbox1_source.addLayout(hbox_sweep)
        vbox1_source.addStretch(1)

        hbox_start = QtWidgets.QHBoxLayout()
        self.start_label = QtWidgets.QLabel("Start (V)", self)
        hbox_start.addWidget(self.start_label)
        self.start_edit = QtWidgets.QLineEdit('-0.01', self)
        self.start_edit.setFixedWidth(120)
        hbox_start.addWidget(self.start_edit)
        vbox1_source.addLayout(hbox_start)

        hbox_limit = QtWidgets.QHBoxLayout()
        self.ilimit_label = QtWidgets.QLabel("I Limit (A)", self)
        hbox_limit.addWidget(self.ilimit_label)
        self.ilimit_edit = QtWidgets.QLineEdit('0.5', self)
        self.ilimit_edit.setFixedWidth(120)
        hbox_limit.addWidget(self.ilimit_edit)
        vbox1_source.addLayout(hbox_limit)
        hbox_source.addLayout(vbox1_source)

        vbox2_source = QtWidgets.QVBoxLayout()
        vbox2_source.addStretch(1)
        hbox_end = QtWidgets.QHBoxLayout()
        self.end_label = QtWidgets.QLabel("End (V)", self)
        hbox_end.addWidget(self.end_label)
        self.end_edit = QtWidgets.QLineEdit('0.7', self)
        self.end_edit.setFixedWidth(120)
        hbox_end.addWidget(self.end_edit)
        vbox2_source.addLayout(hbox_end)

        hbox_delay = QtWidgets.QHBoxLayout()
        self.delay_label = QtWidgets.QLabel("Delay (s)", self)
        hbox_delay.addWidget(self.delay_label)
        self.delay_edit = QtWidgets.QLineEdit('0.025', self)
        self.delay_edit.setFixedWidth(120)
        hbox_delay.addWidget(self.delay_edit)
        vbox2_source.addLayout(hbox_delay)
        hbox_source.addLayout(vbox2_source)

        vbox3_source = QtWidgets.QVBoxLayout()
        vbox3_source.addStretch(1)
        hbox_step = QtWidgets.QHBoxLayout()
        self.step_label = QtWidgets.QLabel("Step (V)", self)
        hbox_step.addWidget(self.step_label)
        self.step_edit = QtWidgets.QLineEdit('0.01', self)  # adjust to update with NSteps
        self.step_edit.setFixedWidth(120)
        hbox_step.addWidget(self.step_edit)
        vbox3_source.addLayout(hbox_step)

        hbox_reps = QtWidgets.QHBoxLayout()
        self.reps_label = QtWidgets.QLabel("Repetitions", self)
        hbox_reps.addWidget(self.reps_label)
        self.reps_edit = QtWidgets.QLineEdit('5', self)
        self.reps_edit.setFixedWidth(120)
        hbox_reps.addWidget(self.reps_edit)
        vbox3_source.addLayout(hbox_reps)
        hbox_source.addLayout(vbox3_source)

        vbox4_source = QtWidgets.QVBoxLayout()
        vbox4_source.addStretch(1)
        hbox_nstep = QtWidgets.QHBoxLayout()
        self.nstep_label = QtWidgets.QLabel("# Steps", self)
        hbox_nstep.addWidget(self.nstep_label)
        self.nstep_edit = QtWidgets.QLineEdit('142', self)  # adjust to update with NSteps
        self.nstep_edit.setFixedWidth(120)
        hbox_nstep.addWidget(self.nstep_edit)
        vbox4_source.addLayout(hbox_nstep)

        self.source_label = QtWidgets.QLabel("Keithley 2400", self)
        vbox4_source.addWidget(self.source_label)
        hbox_source.addLayout(vbox4_source)
        hbox_source.addStretch(1)
        self.source_group_box.setLayout(hbox_source)
        hbox_bottom.addWidget(self.source_group_box, 5)


        self.measure_group_box = QtWidgets.QGroupBox('Measure')
        vbox_measure = QtWidgets.QVBoxLayout()

        hbox_meas_pars = QtWidgets.QHBoxLayout()
        vbox_meas_pars1 = QtWidgets.QVBoxLayout()
        self.current_cb = QtWidgets.QCheckBox('Current', self)
        self.current_cb.setChecked(True)
        vbox_meas_pars1.addWidget(self.current_cb)
        self.power_cb = QtWidgets.QCheckBox('Power', self)
        self.power_cb.setChecked(True)
        vbox_meas_pars1.addWidget(self.power_cb)
        self.temperature_cb = QtWidgets.QCheckBox('Temperature', self)
        self.temperature_cb.setChecked(True)
        vbox_meas_pars1.addWidget(self.temperature_cb)
        hbox_meas_pars.addLayout(vbox_meas_pars1)

        vbox_meas_pars2 = QtWidgets.QVBoxLayout()
        self.voltage_cb = QtWidgets.QCheckBox('Voltage', self)
        self.voltage_cb.setChecked(True)
        vbox_meas_pars2.addWidget(self.voltage_cb)
        self.resistance_cb = QtWidgets.QCheckBox('Resistance', self)
        self.resistance_cb.setChecked(True)
        vbox_meas_pars2.addWidget(self.resistance_cb)
        self.diodes_cb = QtWidgets.QCheckBox('Diodes', self)
        self.diodes_cb.setChecked(True)
        vbox_meas_pars2.addWidget(self.diodes_cb)
        hbox_meas_pars.addLayout(vbox_meas_pars2)
        hbox_meas_pars.addStretch(1)
        vbox_measure.addLayout(hbox_meas_pars)
        vbox_measure.addStretch(1)

        hbox_folder = QtWidgets.QHBoxLayout()
        self.folder_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'folder.png')), '')
        self.folder_button.clicked.connect(self.folder_dialog)
        self.folder_button.setToolTip('Choose folder')
        hbox_folder.addWidget(self.folder_button)
        self.folder_edit = QtWidgets.QLineEdit('\\..', self)
        self.folder_edit.setFixedWidth(180)
        self.folder_edit.setDisabled(True)
        hbox_folder.addWidget(self.folder_edit)
        vbox_measure.addLayout(hbox_folder)
        self.measure_group_box.setLayout(vbox_measure)
        hbox_bottom.addWidget(self.measure_group_box, 2)
        vbox_total.addLayout(hbox_bottom, 1)

        self.setLayout(vbox_total)

        self.mes = sensor.ArduinoSensor(dt=0.25, t=10.0)
        self.register(self.mes)
        self.mes.update.emit()

    def register(self, mes):
        self.mes = mes
        self.mes.update.connect(self.update)

    def update(self):
        if not self.mes:
            return
        self.mes.plot(self.iv_canvas.figure, chs=['temp'])
        self.update_plt.emit()

    def folder_dialog(self):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def pause(self):
        pass