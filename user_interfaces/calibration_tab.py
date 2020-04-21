from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5 import QtWidgets, QtGui, QtCore


class Calibration(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(Calibration, self).__init__(parent)

