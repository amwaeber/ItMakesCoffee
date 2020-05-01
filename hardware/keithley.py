from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pymeasure.instruments.keithley import Keithley2400
from PyQt5 import QtCore
import threading
import time


class Keithley(QtCore.QObject):
    update = QtCore.pyqtSignal()
    save = QtCore.pyqtSignal()

    def __init__(self, gpib_port='GPIB::24', data_points=100, averages=5, repetitions=1, delay=0.25,
                 min_voltage=-0.01, max_voltage=0.7, compliance_current=0.5):
        super(Keithley, self).__init__()
        self.gpib_port = gpib_port
        self.data_points = data_points
        self.averages = averages
        self.repetitions = repetitions
        self.delay = delay
        self.max_voltage = max_voltage
        self.min_voltage = min_voltage
        self.compliance_current = compliance_current
        self.voltages_set = np.linspace(self.min_voltage, self.max_voltage, num=self.data_points)
        self.times = np.zeros_like(self.voltages_set)
        self.voltages = np.zeros_like(self.voltages_set)
        self.currents = np.zeros_like(self.voltages_set)
        self.currents_std = np.zeros_like(self.voltages_set)
        self.resistances = np.zeros_like(self.voltages_set)
        self.powers = np.zeros_like(self.voltages_set)

        self.is_run = True
        self.is_receiving = False
        self.gpib_thread = None

    def config_keithley(self, **kwargs):
        print('Trying to connect to: ' + str(self.gpib_port) + '.')
        if str(self.gpib_port) == 'dummy':
            return
        try:
            self.sourcemeter = Keithley2400(str(self.gpib_port))
            print('Connected to ' + str(self.gpib_port) + '.')
        except:
            print("Failed to connect with " + str(self.gpib_port) + '.')
            self.gpib_port = 'dummy'
            return
        self.sourcemeter.reset()
        self.sourcemeter.use_front_terminals()
        self.sourcemeter.compliance_current = kwargs.get('compliance_current', self.compliance_current)
        self.sourcemeter.measure_current()
        time.sleep(0.1)  # wait here to give the instrument time to react
        self.averages = kwargs.get('averages', self.averages)
        self.sourcemeter.config_buffer(self.averages)
        self.sourcemeter.enable_source()

    def read_keithley_start(self, repetitions=1):
        self.repetitions = repetitions
        for repetition in range(self.repetitions):
            self.is_run = True
            self.is_receiving = False
            if self.gpib_thread is None:
                self.gpib_thread = threading.Thread(target=self.background_thread, args=(repetition,))
                self.gpib_thread.start()
                # Block till we start receiving values
                while not self.is_receiving:
                    time.sleep(0.1)

    def get_keithley_data(self):
        data = pd.DataFrame({
            'Time (s)': self.times,
            'Voltage (V)': self.voltages,
            'Current (A)': self.currents,
            'Current Std (A)': self.currents_std,
            'Resistance (Ohm)': self.resistances,
            'Power (W)': self.powers})
        return data

    def background_thread(self, repetition=0):  # retrieve data
        time.sleep(1.0)  # give some buffer time for retrieving data
        self.config_keithley()
        while self.is_run:
            if str(self.gpib_port) == 'dummy':
                self.is_receiving = True
            else:
                for dp in range(self.data_points):
                    self.sourcemeter.adapter.write(":TRAC:FEED:CONT NEXT;")
                    self.sourcemeter.source_voltage = self.voltages_set[dp]
                    time.sleep(self.delay)
                    self.sourcemeter.start_buffer()
                    self.sourcemeter.wait_for_buffer()
                    self.times[dp] = time.time()
                    self.voltages[dp] = self.sourcemeter.mean_voltage
                    self.currents[dp] = - self.sourcemeter.mean_current
                    self.currents_std[dp] = self.sourcemeter.std_current
                    self.resistances[dp] = abs(self.voltages[dp] / self.currents[dp])
                    self.powers[dp] = abs(self.voltages[dp] * self.currents[dp])
                    self.update.emit()
                    self.is_receiving = True
            self.is_run = False
        self.close(repetition)

    def close(self, repetition=0):
        self.is_run = False
        self.gpib_thread.join()
        if not str(self.gpib_port) == 'dummy':
            self.sourcemeter.shutdown()
            print('Disconnected Keithley...')
        self.save.emit(repetition)
        # df = pd.DataFrame(self.csvData)
        # data.to_csv('example.csv')

    def plot(self, target_fig=None, fname=None):
        """
        plot - plot the result of an IV measurement
        if ax is supplied, plot into ax. Create a new figure otherwise
        if ax is none (new figure), the new figure is displayed by default.
        If a filename string fname is given, the figure is saved to this file and display is suppressed
        fname is an absolute path. No check or indexing is performed to prevent overwriting of existing files
        """

        if target_fig is None:
            fig = Figure()
            canvas = FigureCanvas(fig)
        else:
            fig = target_fig
        fig.clear()
        axis = fig.add_subplot(111)
        axis.set_xlabel("Voltage (V)")
        axis.set_ylabel("Current (A)")
        if self.gpib_port == 'dummy':
            xval = self.voltages_set
            yval = [0] * self.data_points
        else:
            xval = self.voltages
            yval = self.currents
        axis.plot(xval, yval, lw=1.3)
        # spread = (yval.max() - yval.min()) * 100
        # # make sure plotting range is sufficient to display a minimum amount of contrast
        # if spread < 1:
        #     spread = 1
        # upper = yval.max() + .1 * spread
        # lower = yval.min() - .1 * spread
        # axis.set_ylim([lower, upper])
        if target_fig is None:
            if fname is not None:
                fig.tight_layout()
                fig.savefig(fname)
                plt.close(fig)
            else:
                fig.show()
        return fig
