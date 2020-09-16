import copy
import datetime
import numpy as np
import os
import pandas as pd
import pickle
from scipy import optimize
from scipy.optimize import OptimizeWarning
import time
import warnings

from utility import folders
from utility._version import __version__


warnings.simplefilter("error", OptimizeWarning)

efficiency_keys = ['Delta V_oc', 'Delta I_sc', 'Delta P_max', 'Delta Fill Factor', 'Delta T_avg', 'Delta I_1_avg',
                   'Delta I_2_avg', 'Delta I_3_avg', 'Delta I_4_avg']
average_keys = ['Time (s)', 'Open Circuit Voltage V_oc (V)', 'Short Circuit Current I_sc (A)',
                'Maximum Power P_max (W)', 'Fill Factor', 'Average Temperature T_avg (C)',
                'Average Irradiance I_1_avg (W/m2)', 'Average Irradiance I_2_avg (W/m2)',
                'Average Irradiance I_3_avg (W/m2)', 'Average Irradiance I_4_avg (W/m2)']


class DataBundle:
    def __init__(self, *args, **kwargs):
        self.is_reference = False
        self.is_plotted = False

        self.file_path = os.path.normpath(kwargs.get('file_path', '.'))
        self.folder_path = os.path.normpath(kwargs.get('folder_path', '.'))
        self.name = 'default'

        self.version = __version__
        self.time = 0
        self.film_thickness = -1
        self.film_area = -1

        self.n_traces = 0
        self.traces = {}
        self.average_data = pd.DataFrame(columns=['Index', 'Time (s)', 'Voltage (V)', 'Current (A)', 'Power (W)',
                                                  'Temperature (C)', 'Irradiance 1 (W/m2)', 'Irradiance 2 (W/m2)',
                                                  'Irradiance 3 (W/m2)', 'Irradiance 4 (W/m2)'])
        self.values = {key: [0, 0] for key in average_keys}
        self.fitted_values = {key: [0, 0] for key in average_keys}

        self.reference_path = ''
        self.efficiencies = {key: [0, 0] for key in efficiency_keys}
        self.fitted_efficiencies = {key: [0, 0] for key in efficiency_keys}

        self.plot_categories = {'Experiment': str(self.name),
                                'Film Thickness': str(self.film_thickness),
                                'Film Area': str(self.film_area),
                                'Time': str(self.time)
                                }

    def import_from_pickle(self, *args, **kwargs):
        pass

    def import_from_files(self, *args, **kwargs):
        pass

    def update_average(self):
        combined_data = pd.concat((trace.data for trace in self.traces.values() if trace.is_included))
        self.average_data = combined_data.groupby(combined_data.index).mean()
        for key in average_keys:
            trace_values = [trace.values[key][0] for trace in self.traces.values() if trace.is_included]
            if key == 'Time (s)':
                self.values[key] = [trace_values[0], 0]
            else:
                self.values[key] = [np.mean(trace_values), np.std(trace_values)]

    def update_fit(self):
        for key in average_keys:
            trace_values = [trace.fitted_values[key][0] for trace in self.traces.values() if trace.is_included]
            if key == 'Time (s)':
                self.fitted_values[key] = [trace_values[0], 0]
            else:
                self.fitted_values[key] = [np.mean(trace_values), np.std(trace_values)]

    def update_reference(self, ref_experiment):
        if not ref_experiment:
            self.reference_path = ''
            self.efficiencies = {key: [0, 0] for key in efficiency_keys}
            self.fitted_efficiencies = {key: [0, 0] for key in efficiency_keys}
        else:
            self.reference_path = ref_experiment.folder_path
            self.efficiencies = {key: self.get_efficiency(ref_experiment, avg_key) for key, avg_key in
                                 zip(efficiency_keys, average_keys[1:])}
            self.fitted_efficiencies = {key: self.get_fitted_efficiency(ref_experiment, avg_key) for key, avg_key in
                                        zip(efficiency_keys, average_keys[1:])}

    def get_efficiency(self, ref_experiment, key):
        if ref_experiment.values[key][0] == 0:
            return [0, 0]
        else:
            return [100 * (self.values[key][0] - ref_experiment.values[key][0]) / ref_experiment.values[key][0],
                    100 * self.values[key][1] / ref_experiment.values[key][0]]

    def get_fitted_efficiency(self, ref_experiment, key):
        if ref_experiment.values[key][0] == 0:
            return [0, 0]
        else:
            return [100 * (self.fitted_values[key][0] - ref_experiment.fitted_values[key][0]) / ref_experiment.fitted_values[key][0],
                    100 * self.fitted_values[key][1] / ref_experiment.fitted_values[key][0]]

    def update_plot_categories(self):
        self.plot_categories = {'Experiment': str(self.name),
                                'Film Thickness': str(self.film_thickness),
                                'Film Area': str(self.film_area),
                                'Time': str(self.time)
                                }

    def save_pickle(self):
        with open(self.file_path, 'wb') as f:
            pickle.dump([self.version, self.time, self.film_thickness, self.film_area, self.n_traces, self.traces,
                         self.values, self.average_data, self.reference_path, self.efficiencies], f, protocol=-1)

    def load_pickle(self):
        with open(self.file_path, 'rb') as f:
            return pickle.load(f)


