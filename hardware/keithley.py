from pymeasure.instruments.keithley import Keithley2400
import numpy as np
import pandas as pd
import time

# Set the input parameters
data_points = 20
averages = 5
max_voltage = 0.7
min_voltage = -0.01

# Connect and configure the instrument
sourcemeter = Keithley2400("GPIB::24")
sourcemeter.reset()
sourcemeter.use_front_terminals()
sourcemeter.compliance_current = 0.5
sourcemeter.measure_current()
time.sleep(0.1)  # wait here to give the instrument time to react
sourcemeter.config_buffer(averages)

# Allocate arrays to store the measurement results
voltage_set = np.linspace(min_voltage, max_voltage, num=data_points)
times = np.zeros_like(voltage_set)
voltages = np.zeros_like(voltage_set)
currents = np.zeros_like(voltage_set)
current_stds = np.zeros_like(voltage_set)
resistances = np.zeros_like(voltage_set)
powers = np.zeros_like(voltage_set)

sourcemeter.enable_source()

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
