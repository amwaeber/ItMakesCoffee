import numpy as np
from PyQt5 import QtCore
import serial
import threading
import time

port = 'COM3'
timeout = 30
n_ai = 1  # number of analogue inputs (eventually 5?)


class ArduinoSensor(QtCore.QObject):

    def __init__(self, dt=10e-1, t=30.0):
        super(QtCore.QObject, self).__init__()
        self.dt = dt
        self.t = t
        self.ai = np.zeros((int(self.t / self.dt) - 1, n_ai))  # analog in data
        self.ci = np.zeros(int(self.t / self.dt) - 1)  # counter in data
        self.abort = threading.Event()
        self.abort.clear()

    def start(self, t=30.0, mode='confocal', monitor=None, run_ai=False):
        # if monitor is not None:
        #     monitor.register(self)
        if not hasattr(self, 'mes_thread'):
            self.mes_thread = threading.Thread(target=self.run, args=(t, mode, monitor, run_ai))
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

    def run(self, t=30.0, mode='confocal', monitor=None, run_ai=False):
        """
        run - main loop for sensor acquisition. This function is started in a thread by start()
        do not call directly, since it will then block the main loop
        """
        self.ai = np.zeros((int(self.t / self.dt) - 1, n_ai))  # analog in data
        self.ser = serial.Serial('COM3', 9600, timeout=1)  # Establish the connection on a specific port
        time.sleep(1)
        counter = 0
        while not self.abort.isSet():
            b = self.ser.readline()  # read a byte string
            string_n = b.decode()  # decode byte string into Unicode
            string = string_n.rstrip()  # remove \n and \r
            self.ci[counter] = counter
            self.ai[0][counter] = float(string)
            counter = (counter + 1) % self.ci.size  # reset counter to zero
            time.sleep(0.1)
        self.ser.close()




# def sensor_readout(t_plot=10):
#     ser = serial.Serial('COM3', 9600, timeout=1)  # Establish the connection on a specific port
#     time.sleep(2)
#     delay = 0.1  # s
#     for i in range(int(t_plot/delay)):
#         b = ser.readline()  # read a byte string
#         string_n = b.decode()  # decode byte string into Unicode
#         string = string_n.rstrip()  # remove \n and \r
#         flt = float(string)  # convert string to float
#         print(flt)
#         time.sleep(0.1)
