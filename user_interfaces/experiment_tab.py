from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5 import QtWidgets, QtGui, QtCore

import hardware.sensor as sensor
from utility.config import paths


class Experiment(QtWidgets.QWidget):
    update_plt = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(Experiment, self).__init__(parent)

        self.iv_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.iv_canvas.figure.tight_layout(pad=0.3)
        self.update_plt.connect(self.iv_canvas.figure.canvas.draw)

        vbox_labels = QtWidgets.QVBoxLayout()
        vbox_edits = QtWidgets.QVBoxLayout()
        self.temperature_label = QtWidgets.QLabel("Temperature (C)", self)
        vbox_labels.addWidget(self.temperature_label)
        self.temperature_edit = QtWidgets.QLineEdit('25', self)
        vbox_edits.addWidget(self.temperature_edit)
        self.diode1_label = QtWidgets.QLabel("Diode 1 (V)", self)
        vbox_labels.addWidget(self.diode1_label)
        self.diode1_edit = QtWidgets.QLineEdit('0.1', self)
        vbox_edits.addWidget(self.diode1_edit)
        self.diode2_label = QtWidgets.QLabel("Diode 2 (V)", self)
        vbox_labels.addWidget(self.diode2_label)
        self.diode2_edit = QtWidgets.QLineEdit('0.1', self)
        vbox_edits.addWidget(self.diode2_edit)
        self.diode3_label = QtWidgets.QLabel("Diode 3 (V)", self)
        vbox_labels.addWidget(self.diode3_label)
        self.diode3_edit = QtWidgets.QLineEdit('0.1', self)
        vbox_edits.addWidget(self.diode3_edit)
        self.diode4_label = QtWidgets.QLabel("Diode 4 (V)", self)
        vbox_labels.addWidget(self.diode4_label)
        self.diode4_edit = QtWidgets.QLineEdit('0.1', self)
        vbox_edits.addWidget(self.diode4_edit)

        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addWidget(self.iv_canvas)
        hbox1.addLayout(vbox_labels)
        hbox1.addLayout(vbox_edits)
        self.setLayout(hbox1)

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
