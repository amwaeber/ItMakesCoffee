# import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from scipy import optimize

from utility.conversions import timestamp_to_datetime_hour
from utility.data_import import Experiment, Trace


def isc_fit(raw_trace, n_points=3, m0=-1e-2):
    isc_idx = raw_trace.data.index[raw_trace.data['Current (A)'] ==
                                   raw_trace.values['Short Circuit Current I_sc (A)'][0]][0]
    idx_range = [0, isc_idx + n_points]
    slice_df = raw_trace.data[idx_range[0]:idx_range[1]]

    def linear(x, y0, m):
        return y0 + m * x

    popt, pcov = optimize.curve_fit(linear, slice_df['Voltage (V)'], slice_df['Current (A)'],
                                    p0=np.array([raw_trace.values['Short Circuit Current I_sc (A)'][0], m0]))
    # return 'Isc_fit', 'dIsc_fit', 'T_Isc', 'dT_Isc', 'Irrad1_Isc', 'dIrrad1_Isc',...
    return [popt[0], np.sqrt(np.diag(pcov))[0],
            slice_df['Temperature (C)'].mean(), slice_df['Temperature (C)'].std(),
            slice_df['Irradiance 1 (W/m2)'].mean(), slice_df['Irradiance 1 (W/m2)'].std(),
            slice_df['Irradiance 2 (W/m2)'].mean(), slice_df['Irradiance 2 (W/m2)'].std(),
            slice_df['Irradiance 3 (W/m2)'].mean(), slice_df['Irradiance 3 (W/m2)'].std(),
            slice_df['Irradiance 4 (W/m2)'].mean(), slice_df['Irradiance 4 (W/m2)'].std()]


def voc_fit(raw_trace, n_points=5, y00=1, a0=1, b0=1):
    voc_idx = raw_trace.data.index[raw_trace.data['Voltage (V)'] ==
                                   raw_trace.values['Open Circuit Voltage V_oc (V)'][0]][0]
    idx_range = [voc_idx - n_points, voc_idx + n_points]
    slice_df = raw_trace.data[idx_range[0]:idx_range[1]]

    def parabola(x, y0, a, b):
        return y0 + a * x + b * x ** 2

    popt, pcov = optimize.curve_fit(parabola, slice_df['Current (A)'], slice_df['Voltage (V)'],
                                    p0=np.array([y00, a0, b0]))
    # return 'Voc_fit', 'dVoc_fit', 'T_Voc', 'dT_Voc', 'Irrad1_Voc', 'dIrrad1_Voc',...
    return [popt[0], np.sqrt(np.diag(pcov))[0],
            slice_df['Temperature (C)'].mean(), slice_df['Temperature (C)'].std(),
            slice_df['Irradiance 1 (W/m2)'].mean(), slice_df['Irradiance 1 (W/m2)'].std(),
            slice_df['Irradiance 2 (W/m2)'].mean(), slice_df['Irradiance 2 (W/m2)'].std(),
            slice_df['Irradiance 3 (W/m2)'].mean(), slice_df['Irradiance 3 (W/m2)'].std(),
            slice_df['Irradiance 4 (W/m2)'].mean(), slice_df['Irradiance 4 (W/m2)'].std()]


def pmax_fit(raw_trace, n_points=10, i00=4e-5, vt0=7.5e-2, rsh0=150):

    pmax_idx = raw_trace.data.index[raw_trace.data['Power (W)'] == raw_trace.values['Maximum Power P_max (W)'][0]][0]
    idx_range = [pmax_idx - n_points, pmax_idx + n_points]
    slice_df = raw_trace.data[idx_range[0]:idx_range[1]]

    def shockley(v, iph, i0, vt):  # , rsh):
        return iph - i0 * np.exp(v / vt)  # - v / rsh

    popt, pcov = optimize.curve_fit(shockley, slice_df['Voltage (V)'], slice_df['Current (A)'],
                                    p0=np.array([raw_trace.values['Short Circuit Current I_sc (A)'][0], i00, vt0]))  # , rsh0]))
    voltage_pmax = optimize.minimize_scalar(lambda v: - v * shockley(v, *popt)).x
    # return 'Pmax_fit', 'T_Pmax', 'dT_Pmax', 'Irrad1_Pmax', 'dIrrad1_Pmax',...
    return [voltage_pmax * shockley(voltage_pmax, *popt),
            slice_df['Temperature (C)'].mean(), slice_df['Temperature (C)'].std(),
            slice_df['Irradiance 1 (W/m2)'].mean(), slice_df['Irradiance 1 (W/m2)'].std(),
            slice_df['Irradiance 2 (W/m2)'].mean(), slice_df['Irradiance 2 (W/m2)'].std(),
            slice_df['Irradiance 3 (W/m2)'].mean(), slice_df['Irradiance 3 (W/m2)'].std(),
            slice_df['Irradiance 4 (W/m2)'].mean(), slice_df['Irradiance 4 (W/m2)'].std()]


import_labels = {'Open Circuit Voltage V_oc (V)': ['Voc', 'dVoc'],
                 'Short Circuit Current I_sc (A)': ['Isc', 'dIsc'],
                 'Maximum Power P_max (W)': ['Pmax', 'dPmax'],
                 'Fill Factor': ['FF', 'dFF'],
                 'Average Temperature T_avg (C)': ['Tsample', 'dTsample'],
                 'Average Irradiance I_1_avg (W/m2)': ['Irrad1', 'dIrrad1'],
                 'Average Irradiance I_2_avg (W/m2)': ['Irrad2', 'dIrrad2'],
                 'Average Irradiance I_3_avg (W/m2)': ['Irrad3', 'dIrrad3'],
                 'Average Irradiance I_4_avg (W/m2)': ['Irrad4', 'dIrrad4']}

