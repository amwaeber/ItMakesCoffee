from PyQt5 import QtWidgets
from PyQt5.Qt import Qt


class FolderLayout(QtWidgets.QVBoxLayout):

    def __init__(self, parent=None):
        super(FolderLayout, self).__init__(parent)

        self.tree = QtWidgets.QTreeWidget()
        self.headerItem = QtWidgets.QTreeWidgetItem()
        self.item = QtWidgets.QTreeWidgetItem()

        for i in range(3):
            parent = QtWidgets.QTreeWidgetItem(self.tree)
            parent.setText(0, "Parent {}".format(i))
            parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            for x in range(5):
                child = QtWidgets.QTreeWidgetItem(parent)
                child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                child.setText(0, "Child {}".format(x))
                child.setCheckState(0, Qt.Unchecked)

        self.addWidget(self.tree)
