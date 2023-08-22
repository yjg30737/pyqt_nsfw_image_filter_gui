import os, sys

from findPathWidget import FindPathWidget
from script import NSFWModelClass
from notifier import NotifierWidget

# Get the absolute path of the current script file
script_path = os.path.abspath(__file__)

# Get the root directory by going up one level from the script directory
project_root = os.path.dirname(os.path.dirname(script_path))

sys.path.insert(0, project_root)
sys.path.insert(0, os.getcwd())  # Add the current directory as well

from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication, QVBoxLayout, QWidget, QMessageBox, QSystemTrayIcon, \
    QMenu, QAction
from PyQt5.QtCore import QThread, QCoreApplication, Qt, pyqtSignal

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)  # HighDPI support

QApplication.setFont(QFont('Arial', 12))
QApplication.setWindowIcon(QIcon('logo.svg'))


class Thread(QThread):
    afterTaskOver = pyqtSignal(list, list)

    def __init__(self, directory: str, c: NSFWModelClass):
        super(Thread, self).__init__()
        self.__directory = directory
        self.__c = c

    def run(self):
        try:
            result_dict = self.__c.filter_nsfw_image_in_directory(self.__directory, recursive=True)
            self.__c.backup_files_and_remove_nsfw_files(result_dict)
            files_remove = [os.path.relpath(k) for k, v in result_dict.items() if v == 'nsfw']
            files_not_remove = list(set([os.path.relpath(k) for k in result_dict.keys()])-set(files_remove))
            self.afterTaskOver.emit(files_remove, files_not_remove)
        except Exception as e:
            raise Exception(e)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        filename = 'nsfw.299x299.h5'
        self.__c = NSFWModelClass()
        self.__c.set_model(filename)

    def __initUi(self):
        self.setWindowTitle('NSFW Remover')
        self.__findPathWidget = FindPathWidget()
        self.__findPathWidget.setAsDirectory(True)
        self.__findPathWidget.layout().setContentsMargins(0, 0, 0, 0)

        self.__filterBtn = QPushButton('Filter')
        self.__filterBtn.clicked.connect(self.__run)

        lay = QVBoxLayout()
        lay.addWidget(self.__findPathWidget)
        lay.setSpacing(2)
        lay.addWidget(self.__filterBtn)
        lay.setAlignment(Qt.AlignTop)

        mainWidget = QWidget()
        mainWidget.setLayout(lay)

        self.setCentralWidget(mainWidget)

        self.__setTrayMenu()
        QApplication.setQuitOnLastWindowClosed(False)

        self.setFixedSize(self.sizeHint())

    def __setTrayMenu(self):
        # background app
        menu = QMenu()

        action = QAction("Quit", self)
        action.setIcon(QIcon('close.svg'))

        action.triggered.connect(app.quit)

        menu.addAction(action)

        tray_icon = QSystemTrayIcon(app)
        tray_icon.setIcon(QIcon('logo.svg'))
        tray_icon.activated.connect(self.__activated)

        tray_icon.setContextMenu(menu)

        tray_icon.show()

    def __activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()

    def __run(self):
        try:
            directory = self.__findPathWidget.getLineEdit().text()
            self.__t = Thread(directory, self.__c)
            self.__t.started.connect(self.__started)
            self.__t.afterTaskOver.connect(self.__afterTaskOver)
            self.__t.finished.connect(self.__finished)
            self.__t.start()
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def __started(self):
        print('started')
        self.__filterBtn.setEnabled(False)

    def __afterTaskOver(self, files_remove, files_not_remove):
        files_not_remove_str = '\n'.join(files_not_remove)
        files_remove_str = '\n'.join(files_remove)
        text = f'These files were not removed:\n\n' \
               f'{files_not_remove_str}\n\n' \
               f'These files got removed:\n\n' \
               f'{files_remove_str}'
        QMessageBox.information(self, 'Complete!', text)

    def __finished(self):
        self.__filterBtn.setEnabled(True)
        if not self.isVisible():
            self.__notifierWidget = NotifierWidget(informative_text='Task Complete', detailed_text='Click this!')
            self.__notifierWidget.show()
            self.__notifierWidget.doubleClicked.connect(self.show)

    def closeEvent(self, e):
        message = 'The window will be closed. Would you like to continue running this app in the background?'
        closeMessageBox = QMessageBox(self)
        closeMessageBox.setWindowTitle('Wait!')
        closeMessageBox.setText(message)
        closeMessageBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        reply = closeMessageBox.exec()
        # Yes
        if reply == 16384:
            e.accept()
        # No
        elif reply == 65536:
            app.quit()
        return super().closeEvent(e)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())