day_folder = 'C:\\Users\\amwae\\Lambda Energy Ltd Dropbox\\Lambda Energy Main Files\\Technology Development\\0_Data' \
             '\\Solar Simulator\\Films\\2020-03\\31-03-2020'
day_folder = 'C:\\Users\\amwae\\Lambda Energy Ltd Dropbox\\Lambda Energy Main Files\\Technology Development\\0_Data' \
             '\\Solar Simulator\\Calibration\\2020-08\\26-08-2020'
folders = [os.path.join(day_folder, folder) for folder in os.listdir(day_folder)
           if os.path.isdir(os.path.join(day_folder, folder))]
data = pd.DataFrame(columns=['Name', 'Trace', 'Time', 'Isc', 'dIsc', 'Isc_fit', 'dIsc_fit',
                             'Voc', 'dVoc', 'Voc_fit', 'dVoc_fit',
                             'Pmax', 'dPmax', 'Pmax_fit', 'dPmax_fit',
                             'FF', 'dFF', 'FF_fit', 'dFF_fit',
                             'Tsample', 'dTsample', 'T_Isc', 'dT_Isc', 'T_Voc', 'dT_Voc', 'T_Pmax', 'dT_Pmax',
                             'Irrad1', 'dIrrad1', 'Irrad1_Isc', 'dIrrad1_Isc', 'Irrad1_Voc', 'dIrrad1_Voc',
                             'Irrad1_Pmax', 'dIrrad1_Pmax', 'Irrad2', 'dIrrad2', 'Irrad2_Isc', 'dIrrad2_Isc',
                             'Irrad2_Voc', 'dIrrad2_Voc', 'Irrad2_Pmax', 'dIrrad2_Pmax', 'Irrad3', 'dIrrad3',
                             'Irrad3_Isc', 'dIrrad3_Isc', 'Irrad3_Voc', 'dIrrad3_Voc', 'Irrad3_Pmax', 'dIrrad3_Pmax',
                             'Irrad4', 'dIrrad4', 'Irrad4_Isc', 'dIrrad4_Isc', 'Irrad4_Voc', 'dIrrad4_Voc',
                             'Irrad4_Pmax', 'dIrrad4_Pmax'])

folders = [folders[-1]] # folders[:-2] + [folders[-1]]

for folder in folders:
    experiment = Experiment(folder_path=folder)
    for trace in experiment.traces.values():
        idx = len(data.index)
        data.loc[idx] = np.nan
        data.loc[idx]['Name'] = os.path.basename(folder)
        data.loc[idx]['Trace'] = trace.name
        data.loc[idx]['Time'] = timestamp_to_datetime_hour(trace.values['Time (s)'][0])
        for key, value in import_labels.items():
            data.loc[idx][value[0]], data.loc[idx][value[1]] = trace.values[key]
            data.loc[idx].replace(0, np.nan, inplace=True)
            data.loc[idx]['Isc_fit', 'dIsc_fit', 'T_Isc', 'dT_Isc', 'Irrad1_Isc', 'dIrrad1_Isc',
                          'Irrad2_Isc', 'dIrrad2_Isc', 'Irrad3_Isc', 'dIrrad3_Isc', 'Irrad4_Isc',
                          'dIrrad4_Isc'] = isc_fit(trace)
            data.loc[idx]['Voc_fit', 'dVoc_fit', 'T_Voc', 'dT_Voc', 'Irrad1_Voc', 'dIrrad1_Voc',
                          'Irrad2_Voc', 'dIrrad2_Voc', 'Irrad3_Voc', 'dIrrad3_Voc', 'Irrad4_Voc',
                          'dIrrad4_Voc'] = voc_fit(trace)
            data.loc[idx]['Pmax_fit', 'T_Pmax', 'dT_Pmax', 'Irrad1_Pmax', 'dIrrad1_Pmax',
                          'Irrad2_Pmax', 'dIrrad2_Pmax', 'Irrad3_Pmax', 'dIrrad3_Pmax', 'Irrad4_Pmax',
                          'dIrrad4_Pmax'] = pmax_fit(trace)
            data.loc[idx]['FF_fit'] = data.loc[idx]['Pmax_fit'] / (data.loc[idx]['Isc_fit'] * data.loc[idx]['Voc_fit'])
    idx = len(data.index)
    data.loc[idx] = np.nan
    data.loc[idx]['Name'] = os.path.basename(folder)
    data.loc[idx]['Trace'] = 'Average'
    data.loc[idx]['Time'] = timestamp_to_datetime_hour(experiment.values['Time (s)'][0])
    for key, value in import_labels.items():
        data.loc[idx][value[0]], data.loc[idx][value[1]] = experiment.values[key]
    for key in ['Isc_fit', 'T_Isc', 'Irrad1_Isc', 'Irrad2_Isc', 'Irrad3_Isc', 'Irrad4_Isc',
                'Voc_fit', 'FF_fit', 'T_Voc', 'Irrad1_Voc', 'Irrad2_Voc', 'Irrad3_Voc', 'Irrad4_Voc',
                'Pmax_fit', 'T_Pmax', 'Irrad1_Pmax', 'Irrad2_Pmax', 'Irrad3_Pmax', 'Irrad4_Pmax']:
        data.loc[idx][key] = data.loc[idx-experiment.n_traces[0]:idx-1][key].mean()
        data.loc[idx]['d%s' % key] = data.loc[idx-experiment.n_traces[0]:idx-1][key].std()
for key in ['Isc', 'dIsc', 'Isc_fit', 'dIsc_fit', 'Pmax', 'dPmax', 'Pmax_fit', 'dPmax_fit']:
    data[key] *= 1e3
data.to_excel(os.path.join(day_folder, "Summary.xlsx"))
