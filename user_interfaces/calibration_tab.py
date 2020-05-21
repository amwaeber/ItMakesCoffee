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

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.temperature_canvas)
        hbox.addWidget(self.power_canvas)
        self.setLayout(hbox)

        self.mes = sensor.ArduinoSensor(port="COM3", query_period=0.25)
        self.register(self.mes)
        self.mes.update.emit()

    def register(self, mes):
        self.mes = mes
        self.mes.update[list, list].connect(self.update)

    @QtCore.pyqtSlot(list, list)
    def update(self, times, data):
        if not self.mes:
            return
        self.mes.plot(self.temperature_canvas.figure, chs=['temp'])
        self.mes.plot(self.power_canvas.figure, chs=['power'])
        self.update_plt.emit()

    def start(self):
        if self.mes:
            self.mes.close()
        self.mes = sensor.ArduinoSensor(port="COM3", query_period=0.25)
        self.register(self.mes)
        self.mes.read_serial_start()

    def stop(self):
        if self.mes:
            self.mes.close()
