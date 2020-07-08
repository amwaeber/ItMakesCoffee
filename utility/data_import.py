import numpy as np
import os
import pandas as pd
import pickle
import time

from utility import folders
from utility._version import __version__


efficiency_keys = ['Delta V_oc', 'Delta I_sc', 'Delta P_max', 'Delta Fill Factor', 'Delta T_avg', 'Delta I_1_avg',
                   'Delta I_2_avg', 'Delta I_3_avg', 'Delta I_4_avg']
average_keys = ['Open Circuit Voltage V_oc (V)', 'Short Circuit Current I_sc (A)', 'Maximum Power P_max (W)',
                'Fill Factor', 'Average Temperature T_avg (C)', 'Average Irradiance I_1_avg (W/m2)',
                'Average Irradiance I_2_avg (W/m2)', 'Average Irradiance I_3_avg (W/m2)',
                'Average Irradiance I_4_avg (W/m2)']


class Experiment:
    def __init__(self, folder_path='.'):
        self.is_reference = False
        self.is_plotted = False

        self.folder_path = os.path.normpath(folder_path)
        self.name = os.path.basename(self.folder_path)
        n_csv = folders.get_number_of_csv(self.folder_path)

        if os.path.exists(os.path.join(self.folder_path, 'experiment.pkl')):
            try:
                self.version, self.time, self.film_thickness, self.film_area, self.n_traces, self.traces, \
                    self.values, self.average_data, self.reference_path, self.efficiencies = self.load_pickle()
                if any([self.version != __version__, n_csv != self.n_traces]):
                    raise ValueError
            except ValueError:  # mismatch in version or traces, or more parameters added since previous version
                self.import_from_files()
        else:
            self.import_from_files()

        self.plot_categories = {'Experiment': str(self.name),
                                'Film Thickness': str(self.film_thickness),
                                'Film Area': str(self.film_area),
                                'Time': str(self.time)
                                }

    def import_from_files(self):
        self.load_settings()
        self.version = __version__

        self.n_traces = folders.get_number_of_csv(self.folder_path)  # 1st par: new format, 2nd par: kickstart format
        self.traces = {}
        for trace in range(self.n_traces[0]):
            key = 'IV_Curve_%s' % str(trace)
            self.traces[key] = Trace(os.path.join(self.folder_path, key + '.csv'), self.name, key)
        if self.n_traces[1] > 0:  # Import Kickstart files if there are any
            kickstart_files = folders.get_kickstart_paths(self.folder_path)
            for itrace, trace in enumerate(range(self.n_traces[0], self.n_traces[0] + self.n_traces[1])):
                key = 'IV_Curve_%s' % str(trace)
                self.traces[key] = KickstartTrace(os.path.join(self.folder_path, kickstart_files[itrace]),
                                                  self.name, key)
        self.update_average()
        self.update_reference(None)  # set reference and efficiencies to default

    def load_settings(self):
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

    def update_average(self):
        combined_data = pd.concat((trace.data for trace in self.traces.values() if trace.is_included))
        self.average_data = combined_data.groupby(combined_data.index).mean()
        self.values = {key: self.get_average(key) for key in average_keys}

    def get_average(self, key):
        trace_values = [trace.values[key][0] for trace in self.traces.values() if trace.is_included]
        return [np.mean(trace_values), np.std(trace_values)]

    def update_reference(self, ref_experiment):
        if not ref_experiment:
            self.reference_path = ''
            self.efficiencies = {key: [0, 0] for key in efficiency_keys}
        else:
            self.reference_path = ref_experiment.folder_path
            self.efficiencies = {key: self.get_efficiency(ref_experiment, avg_key) for key, avg_key in
                                 zip(efficiency_keys, average_keys)}

    def get_efficiency(self, ref_experiment, key):
        if ref_experiment.values[key][0] == 0:
            return [0, 0]
        else:
            return [100 * (self.values[key][0] - ref_experiment.values[key][0]) / ref_experiment.values[key][0],
                    100 * self.values[key][1] / ref_experiment.values[key][0]]

    def save_pickle(self):
        with open(os.path.join(self.folder_path, 'experiment.pkl'), 'wb') as f:
            pickle.dump([self.version, self.time, self.film_thickness, self.film_area, self.n_traces, self.traces,
                         self.values, self.average_data], f, protocol=-1)

    def load_pickle(self):
        with open(os.path.join(self.folder_path, 'experiment.pkl'), 'rb') as f:
            return pickle.load(f)


