from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.Qt import Qt


class ItemSignal(QtCore.QObject):
    itemChecked = QtCore.pyqtSignal(object, int)


class TreeWidgetItem(QtWidgets.QTreeWidgetItem):
    itemChecked = QtCore.pyqtSignal(object, int)

    def __init__(self, signal, *args, **kwargs):
        QtWidgets.QTreeWidgetItem.__init__(self, *args, **kwargs)
        self.signal = signal

    def setData(self, column, role, value):
        state = self.checkState(column)
        QtWidgets.QTreeWidgetItem.setData(self, column, role, value)
        if role == Qt.CheckStateRole and state != self.checkState(column):
            self.signal.itemChecked.emit(self, column)
