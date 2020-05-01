from pymeasure.instruments.keithley import Keithley2400
import numpy as np
import pandas as pd
import threading
import time



class KeithleyRead:
    def __init__(self, gpib_port='GPIB::24', data_points=100, averages=5, min_voltage=-0.01, max_voltage=0.7,
                 compliance_current=0.5):
        self.gpib_port = gpib_port
        self.data_points = data_points
        self.averages = averages
        self.max_voltage = max_voltage
        self.min_voltage = min_voltage
        self.compliance_current = compliance_current

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
            self.serialConnection.readinto(self.raw_data)
            self.is_receiving = True


# Allocate arrays to store the measurement results
voltage_set = np.linspace(min_voltage, max_voltage, num=data_points)
times = np.zeros_like(voltage_set)
voltages = np.zeros_like(voltage_set)
currents = np.zeros_like(voltage_set)
current_stds = np.zeros_like(voltage_set)
resistances = np.zeros_like(voltage_set)
powers = np.zeros_like(voltage_set)

# Loop through each current point, measure and record the voltage
for i in range(data_points):
    sourcemeter.adapter.write(":TRAC:FEED:CONT NEXT;")

    sourcemeter.source_voltage = voltage_set[i]
    time.sleep(0.25)
    sourcemeter.start_buffer()
    sourcemeter.wait_for_buffer()

    # Record the average and standard deviation
    times[i] = time.time()
    voltages[i] = sourcemeter.mean_voltage
    currents[i] = - sourcemeter.mean_current
    current_stds[i] = sourcemeter.std_current
    resistances[i] = abs(voltages[i] / currents[i])
    powers[i] = abs(voltages[i] * currents[i])

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

sourcemeter.shutdown()
