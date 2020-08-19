import datetime
from PyQt5 import QtWidgets

from utility.config import defaults, write_config


class InfoWidget(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(InfoWidget, self).__init__(parent)

        self.info = list()

        self.setWindowTitle('Experiment Info')

        vbox_total = QtWidgets.QVBoxLayout()

        grid_experiment = QtWidgets.QGridLayout()
        self.experiment_name_label = QtWidgets.QLabel('Experiment Name', self)
        grid_experiment.addWidget(self.experiment_name_label, 0, 0)
        self.experiment_name_edit = QtWidgets.QLineEdit('%s' % defaults['info'][0][0], self)
        self.experiment_name_edit.setFixedWidth(80)
        grid_experiment.addWidget(self.experiment_name_edit, 0, 1)
        self.experiment_date_label = QtWidgets.QLabel('Experiment Date', self)
        grid_experiment.addWidget(self.experiment_date_label, 0, 2)
        self.experiment_date_edit = QtWidgets.QLineEdit('%s' % datetime.date.today(), self)
        self.experiment_date_edit.setFixedWidth(80)
        grid_experiment.addWidget(self.experiment_date_edit, 0, 3)
        vbox_total.addLayout(grid_experiment)

        grid_layout = QtWidgets.QGridLayout()
        self.film_id_label = QtWidgets.QLabel('Film ID', self)
        grid_layout.addWidget(self.film_id_label, 1, 0)
        self.film_id_edit = QtWidgets.QLineEdit('%s' % defaults['info'][2][0], self)
        self.film_id_edit.setFixedWidth(80)
        grid_layout.addWidget(self.film_id_edit, 1, 1)
        self.pv_cell_id_label = QtWidgets.QLabel('PV Cell ID', self)
        grid_layout.addWidget(self.pv_cell_id_label, 1, 2)
        self.pv_cell_id_edit = QtWidgets.QLineEdit('%s' % defaults['info'][3][0], self)
        self.pv_cell_id_edit.setFixedWidth(80)
        grid_layout.addWidget(self.pv_cell_id_edit, 1, 3)

        self.setup_location_label = QtWidgets.QLabel('Setup Location', self)
        grid_layout.addWidget(self.setup_location_label, 2, 0)
        self.setup_location_edit = QtWidgets.QLineEdit('%s' % defaults['info'][4][0], self)
        self.setup_location_edit.setFixedWidth(80)
        grid_layout.addWidget(self.setup_location_edit, 2, 1)
        self.setup_calibrated_label = QtWidgets.QLabel('Calibration Date', self)
        grid_layout.addWidget(self.setup_calibrated_label, 2, 2)
        self.setup_calibrated_edit = QtWidgets.QLineEdit('%s' % defaults['info'][5][0], self)
        self.setup_calibrated_edit.setFixedWidth(80)
        grid_layout.addWidget(self.setup_calibrated_edit, 2, 3)
        self.setup_suns_label = QtWidgets.QLabel('Calibration (suns)', self)
        grid_layout.addWidget(self.setup_suns_label, 3, 0)
        self.setup_suns_edit = QtWidgets.QLineEdit('%s' % defaults['info'][6][0], self)
        self.setup_suns_edit.setFixedWidth(80)
        grid_layout.addWidget(self.setup_suns_edit, 3, 1)
        self.setup_pid_setpoint_label = QtWidgets.QLabel('PID setpoint (C)', self)
        grid_layout.addWidget(self.setup_pid_setpoint_label, 3, 2)
        self.setup_pid_setpoint_edit = QtWidgets.QLineEdit('%s' % defaults['info'][7][0], self)
        self.setup_pid_setpoint_edit.setFixedWidth(80)
        grid_layout.addWidget(self.setup_pid_setpoint_edit, 3, 3)

        self.room_temperature_label = QtWidgets.QLabel('Room Temperature (C)', self)
        grid_layout.addWidget(self.room_temperature_label, 4, 0)
        self.room_temperature_edit = QtWidgets.QLineEdit('%s' % defaults['info'][8][0], self)
        self.room_temperature_edit.setFixedWidth(80)
        grid_layout.addWidget(self.room_temperature_edit, 4, 1)
        self.room_humidity_label = QtWidgets.QLabel('Room Humidity', self)
        grid_layout.addWidget(self.room_humidity_label, 4, 2)
        self.room_humidity_edit = QtWidgets.QLineEdit('%s' % defaults['info'][9][0], self)
        self.room_humidity_edit.setFixedWidth(80)
        grid_layout.addWidget(self.room_humidity_edit, 4, 3)
        vbox_total.addLayout(grid_layout)

        self.buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        vbox_total.addWidget(self.buttonBox)

        self.setLayout(vbox_total)

    def accept(self):
        defaults['info'] = [[self.experiment_name_edit.text()], [self.experiment_date_edit.text()],
                            [self.film_id_edit.text()], [self.pv_cell_id_edit.text()],
                            [self.setup_location_edit.text()], [self.setup_calibrated_edit.text()],
                            [self.setup_suns_edit.text()], [self.setup_pid_setpoint_edit.text()],
                            [self.room_temperature_edit.text()], [self.room_humidity_edit.text()]]
        write_config()
        super(InfoWidget, self).accept()
