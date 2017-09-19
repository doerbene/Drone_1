import sys
import io
import logging
import time
from datetime import datetime
from configparser import ConfigParser
try:                                        # You have to install those two modules
    import smbus
    import RPi.GPIO as GPIO
except:
    print("[Error] Error while importing smbus and RPi")
    sys.exit(1)


class Vector:
    def __init__(self, x, y, z, xstart=0, ystart=0, zstart=0):
        self.x = x
        self.y = y
        self.z = z
        self.xstart = xstart
        self.ystart = ystart
        self.zstart = zstart

    def __init__(self, x, y, z, roll, pitch, yaw):
        self.x = x
        self.y = y
        self.z = z
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw

    def __init__(self, a, b, c, angles=False):
        if angles:
            self.roll = a%360
            self.pitch = b%360
            self.yaw = c%360
        else:
            self.x = a
            self.y = b
            self.z = c


class Sensors:
    # Registers: TODO: Put them into a config to allow other users to switch sensors more easy
    # Accelaration
    REG_ACCELX = [0x3b, 0x3c]       # These 2 Registers are the High and the low byte for our accelaration sensor in x direction
    REG_ACCELY = [0x3d, 0x3e]       # These 2 Registers are the High and the low byte for our accelaration sensor in y direction
    REG_ACCELZ = [0x3f, 0x40]       # These 2 Registers are the High and the low byte for our accelaration sensor in z direction

    # Temperature
    REG_TEMP = [0x41, 0x42]         # These 2 Registers are the High and the low byte for our temperature sensor

    # Gyroscope
    REG_GYROX = [0x43, 0x44]        # These 2 Registers are the High and the low byte for our gyroscope sensor in x direction (roll)
    REG_GYROY = [0x45, 0x46]        # These 2 Registers are the High and the low byte for our gyroscope sensor in y direction (pitch)
    REG_GYROZ = [0x47, 0x48]        # These 2 Registers are the High and the low byte for our gyroscope sensor in z direction (yaw)

    def get_accelaration():
        accelx_high = bus.read_byte_data(69, Sensors.REG_ACCELX[0])
        accelx_low = bus.read_byte_data(69, Sensors.REG_ACCELX[1])
        accely_high = bus.read_byte_data(69, Sensors.REG_ACCELY[0])
        accely_low = bus.read_byte_data(69, Sensors.REG_ACCELY[1])
        accelz_high = bus.read_byte_data(69, Sensors.REG_ACCELZ[0])
        accelz_low = bus.read_byte_data(69, Sensors.REG_ACCELZ[1])

        accelx = (accelx_high << 8) + accelx_low
        accely = (accely_high << 8) + accely_low
        accelz = (accelz_high << 8) + accelz_low

        return Vector(accelx, accely, accelz)

    def get_gyro():
        gyrox_high = bus.read_byte_data(69, Sensors.REG_GYROX[0])
        gyrox_low = bus.read_byte_data(69, Sensors.REG_GYROX[1])
        gyroy_high = bus.read_byte_data(69, Sensors.REG_GYROY[0])
        gyroy_low = bus.read_byte_data(69, Sensors.REG_GYROY[1])
        gyroz_high = bus.read_byte_data(69, Sensors.REG_GYROZ[0])
        gyroz_low = bus.read_byte_data(69, Sensors.REG_GYROZ[1])

        gyrox = (gyrox_high << 8) + gyrox_low
        gyroy = (gyroy_high << 8) + gyroy_low
        gyroz = (gyroz_high << 8) + gyroz_low

        return Vector(gyrox, gyroy, gyroz, angles=True)     # TODO: Check if the sensor really gives back an angle

    def get_temp():
        temp_high = bus.read_byte_data(69, Sensors.REG_TEMP[0])
        temp_low = bus.read_byte_data(69, Sensors.REG_TEMP[1])
        temp = (temp_high << 8) + temp_low
        return temp

    def get_ultrasonic(sensor):     # Sensor is the Sensor which you want to get the ultrasonic information from
        pass
    def get_gps_location():
        pass
    def get_radar(sensor):          # Sensor is the Sensor which you want to get the radar information from -> at this point is not used and implemented
        pass


class Engine:
    def set_voltage_level(engine, voltage):
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
    def return_home():
        pass


class NetworkManager:
    pass


class Logger:           # if an instance is made the program can switch between a debug mode where everything will be logged and a normal mode with no outputs
    def __init__(self):
        if len(sys.argv) > 1:
            if sys.argv[1] == "-d":
                print("[Info] Debug-mode started. Fix your errors :)")
                logging.basicConfig(filename="logs/drone1_(ver."+version+")_" + self.get_time("date") + ".log", format=self.get_time() + ' - %(name)s - %(levelname)s - %(message)s')
                root = logging.getLogger()
                io = logging.StreamHandler(sys.stdout)
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                io.setLevel(logging.DEBUG)
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
    def get_string(section, attribute, config_file="smartdrone1.conf"):
        config = ConfigParser.read(config_file)
        config.sections()
        if not config.has_section(section):
            print("[Warning] No section " + section + " in " + config_file.name + " found!")
            return None
        result = config[section][attribute]
        if result is None:
            print("[Warning] The result is None")
        return result

    def set_string(section, attribute, value, config_file="smartdrone1.conf"):
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
    print("[Info] Logger successfully initialized")

bus = smbus.SMBus(1)

print(Sensors.get_accelaration().x)

