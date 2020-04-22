import collections
import copy
import serial
import struct
import threading
import time


class SerialRead:
    def __init__(self, serial_port='COM3', serial_baud=38400, read_length=100, data_num_bytes=2, num_plots=5):
        self.port = serial_port
        self.baud = serial_baud
        self.plot_max_length = read_length
        self.data_num_bytes = data_num_bytes
        self.num_plots = num_plots
        self.raw_data = bytearray(num_plots * data_num_bytes)
        self.data_type = None
        if data_num_bytes == 2:
            self.data_type = 'h'  # 2 byte integer
        elif data_num_bytes == 4:
            self.data_type = 'f'  # 4 byte float
        self.data = []
        self.times = []
        self.private_data = None
        for i in range(num_plots):  # give an array for each type of data and store them in a list
            self.data.append(collections.deque([0] * read_length, maxlen=read_length))
            self.times.append(collections.deque([0.1] * read_length, maxlen=read_length))
        self.start_time = time.time()
        self.is_run = True
        self.is_receiving = False
        self.thread = None
        self.plot_timer = 0
        self.previous_timer = 0
        # self.csvData = []

        print('Trying to connect to: ' + str(serial_port) + ' at ' + str(serial_baud) + ' BAUD.')
        try:
            self.serialConnection = serial.Serial(serial_port, serial_baud, timeout=4)
            print('Connected to ' + str(serial_port) + ' at ' + str(serial_baud) + ' BAUD.')
        except:
            print("Failed to connect with " + str(serial_port) + ' at ' + str(serial_baud) + ' BAUD.')

    def read_serial_start(self):
        if self.thread is None:
            self.thread = threading.Thread(target=self.background_thread)
            self.thread.start()
            # Block till we start receiving values
            while not self.is_receiving:
                time.sleep(0.1)

    def get_serial_data(self, plt_number):
        current_time = time.time() - self.start_time
        self.times[plt_number].append(current_time)
        self.private_data = copy.deepcopy(
            self.raw_data)  # so that the 5 values in our plots will be synchronized to the same sample time
        data = self.private_data[(plt_number * self.data_num_bytes):(self.data_num_bytes +
                                                                     plt_number * self.data_num_bytes)]
        value,  = struct.unpack(self.data_type, data)
        if plt_number == 0:
            value = value / 1024. * 5 * 100  # convert to celsius (10mV = 1C)
        else:
            value = value / 1024. * 5  # convert to voltage
        self.data[plt_number].append(value)    # we get the latest data point and append it to our array
        return self.times[plt_number], self.data[plt_number]
        # self.csvData.append([self.data[0][-1], self.data[1][-1], self.data[2][-1]])

    def background_thread(self):  # retrieve data
        time.sleep(1.0)  # give some buffer time for retrieving data
        self.serialConnection.reset_input_buffer()
        self.start_time = time.time()
        while self.is_run:
            self.serialConnection.readinto(self.raw_data)
            self.is_receiving = True

    def close(self):
        self.is_run = False
        self.thread.join()
        self.serialConnection.close()
        print('Disconnected...')
        # df = pd.DataFrame(self.csvData)
        # df.to_csv('/home/rikisenia/Desktop/data.csv')