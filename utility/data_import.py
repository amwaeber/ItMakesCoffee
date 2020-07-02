import numpy as np
import os
import pandas as pd
import pickle
import time

from utility import folders


class Experiment:
    def __init__(self, folder_path='.'):
        self.reference = False
        self.plot = False
        self.stats = False

        self.folder_path = os.path.normpath(folder_path)
        self.name = os.path.basename(self.folder_path)
        n_csv = folders.get_number_of_csv(self.folder_path)

        if os.path.exists(os.path.join(self.folder_path, 'experiment.pkl')):
            self.time, self.film_thickness, self.film_area, self.n_traces, self.traces, self.values, self.average_data\
                = self.load()
            if n_csv != self.n_traces:
                self.import_from_files()
        else:
            self.import_from_files()

        self.efficiencies = {'Delta V_oc': [0, 0],
                             'Delta I_sc': [0, 0],
                             'Delta P_max': [0, 0],
                             'Delta Fill Factor': [0, 0],
                             'Delta T_avg': [0, 0],
                             'Delta I_1_avg': [0, 0],
                             'Delta I_2_avg': [0, 0],
                             'Delta I_3_avg': [0, 0],
                             'Delta I_4_avg': [0, 0]
                             }

        self.plot_categories = {'Experiment': str(self.name),
                                'Film Thickness': str(self.film_thickness),
                                'Film Area': str(self.film_area),
                                'Time': str(self.time)
                                }

    def update_efficiencies(self, reference_experiment):
        if not reference_experiment:
            self.efficiencies = {'Delta V_oc': [0, 0],
                                 'Delta I_sc': [0, 0],
                                 'Delta P_max': [0, 0],
                                 'Delta Fill Factor': [0, 0],
                                 'Delta T_avg': [0, 0],
                                 'Delta I_1_avg': [0, 0],
                                 'Delta I_2_avg': [0, 0],
                                 'Delta I_3_avg': [0, 0],
                                 'Delta I_4_avg': [0, 0]
                                 }
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
            self.efficiencies['Delta I_1_avg'] = [100 * (self.values['Average Irradiance I_1_avg (W/m2)'][0] -
                                                  reference_experiment.values['Average Irradiance I_1_avg (W/m2)'][0]) /
                                                  reference_experiment.values['Average Irradiance I_1_avg (W/m2)'][0],
                                                  100 * self.values['Average Irradiance I_1_avg (W/m2)'][1] /
                                                  reference_experiment.values['Average Irradiance I_1_avg (W/m2)'][0]]
            self.efficiencies['Delta I_2_avg'] = [100 * (self.values['Average Irradiance I_2_avg (W/m2)'][0] -
                                                  reference_experiment.values['Average Irradiance I_2_avg (W/m2)'][0]) /
                                                  reference_experiment.values['Average Irradiance I_2_avg (W/m2)'][0],
                                                  100 * self.values['Average Irradiance I_2_avg (W/m2)'][1] /
                                                  reference_experiment.values['Average Irradiance I_2_avg (W/m2)'][0]]
            self.efficiencies['Delta I_3_avg'] = [100 * (self.values['Average Irradiance I_3_avg (W/m2)'][0] -
                                                  reference_experiment.values['Average Irradiance I_3_avg (W/m2)'][0]) /
                                                  reference_experiment.values['Average Irradiance I_3_avg (W/m2)'][0],
                                                  100 * self.values['Average Irradiance I_3_avg (W/m2)'][1] /
                                                  reference_experiment.values['Average Irradiance I_3_avg (W/m2)'][0]]
            self.efficiencies['Delta I_4_avg'] = [100 * (self.values['Average Irradiance I_4_avg (W/m2)'][0] -
                                                  reference_experiment.values['Average Irradiance I_4_avg (W/m2)'][0]) /
                                                  reference_experiment.values['Average Irradiance I_4_avg (W/m2)'][0],
                                                  100 * self.values['Average Irradiance I_4_avg (W/m2)'][1] /
                                                  reference_experiment.values['Average Irradiance I_4_avg (W/m2)'][0]]

    def store(self):
        with open(os.path.join(self.folder_path, 'experiment.pkl'), 'wb') as f:
            pickle.dump([self.time, self.film_thickness, self.film_area, self.n_traces, self.traces, self.values,
                        self.average_data], f, protocol=-1)

    def load(self):
        with open(os.path.join(self.folder_path, 'experiment.pkl'), 'rb') as f:
            return pickle.load(f)

    def import_from_files(self):
        try:
            with open(os.path.join(self.folder_path, 'Settings.txt')) as f:
                file_contents = f.readlines()
                self.time = file_contents[0].strip('\n')
                if file_contents[2].startswith("Film"):
                    self.film_thickness = file_contents[3].strip('\n').split(' ')[-1]
                    self.film_area = file_contents[4].strip('\n').split(' ')[-1]
                else:
                    self.film_thickness = -1
                    self.film_area = -1
        except FileNotFoundError:
            self.time = folders.get_datetime(self.folder_path)
            self.film_thickness = -1
            self.film_area = -1
        self.n_traces = folders.get_number_of_csv(self.folder_path)  # 1st par: new format, 2nd par: kickstart format
        self.traces = {}
        for trace in range(self.n_traces[0]):
            key = 'IV_Curve_%s' % str(trace)
            self.traces[key] = Trace(os.path.join(self.folder_path, key + '.csv'), self.name)
        if self.n_traces[1] > 0:  # Import Kickstart files if there are any
            kickstart_files = folders.get_kickstart_paths(self.folder_path)
            for itrace, trace in enumerate(range(self.n_traces[0], self.n_traces[0] + self.n_traces[1])):
                key = 'IV_Curve_%s' % str(trace)
                self.traces[key] = KickstartTrace(os.path.join(self.folder_path, kickstart_files[itrace]), self.name)
    # if not hasattr(self, 'values'):
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


class KickstartTrace:
    def __init__(self, data_path='.', experiment=None):
        self.data_path = os.path.normpath(data_path)
        self.experiment = experiment
        self.data = pd.read_csv(self.data_path, sep=',', header=0, index_col=0, skiprows=33,
                                names=["Time (s)", "Voltage (V)", "Current (A)"])
        self.time = time.mktime(time.strptime(os.path.basename(self.data_path).split(' ')[-1], "%Y-%m-%dT%H.%M.%S.csv"))
        self.data['Index'] = -1
        self.data['Time (s)'] = self.data['Time (s)'] + self.time
        self.data['Current (A)'] = - self.data['Current (A)']
        self.data['Power (W)'] = self.data['Voltage (V)'] * self.data['Current (A)']
        for item in ["Temperature (C)", "Irradiance 1 (W/m2)", "Irradiance 2 (W/m2)", "Irradiance 3 (W/m2)",
                     "Irradiance 4 (W/m2)"]:
            self.data[item] = -1
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
        self.values['Average Temperature T_avg (C)'] = [-1, 0]  # C
        self.values['Average Irradiance I_1_avg (W/m2)'] = [-1, 0]  # W/m2
        self.values['Average Irradiance I_2_avg (W/m2)'] = [-1, 0]  # W/m2
        self.values['Average Irradiance I_3_avg (W/m2)'] = [-1, 0]  # W/m2
        self.values['Average Irradiance I_4_avg (W/m2)'] = [-1, 0]  # W/m2