class Experiment(DataBundle):
    def __init__(self, folder_path='.'):
        super().__init__(folder_path=folder_path)

        self.name = os.path.basename(self.folder_path)
        self.file_path = os.path.join(self.folder_path, 'experiment.pkl')

        self.import_from_pickle()
        self.update_plot_categories()

    def import_from_pickle(self):
        n_csv = folders.get_number_of_csv(self.folder_path)
        if os.path.exists(self.file_path):
            try:
                self.version, self.time, self.film_thickness, self.film_area, self.n_traces, self.traces, \
                    self.values, self.average_data, self.reference_path, self.efficiencies = self.load_pickle()
                if any([self.version != __version__, n_csv != self.n_traces]):
                    raise ValueError
            except ValueError:  # mismatch in version or traces, or more parameters added since previous version
                self.import_from_files()
        else:
            self.import_from_files()

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
        self.update_fit()
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


class Group(DataBundle):
    def __init__(self, file_path='.', trace_paths=None):
        super().__init__(file_path=file_path)

        self.folder_path = os.path.dirname(self.file_path)
        self.name = os.path.splitext(os.path.basename(self.file_path))[0]

        self.import_from_pickle(trace_paths)
        self.update_plot_categories()

    def import_from_pickle(self, trace_paths):
        if os.path.exists(self.file_path):
            try:
                self.version, self.time, self.film_thickness, self.film_area, self.n_traces, self.traces, \
                    self.values, self.average_data, self.reference_path, self.efficiencies = self.load_pickle()
            except ValueError:  # mismatch in version or traces, or more parameters added since previous version
                self.failed_import()
        else:
            self.import_from_files(trace_paths)

    def failed_import(self):
        print('Could not import %s.' % self.file_path)

    def import_from_files(self, trace_paths=None, *args, **kwargs):
        self.version = __version__
        self.n_traces = [len(trace_paths)]  # 1st par: new format, 2nd par: kickstart format
        self.traces = {}
        for itrace, trace_path in enumerate(trace_paths):
            key = 'IV_Curve_%s' % str(itrace)
            if os.path.basename(trace_path).startswith('IV_Curve_'):
                self.traces[key] = Trace(trace_path, self.name, key)
            else:
                self.traces[key] = KickstartTrace(trace_path, self.name, key)
            if itrace == 0:
                self.time = self.traces[key].time
                self.film_thickness = self.traces[key].film_thickness
                self.film_area = self.traces[key].film_area
            else:
                self.time = min([self.time, self.traces[key].time])
                self.film_thickness = -1 if self.film_thickness != self.traces[key].film_thickness \
                    else self.film_thickness
                self.film_area = -1 if self.film_area != self.traces[key].film_area else self.film_area
        self.time = datetime.datetime.fromtimestamp(self.time).strftime("%Y-%m-%d %H:%M:%S")
        self.update_average()
        self.update_fit()
        self.update_reference(None)  # set reference and efficiencies to default


