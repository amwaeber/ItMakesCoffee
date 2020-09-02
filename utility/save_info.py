import datetime
import pandas as pd

info_pars = ['folder', 'experiment_name', 'experiment_date', 'film_id', 'pv_cell_id', 'setup_location',
             'setup_calibrated', 'setup_suns', 'pid_proportional_band', 'pid_integral',
             'pid_derivative', 'pid_fuzzy_overshoot', 'pid_heat_tcr1', 'pid_cool_tcr2',
             'pid_setpoint', 'room_temperature', 'room_humidity']

info_defaults = [['.'], ['N/A'], [datetime.date.today()], ['unknown'], ['unknown'], ['Vinery Way'],
                 [datetime.date(1970, 1, 1)], [-1], [8], [209], [38], [0.46], [0.1], [0.1], [25],
                 [-1], [-1]]


def save_info(file_path='.', **kwargs):
    df = pd.DataFrame({par: kwargs.get(par, info_defaults[i]) for i, par in enumerate(info_pars)})
    df.to_csv(file_path)
