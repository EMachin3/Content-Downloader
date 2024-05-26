import sys
import os
from PySide6 import QtCore
from PySide6.QtWidgets import QApplication, QDialog, QLineEdit, QPushButton, QProgressBar, QVBoxLayout, QCheckBox, QButtonGroup, QLabel, QFileDialog, QMessageBox
from PySide6.QtCore import QThread
from downloader import DownloadWorker
from logger import MyLogger

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
        self.progressBar = QProgressBar()
        self.progressBar.hide() # start out with progress hidden
        self.downloadFinishedLabel = QLabel("Download finished!", alignment=QtCore.Qt.AlignCenter)
        self.downloadFinishedLabel.hide()
        self.goButton = QPushButton("Go!")

        # Create downloader and associated interface widgets
        self.downloadType = 'v' #default to downloading video
        self.video = QCheckBox("Video")
        self.video.setChecked(True)
        self.audio = QCheckBox("Audio")
        buttonGroup = QButtonGroup(layout)
        buttonGroup.addButton(self.video)
        buttonGroup.addButton(self.audio)

        # Connect signals to slots
        self.goButton.clicked.connect(self.download)
        self.goButton.clicked.connect(self.disableGo)
        self.goButton.clicked.connect(self.progressBar.show)
        self.goButton.clicked.connect(self.downloadFinishedLabel.hide)
        self.changeDownloadFolderButton.clicked.connect(self.changeDownloadFolder)
        self.changeDownloadFolderButton.clicked.connect(self.progressBar.hide)
        self.changeDownloadFolderButton.clicked.connect(self.downloadFinishedLabel.hide)
        buttonGroup.buttonToggled.connect(self.changeDownloadType)
        buttonGroup.buttonToggled.connect(self.progressBar.hide)
        buttonGroup.buttonToggled.connect(self.downloadFinishedLabel.hide)

        # Add widgets to the layout
        layout.addWidget(self.title)
        layout.addWidget(self.enterURLLabel)
        layout.addWidget(self.enterURL)
        layout.addWidget(self.downloadFolderLabel)
        layout.addWidget(self.changeDownloadFolderButton)
        layout.addWidget(self.video)
        layout.addWidget(self.audio)
        layout.addWidget(self.progressBar)
        layout.addWidget(self.downloadFinishedLabel)
        layout.addWidget(self.goButton)

    def download(self):
        self.logger = MyLogger()
        self.worker = DownloadWorker(self.enterURL.text(), self.downloadFolder, self.logger)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        if self.downloadType == 'v':
            self.thread.started.connect(self.worker.download_video)
        else:
            self.thread.started.connect(self.worker.download_audio)
        self.worker.progress.connect(self.progressBar.setValue)
        self.worker.downloadSuccessful.connect(self.downloadFinishedLabel.show)
        self.logger.downloadError.connect(self.alertDownloadFailed)
        self.logger.downloadError.connect(self.progressBar.hide)
        self.logger.alreadyDownloaded.connect(self.alertAlreadyDownloaded)
        self.logger.alreadyDownloaded.connect(self.progressBar.hide)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.enableGo)
        self.thread.start()

    def changeDownloadFolder(self):
        newFolder = QFileDialog.getExistingDirectory(self, caption="Select a folder")
        if newFolder == '': #user pressed cancel instead of open
            return #don't change anything
        self.downloadFolder = newFolder
        self.downloadFolderLabel.setText("Current Download Folder: " + newFolder)

    def changeDownloadType(self, button, isChecked):
        if isChecked:
            if button == self.video:
                self.downloadType = 'v'
            else:
                self.downloadType = 'a'

    def disableGo(self):
        self.goButton.setEnabled(False)
        self.progressBar.setValue(0)
        
    def enableGo(self):
        self.goButton.setEnabled(True)

    def alertAlreadyDownloaded(self):
        alert = QMessageBox()
        alert.setIcon(QMessageBox.Information)
        alert.setText("File has already been downloaded.")
        alert.setWindowTitle("Download failed")
        alert.setStandardButtons(QMessageBox.Ok)
        alert.exec()

    def alertDownloadFailed(self, msg):
        error = QMessageBox()
        error.setIcon(QMessageBox.Critical)
        error.setText("Error: Download failed.\n\nMake sure the URL is correct and you are allowed to access the content.\n\nClick \"Show Details\" to see detailed error information.")
        error.setDetailedText(msg)
        error.setWindowTitle("Download failed")
        error.setStandardButtons(QMessageBox.Ok)
        error.exec()

if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    # Create and show the interface
    interface = Interface()
    interface.show()
    # Run the main Qt loop
    sys.exit(app.exec())
