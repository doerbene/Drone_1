import sys
import io
import logging
import time
from datetime import datetime


class Balance_mode:
    pass


class Control_mode:
    pass


class Logger:           # if an instance is made the program can switch between a debug mode where everything will be logged and a normal mode with no outputs
    def __init__(self):
        if len(sys.argv) > 1:
            if sys.argv[1] == "-d":
                print("[Info] Debug-mode started")
                logging.basicConfig(filename="logs/drone1_(ver."+version+")_" + self.get_time("date") + ".log", format=self.get_time() + ' - %(name)s - %(levelname)s - %(message)s')
                root = logging.getLogger()
                io = logging.StreamHandler(sys.stdout)
                io.setLevel(logging.DEBUG)
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                io.setFormatter(formatter)
                root.addHandler(io)
                root.setLevel(logging.DEBUG)
                self.logging = True
                self.log = logging
        else:
            self.logging = False
            print("[Info] Normal-mode started. Ready to fly :)")

    def get_time(self, string=""):
        date = datetime.now()
        if string is "date":
            return (str(date.year) + "_" + str(date.month) + "_" + str(date.day))
        else:
            return (str(date.year) + "-" + str(date.month) + "-" + str(date.day) + " " + str(date.hour) + ":" + str(date.minute) + ":" + str(date.second) + "'" + str(date.microsecond))


version = "1.0"
print("[Info] Smartdrone_1 (ver. " + version + ") is starting")
log = Logger()
if log.logging:
    def print(*args, **kwargs):
        log.log.info(*args, **kwargs)
    print("[Info] Debug-mode started. Fix your errors :)")

print("[Info] Logger successfully initialized")
