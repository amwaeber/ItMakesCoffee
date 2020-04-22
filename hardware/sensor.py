import matplotlib.animation as animation
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from PyQt5 import QtCore
import serial
import threading
import time

from hardware.arduino_ai import SerialRead

port_name = 'COM3'
baud_rate = 38400
max_data_points = 100
data_num_bytes = 4
n_ai = 5  # number of analogue inputs (eventually 5?)
timeout = 30


class ArduinoSensor(QtCore.QObject):
    update = QtCore.pyqtSignal()

    def __init__(self, dt=10e-1, t=30.0):
        super(QtCore.QObject, self).__init__()
        self.dt = dt
        self.t = t
        self.ai = np.zeros((int(self.t / self.dt) - 1, n_ai))  # analog in data
        self.ci = np.zeros(int(self.t / self.dt) - 1)  # counter in data
        self.abort = threading.Event()
        self.abort.clear()

    def start(self, t=30.0, monitor=None):
        # if monitor is not None:
        #     monitor.register(self)
        if not hasattr(self, 'mes_thread'):
            self.mes_thread = threading.Thread(target=self.run, args=(t, monitor))
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
        self.ser = SerialRead(port_name, baud_rate, max_data_points, data_num_bytes, n_ai)
        self.ser.read_serial_start()
        while not self.abort.isSet():
            time.sleep(self.dt)
            self.update.emit()
        self.ser.close()

        # self.ai = np.zeros((int(self.t / self.dt) - 1, n_ai))  # analog in data
        # self.ser = serial.Serial(port_name, baud_rate, timeout=1)  # Establish the connection on a specific port
        # time.sleep(1)
        # counter = 0
        # while not self.abort.isSet():
        #     b = self.ser.readline()  # read a byte string
        #     string_n = b.decode()  # decode byte string into Unicode
        #     string = string_n.rstrip()  # remove \n and \r
        #     self.ci[counter] = counter
        #     self.ai[counter][0] = float(string)*100  # Celsius
        #     counter = (counter + 1) % self.ci.size  # reset counter to zero
        #     time.sleep(self.dt)
        #     self.update.emit()
        # self.ser.close()

    def plot(self, target_fig=None, fname=None, chs=None):
        """
        plot - plot the result of an ODMR measurement
        if ax is supplied, plot into ax. Create a new figure otherwise
        if ax is none (new figure), the new figure is displayed by default.
        If a filename string fname is given, the figure is saved to this file and display is suppressed
        fname is an absolute path. No check or indexing is performed to prevent overwriting of existing files
        """
        plot_interval = 50

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
            # lines = axis.plot([], [], 'b-')[0]
            # anim = animation.FuncAnimation(fig, self.update_plot, fargs=(lines, 0), interval=plot_interval)
            if not hasattr(self, 'ser'):
                xval, yval = range(max_data_points), [0] * max_data_points
            else:
                xval, yval = self.ser.get_serial_data(0)
                yval = yval * 100
            axis.plot(xval, yval, lw=1.3)
            # spread = (yval.max() - yval.min()) * 100
            # # make sure plotting range is sufficient to display a minimum amount of contrast
            # if spread < 1:
            #     spread = 1
            # upper = yval.max() + .1 * spread
            # lower = yval.min() - .1 * spread
            # # spread = (self.ai[:, 0].max() - self.ai[:, 0].min())
            # # # make sure plotting range is sufficient to display a minimum amount of contrast
            # # if spread < 1:
            # #     spread = 1
            # # upper = self.ai[:, 0].max() + .1 * spread
            # # lower = self.ai[:, 0].min() - .1 * spread
            # axis.set_ylim([lower, upper])
        if 'power' in chs:
            axis.set_xlabel("Time (s)")
            axis.set_ylabel("Diode Voltage (V)")
        #     # style = ['b-', 'r-', 'g-', 'k']
        #     # anim = []
            for i in [1, 2, 3, 4]:
                if not hasattr(self, 'ser'):
                    xval, yval = range(max_data_points), [0] * max_data_points
                else:
                    xval, yval = self.ser.get_serial_data(i)
                axis.plot(xval, yval, lw=1.3)
        #         # lines = axis.plot([], [], style[i])[0]
        #         # anim.append(animation.FuncAnimation(fig, self.update_plot, fargs=(lines, i), interval=plot_interval))
        #     spread = (yval.max() - yval.min())
        #     # make sure plotting range is sufficient to display a minimum amount of contrast
        #     if spread < 0.01:
        #         spread = 0.01
        #     upper = yval.max() + .1 * spread
        #     lower = yval.min() - .1 * spread
        #     # axis.plot(self.ci*self.dt, self.ai[:, 1], lw=1.3)
        #     # axis.plot(self.ci*self.dt, self.ai[:, 2], lw=1.3)
        #     # axis.plot(self.ci*self.dt, self.ai[:, 3], lw=1.3)
        #     # axis.plot(self.ci*self.dt, self.ai[:, 4], lw=1.3)
        #     # spread = (self.ai[:, 1].max()-self.ai[:, 1].min())
        #     # if spread < .01:
        #     #     spread = .01
        #     # upper = self.ci.max() + .1*spread
        #     # lower = self.ci.min() - .1*spread
        #     axis.set_ylim([lower, upper])
        if target_fig is None:
            if fname is not None:
                fig.tight_layout()
                fig.savefig(fname)
                plt.close(fig)
            else:
                fig.show()
        return fig

    def update_plot(self, frame, lines, plt_number):
        xval, yval = self.ser.get_serial_data(plt_number)
        lines.set_data(xval, yval*100)
        spread = (yval.max() - yval.min())*100
        # make sure plotting range is sufficient to display a minimum amount of contrast
        if spread < 1:
            spread = 1
        upper = yval.max() + .1 * spread
        lower = yval.min() - .1 * spread
        # axis.set_ylim([lower, upper])


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
