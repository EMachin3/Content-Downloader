import sys
import time
import re
from yt_dlp import YoutubeDL
import os
from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QApplication, QDialog, QLineEdit, QPushButton, QVBoxLayout, QCheckBox, QButtonGroup, QLabel, QFileDialog, QMessageBox
from PySide6.QtCore import QObject, QThread, Signal
#from downloader import Downloader

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
        #self.downloader = Downloader()
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
        #rectode = -1
        #self.downloader.set_url(self.enterURL.text())
        #self.worker = DownloadWorker(self.downloader)
        self.worker = DownloadWorker(self.enterURL.text(), self.downloadFolder)
        #self.worker.set_url(self.enterURL.text())
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        if self.downloadType == 'v':
            self.thread.started.connect(self.worker.download_video)
        else:
            self.thread.started.connect(self.worker.download_audio)
        self.worker.progress.connect(self.printProgress)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()
        #TODO: need to add logic to lock out buttons or queue downloads or something
        #   current implementation probably supports multiple downloads, test that
        #TODO: also figure out a way to display download progress to user

    def changeDownloadFolder(self):
        newFolder = QFileDialog.getExistingDirectory(self, caption="Select a folder")
        if newFolder == '': #user pressed cancel instead of open
            return #don't change anything
        self.downloadFolder = newFolder
        #self.downloader.change_download_dir(newFolder)
        self.downloadFolderLabel.setText("Current Download Folder: " + newFolder)

    def changeDownloadType(self, button, isChecked):
        if isChecked:
            if button == self.video:
                self.downloadType = 'v'
            else:
                self.downloadType = 'a'

    '''
    TODO: add more detailed error info from stdout if possible
    also this currently is not used lol
    '''
    def alert_download_failed(self):
        error = QMessageBox()
        error.setIcon(QMessageBox.Critical)
        error.setText("Download failed.")
        error.setInformativeText("Make sure the URL is correct and you are allowed to access the content.")
        error.setWindowTitle("Error: Download failed")
        error.setStandardButtons(QMessageBox.Ok)
        error.setStyleSheet("QLabel{min-width: 150px;}")
        error.exec()
    def printProgress(self, bruh):
        print(bruh)
'''
TODO: maybe use a threadpool instead
TODO: change from wrapping Downloader to just being Downloader itself
'''
class DownloadWorker(QObject):
    finished = QtCore.Signal()
    progress = QtCore.Signal(float)
    def __init__(self, URL, downloadFolder):
        super().__init__()
        self.URL = URL
        self.audio_cfg = {'format': 'm4a/bestaudio/best', 
                          'outtmpl': os.path.join(downloadFolder, "%(title)s.%(ext)s"),
                          'progress_hooks': [self.my_hook],
        }
        self.video_cfg = {'outtmpl': os.path.join(downloadFolder, "%(title)s.%(ext)s"),
                          'progress_hooks': [self.my_hook],
        }
    def my_hook(self, d):
        # if d['status'] == 'finished':
        #     file_tuple = os.path.split(os.path.abspath(d['filename']))
        #     print("Done downloading {}".format(file_tuple[1]))
        if d['status'] == 'downloading':
            #p = d['_percent_str'].strip()
            #p = p.replace('%', '')
            # try:
            p = self.getFloat(d['_percent_str'])
            self.progress.emit(p)
            #print(p)
            # except ValueError:
            #     print('that didnt work')
            # except Exception as ex:
            #     template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            #     message = template.format(type(ex).__name__, ex.args)
            #     print(message)
            #print("Is P a float? " + isinstance(p, float))
            #print("This is P: " + float(p))
            #self.progress.setValue(float(p))
            #print(d['filename'], d['_percent_str'], d['_eta_str'])
            #self.progress.emit(float(p))
            #self.progress.emit(4.5)
            #self.progress.emit(p)
            '''self.progress.emit(something?)'''
    '''Extracts the float number from _percent_str by removing the percent and ANSI formatting and casting to a float.
    Regex for ANSI from https://www.tutorialspoint.com/How-can-I-remove-the-ANSI-escape-sequences-from-a-string-in-python
    I added the \% to remove the percent.'''
    def getFloat(self, line):
        getFloatPattern = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]|\%')
        return float(getFloatPattern.sub('', line))
    '''
    This stuff is currently commented because the plan is to redesign the layout of the code
    so that the DownloadWorker is created to do one download and then deleted, so functionality
    to change the URL isn't needed.
    '''
    #def set_url(self, URL):
    #    self.URL = URL
    #def change_download_dir(self, directory):
    #    self.audio_cfg['outtmpl'] = os.path.join(directory, "%(title)s.%(ext)s")
    #    self.video_cfg['outtmpl'] = os.path.join(directory, "%(title)s.%(ext)s")
    def download_video(self):
        with YoutubeDL(self.video_cfg) as ydl:
            try:
                ydl.download(self.URL)
            except Exception:
                return 1 #returns are useless, do something else
            else:
                return 0
            finally:
                self.finished.emit()

    def download_audio(self):
        with YoutubeDL(self.audio_cfg) as ydl:
            try:
                ydl.download(self.URL)
            except Exception: #this is kind of useless right now but might be
                              #important later when i add error handling
                return 1
            else:
                return 0
            finally:
                self.finished.emit()

if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    # Create and show the interface
    interface = Interface()
    interface.show()
    # Run the main Qt loop
    sys.exit(app.exec())