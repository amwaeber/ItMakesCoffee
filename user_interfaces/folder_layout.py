import os
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.Qt import Qt

from utility.config import paths
from utility.folder_functions import get_list_of_csv


class Folders(QtWidgets.QWidget):
    file_paths = QtCore.pyqtSignal(list, list)

    def __init__(self, parent=None):
        super(Folders, self).__init__(parent)

        self.picked_file_path = ''
        self.reference_files = list()
        self.selection_files = list()

        self.folder_group_box = QtWidgets.QGroupBox('Folders')
        self.folder_model = QtWidgets.QFileSystemModel()
        self.folder_model.setRootPath('')
        self.folder_tree = QtWidgets.QTreeView()
        self.folder_tree.setModel(self.folder_model)
        self.folder_tree.setCurrentIndex(self.folder_model.index(paths['last_data']))

        self.folder_tree.setAnimated(False)
        self.folder_tree.setIndentation(20)
        self.folder_tree.setSortingEnabled(True)
        self.folder_tree.setColumnWidth(0, 500)
        self.folder_tree.clicked.connect(self.pick_files)
        self.folder_layout = QtWidgets.QHBoxLayout()
        self.folder_layout.addWidget(self.folder_tree)
        self.folder_group_box.setLayout(self.folder_layout)

        self.add_reference_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'right_double_arrow.png')), '')
        self.add_reference_button.clicked.connect(self.add_reference)
        self.add_reference_button.setToolTip('Add reference')
        self.remove_reference_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'left_double_arrow.png')), '')
        self.remove_reference_button.clicked.connect(self.remove_reference)
        self.remove_reference_button.setToolTip('Remove reference')

        self.reference_group_box = QtWidgets.QGroupBox('Reference curve')
        self.reference_tree = QtWidgets.QTreeWidget()
        self.reference_tree.header().hide()
        self.reference_layout = QtWidgets.QHBoxLayout()
        self.reference_layout.addWidget(self.reference_tree)
        self.reference_group_box.setLayout(self.reference_layout)

        self.add_selection_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'right_double_arrow.png')), '')
        self.add_selection_button.clicked.connect(self.add_selection)
        self.add_selection_button.setToolTip('Add selection')
        self.remove_selection_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'left_double_arrow.png')), '')
        self.remove_selection_button.clicked.connect(self.remove_selection)
        self.remove_selection_button.setToolTip('Remove selection')

        self.selection_group_box = QtWidgets.QGroupBox('Curves for Analysis')
        self.selection_tree = QtWidgets.QTreeWidget()
        self.selection_layout = QtWidgets.QHBoxLayout()
        self.selection_layout.addWidget(self.selection_tree)
        self.selection_group_box.setLayout(self.selection_layout)
        self.selection_tree.header().hide()

        vbox = QtWidgets.QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(self.add_reference_button)
        vbox.addWidget(self.remove_reference_button)
        vbox.addStretch(1)
        hbox = QtWidgets.QHBoxLayout()
        hbox.addLayout(vbox)
        hbox.addWidget(self.reference_group_box)

        vbox2 = QtWidgets.QVBoxLayout()
        vbox2.addStretch(1)
        vbox2.addWidget(self.add_selection_button)
        vbox2.addWidget(self.remove_selection_button)
        vbox2.addStretch(1)
        hbox2 = QtWidgets.QHBoxLayout()
        hbox2.addLayout(vbox2)
        hbox2.addWidget(self.selection_group_box)

        vbox_large = QtWidgets.QVBoxLayout()
        vbox_large.addLayout(hbox)
        vbox_large.addLayout(hbox2)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.folder_group_box)
        hbox.addLayout(vbox_large)
        self.setLayout(hbox)

    def add_reference(self):
        csv_list = get_list_of_csv(self.picked_file_path)
        if csv_list:
            self.reference_files = self.reference_files + csv_list
            self.reference_files = list(dict.fromkeys(self.reference_files))
            self.update_tree(self.reference_tree, self.reference_files)

    def add_selection(self):
        csv_list = get_list_of_csv(self.picked_file_path)
        if csv_list:
            self.selection_files = self.selection_files + csv_list
            self.selection_files = list(dict.fromkeys(self.selection_files))
            self.update_tree(self.selection_tree, self.selection_files)

    @QtCore.pyqtSlot()
    def get_paths(self):
        self.file_paths.emit(self.reference_files, self.selection_files)

    def get_picked_reference(self):
        picked_reference = list()
        for item in self.reference_tree.findItems("", Qt.MatchContains | Qt.MatchRecursive):
            if item.checkState(0) == 2:
                picked_reference = [file for file in self.reference_files if item.text(0) in file]
        return picked_reference

    def get_picked_selection(self):
        picked_selection = list()
        for item in self.selection_tree.findItems("", Qt.MatchContains | Qt.MatchRecursive):
            if item.checkState(0) == 2:
                picked_selection = [file for file in self.selection_files if item.text(0) in file]
        return picked_selection

    def remove_reference(self):
        for item in self.reference_tree.findItems("", Qt.MatchContains | Qt.MatchRecursive):
            if item.checkState(0) == 2:
                self.reference_files = [file for file in self.reference_files if not(item.text(0) in file)]
        self.update_tree(self.reference_tree, self.reference_files)

    def remove_selection(self):
        for item in self.selection_tree.findItems("", Qt.MatchContains | Qt.MatchRecursive):
            if item.checkState(0) == 2:
                self.selection_files = [file for file in self.selection_files if not (item.text(0) in file)]
        self.update_tree(self.selection_tree, self.selection_files)

    def pick_files(self, signal):
        self.picked_file_path = self.folder_tree.model().filePath(signal)

    @staticmethod
    def update_tree(tree_widget, file_paths):
        tree_widget.clear()
        for path in file_paths:
            dirname = os.path.dirname(path)
            folder = tree_widget.findItems(dirname, QtCore.Qt.MatchExactly)
            if folder:
                file = QtWidgets.QTreeWidgetItem(folder[0])
                file.setText(0, os.path.basename(path))
                file.setFlags(int(file.flags()) | Qt.ItemIsUserCheckable)
                file.setCheckState(0, Qt.Unchecked)
            else:
                folder = QtWidgets.QTreeWidgetItem(tree_widget)
                folder.setText(0, dirname)
                folder.setFlags(int(folder.flags()) | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
                file = QtWidgets.QTreeWidgetItem(folder)
                file.setText(0, os.path.basename(path))
                file.setFlags(int(file.flags()) | Qt.ItemIsUserCheckable)
                file.setCheckState(0, Qt.Unchecked)
