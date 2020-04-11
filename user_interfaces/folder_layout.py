import os
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.Qt import Qt

from utility.config import paths
from utility.folder_functions import get_list_of_csv


class FolderLayout(QtWidgets.QHBoxLayout):

    def __init__(self, parent=None):
        super(FolderLayout, self).__init__(parent)

        self.selected_file_path = ''
        self.reference_files = list()

        self.folder_model = QtWidgets.QFileSystemModel()
        self.folder_model.setRootPath('')
        self.folder_tree = QtWidgets.QTreeView()
        self.folder_tree.setModel(self.folder_model)

        self.folder_tree.setAnimated(False)
        self.folder_tree.setIndentation(20)
        self.folder_tree.setSortingEnabled(True)
        self.folder_tree.clicked.connect(self.select_files)

        self.add_reference_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'right_double_arrow.png')), '')
        self.add_reference_button.clicked.connect(self.add_reference)
        self.add_reference_button.setToolTip('Add reference')
        self.remove_reference_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'left_double_arrow.png')), '')
        self.remove_reference_button.clicked.connect(self.remove_reference)
        self.add_reference_button.setToolTip('Remove reference')

        self.reference_tree = QtWidgets.QTreeWidget()
        self.headerItem = QtWidgets.QTreeWidgetItem()
        self.item = QtWidgets.QTreeWidgetItem()

        for i in range(3):
            parent = QtWidgets.QTreeWidgetItem(self.reference_tree)
            parent.setText(0, "Parent {}".format(i))
            parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            for x in range(5):
                child = QtWidgets.QTreeWidgetItem(parent)
                child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                child.setText(0, "Child {}".format(x))
                child.setCheckState(0, Qt.Unchecked)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.add_reference_button)
        vbox.addWidget(self.remove_reference_button)

        self.addWidget(self.folder_tree)
        self.addLayout(vbox)
        self.addWidget(self.reference_tree)
        # self.addWidget(self.selection_tree)

    def add_reference(self):
        self.reference_files = get_list_of_csv(self.selected_file_path)
        print(self.reference_files)

    def remove_reference(self):
        pass

    def select_files(self, signal):
        self.selected_file_path = self.folder_tree.model().filePath(signal)
