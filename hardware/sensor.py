import collections
from PyQt5 import QtCore
import serial
import struct
import threading
import time

import helper_classes.conversions as conversions


class ArduinoSensor(QtCore.QObject):
    update = QtCore.pyqtSignal()

    def __init__(self, port='COM3', baud=38400, n_data_points=100, data_num_bytes=2, n_ai=5, timeout=30.0,
                 query_period=0.25):
        super(ArduinoSensor, self).__init__()
        self.port = port
        self.baud_rate = baud
        self.query_period = query_period
        self.n_data_points = n_data_points
        self.data_num_bytes = data_num_bytes
        if self.data_num_bytes == 2:
            self.data_type = 'h'  # 2 byte integer
        elif self.data_num_bytes == 4:
            self.data_type = 'f'  # 4 byte float
        self.n_ai = n_ai  # number of analogue inputs
        self.timeout = timeout
        self.raw_data = bytearray(self.n_ai * data_num_bytes)
        self.data = []
        self.times = []
        for i in range(self.n_ai):  # give an array for each type of data and store them in a list
            self.data.append(collections.deque([0] * self.n_data_points, maxlen=self.n_data_points))
            self.times.append(collections.deque([0.1] * self.n_data_points, maxlen=self.n_data_points))

        self.update_timer = 0
        self.is_run = True
        self.is_receiving = False
        self.serial_thread = None
        self.serialConnection = None

    def read_serial_start(self):
        if self.serial_thread is None:
            self.serial_thread = threading.Thread(target=self.background_thread)
            self.serial_thread.start()
            # Block till we start receiving values
            while not self.is_receiving:
                time.sleep(0.1)

    def config_sensor(self):
        print('Trying to connect to: ' + str(self.port) + ' at ' + str(self.baud_rate) + ' BAUD.')
        if str(self.port) == 'dummy':
            return
        try:
            self.serialConnection = serial.Serial(self.port, self.baud_rate, timeout=4)
            print('Connected to ' + str(self.port) + ' at ' + str(self.baud_rate) + ' BAUD.')
        except serial.serialutil.SerialException:
            print("Failed to connect with " + str(self.port) + ' at ' + str(self.baud_rate) + ' BAUD.')
            self.port = 'dummy'
            return
        self.serialConnection.reset_input_buffer()

    def get_serial_data(self, plt_number):
        self.times[plt_number].append(time.time())
        data = self.raw_data[(plt_number * self.data_num_bytes):(self.data_num_bytes +
                                                                 plt_number * self.data_num_bytes)]
        value,  = struct.unpack(self.data_type, data)
        if plt_number == 0:
            value = conversions.voltage_to_temperature(conversions.digital_to_voltage(value, bits=10))
        else:
            value = conversions.voltage_to_power(conversions.digital_to_voltage(value, bits=10))
        self.data[plt_number].append(value)    # we get the latest data point and append it to our array
        return [list(self.times[plt_number]), list(self.data[plt_number])]

    def background_thread(self):  # retrieve data
        time.sleep(1.0)  # give some buffer time for retrieving data
        self.config_sensor()
        while self.is_run:
            if str(self.port) == 'dummy':
                self.is_receiving = True
            else:
                self.serialConnection.readinto(self.raw_data)
                if (time.time() - self.update_timer) > self.query_period:
                    self.update.emit()
                    self.update_timer = time.time()
                self.is_receiving = True

    def close(self):
        self.is_run = False
        if self.serial_thread is not None:
            self.serial_thread.join()
        if not str(self.port) == 'dummy':
            self.serialConnection.close()
            print('Disconnected serial port...')

    def get_sensor_latest(self):
        if not self.port == 'dummy':
            sensor_readout = [self.get_serial_data(i)[1][-1] for i in range(self.n_ai)]
        else:
            sensor_readout = [-1.0 for _ in range(self.n_ai)]
        return sensor_readout

    def get_sensor_traces(self):
        if not self.port == 'dummy':
            sensor_traces = [self.get_serial_data(i) for i in range(self.n_ai)]
        else:
            sensor_traces = [[list(range(self.n_data_points)), [0] * self.n_data_points] for _ in range(self.n_ai)]
        return sensor_traces
