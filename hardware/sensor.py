from PyQt5 import QtCore
import serial
import threading
from time import sleep

timeout = 30


class ArduinoSensor(QtCore.QObject):

    def __init__(self, dt=10e-1, t=30.0):
        super(QtCore.QObject, self).__init__()
        self.dt = dt
        self.t = t
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









def sensor_readout(t_plot=10):
    ser = serial.Serial('COM3', 9600, timeout=1) # Establish the connection on a specific port
    delay = 0.1  # s

counter = 32 # Below 32 everything in ASCII is gibberish
while True:
    counter +=1
    print(ser.readline()) # Read the newest output from the Arduino
    sleep(.1) # Delay for one tenth of a second
    if counter == 255:
        counter = 32

