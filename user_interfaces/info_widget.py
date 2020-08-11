import datetime
from PyQt5 import QtWidgets

from utility.save_info import info_defaults


class InfoWidget(QtWidgets.QDialog):

    def __init__(self, parent=None, defaults=None):
        super(InfoWidget, self).__init__(parent)

        defaults = info_defaults if defaults is None else defaults
        self.info = list()

        self.setWindowTitle('Experiment Info')

        vbox_total = QtWidgets.QVBoxLayout()

        grid_experiment = QtWidgets.QGridLayout()
        self.experiment_name_label = QtWidgets.QLabel('Experiment Name', self)
        grid_experiment.addWidget(self.experiment_name_label, 0, 0)
        self.experiment_name_edit = QtWidgets.QLineEdit('%s' % defaults[0][0], self)
        self.experiment_name_edit.setFixedWidth(80)
        grid_experiment.addWidget(self.experiment_name_edit, 0, 1)
        self.experiment_date_label = QtWidgets.QLabel('Experiment Date', self)
        grid_experiment.addWidget(self.experiment_date_label, 0, 2)
        self.experiment_date_edit = QtWidgets.QLineEdit('%s' % defaults[1][0], self)
        self.experiment_date_edit.setFixedWidth(80)
        grid_experiment.addWidget(self.experiment_date_edit, 0, 3)
        vbox_total.addLayout(grid_experiment)

        separator = QtWidgets.QFrame()
        separator.Shape(QtWidgets.QFrame.HLine)
        separator.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        vbox_total.addWidget(separator)

        grid_layout = QtWidgets.QGridLayout()
        self.film_id_label = QtWidgets.QLabel('Film ID', self)
        grid_layout.addWidget(self.film_id_label, 1, 0)
        self.film_id_edit = QtWidgets.QLineEdit('%s' % defaults[2][0], self)
        self.film_id_edit.setFixedWidth(80)
        grid_layout.addWidget(self.film_id_edit, 1, 1)
        self.film_date_label = QtWidgets.QLabel('Film Date', self)
        grid_layout.addWidget(self.film_date_label, 1, 2)
        self.film_date_edit = QtWidgets.QLineEdit('%s' % defaults[3][0], self)
        self.film_date_edit.setFixedWidth(80)
        grid_layout.addWidget(self.film_date_edit, 1, 3)
        self.film_thickness_label = QtWidgets.QLabel('Film Thickness (mm)', self)
        grid_layout.addWidget(self.film_thickness_label, 2, 0)
        self.film_thickness_edit = QtWidgets.QLineEdit('%s' % defaults[4][0], self)
        self.film_thickness_edit.setFixedWidth(80)
        grid_layout.addWidget(self.film_thickness_edit, 2, 1)
        self.film_area_label = QtWidgets.QLabel('Film Area (cm2)', self)
        grid_layout.addWidget(self.film_area_label, 2, 2)
        self.film_area_edit = QtWidgets.QLineEdit('%s' % defaults[5][0], self)
        self.film_area_edit.setFixedWidth(80)
        grid_layout.addWidget(self.film_area_edit, 2, 3)
        self.film_matrix_label = QtWidgets.QLabel('Film Matrix', self)
        grid_layout.addWidget(self.film_matrix_label, 3, 0)
        self.film_matrix_edit = QtWidgets.QLineEdit('%s' % defaults[6][0], self)
        self.film_matrix_edit.setFixedWidth(80)
        grid_layout.addWidget(self.film_matrix_edit, 3, 1)
        self.film_qds_label = QtWidgets.QLabel('Film QDs', self)
        grid_layout.addWidget(self.film_qds_label, 3, 2)
        self.film_qds_edit = QtWidgets.QLineEdit('%s' % defaults[7][0], self)
        self.film_qds_edit.setFixedWidth(80)
        grid_layout.addWidget(self.film_qds_edit, 3, 3)
        self.film_qd_concentration_label = QtWidgets.QLabel('Film QD Concentration (mg/g)', self)
        grid_layout.addWidget(self.film_qd_concentration_label, 4, 0)
        self.film_qd_concentration_edit = QtWidgets.QLineEdit('%s' % defaults[8][0], self)
        self.film_qd_concentration_edit.setFixedWidth(80)
        grid_layout.addWidget(self.film_qd_concentration_edit, 4, 1)
        self.film_qd_emission_label = QtWidgets.QLabel('Film QD Emission (nm)', self)
        grid_layout.addWidget(self.film_qd_emission_label, 4, 2)
        self.film_qd_emission_edit = QtWidgets.QLineEdit('%s' % defaults[9][0], self)
        self.film_qd_emission_edit.setFixedWidth(80)
        grid_layout.addWidget(self.film_qd_emission_edit, 4, 3)
        self.film_solvent_label = QtWidgets.QLabel('Film Solvent', self)
        grid_layout.addWidget(self.film_solvent_label, 5, 0)
        self.film_solvent_edit = QtWidgets.QLineEdit('%s' % defaults[10][0], self)
        self.film_solvent_edit.setFixedWidth(80)
        grid_layout.addWidget(self.film_solvent_edit, 5, 1)

        self.pv_cell_id_label = QtWidgets.QLabel('PV Cell ID', self)
        grid_layout.addWidget(self.pv_cell_id_label, 6, 0)
        self.pv_cell_id_edit = QtWidgets.QLineEdit('%s' % defaults[11][0], self)
        self.pv_cell_id_edit.setFixedWidth(80)
        grid_layout.addWidget(self.pv_cell_id_edit, 6, 1)
        self.pv_cell_type_label = QtWidgets.QLabel('PV cell type', self)
        grid_layout.addWidget(self.pv_cell_type_label, 6, 2)
        self.pv_cell_type_edit = QtWidgets.QLineEdit('%s' % defaults[12][0], self)
        self.pv_cell_type_edit.setFixedWidth(80)
        grid_layout.addWidget(self.pv_cell_type_edit, 6, 3)
        self.pv_cell_area_label = QtWidgets.QLabel('PV cell area (cm2)', self)
        grid_layout.addWidget(self.pv_cell_area_label, 7, 0)
        self.pv_cell_area_edit = QtWidgets.QLineEdit('%s' % defaults[13][0], self)
        self.pv_cell_area_edit.setFixedWidth(80)
        grid_layout.addWidget(self.pv_cell_area_edit, 7, 1)

        self.setup_location_label = QtWidgets.QLabel('Setup Location', self)
        grid_layout.addWidget(self.setup_location_label, 8, 0)
        self.setup_location_edit = QtWidgets.QLineEdit('%s' % defaults[14][0], self)
        self.setup_location_edit.setFixedWidth(80)
        grid_layout.addWidget(self.setup_location_edit, 8, 1)
        self.setup_calibrated_label = QtWidgets.QLabel('Calibration Date', self)
        grid_layout.addWidget(self.setup_calibrated_label, 8, 2)
        self.setup_calibrated_edit = QtWidgets.QLineEdit('%s' % defaults[15][0], self)
        self.setup_calibrated_edit.setFixedWidth(80)
        grid_layout.addWidget(self.setup_calibrated_edit, 8, 3)
        self.setup_suns_label = QtWidgets.QLabel('Calibration (suns)', self)
        grid_layout.addWidget(self.setup_suns_label, 9, 0)
        self.setup_suns_edit = QtWidgets.QLineEdit('%s' % defaults[16][0], self)
        self.setup_suns_edit.setFixedWidth(80)
        grid_layout.addWidget(self.setup_suns_edit, 9, 1)
        self.setup_pid_setpoint_label = QtWidgets.QLabel('PID setpoint (C)', self)
        grid_layout.addWidget(self.setup_pid_setpoint_label, 9, 2)
        self.setup_pid_setpoint_edit = QtWidgets.QLineEdit('%s' % defaults[17][0], self)
        self.setup_pid_setpoint_edit.setFixedWidth(80)
        grid_layout.addWidget(self.setup_pid_setpoint_edit, 9, 3)

        self.room_temperature_label = QtWidgets.QLabel('Room Temperature (C)', self)
        grid_layout.addWidget(self.room_temperature_label, 10, 0)
        self.room_temperature_edit = QtWidgets.QLineEdit('%s' % defaults[18][0], self)
        self.room_temperature_edit.setFixedWidth(80)
        grid_layout.addWidget(self.room_temperature_edit, 10, 1)
        self.room_humidity_label = QtWidgets.QLabel('Room Humidity', self)
        grid_layout.addWidget(self.room_humidity_label, 10, 2)
        self.room_humidity_edit = QtWidgets.QLineEdit('%s' % defaults[19][0], self)
        self.room_humidity_edit.setFixedWidth(80)
        grid_layout.addWidget(self.room_humidity_edit, 10, 3)
        vbox_total.addLayout(grid_layout)

        self.buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        vbox_total.addWidget(self.buttonBox)

        self.setLayout(vbox_total)

    def accept(self):
        self.info = [[self.experiment_name_edit.text()], [self.experiment_date_edit.text()],
                     [self.film_id_edit.text()], [self.film_date_edit.text()],
                     [self.film_thickness_edit.text()], [self.film_area_edit.text()],
                     [self.film_matrix_edit.text()], [self.film_qds_edit.text()],
                     [self.film_qd_concentration_edit.text()], [self.film_qd_emission_edit.text()],
                     [self.film_solvent_edit.text()],
                     [self.pv_cell_id_edit.text()], [self.pv_cell_type_edit.text()],
                     [self.pv_cell_area_edit.text()],
                     [self.setup_location_edit.text()], [self.setup_calibrated_edit.text()],
                     [self.setup_suns_edit.text()], [self.setup_pid_setpoint_edit.text()],
                     [self.room_temperature_edit.text()], [self.room_humidity_edit.text()]]
        super(InfoWidget, self).accept()
