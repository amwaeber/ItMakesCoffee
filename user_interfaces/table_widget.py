from PyQt5 import QtWidgets

from user_interfaces.analysis_tab import Analysis
from user_interfaces.experiment_tab import Experiment


class TableWidget(QtWidgets.QWidget):

    def __init__(self, parent):
        super(TableWidget, self).__init__(parent)

        self.layout = QtWidgets.QVBoxLayout(self)

        # Initialize tab screen
        self.tabs = QtWidgets.QTabWidget()

        self.tab_experiment = Experiment(self)
        self.tabs.addTab(self.tab_experiment, "Experiment")

        self.tab_analysis = Analysis(self)
        self.tabs.addTab(self.tab_analysis, "Analysis")

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
