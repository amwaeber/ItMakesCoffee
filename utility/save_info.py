import datetime
import pandas as pd

info_pars = ['experiment_name', 'experiment_date', 'film_id', 'film_date', 'film_thickness', 'film_area',
             'film_matrix', 'film_qds', 'film_qd_concentration', 'film_qd_emission', 'film_solvent', 'pv_cell_id',
             'pv_cell_type', 'pv_cell_area', 'setup_location', 'setup_calibrated', 'setup_suns', 'setup_pid_setpoint',
             'room_temperature', 'room_humidity']

info_defaults = [['N/A'], [datetime.date.today()], ['unknown'], [datetime.date(1970, 1, 1)], [-1], [-1],
                 ['unknown'], ['unknown'], [-1], [-1], ['unknown'], ['unknown'], ['mc-Si'], [-1], ['Vinery Way'],
                 [datetime.date(1970, 1, 1)], [-1], [25], [-1], [-1]]


def save_info(file_path='.', **kwargs):
    df = pd.DataFrame({par: kwargs.get(par, info_defaults[i]) for i, par in enumerate(info_pars)})
    df.to_csv(file_path)
