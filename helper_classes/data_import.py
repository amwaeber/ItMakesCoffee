import numpy as np
import os
import pandas as pd
import time

from utility import folder_functions


class Experiment:
    def __init__(self, folder_path='.'):
        self.folder_path = os.path.normpath(folder_path)
        self.name = os.path.basename(folder_path)
        try:
            with open(os.path.join(folder_path, 'Settings.txt')) as f:
                self.time = f.readline().strip('\n')
        except FileNotFoundError:
            self.time = folder_functions.get_datetime(folder_path)
        self.n_traces = folder_functions.get_number_of_csv(folder_path)
        self.traces = {}
        for trace in range(self.n_traces):
            key = 'IV_Curve_%s' % str(trace)
            self.traces[key] = Trace(os.path.join(folder_path, key + '.csv'), self.name)
        if self.n_traces > 0:
            combined_data = pd.concat((trace.data for trace in self.traces.values()))
            self.average_data = combined_data.groupby(combined_data.index).mean()
            v_oc = [trace.v_oc for trace in self.traces.values()]
            self.v_oc = [np.mean(v_oc), np.std(v_oc)]
            i_sc = [trace.i_sc for trace in self.traces.values()]
            self.i_sc = [np.mean(i_sc), np.std(i_sc)]
            power_max = [trace.power_max for trace in self.traces.values()]
            self.power_max = [np.mean(power_max), np.std(power_max)]
            fill_factor = [trace.fill_factor for trace in self.traces.values()]
            self.fill_factor = [np.mean(fill_factor), np.std(fill_factor)]
            temperature = [trace.temperature[0] for trace in self.traces.values()]
            self.temperature = [np.mean(temperature), np.std(temperature)]
            irradiance_1 = [trace.irradiance_1[0] for trace in self.traces.values()]
            self.irradiance_1 = [np.mean(irradiance_1), np.std(irradiance_1)]
            irradiance_2 = [trace.irradiance_2[0] for trace in self.traces.values()]
            self.irradiance_2 = [np.mean(irradiance_2), np.std(irradiance_2)]
            irradiance_3 = [trace.irradiance_3[0] for trace in self.traces.values()]
            self.irradiance_3 = [np.mean(irradiance_3), np.std(irradiance_3)]
            irradiance_4 = [trace.irradiance_4[0] for trace in self.traces.values()]
            self.irradiance_4 = [np.mean(irradiance_4), np.std(irradiance_4)]


class Trace:
    def __init__(self, data_path='.', experiment=None):
        self.data_path = os.path.normpath(data_path)
        self.experiment = experiment
        self.data = pd.read_csv(self.data_path, index_col=0)
        self.time = self.data['Time (s)'].min()
        self.v_oc = self.data.loc[self.data['Current (A)'].abs() == self.data['Current (A)'].abs().min(),
                                  ['Voltage (V)']].values[0, 0]  # V
        self.i_sc = self.data.loc[self.data['Voltage (V)'].abs() == self.data['Voltage (V)'].abs().min(),
                                  ['Current (A)']].values[0, 0]  # A
        self.power_max = self.data['Power (W)'].max()  # W
        self.fill_factor = abs(self.power_max / (self.v_oc * self.i_sc))
        self.temperature = [self.data['Temperature (C)'].mean(), self.data['Temperature (C)'].std()]  # C
        self.irradiance_1 = [self.data['Irradiance 1 (W/m2)'].mean(), self.data['Irradiance 1 (W/m2)'].std()]  # W/m2
        self.irradiance_2 = [self.data['Irradiance 2 (W/m2)'].mean(), self.data['Irradiance 2 (W/m2)'].std()]  # W/m2
        self.irradiance_3 = [self.data['Irradiance 3 (W/m2)'].mean(), self.data['Irradiance 3 (W/m2)'].std()]  # W/m2
        self.irradiance_4 = [self.data['Irradiance 4 (W/m2)'].mean(), self.data['Irradiance 4 (W/m2)'].std()]  # W/m2


class CsvFile:
    def __init__(self):
        self.file_name = ''
        self.experiment = 'n/a'
        self.data = pd.DataFrame()
        self.time = 0
        self.v_oc = -1
        self.i_sc = -1
        self.fill_factor = -1
        self.power_max = -1
        self.temperature = -1
        self.irradiance = -1

    def load_file(self, fname):
        self.file_name = fname
        self.experiment = os.path.split(os.path.dirname(self.file_name))[-1]
        self.data = pd.read_csv(self.file_name, sep=',', header=0, index_col=0, skiprows=1,
                                names=["Time (s)", "Voltage (V)", "Current (A)", "Current Std (A)" ,
                                       "Resistance (Ohm)", "Power (W)", "Temperature (C)", "Irradiance 1 (W/m2)",
                                       "Irradiance 2 (W/m2)", "Irradiance 3 (W/m2)", "Irradiance 4 (W/m2)"])
        self.time = self.data['Time (s)'].min()  # s
        self.v_oc = self.data.loc[self.data['Current (A)'].abs() == self.data['Current (A)'].abs().min(),
                                  ['Voltage (V)']].values[0, 0]  # V
        self.i_sc = self.data.loc[self.data['Voltage (V)'].abs() == self.data['Voltage (V)'].abs().min(),
                                  ['Current (A)']].values[0, 0]  # A
        self.power_max = self.data['Power (W)'].max()  # W
        self.fill_factor = self.power_max / (self.v_oc * self.i_sc)
        self.temperature = self.data['Time (s)'].mean()
        self.irradiance = (self.data['Irradiance 1 (W/m2)'].mean() + self.data['Irradiance 2 (W/m2)'].mean() +
                           self.data['Irradiance 3 (W/m2)'].mean() + self.data['Irradiance 4 (W/m2)'].mean()) / 4


class CsvFileKickstart:
    def __init__(self):
        self.file_name = ''
        self.time = 0
        self.experiment = 'n/a'
        self.sourcemeter = pd.DataFrame()
        self.data = pd.DataFrame()
        self.power_max = -1
        self.v_oc = -1
        self.i_sc = -1
        self.fill_factor = -1
        self.temperature = -1
        self.irradiance = -1

    def load_file(self, fname):
        self.file_name = fname
        self.time = time.mktime(time.strptime(self.file_name.split(' ')[-1], "%Y-%m-%dT%H.%M.%S.csv"))
        self.experiment = os.path.split(os.path.dirname(self.file_name))[-1]
        self.sourcemeter = pd.read_csv(self.file_name, sep=',', header=None, chunksize=33)
        self.data = pd.read_csv(self.file_name, sep=',', header=0, index_col=0, skiprows=33,
                                names=["Time", "Voltage", "Current"])
        self.data['Current'] = - self.data['Current']
        self.data['Power'] = self.data['Current'] * self.data['Voltage']
        self.power_max = self.data['Power'].max()  # W
        self.v_oc = self.data.loc[self.data['Current'].abs() == self.data['Current'].abs().min(),
                                  ['Voltage']].values[0, 0]  # V
        self.i_sc = self.data.loc[self.data['Voltage'].abs() == self.data['Voltage'].abs().min(),
                                  ['Current']].values[0, 0]  # A
        self.fill_factor = self.power_max / (self.v_oc * self.i_sc)
