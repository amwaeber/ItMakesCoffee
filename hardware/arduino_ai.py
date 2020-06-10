import collections
import copy
from PyQt5 import QtCore
import serial
import struct
import threading
import time

import helper_classes.conversions as conversions


class SerialRead(QtCore.QObject):
    to_log = QtCore.pyqtSignal(str)

    def __init__(self, serial_port='COM3', serial_baud=38400, n_data_points=100, data_num_bytes=2, n_ai=5):
        super(SerialRead, self).__init__()
        self.port = serial_port
        self.baud = serial_baud
        self.n_data_points = n_data_points
        self.data_num_bytes = data_num_bytes
        self.n_ai = n_ai
        self.raw_data = bytearray(self.n_ai * self.data_num_bytes)
        self.data_type = None
        if self.data_num_bytes == 2:
            self.data_type = 'h'  # 2 byte integer
        elif self.data_num_bytes == 4:
            self.data_type = 'f'  # 4 byte float
        self.data = []
        self.times = []
        self.init_time = time.time()
        self.private_data = None
        for i in range(self.n_ai):  # give an array for each type of data and store them in a list
            self.data.append(collections.deque([0] * self.n_data_points, maxlen=self.n_data_points))
            self.times.append(collections.deque([0.1] * self.n_data_points, maxlen=self.n_data_points))
        self.is_run = True
        self.is_receiving = False
        self.thread = None
        self.serialConnection = None

    def connect(self):
        if str(self.port) == 'dummy':
            return
        self.to_log.emit('<span style=\" color:#000000;\" >Trying to connect to: ' + str(self.port) + ' at '
                         + str(self.baud) + ' BAUD.</span>')
        try:
            self.serialConnection = serial.Serial(self.port, self.baud, timeout=4)
            self.to_log.emit('<span style=\" color:#32cd32;\" >Connected to ' + str(self.port) + ' at ' +
                             str(self.baud) + ' BAUD.</span>')
        except serial.serialutil.SerialException:
            self.port = 'dummy'
            self.to_log.emit('<span style=\" color:#ff0000;\" >Failed to connect with ' + str(self.port) +
                             ' at ' + str(self.baud) + ' BAUD.</span>')

    def read_serial_start(self):
        if self.thread is None:
            self.thread = threading.Thread(target=self.background_thread)
            self.thread.start()
            # Block till we start receiving values
            while not self.is_receiving:
                time.sleep(0.1)

    def get_serial_data(self, plt_number):
        self.times[plt_number].append(time.time() - self.init_time)
        self.private_data = copy.deepcopy(
            self.raw_data)  # so that the 5 values in our plots will be synchronized to the same sample time
        data = self.private_data[(plt_number * self.data_num_bytes):(self.data_num_bytes +
                                                                     plt_number * self.data_num_bytes)]
        value,  = struct.unpack(self.data_type, data)
        if plt_number == 0:
            value = conversions.voltage_to_temperature(conversions.digital_to_voltage(value, bits=10))
        else:
            value = conversions.voltage_to_power(conversions.digital_to_voltage(value, bits=10))
        self.data[plt_number].append(value)  # we get the latest data point and append it to our array
        return self.times[plt_number], self.data[plt_number], self.data[plt_number][-1]

    def background_thread(self):  # retrieve data
        time.sleep(1.0)  # give some buffer time for retrieving data
        while self.is_run:
            if str(self.port) == 'dummy':
                self.is_receiving = True
            else:
                try:
                    self.serialConnection.reset_input_buffer()
                    self.serialConnection.readinto(self.raw_data)
                    self.is_receiving = True
                except (AttributeError, serial.serialutil.SerialException):
                    self.port = 'dummy'
                    self.is_run = False
                    self.to_log.emit('<span style=\" color:#ff0000;\" >Lost connection to Arduino. Check connection '
                                     'and refresh COM ports.</span>')

    def close(self):
        self.is_run = False
        if self.thread is not None:
            self.thread.join()
        if not str(self.port) == 'dummy':
            self.serialConnection.close()
            self.to_log.emit('<span style=\" color:#000000;\" >Disconnected serial port...</span>')