class Trace:
    def __init__(self, data_path='.', experiment=None, key=None):
        self.data_path = os.path.normpath(data_path)
        self.name = key
        self.is_included = True
        self.experiment = experiment
        self.data = pd.read_csv(self.data_path, header=None, index_col=0, skiprows=1,
                                names=["Index", "Time (s)", "Voltage (V)", "Current (A)", "Current Std (A)",
                                       "Resistance (Ohm)", "Power (W)", "Temperature (C)", "Irradiance 1 (W/m2)",
                                       "Irradiance 2 (W/m2)", "Irradiance 3 (W/m2)", "Irradiance 4 (W/m2)"],
                                usecols=[0, 1, 2, 3, 6, 7, 8, 9, 10, 11])
        self.time = self.data['Time (s)'].min()
        self.values = {'Open Circuit Voltage V_oc (V)': [self.get_voc(), 0],
                       'Short Circuit Current I_sc (A)': [self.get_isc(), 0],
                       'Maximum Power P_max (W)': [self.get_pmax(), 0],
                       'Fill Factor': [self.get_fill_factor(), 0]}
        for key, col in zip(average_keys[4:], self.data.columns.values[4:]):
            self.values[key] = [self.data[col].mean(), self.data[col].std()]

    def get_voc(self):
        return self.data.loc[self.data['Current (A)'].abs() == self.data['Current (A)'].abs().min(),
                             ['Voltage (V)']].values[0, 0]

    def get_isc(self):
        return self.data.loc[self.data['Voltage (V)'].abs() == self.data['Voltage (V)'].abs().min(),
                             ['Current (A)']].values[0, 0]

    def get_pmax(self):
        pmax = self.data.loc[self.data['Current (A)'] > 0]['Power (W)'].max()
        return pmax if not np.isnan(pmax) else 0.0

    def get_fill_factor(self):
        vocisc = self.get_voc() * self.get_isc()
        if vocisc == 0:
            return 0.0
        else:
            return abs(self.get_pmax() / vocisc)


class KickstartTrace:
    def __init__(self, data_path='.', experiment=None, key=None):
        self.data_path = os.path.normpath(data_path)
        self.name = key
        self.is_included = True
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
        self.values = {'Open Circuit Voltage V_oc (V)': [self.get_voc(), 0],
                       'Short Circuit Current I_sc (A)': [self.get_isc(), 0],
                       'Maximum Power P_max (W)': [self.get_pmax(), 0],
                       'Fill Factor': [self.get_fill_factor(), 0]}
        for key in average_keys[4:]:
            self.values[key] = [-1, 0.0]

    def get_voc(self):
        return self.data.loc[self.data['Current (A)'].abs() == self.data['Current (A)'].abs().min(),
                             ['Voltage (V)']].values[0, 0]

    def get_isc(self):
        return self.data.loc[self.data['Voltage (V)'].abs() == self.data['Voltage (V)'].abs().min(),
                             ['Current (A)']].values[0, 0]

    def get_pmax(self):
        pmax = self.data.loc[self.data['Current (A)'] > 0]['Power (W)'].max()
        return pmax if not np.isnan(pmax) else 0.0

    def get_fill_factor(self):
        vocisc = self.get_voc() * self.get_isc()
        if vocisc == 0:
            return 0.0
        else:
            return abs(self.get_pmax() / vocisc)
