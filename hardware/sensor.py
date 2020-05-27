from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from PyQt5 import QtCore
import threading
import time

from hardware.arduino_ai import SerialRead


class ArduinoSensor(QtCore.QObject):
    update = QtCore.pyqtSignal()
    to_log = QtCore.pyqtSignal(str)

    def __init__(self, port='COM3', baud=38400, n_data_points=100, data_num_bytes=2, n_ai=5, timeout=30.0,
                 query_period=0.25):
        super(ArduinoSensor, self).__init__()
        self.port = port
        self.baud_rate = baud
        self.query_period = query_period
        self.n_data_points = n_data_points
        self.data_num_bytes = data_num_bytes
        self.n_ai = n_ai  # number of analogue inputs
        self.timeout = timeout
        self.abort = threading.Event()
        self.abort.clear()
        self.ser = None
        self.mes_thread = None

    def start(self):
        if self.mes_thread is None:
            self.mes_thread = threading.Thread(target=self.run)
            self.mes_thread.start()
        else:
            print('Warning: self.thread already existing.')

    def stop(self):
        if self.mes_thread is not None:
            self.abort.set()
            self.mes_thread.join(self.timeout)
            if not self.mes_thread.is_alive():
                del self.mes_thread
            else:
                print('Warning: failed to stop measurement.')

    def run(self):
        """
        run - main loop for sensor acquisition. This function is started in a thread by start()
        do not call directly, since it will then block the main loop
        """
        self.ser = SerialRead(self.port, self.baud_rate, self.n_data_points, self.data_num_bytes, self.n_ai)
        self.ser.to_log.connect(self.log_pipeline)
        self.ser.connect()
        self.ser.read_serial_start()
        while not self.abort.isSet():
            time.sleep(self.query_period)
            self.update.emit()
        self.ser.close()

    @QtCore.pyqtSlot(str)
    def log_pipeline(self, string):
        self.to_log.emit(string)

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
        else:
            fig = target_fig
        fig.clear()
        axis = fig.add_subplot(111)
        if 'temp' in chs:
            axis.set_xlabel("Time (s)")
            axis.set_ylabel("Temperature (C)")
            if self.ser is None:
                xval, yval = range(self.n_data_points), [0] * self.n_data_points
            else:
                xval, yval, _ = self.ser.get_serial_data(0)
                yval = yval * 100
            axis.plot(xval, yval, lw=1.3)
        if 'power' in chs:
            axis.set_xlabel("Time (s)")
            axis.set_ylabel("Illumination (W/m2)")
            for i in [1, 2, 3, 4]:
                if self.ser is None:
                    xval, yval = range(self.n_data_points), [0] * self.n_data_points
                else:
                    xval, yval, _ = self.ser.get_serial_data(i)
                axis.plot(xval, yval, lw=1.3)
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
            sensor_readout = [self.ser.get_serial_data(i)[2] for i in range(self.n_ai)]
        else:
            sensor_readout = [-1.0 for _ in range(self.n_ai)]
        return sensor_readout
