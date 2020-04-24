from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from PyQt5 import QtCore
import threading
import time

from hardware.arduino_ai import SerialRead

baud_rate = 38400
max_data_points = 100
data_num_bytes = 2
n_ai = 5  # number of analogue inputs
timeout = 30


class ArduinoSensor(QtCore.QObject):
    update = QtCore.pyqtSignal()

    def __init__(self, port='COM3', dt=10e-1, t=30.0):
        super(QtCore.QObject, self).__init__()
        self.port = port
        self.dt = dt
        self.t = t
        self.ai = np.zeros((int(self.t / self.dt) - 1, n_ai))  # analog in data
        self.ci = np.zeros(int(self.t / self.dt) - 1)  # counter in data
        self.abort = threading.Event()
        self.abort.clear()

    def start(self, t=30.0):
        if not hasattr(self, 'mes_thread'):
            self.mes_thread = threading.Thread(target=self.run, args=(t,))
            self.mes_thread.start()
        else:
            print('Warning: self.thread already existing.')

    def stop(self):
        if hasattr(self, 'mes_thread'):
            self.abort.set()
            self.mes_thread.join(timeout)
            if not self.mes_thread.is_alive():
                del self.mes_thread
            else:
                print('Warning: failed to stop measurement.')

    def run(self, t=30.0):
        """
        run - main loop for sensor acquisition. This function is started in a thread by start()
        do not call directly, since it will then block the main loop
        """
        if not self.port == 'dummy':
            self.ser = SerialRead(self.port, baud_rate, max_data_points, data_num_bytes, n_ai)
            self.ser.read_serial_start()
            while not self.abort.isSet():
                time.sleep(self.dt)
                self.update.emit()
            self.ser.close()
        else:
            pass

    def plot(self, target_fig=None, fname=None, chs=None):
        """
        plot - plot the result of an ODMR measurement
        if ax is supplied, plot into ax. Create a new figure otherwise
        if ax is none (new figure), the new figure is displayed by default.
        If a filename string fname is given, the figure is saved to this file and display is suppressed
        fname is an absolute path. No check or indexing is performed to prevent overwriting of existing files
        """

        if chs is None:
            chs = []
        if target_fig is None:
            fig = Figure()
            canvas = FigureCanvas(fig)
        else:
            fig = target_fig
        fig.clear()
        axis = fig.add_subplot(111)
        if 'temp' in chs:
            axis.set_xlabel("Time (s)")
            axis.set_ylabel("Temperature (C)")
            if not hasattr(self, 'ser') or self.port == 'dummy':
                xval, yval = range(max_data_points), [0] * max_data_points
            else:
                xval, yval, _ = self.ser.get_serial_data(0)
                yval = yval * 100
            axis.plot(xval, yval, lw=1.3)
            # spread = (yval.max() - yval.min()) * 100
            # # make sure plotting range is sufficient to display a minimum amount of contrast
            # if spread < 1:
            #     spread = 1
            # upper = yval.max() + .1 * spread
            # lower = yval.min() - .1 * spread
            # axis.set_ylim([lower, upper])
        if 'power' in chs:
            axis.set_xlabel("Time (s)")
            axis.set_ylabel("Diode Readout Voltage (V)")
            for i in [1, 2, 3, 4]:
                if not hasattr(self, 'ser') or self.port == 'dummy':
                    xval, yval = range(max_data_points), [0] * max_data_points
                else:
                    xval, yval, _ = self.ser.get_serial_data(i)
                axis.plot(xval, yval, lw=1.3)
        #     spread = (yval.max() - yval.min())
        #     # make sure plotting range is sufficient to display a minimum amount of contrast
        #     if spread < 0.01:
        #         spread = 0.01
        #     upper = yval.max() + .1 * spread
        #     lower = yval.min() - .1 * spread
        #     axis.set_ylim([lower, upper])
        if target_fig is None:
            if fname is not None:
                fig.tight_layout()
                fig.savefig(fname)
                plt.close(fig)
            else:
                fig.show()
        return fig

    def get_sensor_latest(self):
        if not self.port == 'dummy':
            sensor_readout = [self.ser.get_serial_data(i)[2] for i in range(5)]
        else:
            sensor_readout = [-1.0 for _ in range(5)]
        return sensor_readout
