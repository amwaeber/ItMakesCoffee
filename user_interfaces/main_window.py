import os
from PyQt5 import QtWidgets, QtGui

from user_interfaces.table_widget import TableWidget
from utility import config


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        config.read_config()
        self.init_ui()

    def init_ui(self):
        self.setWindowIcon(QtGui.QIcon(os.path.join(config.paths['icons'], 'coffee.png')))
        self.setWindowTitle("%s %s" % (config.global_confs['progname'], config.global_confs['progversion']))

        self.table_widget = TableWidget(self)  # create multiple document interface widget
        self.setCentralWidget(self.table_widget)
        self.showMaximized()

    def closeEvent(self, *args, **kwargs):
        super(QtWidgets.QMainWindow, self).closeEvent(*args, **kwargs)

        # Disconnect sensor before shutdown
        self.table_widget.tab_experiment.stop_sensor()

        # Save newly created experiment analyses
        for experiment in self.table_widget.tab_analysis.experiment_dict.values():
            experiment.save_pickle()

        # Update config ini with current paths
        config.write_config(save_path=str(self.table_widget.tab_experiment.directory),
                            plot_path=str(self.table_widget.tab_analysis.plot_directory),
                            export_path=str(self.table_widget.tab_analysis.export_directory),
                            arduino=str(self.table_widget.tab_experiment.sensor_cb.currentText()),
                            keithley=str(self.table_widget.tab_experiment.source_cb.currentText()))
