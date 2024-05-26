import os, re
from PySide6 import QtCore
from PySide6.QtCore import QObject
from yt_dlp import YoutubeDL

class DownloadWorker(QObject):
    finished = QtCore.Signal()
    downloadSuccessful = QtCore.Signal()
    progress = QtCore.Signal(float)
    def __init__(self, URL, downloadFolder, logger):
        super().__init__()
        self.URL = URL
        self.logger = logger
        self.audio_cfg = {'format': 'm4a/bestaudio/best', 
                          'outtmpl': os.path.join(downloadFolder, "%(title)s.%(ext)s"),
                          'progress_hooks': [self.my_hook],
                          'logger': self.logger,
        }
        self.video_cfg = {'format': 'mp4/bestaudio/best',
                          'outtmpl': os.path.join(downloadFolder, "%(title)s.%(ext)s"),
                          'progress_hooks': [self.my_hook],
                          'logger': self.logger,
        }
    def my_hook(self, d):
        if d['status'] == 'downloading':
            p = self.getFloat(d['_percent_str'])
            self.progress.emit(p)
    '''Extracts the float number from _percent_str by removing the percent and ANSI formatting and casting to a float.
    Regex for ANSI from https://www.tutorialspoint.com/How-can-I-remove-the-ANSI-escape-sequences-from-a-string-in-python
    I added the \% to remove the percent.'''
    def getFloat(self, line):
        getFloatPattern = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]|\%')
        return float(getFloatPattern.sub('', line))
    def download_video(self):
        with YoutubeDL(self.video_cfg) as ydl:
            try:
                ydl.download(self.URL)
            except Exception: #don't want exceptions to crash program, instead just
                              #report it to the user using the logger
                return 1
            else:
                self.downloadSuccessful.emit()
                return 0
            finally:
                self.finished.emit()

    def download_audio(self):
        with YoutubeDL(self.audio_cfg) as ydl:
            try:
                ydl.download(self.URL)
            except Exception: 
                return 1
            else:
                self.downloadSuccessful.emit()
                return 0
            finally:
                self.finished.emit()