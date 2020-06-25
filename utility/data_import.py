import numpy as np
import os
import pandas as pd
import time

from utility import folders


class Experiment:
    def __init__(self, folder_path='.'):
        self.reference = False
        self.plot = False
        self.stats = False

        self.folder_path = os.path.normpath(folder_path)
        self.name = os.path.basename(folder_path)
        try:
            with open(os.path.join(folder_path, 'Settings.txt')) as f:
                self.time = f.readline().strip('\n')
        except FileNotFoundError:
            self.time = folders.get_datetime(folder_path)
        self.n_traces = folders.get_number_of_csv(folder_path)
        self.traces = {}
        for trace in range(self.n_traces):
            key = 'IV_Curve_%s' % str(trace)
            self.traces[key] = Trace(os.path.join(folder_path, key + '.csv'), self.name)
        self.values = {}
        combined_data = pd.concat((trace.data for trace in self.traces.values()))
        self.average_data = combined_data.groupby(combined_data.index).mean()
        v_oc = [trace.values['Open Circuit Voltage V_oc (V)'][0] for trace in self.traces.values()]
        self.values['Open Circuit Voltage V_oc (V)'] = [np.mean(v_oc), np.std(v_oc)]
        i_sc = [trace.values['Short Circuit Current I_sc (A)'][0] for trace in self.traces.values()]
        self.values['Short Circuit Current I_sc (A)'] = [np.mean(i_sc), np.std(i_sc)]
        power_max = [trace.values['Maximum Power P_max (W)'][0] for trace in self.traces.values()]
        self.values['Maximum Power P_max (W)'] = [np.mean(power_max), np.std(power_max)]
        fill_factor = [trace.values['Fill Factor'][0] for trace in self.traces.values()]
        self.values['Fill Factor'] = [np.mean(fill_factor), np.std(fill_factor)]
        temperature = [trace.values['Average Temperature T_avg (C)'][0] for trace in self.traces.values()]
        self.values['Average Temperature T_avg (C)'] = [np.mean(temperature), np.std(temperature)]
        irradiance_1 = [trace.values['Average Irradiance I_1_avg (W/m2)'][0] for trace in self.traces.values()]
        self.values['Average Irradiance I_1_avg (W/m2)'] = [np.mean(irradiance_1), np.std(irradiance_1)]
        irradiance_2 = [trace.values['Average Irradiance I_2_avg (W/m2)'][0] for trace in self.traces.values()]
        self.values['Average Irradiance I_2_avg (W/m2)'] = [np.mean(irradiance_2), np.std(irradiance_2)]
        irradiance_3 = [trace.values['Average Irradiance I_3_avg (W/m2)'][0] for trace in self.traces.values()]
        self.values['Average Irradiance I_3_avg (W/m2)'] = [np.mean(irradiance_3), np.std(irradiance_3)]
        irradiance_4 = [trace.values['Average Irradiance I_4_avg (W/m2)'][0] for trace in self.traces.values()]
        self.values['Average Irradiance I_4_avg (W/m2)'] = [np.mean(irradiance_4), np.std(irradiance_4)]

        self.efficiencies = {'Delta V_oc': [0, 0],
                             'Delta I_sc': [0, 0],
                             'Delta P_max': [0, 0],
                             'Delta Fill Factor': [0, 0],
                             'Delta T_avg': [0,0]}

    def update_efficiencies(self, reference_experiment):
        if not reference_experiment:
            self.efficiencies = {'Delta V_oc': [0, 0],
                                 'Delta I_sc': [0, 0],
                                 'Delta P_max': [0, 0],
                                 'Delta Fill Factor': [0, 0],
                                 'Delta T_avg': [0, 0]}
        else:
            self.efficiencies['Delta V_oc'] = [100 * (self.values['Open Circuit Voltage V_oc (V)'][0] -
                                               reference_experiment.values['Open Circuit Voltage V_oc (V)'][0]) /
                                               reference_experiment.values['Open Circuit Voltage V_oc (V)'][0],
                                               100 * self.values['Open Circuit Voltage V_oc (V)'][1] /
                                               reference_experiment.values['Open Circuit Voltage V_oc (V)'][0]]
            self.efficiencies['Delta I_sc'] = [100 * (self.values['Short Circuit Current I_sc (A)'][0] -
                                               reference_experiment.values['Short Circuit Current I_sc (A)'][0]) /
                                               reference_experiment.values['Short Circuit Current I_sc (A)'][0],
                                               100 * self.values['Short Circuit Current I_sc (A)'][1] /
                                               reference_experiment.values['Short Circuit Current I_sc (A)'][0]]
            self.efficiencies['Delta P_max'] = [100 * (self.values['Maximum Power P_max (W)'][0] -
                                                reference_experiment.values['Maximum Power P_max (W)'][0]) /
                                                reference_experiment.values['Maximum Power P_max (W)'][0],
                                                100 * self.values['Maximum Power P_max (W)'][1] /
                                                reference_experiment.values['Maximum Power P_max (W)'][0]]
            self.efficiencies['Delta Fill Factor'] = [100 * (self.values['Fill Factor'][0] -
                                                      reference_experiment.values['Fill Factor'][0]) /
                                                      reference_experiment.values['Fill Factor'][0],
                                                      100 * self.values['Fill Factor'][1] /
                                                      reference_experiment.values['Fill Factor'][0]]
            self.efficiencies['Delta T_avg'] = [100 * (self.values['Average Temperature T_avg (C)'][0] -
                                                reference_experiment.values['Average Temperature T_avg (C)'][0]) /
                                                reference_experiment.values['Average Temperature T_avg (C)'][0],
                                                100 * self.values['Average Temperature T_avg (C)'][1] /
                                                reference_experiment.values['Average Temperature T_avg (C)'][0]]


