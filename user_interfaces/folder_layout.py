import os
from PyQt5 import QtWidgets, QtGui
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
        self.folder_tree.setCurrentIndex(self.folder_model.index(paths['last_data']))

        self.folder_tree.setAnimated(False)
        self.folder_tree.setIndentation(20)
        self.folder_tree.setSortingEnabled(True)
        self.folder_tree.setColumnWidth(0, 500)
        self.folder_tree.clicked.connect(self.select_files)

        self.add_reference_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'right_double_arrow.png')), '')
        self.add_reference_button.clicked.connect(self.add_reference)
        self.add_reference_button.setToolTip('Add reference')
        self.remove_reference_button = QtWidgets.QPushButton(
            QtGui.QIcon(os.path.join(paths['icons'], 'left_double_arrow.png')), '')
        self.remove_reference_button.clicked.connect(self.remove_reference)
        self.add_reference_button.setToolTip('Remove reference')

        self.reference_group_box = QtWidgets.QGroupBox('Reference curve')
        self.reference_tree = QtWidgets.QTreeWidget()
        self.reference_layout = QtWidgets.QHBoxLayout()
        self.reference_layout.addWidget(self.reference_tree)
        self.reference_group_box.setLayout(self.reference_layout)

        self.reference_tree.header().hide()

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.add_reference_button)
        vbox.addWidget(self.remove_reference_button)

        self.addWidget(self.folder_tree)
        self.addLayout(vbox)
        self.addWidget(self.reference_group_box)
        # self.addWidget(self.selection_tree)

    def add_reference(self):
        csv_list = get_list_of_csv(self.selected_file_path)
        if csv_list:
            self.reference_files = self.reference_files + csv_list
            self.reference_files = list(dict.fromkeys(self.reference_files))
            self.update_tree(self.reference_tree, self.reference_files)
        print(self.reference_files)

    def remove_reference(self):
        pass

    def select_files(self, signal):
        self.selected_file_path = self.folder_tree.model().filePath(signal)

    def update_tree(self, tree_widget, file_paths):
        tree_widget.clear()
        i_dir = 0
        for path in file_paths:
            if os.path.isdir(path):
                folder = QtWidgets.QTreeWidgetItem(tree_widget)
                folder.setText(0, path)
                folder.setFlags(folder.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
                i_dir = i_dir + 1
            elif os.path.isfile(path):
                if i_dir == 0:
                    file = QtWidgets.QTreeWidgetItem(tree_widget)
                else:
                    file = QtWidgets.QTreeWidgetItem(folder)
                file.setText(0, os.path.basename(path))
                file.setFlags(file.flags() | Qt.ItemIsUserCheckable)
                file.setCheckState(0, Qt.Unchecked)

'C:/Users/amwae/Python/Lambda/test/03-04-2020/PV 1st/IV Characterizer-1 Run 667 2020-04-03T15.28.37.csv'
'C:/Users/amwae/Python/Lambda/test/03-04-2020/PV 1st\\IV Characterizer-1 Run 667 2020-04-03T15.28.37.csv'