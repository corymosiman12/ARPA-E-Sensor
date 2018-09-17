import pysftp
import threading
import os
from datetime import datetime, timedelta
import time

class MyAudio(threading.Thread):
    def __init__(self, audio_root, pi_ip_address):
        threading.Thread.__init__(self)
        print('Initializing MyAudio')
        # self.setDaemon(True)
        self.audio_root = audio_root
        self.audio_root_date = os.path.join(self.audio_root, datetime.now().strftime('%Y-%m-%d'))
        self.pi_ip_address = pi_ip_address
        self.pi_audio_root = '/home/pi/audio'
        self.pi_audio_root_date = os.path.join(self.pi_audio_root, datetime.now().strftime("%Y-%m-%d"))
        self.start()

    def audio_dir_update(self):
        while True:
            date_dir = os.path.join(self.audio_root, datetime.now().strftime("%Y-%m-%d"))
            if not os.path.isdir(date_dir):
                os.makedirs(date_dir)
                self.audio_root_date = date_dir
                print('Created: {}'.format(date_dir))

            min_dir = os.path.join(self.audio_root_date, datetime.now().strftime('%H%M'))
            if not os.path.isdir(min_dir):
                os.makedirs(min_dir)
                t = datetime.now() - timedelta(minutes = 1)
                prev_min_dir = os.path.join(self.audio_root_date, t.strftime('%H%M'))
                self.audio_dir = prev_min_dir
                print('Created: {}'.format(min_dir))

    def run(self):
        dir_create = threading.Thread(target=self.audio_dir_update)
        dir_create.start()
        while True:
            if datetime.now().second == 0:
                time.sleep(10)
                t = datetime.now() - timedelta(minutes = 1)
                pi_audio_dir = os.path.join(self.pi_audio_root, t.strftime('%Y-%m-%d'), t.strftime('%H%M'))
                print('Transferring files from: {}\tTo: {}'.format(pi_audio_dir, self.audio_dir))
                with pysftp.Connection(self.pi_ip_address, username='pi', password='sensor') as sftp:
                    sftp.get_d(pi_audio_dir, self.audio_dir, preserve_mtime=True)