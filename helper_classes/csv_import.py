import os
import pandas as pd
import time


class CsvFile:
    def __init__(self):
        self.file_name = ''
        self.timestamp = 0
        self.experiment = 'n/a'
        self.sourcemeter = pd.DataFrame()
        self.data = pd.DataFrame()
        self.power_max = -1
        self.v_oc = -1
        self.i_sc = -1
        self.fill_factor = -1

    def load_file(self, fname):
        self.file_name = fname
        self.timestamp = time.mktime(time.strptime(self.file_name.split(' ')[-1], "%Y-%m-%dT%H.%M.%S.csv"))
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
