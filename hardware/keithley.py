import numpy as np
import pandas as pd
import pyqtgraph as pg
from pymeasure.instruments.keithley import Keithley2400
from PyQt5 import QtCore
import pyvisa
import threading
import time


class Keithley(QtCore.QObject):
    update = QtCore.pyqtSignal(int)
    save_settings = QtCore.pyqtSignal()
    restart_sensor = QtCore.pyqtSignal()
    save = QtCore.pyqtSignal(int)
    to_log = QtCore.pyqtSignal(str)
    end_of_experiment = QtCore.pyqtSignal()

    def __init__(self, gpib_port='GPIB::24', n_data_points=100, averages=5, repetitions=1, repetition_delay=2.0,
                 delay=0.25, experiment_delay=1.0, min_voltage=-0.01, max_voltage=0.7, compliance_current=0.5):
        super(Keithley, self).__init__()
        self.gpib_port = gpib_port
        self.n_data_points = n_data_points
        self.averages = averages
        self.repetitions = repetitions
        self.repetition_delay = repetition_delay
        self.delay = delay
        self.experiment_delay = experiment_delay
        self.max_voltage = max_voltage
        self.min_voltage = min_voltage
        self.compliance_current = compliance_current
        self.voltages_set = np.linspace(self.min_voltage, self.max_voltage, num=self.n_data_points)
        self.times = np.zeros_like(self.voltages_set)
        self.voltages = np.zeros_like(self.voltages_set)
        self.currents = np.zeros_like(self.voltages_set)
        self.currents_std = np.zeros_like(self.voltages_set)
        self.resistances = np.zeros_like(self.voltages_set)
        self.powers = np.zeros_like(self.voltages_set)

        self.is_run = True
        # self.is_receiving = False
        self.gpib_thread = None
        self.sourcemeter = None

    def config_keithley(self, **kwargs):
        self.to_log.emit('<span style=\" color:#000000;\" >Trying to connect to: ' + str(self.gpib_port) + '.</span>')
        if str(self.gpib_port) == 'dummy':
            return
        try:
            self.sourcemeter = Keithley2400(str(self.gpib_port))
            self.to_log.emit('<span style=\" color:#32cd32;\" >Connected to ' + str(self.gpib_port) + '.</span>')
        except pyvisa.errors.VisaIOError:
            self.to_log.emit('<span style=\" color:#ff0000;\" >Failed to connect with ' + str(self.gpib_port) +
                             '.</span>')
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

    def read_keithley_start(self):
        self.is_run = True
        # self.is_receiving = False
        if self.gpib_thread is None:
            self.gpib_thread = threading.Thread(target=self.background_thread)
            self.gpib_thread.start()
            # # Block till we start receiving values
            # while not self.is_receiving:
            #     time.sleep(0.1)

    def get_keithley_data(self):
        data = pd.DataFrame({
            'Time (s)': self.times,
            'Voltage (V)': self.voltages,
            'Current (A)': self.currents,
            'Current Std (A)': self.currents_std,
            'Resistance (Ohm)': self.resistances,
            'Power (W)': self.powers})
        return data

    def background_thread(self):  # retrieve data
        time.sleep(1.0)  # give some buffer time for retrieving data
        time.sleep(self.experiment_delay)  # pause between experiments
        self.config_keithley()
        while self.is_run:
            self.save_settings.emit()
            for repetition in range(self.repetitions):
                self.restart_sensor.emit()
                time.sleep(5.0)  # give time for sensor connection to re-establish itself
                if str(self.gpib_port) == 'dummy':
                    for dp in range(self.n_data_points):
                        if not self.is_run:
                            self.to_log.emit('<span style=\" color:#ff0000;\" >Scan aborted.</span>')
                            return
                        time.sleep(self.delay)
                        self.times[dp] = time.time()
                        self.update.emit(dp)
                        # self.is_receiving = True
                else:
                    for dp in range(self.n_data_points):
                        if not self.is_run:
                            self.to_log.emit('<span style=\" color:#ff0000;\" >Scan aborted.</span>')
                            return
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
                        self.update.emit(dp)
                        # self.is_receiving = True
                    self.sourcemeter.source_voltage = 0
                self.save.emit(repetition)
                self.to_log.emit('<span style=\" color:#1e90ff;\" >Finished curve #%s</span>' % str(repetition + 1))
                if repetition < self.repetitions - 1:
                    time.sleep(self.repetition_delay)
                else:
                    self.to_log.emit('<span style=\" color:#32cd32;\" >Finished IV scan.</span>')
            self.is_run = False
        self.end_of_experiment.emit()

    def close(self):
        self.is_run = False
        if self.gpib_thread is not None:
            self.gpib_thread.join()
        if not str(self.gpib_port) == 'dummy':
            self.sourcemeter.shutdown()
            self.to_log.emit('<span style=\" color:#000000;\" >Disconnected Keithley...</span>')

    def line_plot(self, target_line=None):
        if target_line is None:
            graph = pg.PlotWidget()
            target_line = graph.plot()
        if self.gpib_port == 'dummy':
            xval, yval = [], []
        else:
            xval, yval = self.voltages_set, self.currents
        target_line.setData(xval, yval)
