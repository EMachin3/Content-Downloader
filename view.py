import sys
import os
from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QApplication, QDialog, QLineEdit, QPushButton, QVBoxLayout, QCheckBox, QButtonGroup, QLabel, QFileDialog, QMessageBox
from PySide6.QtCore import QObject, QThread, Signal
from downloader import Downloader

class Interface(QDialog):

    def __init__(self, parent=None):
        super(Interface, self).__init__(parent)
        layout = QVBoxLayout(self)
        self.setWindowTitle("Content Downloader")

        # Create interface widgets and associated fields
        self.title = QLabel("<h2>Content Downloader</h2>", alignment=QtCore.Qt.AlignCenter)
        self.enterURLLabel = QLabel("Enter URL", alignment=QtCore.Qt.AlignCenter)
        self.enterURL = QLineEdit("https://example.org")
        self.downloadFolder = os.path.join(os.path.expanduser("~"), "Downloads")
        self.downloadFolderLabel = QLabel("Current Download Folder: " + self.downloadFolder, alignment=QtCore.Qt.AlignCenter)

        self.changeDownloadFolderButton = QPushButton("Change Download Folder")
        self.goButton = QPushButton("Go!")

        # Create downloader and associated interface widgets
        self.downloader = Downloader()
        self.downloadType = 'v' #default to downloading video
        self.video = QCheckBox("Video")
        self.video.setChecked(True)
        self.audio = QCheckBox("Audio")
        buttonGroup = QButtonGroup(layout)
        buttonGroup.addButton(self.video)
        buttonGroup.addButton(self.audio)

        # Connect signals to slots
        self.goButton.clicked.connect(self.download)
        self.changeDownloadFolderButton.clicked.connect(self.changeDownloadFolder)
        buttonGroup.buttonToggled.connect(self.changeDownloadType)

        # Add widgets to the layout
        layout.addWidget(self.title)
        layout.addWidget(self.enterURLLabel)
        layout.addWidget(self.enterURL)
        layout.addWidget(self.downloadFolderLabel)
        layout.addWidget(self.changeDownloadFolderButton)
        layout.addWidget(self.video)
        layout.addWidget(self.audio)
        layout.addWidget(self.goButton)
        #layout.addWidget(buttonGroup)

    def download(self):
        rectode = -1
        self.downloader.set_url(self.enterURL.text())
        self.worker = DownloadWorker(self.downloader)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        if self.downloadType == 'v':
            self.thread.started.connect(self.worker.download_video)
        else:
            self.thread.started.connect(self.worker.download_audio)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()
        #TODO: need to add logic to lock out buttons or queue downloads or something
        #TODO: also figure out a way to display download progress to user

    def changeDownloadFolder(self):
        newFolder = QFileDialog.getExistingDirectory(self, caption="Select a folder")
        if newFolder == '': #user pressed cancel instead of open
            return #don't change anything
        self.downloadFolder = newFolder
        self.downloader.change_download_dir(newFolder)
        self.downloadFolderLabel.setText("Current Download Folder: " + newFolder)

    def changeDownloadType(self, button, isChecked):
        if isChecked:
            if button == self.video:
                self.downloadType = 'v'
            else:
                self.downloadType = 'a'

    '''
    TODO: add more detailed error info from stdout if possible
    '''
    def alert_download_failed(self):
        error = QMessageBox()
        error.setIcon(QMessageBox.Critical)
        error.setText("Download failed.")
        error.setInformativeText("Make sure the URL is correct and you are allowed to access the content.")
        error.setWindowTitle("Error: Download failed")
        error.setStandardButtons(QMessageBox.Ok)
        error.setStyleSheet("QLabel{min-width: 150px;}");
        error.exec()
'''
TODO: maybe use a threadpool instead
'''
class DownloadWorker(QObject):
    finished = QtCore.Signal()
    progress = QtCore.Signal(int)
    def __init__(self, downloader):
        super().__init__()
        #self.finished = QtCore.Signal()
        #self.progress = QtCore.Signal(int)
        self.downloader = downloader

    def download_video(self):
        self.downloader.download_video()
        self.finished.emit()

    def download_audio(self):
        self.downloader.download_audio()
        self.finished.emit()

if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    # Create and show the interface
    interface = Interface()
    interface.show()
    # Run the main Qt loop
    sys.exit(app.exec())
