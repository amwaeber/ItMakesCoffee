import os
import pandas as pd
import time


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