class Trace:
    def __init__(self, data_path='.', experiment=None):
        self.data_path = os.path.normpath(data_path)
        self.experiment = experiment
        self.data = pd.read_csv(self.data_path,  header=None, index_col=0, skiprows=1,
                                names=["Index", "Time (s)", "Voltage (V)", "Current (A)", "Current Std (A)",
                                       "Resistance (Ohm)", "Power (W)", "Temperature (C)", "Irradiance 1 (W/m2)",
                                       "Irradiance 2 (W/m2)", "Irradiance 3 (W/m2)", "Irradiance 4 (W/m2)"],
                                usecols=[0, 1, 2, 3, 6, 7, 8, 9, 10, 11])
        self.time = self.data['Time (s)'].min()
        self.values = {}
        self.values['Open Circuit Voltage V_oc (V)'] = [self.data.loc[self.data['Current (A)'].abs() ==
                                                                      self.data['Current (A)'].abs().min(),
                                                                      ['Voltage (V)']].values[0, 0], 0]  # V
        self.values['Short Circuit Current I_sc (A)'] = [self.data.loc[self.data['Voltage (V)'].abs() ==
                                                                       self.data['Voltage (V)'].abs().min(),
                                                                       ['Current (A)']].values[0, 0], 0]  # A
        self.values['Maximum Power P_max (W)'] = [self.data.loc[self.data['Current (A)'] > 0]['Power (W)'].max(), 0]  # W
        self.values['Fill Factor'] = [abs(self.values['Maximum Power P_max (W)'][0] /
                                          (self.values['Open Circuit Voltage V_oc (V)'][0] *
                                           self.values['Short Circuit Current I_sc (A)'][0])), 0]
        self.values['Average Temperature T_avg (C)'] = [self.data['Temperature (C)'].mean(),
                                                        self.data['Temperature (C)'].std()]  # C
        self.values['Average Irradiance I_1_avg (W/m2)'] = [self.data['Irradiance 1 (W/m2)'].mean(),
                                                            self.data['Irradiance 1 (W/m2)'].std()]  # W/m2
        self.values['Average Irradiance I_2_avg (W/m2)'] = [self.data['Irradiance 2 (W/m2)'].mean(),
                                                            self.data['Irradiance 2 (W/m2)'].std()]  # W/m2
        self.values['Average Irradiance I_3_avg (W/m2)'] = [self.data['Irradiance 3 (W/m2)'].mean(),
                                                            self.data['Irradiance 3 (W/m2)'].std()]  # W/m2
        self.values['Average Irradiance I_4_avg (W/m2)'] = [self.data['Irradiance 4 (W/m2)'].mean(),
                                                            self.data['Irradiance 4 (W/m2)'].std()]  # W/m2


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
