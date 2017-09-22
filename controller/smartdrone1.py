import sys
import io
import logging
import time
import math
from datetime import datetime
from configparser import ConfigParser
try:                                      # You have to install those two modules
    import smbus
    import pigpio
except:
    print("[Error] Error while importing smbus and pigpio")
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
            self.roll = a
            self.pitch = b
            self.yaw = c
        else:
            self.x = a
            self.y = b
            self.z = c

    def add_vectors(vec1, vec2, same_direction = True):
        if same_direction:
            vec1.x += vec2.x
            vec1.y += vec2.y
            vec1.z += vec2.z
            return vec1
        else:
            pass


class ConfigLoader:
    def get_string(section, attribute, config_file="smartdrone1.conf"):
        config = ConfigParser()
        config.read(config_file)
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


class Sensors:
    # device
    address = ConfigLoader.get_string("GyroAccTempSensor", "address")

    # gyro
    REG_GYROX = ConfigLoader.get_string("GyroAccTempSensor", "gyro_roll")
    REG_GYROY = ConfigLoader.get_string("GyroAccTempSensor", "gyro_pitch")
    REG_GYROZ = ConfigLoader.get_string("GyroAccTempSensor", "gyro_yaw")

    # temp
    REG_TEMP = ConfigLoader.get_string("GyroAccTempSensor", "temp")

    # accel
    REG_ACCELX = ConfigLoader.get_string("GyroAccTempSensor", "acc_x")
    REG_ACCELY = ConfigLoader.get_string("GyroAccTempSensor", "acc_y")
    REG_ACCELZ = ConfigLoader.get_string("GyroAccTempSensor", "acc_z")

    acceX0 = 0
    acceY0 = 0
    acceZ0 = 0
    gyroX0 = 0
    gyroY0 = 0
    gyroZ0 = 0

    def read_word(reg):
        h = bus.read_byte_data(int(Sensors.address, 16), int(reg, 16))
        l = bus.read_byte_data(int(Sensors.address, 16), int(reg, 16)+1)
        return ((h << 8) + l)

    def read_word_2c(reg):
        val = Sensors.read_word(reg)
        if val >= 0x8000:
            return -(65536-val)
        else:
            return val

    def initialize():
        print("[Info] Sensor calibration...")
        times = 0
        acc = Vector(0, 0, 0)
        gyro = Vector(0, 0, 0)
        for i in range (1000):
            acc = Vector.add_vectors(acc, Sensors.get_accelaration())
            gyro = Vector.add_vectors(gyro, Sensors.get_gyro())
            times += 1

        Sensors.acceX0 = -acc.x/times
        Sensors.acceY0 = -acc.y/times
        Sensors.acceZ0 = 1-acc.z/times
        Sensors.gyroX0 = -gyro.x/times
        Sensors.gyroY0 = -gyro.y/times
        Sensors.gyroZ0 = -gyro.z/times
        print("[Info] Sensors calibrated.")

    def get_gyro():
        gyrox = (int(str(Sensors.read_word_2c(Sensors.REG_GYROX)), 16) + Sensors.gyroX0)/131
        gyroy = (int(str(Sensors.read_word_2c(Sensors.REG_GYROY)), 16) + Sensors.gyroY0)/131
        gyroz = (int(str(Sensors.read_word_2c(Sensors.REG_GYROZ)), 16) + Sensors.gyroZ0)/131
        return Vector(gyrox, gyroy, gyroz)     # TODO: Check if the sensor really gives back an angle

    def get_accelaration():
        accelx = int(str(Sensors.read_word_2c(Sensors.REG_ACCELX)), 16) / 16384 + Sensors.acceX0
        accely = int(str(Sensors.read_word_2c(Sensors.REG_ACCELY)), 16) / 16384 + Sensors.acceY0
        accelz = int(str(Sensors.read_word_2c(Sensors.REG_ACCELZ)), 16) / 16384 + Sensors.acceZ0
        return Vector(accelx, accely, accelz)

    def dist(a, b):
        return math.sqrt((a*a)+(b*b))

    def get_rotation():
        acc = Sensors.get_accelaration()
        rotX = math.degrees(math.atan2(acc.y, dist(acc.x, acc.z)))
        rotY = math.degrees(math.atan2(acc.x, dist(acc.y, acc.z)))
        rotZ = math.degrees(math.atan2(acc.z, dist(acc.x, acc.y))) # TODO: get the right formula
        return Vector(rotX, rotY, rotZ, True)

    def get_temp():
        return (int(read_word_2c(REG_TEMP), 16) / 340 + 36.53)

