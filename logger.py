from PySide6 import QtCore
from PySide6.QtCore import QObject
import re
'''
This class is instantiated within Interface then passed to downloader so the
the error signal can connect to some slot that displays the error info
'''
class MyLogger(QObject):
    downloadError = QtCore.Signal(str)
    alreadyDownloaded = QtCore.Signal()

    def debug(self, msg):
        # For compatibility with youtube-dl, both debug and info are passed into debug
        # You can distinguish them by the prefix '[debug] '
        if msg.startswith('[debug] '):
            pass
        else:
            self.info(msg)

    def info(self, msg):
        #print(msg)
        if  msg.startswith('[download] ') and msg.endswith('has already been downloaded'):
            self.alreadyDownloaded.emit()

    def warning(self, msg):
        pass

    def error(self, msg):
        self.downloadError.emit(self.removeANSI(msg))

    def removeANSI(self, msg):
        removeANSIPattern = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
        return removeANSIPattern.sub('', msg)