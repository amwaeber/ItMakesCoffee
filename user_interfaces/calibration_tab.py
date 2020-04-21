from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import os
from PyQt5 import QtWidgets, QtGui, QtCore

import hardware.sensor as sensor
from utility.config import paths


class Calibration(QtWidgets.QWidget):
    update_plt = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(Calibration, self).__init__(parent)

        self.temperature_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.temperature_canvas.figure.tight_layout(pad=0.3)
        self.update_plt.connect(self.temperature_canvas.figure.canvas.draw)
        self.power_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.power_canvas.figure.tight_layout(pad=0.3)
        self.update_plt.connect(self.power_canvas.figure.canvas.draw)

        self.start_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'start.png')), '')
        self.start_button.clicked.connect(self.start)
        self.start_button.setToolTip('Run acquisition')
        self.stop_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'stop.png')), '')
        self.stop_button.clicked.connect(self.stop)
        self.stop_button.setToolTip('Stop acquisition')

        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addWidget(self.temperature_canvas)
        hbox1.addWidget(self.power_canvas)
        hbox2 = QtWidgets.QHBoxLayout()
        hbox2.addWidget(self.start_button)
        hbox2.addWidget(self.stop_button)
        hbox2.addStretch(1)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        self.setLayout(vbox)

        self.mes = sensor.ArduinoSensor(dt=0.25, t=10.0)
        self.register(self.mes)
        self.mes.update.emit()

    def register(self, mes):
        self.mes = mes
        self.mes.update.connect(self.update)

    def update(self):
        if not self.mes:
            return
        self.mes.plot(self.temperature_canvas.figure, chs=['temp'])
        self.mes.plot(self.power_canvas.figure, chs=['power'])
        self.update_plt.emit()

    def start(self):
        if self.mes:
            self.mes.stop()
        self.mes = sensor.ArduinoSensor(dt=0.25, t=10.0)
        self.register(self.mes)
        self.mes.start(t=10.0)

    def stop(self):
        if self.mes:
            self.mes.stop()