class Data:
    def __init__(self, data_path='.', *args, **kwargs):
        self.data_path = os.path.normpath(data_path)
        self.name = kwargs.get('key', 'default')
        self.experiment = kwargs.get('experiment', 'none')
        self.is_included = True

        self.film_thickness = -1
        self.film_area = -1
        self.load_settings()
        self.data = pd.DataFrame(columns=['Index', 'Time (s)', 'Voltage (V)', 'Current (A)', 'Power (W)',
                                          'Temperature (C)', 'Irradiance 1 (W/m2)', 'Irradiance 2 (W/m2)',
                                          'Irradiance 3 (W/m2)', 'Irradiance 4 (W/m2)'])
        self.time = 0
        self.values = {key: [0, 0] for key in average_keys}
        self.fitted_values = {key: [0, 0] for key in average_keys}

    def load_settings(self):
        try:
            with open(os.path.join(os.path.dirname(self.data_path), 'Settings.txt')) as f:
                file_contents = f.readlines()
                if file_contents[2].startswith("Film"):
                    self.film_thickness = file_contents[3].strip('\n').split(' ')[-1]
                    self.film_area = file_contents[4].strip('\n').split(' ')[-1]
                else:
                    self.film_thickness = -1
                    self.film_area = -1
        except FileNotFoundError:
            self.film_thickness = -1
            self.film_area = -1

    def fill_missing_values(self, column=None):  # To fix temporarily the missing first sensor values issue
        self.data[column].replace([0, -1], np.nan, inplace=True)
        self.data[column].fillna(method='backfill', inplace=True)
        self.data[column].fillna(method='pad', inplace=True)
        self.data[column].fillna(value=-1, inplace=True)

    def get_voc(self):
        try:
            voc = self.data.loc[self.data['Current (A)'].abs() == self.data['Current (A)'].abs().min(),
                                ['Voltage (V)']].values[0, 0]
        except IndexError:
            voc = 0
        return voc

    def fit_voc(self, n_points=5, y00=1, a0=1, b0=1):
        voc_idx = self.data.index[self.data['Voltage (V)'] ==
                                  self.values['Open Circuit Voltage V_oc (V)'][0]][0]
        idx_range = [voc_idx - n_points, voc_idx + n_points]
        slice_df = self.data[idx_range[0]:idx_range[1]]

        try:
            popt, pcov = optimize.curve_fit(lambda x, y0, a, b: y0 + a * x + b * x ** 2,
                                            slice_df['Current (A)'],
                                            slice_df['Voltage (V)'],
                                            p0=np.array([y00, a0, b0]))
        except OptimizeWarning:
            return [0, 0]
        return [popt[0], np.sqrt(np.diag(pcov))[0]]

    def get_isc(self):
        try:
            isc = self.data.loc[self.data['Voltage (V)'].abs() == self.data['Voltage (V)'].abs().min(),
                                ['Current (A)']].values[0, 0]
        except IndexError:
            isc = 0
        return isc

    def fit_isc(self, n_points=3, m0=-1e-2):
        isc_idx = self.data.index[self.data['Current (A)'] ==
                                  self.values['Short Circuit Current I_sc (A)'][0]][0]
        idx_range = [0, isc_idx + n_points]
        slice_df = self.data[idx_range[0]:idx_range[1]]

        try:
            popt, pcov = optimize.curve_fit(lambda x, y0, m: y0 + m * x,
                                            slice_df['Voltage (V)'],
                                            slice_df['Current (A)'],
                                            p0=np.array([self.values['Short Circuit Current I_sc (A)'][0], m0]))
        except OptimizeWarning:
            return [0, 0]
        return [popt[0], np.sqrt(np.diag(pcov))[0]]

    def get_pmax(self):
        try:
            if any(self.data['Current (A)'] > 0):
                pmax = self.data.loc[self.data['Current (A)'] > 0]['Power (W)'].max()
            else:
                pmax = 0
        except IndexError:
            pmax = 0
        return pmax

    def fit_pmax(self, n_points=10, i00=4e-5, vt0=7.5e-2):
        pmax_idx = self.data.index[self.data['Power (W)'] == self.values['Maximum Power P_max (W)'][0]][0]
        idx_range = [pmax_idx - n_points, pmax_idx + n_points]
        slice_df = self.data[idx_range[0]:idx_range[1]]

        def shockley(v, iph, i0, vt):
            return iph - i0 * np.exp(v / vt)

        try:
            popt, pcov = optimize.curve_fit(shockley,
                                            slice_df['Voltage (V)'],
                                            slice_df['Current (A)'],
                                            p0=np.array([self.values['Short Circuit Current I_sc (A)'][0], i00, vt0]))
            voltage_pmax = optimize.minimize_scalar(lambda v: - v * shockley(v, *popt)).x
        except OptimizeWarning:
            return [0, 0]
        return [voltage_pmax * shockley(voltage_pmax, *popt), 0]

    @staticmethod
    def get_fill_factor(voc, isc, pmax):
        vocisc = voc * isc
        if vocisc <= 0:
            return 0
        else:
            return abs(pmax / vocisc)