#    def get_ultrasonic(sensor):     # Sensor is the Sensor which you want to get the ultrasonic information from
#        pass
#    def get_gps_location():
#        pass
#    def get_radar(sensor):          # Sensor is the Sensor which you want to get the radar information from -> at this point is not used and implemented
#        pass


class Engine:
    engine_activation_pin = [[ConfigLoader.get_string("engine1", "activation_pin"), False],    # The variable engine_activation_pin contains
                             [ConfigLoader.get_string("engine2", "activation_pin"), False],    # data to the activation_pin of an engine it
                             [ConfigLoader.get_string("engine3", "activation_pin"), False],    # should affect and to the current state of that
                             [ConfigLoader.get_string("engine4", "activation_pin"), False]]    # particular pin (High = True, Low = False)
    engine_control_pin = [[ConfigLoader.get_string("engine1", "control_pin"), 0, ConfigLoader.get_string("engine1", "trim_level"), ConfigLoader.get_string("engine1", "activation_level"), ConfigLoader.get_string("engine1", "max_level")],   # The variable engine_control_pin contains data to the control_pin of
                          [ConfigLoader.get_string("engine2", "control_pin"), 0, ConfigLoader.get_string("engine2", "trim_level"), ConfigLoader.get_string("engine2", "activation_level"), ConfigLoader.get_string("engine2", "max_level")],   # an engine it should affect, to the current voltage of that particular
                          [ConfigLoader.get_string("engine3", "control_pin"), 0, ConfigLoader.get_string("engine3", "trim_level"), ConfigLoader.get_string("engine3", "activation_level"), ConfigLoader.get_string("engine3", "max_level")],   # engine (0 = no_voltage; min_u = activation_level, max_u = 255) and the trim_level which
                          [ConfigLoader.get_string("engine4", "control_pin"), 0, ConfigLoader.get_string("engine4", "trim_level"), ConfigLoader.get_string("engine4", "activation_level"), ConfigLoader.get_string("engine4", "max_level")]]   # will affect the voltage a tiny bit. On top of that also the activation_level is saved here

    def reload () :
            engine_activation_pin = [[ConfigLoader.get_string("engine1", "activation_pin"), False],    # The variable engine_activation_pin contains
                                     [ConfigLoader.get_string("engine2", "activation_pin"), False],    # data to the activation_pin of an engine it
                                     [ConfigLoader.get_string("engine3", "activation_pin"), False],    # should affect and to the current state of that
                                     [ConfigLoader.get_string("engine4", "activation_pin"), False]]    # particular pin (High = True, Low = False)
            engine_control_pin = [[ConfigLoader.get_string("engine1", "control_pin"), 0, ConfigLoader.get_string("engine1", "trim_level"), ConfigLoader.get_string("engine1", "activation_level"), ConfigLoader.get_string("engine1", "max_level")],   # The variable engine_control_pin contains data to the control_pin of
                                  [ConfigLoader.get_string("engine2", "control_pin"), 0, ConfigLoader.get_string("engine2", "trim_level"), ConfigLoader.get_string("engine2", "activation_level"), ConfigLoader.get_string("engine2", "max_level")],   # an engine it should affect, to the current voltage of that particular
                                  [ConfigLoader.get_string("engine3", "control_pin"), 0, ConfigLoader.get_string("engine3", "trim_level"), ConfigLoader.get_string("engine3", "activation_level"), ConfigLoader.get_string("engine3", "max_level")],   # engine (0 = no_voltage; min_u = activation_level, max_u = 255) and the trim_level which
                                  [ConfigLoader.get_string("engine4", "control_pin"), 0, ConfigLoader.get_string("engine4", "trim_level"), ConfigLoader.get_string("engine4", "activation_level"), ConfigLoader.get_string("engine4", "max_level")]]   # will affect the voltage a tiny bit. On top of that also the activation_level is saved here

    def set_voltage_level(engine, voltage):
        if engine_control_pin[engine][2] != 0 and voltage != 0:
            voltage = voltage + voltage * engine_control_pin[engine][2]
        if voltage > Engine.engine_control_pin[engine][4]:               # default: 255 is 100%
            voltage = Engine.engine_control_pin[engine][4]
        if voltage >= engine_control_pin[engine][3] and not Engine.engine_activation_pin[engine][1]:
            Engine.engine_activation_pin[engine][1] = True
            pi.write(Engine.engine_activation_pin[engine][0], 1)               # This sets the activation_pin to High voltage
            print("[Info] Activation-Pin activated -> engines are online now.")
        elif voltage < engine_control_pin[engine][3]:
            voltage = 0
            if Engine.engine_activation_pin[engine][1]:
                pi.write(Engine.engine_activation_pin[engine][0], 0)               # This sets the activation_pin to Low voltage
                Engine.engine_activation_pin[engine][1] = False
                print("[Info] Activation-Pin deactivated -> engines are offline now.")

        pi.set_PWM_dutycycle(Engine.engine_control_pin[engine][0])
        Engine.engine_control_pin[engine][1] = voltage
        print("[Info] Engine " + engine + "'s power was set to " + str(voltage/(256-engine_control_pin[engine][3]) * 100)[:4] + "%.")

    def get_voltage_level(engine, pintype):                     # Pintype 1 = activation_pin; 2 = control_pin
        if pintype == 1:
            return Engine.engine_activation_pin[engine][1]
        elif pintype == 2:
            return Engine.engine_control_pin[engine][1]

    def get_trim_level(engine):
        return Engine.engine_control_pin[engine][2]

    def trim():
        print("[Info] Starting to trim enginges...")
        accelaration = Sensors.get_accelaration()
        rotation = Sensors.get_rotation()
        print("[Info] Trimming Engine 1 and 2...")
        if Engine.get_voltage_level(0, 2) == 0 and Engine.get_voltage_level(1, 2) == 0 and Engine.get_voltage_level(2, 2) == 0 and Engine.get_voltage_level(3, 2) == 0 and int(accelaration.x) == 0 and int(acceleration.y) == 0 and int(accelaration.z) == 1 and int(rotation.roll) == 0 and int(rotation.pitch) == 0:
            # TODO: make an own method for this
            Engine.set_voltage_level(0, Engine.engine_control_pin[0][3])
            Engine.set_voltage_level(1, Engine.engine_control_pin[1][3])
            while (math.abs(rotation.roll):
                if rotation.pitch > 0.5:
                    Engine.set_voltage_level(1, Engine.get_voltage_level(1, 2)-1)
                if rotation.roll < -0.5:
                    Enging.set_voltage_level(0, Engine.get_voltage_level(0, 2)-1)
                Engine.set_voltage_level(0, Engine.get_voltage_level(0, 2)+1)
                Engine.set_voltage_level(1, Engine.get_voltage_level(1, 2)+1)
                rotation = Sensors.get_rotation()
                if math.abs(rotation.pitch) > 2:
                    Engine.set_voltage_level(0, 0)
                    Engine.set_voltage_level(1, 0)          # If something goes wrong we land here...
                    print("[Error] Something went wrong while trimming engine 1 and 2!")
                    return False
            power = [Engine.get_voltage_level(0, 2), Engine.get_voltage_level(1, 2)]
            engine1 = 0
            engine2 = 0
            pwdif = power[1]-power[0]
            pwdif2 = power[0]-power[1]
            if pwdif>0:                     # TODO: Check this! It was late tonight!
                engine1 = pwdif
            elif pwdif2>0:
                engine2 = pwdif2
            ConfigLoader.set_string("engine1", "trim_level", engine1)
            ConfigLoader.set_string("engine2", "trim_level", engine2)
            ConfigLoader.set_string("engine1", "max_level", ConfigLoader.get_string("engine1", "max_level" + engine1))
            ConfigLoader.set_string("engine2", "max_level", ConfigLoader.get_string("engine2", "max_level" + engine2))
            print("[Info] Successfully trimmed engine 1 and 2.")
            print("[Info] Trimming Engine 3 and 4...")
            Engine.set_voltage_level(2, Engine.engine_control_pin[2][3])
            Engine.set_voltage_level(3, Engine.engine_control_pin[3][3])
            while (math.abs(rotation.roll):
                if rotation.pitch > 0.5:
                    Engine.set_voltage_level(3, Engine.get_voltage_level(3, 2)-1)
                if rotation.roll < -0.5:
                    Enging.set_voltage_level(2, Engine.get_voltage_level(2, 2)-1)
                Engine.set_voltage_level(2, Engine.get_voltage_level(2, 2)+1)
                Engine.set_voltage_level(3, Engine.get_voltage_level(3, 2)+1)
                rotation = Sensors.get_rotation()
                if math.abs(rotation.pitch) > 2:
                    Engine.set_voltage_level(2, 0)
                    Engine.set_voltage_level(3, 0)          # If something goes wrong we land here...
                    print("[Error] Something went wrong while trimming Engine 3 and 4!")
                    return False
                power.append(Engine.get_voltage_level(2, 2), Engine.get_voltage_level(3, 2))
                engine3 = 0
                engine4 = 0
                pwdif = power[3]-power[2]
                pwdif2 = power[2]-power[3]
                if pwdif>0:                     # TODO: Check this! It was late tonight!
                    engine3 = pwdif
                elif pwdif2>0:
                    engine4 = pwdif2
                ConfigLoader.set_string("engine3", "trim_level", engine3)
                ConfigLoader.set_string("engine4", "trim_level", engine4)
                ConfigLoader.set_string("engine1", "max_level", ConfigLoader.get_string("engine1", "max_level" + engine3))
                ConfigLoader.set_string("engine2", "max_level", ConfigLoader.get_string("engine2", "max_level" + engine4))

            print("[Info] Successfully trimmed engine 3 and 4.")
            print("[Info] Trimming successful!")
            # TODO: Fine trimming
            reloadEngine()
            return True
        else:
            print("[Warning] You can't trim if the drone is not on the ground or on a plain surface!")
            return False


    def trim(engine):       # here the program can maybe change the activation_level because of looking at the power consumption
        pass


class Balance_mode:
    def breaking():
        pass
    def maintain_location():
        pass
    def maintain_angle():
        pass


class Control_mode:
    def autotrim():
        print("[Info] Autotrim activated")
        Balance_mode.breaking()
        Balance_mode.maintain_location()
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
    logging = False
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
    print("[Info] Logger successfully initialized")

bus = smbus.SMBus(1)

Sensors.initialize()

while(True):             # Just testing
    #print(Sensors.get_accelaration().x)
    #print(Sensors.get_accelaration().y)
    #print(Sensors.get_accelaration().z)
    print(Sensors.get_gyro().x)
    print(Sensors.get_gyro().y)
    print(Sensors.get_gyro().z)
    print("")
    time.sleep(0.5)
i = pigpio.pi()
