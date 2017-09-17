import sys
import io
import logging
import time
import RPi.GPIO as GPIO
from datetime import datetime
from configparser import ConfigParser


class Vector:
    __init__(self, xstart=0, ystart=0, zstart=0 , x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.xstart = xstart
        self.ystart = ystart
        self.zstart = zstart

    __init__(self, x, y, z, roll, pitch, yaw):
        self.x = x
        self.y = y
        self.z = z
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw


class Sensors:
    def get_accelaration(sensor=0): # Sensor here is just for later additions to the drone and won't affect this program in any wise at this point
        pass
    def get_gyro(sensor=0):         # Sensor here is just for later additions to the drone and won't affect this program in any wise at this point
        pass
    def get_ultrasonic(sensor):     # Sensor is the Sensor which you want to get the ultrasonic information from
        pass
    def get_gps_location():
        pass
    def get_radar(sensor):          # Sensor is the Sensor which you want to get the radar information from -> at this point is not used and implemented
        pass


class Engine:
    def set_voltage_level(engine):
        pass
    def get_voltage_level(engine):
        pass
    def trim(engine):
        pass


class Balance_mode:
    def maintain_location():
        pass
    def maintain_angle():
        pass


class Control_mode:
    def autotrim():
        print("[Info] Autotrim activated")
    def anti_collision():                           # This method is just for later states of that program and won't be implemented at first
        pass
    def set_speed_level(new_speed):                 # The speed_level is the rate of how many percent an engine can get of its max-power
        pass
    def get_speed_level():
        pass
    def accelerate(direction):
        pass


class Logger:           # if an instance is made the program can switch between a debug mode where everything will be logged and a normal mode with no outputs
    def __init__(self):
        if len(sys.argv) > 1:
            if sys.argv[1] == "-d":
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

class ConfigLoader:
    def get_string(config_file="smartdrone1.conf", section, attribute):
        config = ConfigParser.read(config_file)
        config.sections()
        if not config.has_section(section):
            print("[Warning] No section " + section + " in " + config_file.name + " found!")
            return None
        result = config[section][attribute]
        if result is None:
            print("[Warning] The result is None")
        return result

    def set_string(config_file="smartdrone1.conf", section, attribute, value):
        config = ConfigParser.read(config_file)
        if config.has_section(section) is False:
            config.add_section(section)
        config.set(section, attribute, value)
        config.write()
        print("[Info] " + section + "." + attribute + " of " + config_file.name + " is now " + value + ".")


version = "1.0"
print("[Info] Smartdrone_1 (ver. " + version + ") is starting")
log = Logger()
if log.logging:
    def print(*args, **kwargs):
        log.log.info(*args, **kwargs)
    print("[Info] Debug-mode started. Fix your errors :)")

print("[Info] Logger successfully initialized")
