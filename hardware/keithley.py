from pymeasure.instruments.keithley import Keithley2400
import numpy as np
import pandas as pd
import threading
import time



class Keithley:
    def __init__(self, gpib_port='GPIB::24', data_points=100, averages=5, delay=0.25,
                 min_voltage=-0.01, max_voltage=0.7, compliance_current=0.5):
        self.gpib_port = gpib_port
        self.data_points = data_points
        self.averages = averages
        self.delay = delay
        self.max_voltage = max_voltage
        self.min_voltage = min_voltage
        self.compliance_current = compliance_current
        self.voltages_set = np.linspace(self.min_voltage, self.max_voltage, num=self.data_points)
        self.times = np.zeros_like(self.voltages_set)
        self.voltages = np.zeros_like(self.voltages_set)
        self.currents = np.zeros_like(self.voltages_set)
        self.currents_std = np.zeros_like(self.voltages_set)

        self.is_run = True
        self.is_receiving = False
        self.gpib_thread = None

    def config_keithley(self, **kwargs):
        print('Trying to connect to: ' + str(self.gpib_port) + '.')
        try:
            self.sourcemeter = Keithley2400("GPIB::24")
            print('Connected to ' + str(self.gpib_port) + '.')
        except:
            print("Failed to connect with " + str(self.gpib_port) + '.')
        self.sourcemeter.reset()
        self.sourcemeter.use_front_terminals()
        self.sourcemeter.compliance_current = kwargs.get('compliance_current', self.compliance_current)
        self.sourcemeter.measure_current()
        time.sleep(0.1)  # wait here to give the instrument time to react
        self.averages = kwargs.get('averages', self.averages)
        self.sourcemeter.config_buffer(self.averages)
        self.sourcemeter.enable_source()

    def read_keithley_start(self):
        if self.gpib_thread is None:
            self.gpib_thread = threading.Thread(target=self.background_thread)
            self.gpib_thread.start()
            # Block till we start receiving values
            while not self.is_receiving:
                time.sleep(0.1)

    def background_thread(self):  # retrieve data
        time.sleep(1.0)  # give some buffer time for retrieving data
        self.config_keithley()
        while self.is_run:
            for dp in range(self.data_points):
                self.sourcemeter.adapter.write(":TRAC:FEED:CONT NEXT;")
                self.sourcemeter.source_voltage = self.voltages_set[i]
                time.sleep(self.delay)
                self.sourcemeter.start_buffer()
                self.sourcemeter.wait_for_buffer()
                self.times[i] = time.time()
                self.voltages[i] = self.sourcemeter.mean_voltage
                self.currents[i] = - self.sourcemeter.mean_current
                self.currents_std[i] = self.sourcemeter.std_current
                self.is_receiving = True
            self.is_run = False

    def close(self):
        self.is_run = False
        self.gpib_thread.join()
        self.sourcemeter.shutdown()
        print('Disconnected Keithley...')
        # df = pd.DataFrame(self.csvData)
        # df.to_csv('/home/rikisenia/Desktop/data.csv')
        
# Save the data columns in a CSV file
data = pd.DataFrame({
    'Time (s)': times,
    'Voltage (V)': voltages,
    'Current (A)': currents,
    'Current Std (A)': current_stds,
    'Resistance (Ohm)': resistances,
    'Power (W)': powers,
})
data.to_csv('example.csv')

