from PyQt5 import QtCore
import pyqtgraph as pg
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

    def line_plot(self, target_line=None, channel=None):
        if target_line is None:
            graph = pg.PlotWidget()
            target_line = graph.plot()
        if self.ser is None:
            xval, yval = list(range(self.n_data_points)), [0] * self.n_data_points
        elif channel == 'temp':
            xval, yval, _ = self.ser.get_serial_data(0)
            yval = yval * 100
        elif channel == 'power1':
            xval, yval, _ = self.ser.get_serial_data(1)
        elif channel == 'power2':
            xval, yval, _ = self.ser.get_serial_data(2)
        elif channel == 'power3':
            xval, yval, _ = self.ser.get_serial_data(3)
        elif channel == 'power4':
            xval, yval, _ = self.ser.get_serial_data(4)
        else:
            xval, yval = list(range(self.n_data_points)), [0] * self.n_data_points
        target_line.setData(xval, yval)

    def get_sensor_latest(self):
        if not self.port == 'dummy':
            sensor_readout = [self.ser.get_serial_data(i)[2] for i in range(self.n_ai)]
        else:
            sensor_readout = [-1.0 for _ in range(self.n_ai)]
        return sensor_readout
