from yt_dlp import YoutubeDL
import os

class Downloader():
    def __init__(self):
        self.audio_cfg = {'format': 'm4a/bestaudio/best', 'outtmpl': os.path.join(os.path.expanduser("~"), "Downloads", "%(title)s.%(ext)s")}
        self.video_cfg = {'outtmpl': os.path.join(os.path.expanduser("~"), "Downloads", "%(title)s.%(ext)s")}
    def set_url(self, URL):
        self.URL = URL
    def change_download_dir(self, directory):
        self.audio_cfg['outtmpl'] = os.path.join(directory, "%(title)s.%(ext)s")
        self.video_cfg['outtmpl'] = os.path.join(directory, "%(title)s.%(ext)s")
    def download_audio(self):
        with YoutubeDL(self.audio_cfg) as ydl:
            try:
                ydl.download(self.URL)
            except Exception: #this is kind of useless right now but might be
                              #important later when i add error handling
                return 1
            else:
                return 0
    def download_video(self):
        with YoutubeDL(self.video_cfg) as ydl:
            try:
                ydl.download(self.URL)
            except Exception:
                return 1
            else:
                return 0