class Trace(Data):
    def __init__(self, data_path='.', experiment=None, key=None):
        super().__init__(data_path=data_path, experiment=experiment, key=key)
        self.csv_import()

    def csv_import(self):
        self.data = pd.read_csv(self.data_path, header=None, index_col=0, skiprows=3,
                                names=["Index", "Time (s)", "Voltage (V)", "Current (A)", "Current Std (A)",
                                       "Resistance (Ohm)", "Power (W)", "Temperature (C)", "Irradiance 1 (W/m2)",
                                       "Irradiance 2 (W/m2)", "Irradiance 3 (W/m2)", "Irradiance 4 (W/m2)"],
                                usecols=[0, 1, 2, 3, 6, 7, 8, 9, 10, 11])
        for col in ["Temperature (C)", "Irradiance 1 (W/m2)", "Irradiance 2 (W/m2)", "Irradiance 3 (W/m2)",
                    "Irradiance 4 (W/m2)"]:
            self.fill_missing_values(col)
        self.time = self.data['Time (s)'].min()
        self.values = {'Open Circuit Voltage V_oc (V)': [self.get_voc(), 0],
                       'Short Circuit Current I_sc (A)': [self.get_isc(), 0],
                       'Maximum Power P_max (W)': [self.get_pmax(), 0],
                       'Fill Factor': [self.get_fill_factor(self.values['Open Circuit Voltage V_oc (V)'][0],
                                                            self.values['Short Circuit Current I_sc (A)'][0],
                                                            self.values['Maximum Power P_max (W)'][0]), 0],
                       'Time (s)': [self.time, 0]}
        for key, col in zip(average_keys[5:], self.data.columns.values[4:]):
            self.values[key] = [self.data[col].mean(), self.data[col].std()]
        self.fitted_values = copy.deepcopy(self.values)
        self.fitted_values['Open Circuit Voltage V_oc (V)'] = self.fit_voc()
        self.fitted_values['Short Circuit Current I_sc (A)'] = self.fit_isc()
        self.fitted_values['Maximum Power P_max (W)'] = self.fit_pmax()
        self.fitted_values['Fill Factor'] = [self.get_fill_factor(self.fitted_values['Open Circuit Voltage V_oc (V)'][0],
                                             self.fitted_values['Short Circuit Current I_sc (A)'][0],
                                             self.fitted_values['Maximum Power P_max (W)'][0]), 0]


class KickstartTrace(Data):
    def __init__(self, data_path='.', experiment=None, key=None):
        super().__init__(data_path=data_path, experiment=experiment, key=key)
        self.csv_import()

    def csv_import(self):
        self.data = pd.read_csv(self.data_path, sep=',', header=0, index_col=0, skiprows=33,
                                names=["Time (s)", "Voltage (V)", "Current (A)"])
        self.time = time.mktime(time.strptime(os.path.basename(self.data_path).split(' ')[-1], "%Y-%m-%dT%H.%M.%S.csv"))
        self.data['Time (s)'] = self.data['Time (s)'] + self.time
        self.data['Current (A)'] = - self.data['Current (A)']
        self.data['Power (W)'] = self.data['Voltage (V)'] * self.data['Current (A)']
        for item in ['Index', "Temperature (C)", "Irradiance 1 (W/m2)", "Irradiance 2 (W/m2)", "Irradiance 3 (W/m2)",
                     "Irradiance 4 (W/m2)"]:
            self.data[item] = -1
        self.values['Open Circuit Voltage V_oc (V)'] = [self.get_voc(), 0]
        self.values['Short Circuit Current I_sc (A)'] = [self.get_isc(), 0]
        self.values['Maximum Power P_max (W)'] = [self.get_pmax(), 0]
        self.values['Fill Factor'] = [self.get_fill_factor(self.values['Open Circuit Voltage V_oc (V)'][0],
                                                           self.values['Short Circuit Current I_sc (A)'][0],
                                                           self.values['Maximum Power P_max (W)'][0]), 0]
        self.values['Time (s)'] = [self.time, 0]
        self.fitted_values = copy.deepcopy(self.values)
        self.fitted_values['Open Circuit Voltage V_oc (V)'] = self.fit_voc()
        self.fitted_values['Short Circuit Current I_sc (A)'] = self.fit_isc()
        self.fitted_values['Maximum Power P_max (W)'] = self.fit_pmax()
        self.fitted_values['Fill Factor'] = [self.get_fill_factor(self.fitted_values['Open Circuit Voltage V_oc (V)'][0],
                                             self.fitted_values['Short Circuit Current I_sc (A)'][0],
                                             self.fitted_values['Maximum Power P_max (W)'][0]), 0]
