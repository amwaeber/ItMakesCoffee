import sys

from PyQt5 import QtWidgets

from user_interfaces.main_window import MainWindow


def main():
    app = QtWidgets.QApplication(sys.argv)
    # app.aboutToQuit.connect()  # TODO: sort orderly shutdown, disconnecting COM port etc
    window = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':  # runs only if file is executed, not when it's imported
    main()
