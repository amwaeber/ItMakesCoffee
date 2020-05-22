from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5 import QtWidgets, QtCore
import time


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

        self.plot(target_fig=self.temperature_canvas.figure, chs=['temp'])
        self.plot(target_fig=self.power_canvas.figure, chs=['power'])
        self.update_plt.emit()

    @QtCore.pyqtSlot(list)
    def update(self, sensor_traces):
        time.sleep(0.01)
        self.plot(target_fig=self.temperature_canvas.figure, chs=['temp'], data=sensor_traces)
        self.plot(target_fig=self.power_canvas.figure, chs=['power'], data=sensor_traces)
        self.update_plt.emit()

    @staticmethod
    def plot(target_fig=None, chs=None, data=None):
        if target_fig is None:
            fig = Figure()
        else:
            fig = target_fig
        if chs is None:
            chs = []
        if data is None:
            data = [[list(range(100)), [0] * 100] for _ in range(5)]

        fig.clear()
        axis = fig.add_subplot(111)
        if 'temp' in chs:
            axis.set_xlabel("Time (s)")
            axis.set_ylabel("Temperature (C)")
            xval, yval = data[0]
            axis.plot(xval, yval, lw=1.3)
        if 'power' in chs:
            axis.set_xlabel("Time (s)")
            axis.set_ylabel("Illumination (W/m2)")
            for i in [1, 2, 3, 4]:
                xval, yval = data[i]
                axis.plot(xval, yval, lw=1.3)
        return fig
