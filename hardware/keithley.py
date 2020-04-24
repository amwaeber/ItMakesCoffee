from pymeasure.instruments.keithley import Keithley2400
import numpy as np
import pandas as pd
from time import sleep

# Set the input parameters
data_points = 142
averages = 5
max_voltage = 0.7
min_voltage = -0.01

# Connect and configure the instrument
sourcemeter = Keithley2400("GPIB::24")
sourcemeter.reset()
sourcemeter.use_front_terminals()
sourcemeter.compliance_current = 0.5
sourcemeter.measure_current()
sleep(0.1)  # wait here to give the instrument time to react
sourcemeter.config_buffer(averages)

# Allocate arrays to store the measurement results
voltages = np.linspace(min_voltage, max_voltage, num=data_points)
currents = np.zeros_like(voltages)
current_stds = np.zeros_like(voltages)
resistance = np.zeros_like(voltages)
resistance_stds = np.zeros_like(voltages)

sourcemeter.enable_source()

# Loop through each current point, measure and record the voltage
for i in range(data_points):
    # if i > 0:
    #     sourcemeter.reset_buffer()
    sourcemeter.source_voltage = voltages[i]
    sleep(0.25)
    sourcemeter.start_buffer()
    # else:
    #     sourcemeter.reset_buffer()
    sourcemeter.wait_for_buffer()

    # Record the average and standard deviation
    _, currents[i], resistance[i] = sourcemeter.means
    _, current_stds[i], resistance_stds[i] = sourcemeter.standard_devs

    print(sourcemeter.means)
    sourcemeter.reset_buffer()
    # sourcemeter.adapter.write(":STAT:PRES;")
    # sourcemeter.adapter.write("*CLS;")
    # sourcemeter.adapter.write(":TRAC:CLEAR;")
    # sourcemeter.adapter.write(":TRAC:FEED:CONT NEXT;")


# Save the data columns in a CSV file
data = pd.DataFrame({
    'Voltage (V)': voltages,
    'Current (A)': currents,
    'Current Std (A)': current_stds,
    'Resistance (Ohm)': resistance,
    'Resistance Std (Ohm)': resistance_stds,
})
data.to_csv('example.csv')

sourcemeter.shutdown()
