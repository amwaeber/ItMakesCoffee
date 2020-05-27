# import collections
# from PyQt5 import QtCore
# import serial
# import struct
# import threading
# import time
#
# import helper_classes.conversions as conversions
#
#
# class ArduinoSensor(QtCore.QObject):
#     update = QtCore.pyqtSignal()
#
#     def __init__(self, port='COM3', baud=38400, n_data_points=100, data_num_bytes=2, n_ai=5, timeout=30.0,
#                  query_period=0.25):
#         super(ArduinoSensor, self).__init__()
#         self.port = port
#         self.baud_rate = baud
#         self.query_period = query_period
#         self.n_data_points = n_data_points
#         self.data_num_bytes = data_num_bytes
#         if self.data_num_bytes == 2:
#             self.data_type = 'h'  # 2 byte integer
#         elif self.data_num_bytes == 4:
#             self.data_type = 'f'  # 4 byte float
#         self.n_ai = n_ai  # number of analogue inputs
#         self.timeout = timeout
#         self.raw_data = bytearray(self.n_ai * data_num_bytes)
#         self.data = []
#         self.times = []
#         for i in range(self.n_ai):  # give an array for each type of data and store them in a list
#             self.data.append(collections.deque([0] * self.n_data_points, maxlen=self.n_data_points))
#             self.times.append(collections.deque([0.1] * self.n_data_points, maxlen=self.n_data_points))
#
#         self.update_timer = 0
#         self.is_run = True
#         self.is_receiving = False
#         self.serial_thread = None
#         self.serialConnection = None
#
#     def read_serial_start(self):
#         if self.serial_thread is None:
#             self.serial_thread = threading.Thread(target=self.background_thread)
#             self.serial_thread.start()
#             # Block till we start receiving values
#             while not self.is_receiving:
#                 time.sleep(0.1)
#
#     def config_sensor(self):
#         print('Trying to connect to: ' + str(self.port) + ' at ' + str(self.baud_rate) + ' BAUD.')
#         if str(self.port) == 'dummy':
#             return
#         try:
#             self.serialConnection = serial.Serial(self.port, self.baud_rate, timeout=4)
#             print('Connected to ' + str(self.port) + ' at ' + str(self.baud_rate) + ' BAUD.')
#         except serial.serialutil.SerialException:
#             print("Failed to connect with " + str(self.port) + ' at ' + str(self.baud_rate) + ' BAUD.')
#             self.port = 'dummy'
#             return
#         self.serialConnection.reset_input_buffer()
#
#     def get_serial_data(self, plt_number):
#         self.times[plt_number].append(time.time())
#         data = self.raw_data[(plt_number * self.data_num_bytes):(self.data_num_bytes +
#                                                                  plt_number * self.data_num_bytes)]
#         value,  = struct.unpack(self.data_type, data)
#         if plt_number == 0:
#             value = conversions.voltage_to_temperature(conversions.digital_to_voltage(value, bits=10))
#         else:
#             value = conversions.voltage_to_power(conversions.digital_to_voltage(value, bits=10))
#         self.data[plt_number].append(value)    # we get the latest data point and append it to our array
#         return [list(self.times[plt_number]), list(self.data[plt_number])]
#
#     def background_thread(self):  # retrieve data
#         time.sleep(1.0)  # give some buffer time for retrieving data
#         self.config_sensor()
#         while self.is_run:
#             if str(self.port) == 'dummy':
#                 self.is_receiving = True
#             else:
#                 self.serialConnection.readinto(self.raw_data)
#                 if (time.time() - self.update_timer) > self.query_period:
#                     self.update.emit()
#                     self.update_timer = time.time()
#                 self.is_receiving = True
#
#     def close(self):
#         self.is_run = False
#         if self.serial_thread is not None:
#             self.serial_thread.join()
#         if not str(self.port) == 'dummy':
#             self.serialConnection.close()
#             print('Disconnected serial port...')
#
#     def get_sensor_latest(self):
#         if not self.port == 'dummy':
#             sensor_readout = [self.get_serial_data(i)[1][-1] for i in range(self.n_ai)]
#         else:
#             sensor_readout = [-1.0 for _ in range(self.n_ai)]
#         return sensor_readout
#
#     def get_sensor_traces(self):
#         if not self.port == 'dummy':
#             sensor_traces = [self.get_serial_data(i) for i in range(self.n_ai)]
#         else:
#             sensor_traces = [[list(range(self.n_data_points)), [0] * self.n_data_points] for _ in range(self.n_ai)]
#         return sensor_traces
#
#

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
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
            canvas = FigureCanvas(fig)
        else:
            fig = target_fig
        fig.clear()
        axis = fig.add_subplot(111)
        if 'temp' in chs:
            axis.set_xlabel("Time (s)")
            axis.set_ylabel("Temperature (C)")
            if not hasattr(self, 'ser'):
                xval, yval = range(self.n_data_points), [0] * self.n_data_points
            else:
                xval, yval, _ = self.ser.get_serial_data(0)
                yval = yval * 100
            axis.plot(xval, yval, lw=1.3)
        if 'power' in chs:
            axis.set_xlabel("Time (s)")
            axis.set_ylabel("Diode Readout Voltage (V)")
            for i in [1, 2, 3, 4]:
                if not hasattr(self, 'ser'):
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
            sensor_readout = [self.ser.get_serial_data(i)[1][-1] for i in range(self.n_ai)]
        else:
            sensor_readout = [-1.0 for _ in range(self.n_ai)]
        return sensor_readout

    def get_sensor_traces(self):
        if not self.port == 'dummy':
            sensor_traces = [self.ser.get_serial_data(i) for i in range(self.n_ai)]
        else:
            sensor_traces = [[list(range(self.n_data_points)), [0] * self.n_data_points] for _ in range(self.n_ai)]
        return sensor_traces
