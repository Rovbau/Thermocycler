# Program reads from the One-Wire-Bus data from DS18B20 Tempsensors
# Sensors must be connecte on GPIO.4 (Pull-Up to 3.3V)

import time

temp_device_one = '/sys/bus/w1/devices/28-00000de9229f'
temp_device_two = '/sys/bus/w1/devices/28-00000de9a375'

class TempSensors():
    def __init__(self):
        pass

    def read_temp_raw(self, device):
        """Reads raw data from sensor file"""
        device_file = device + '/w1_slave'
        f = open(device_file, 'r')
        lines = f.readlines()
        f.close()
        return(lines)

    def read_temp(self, device):
        """Converts raw_data to Celsius, Return: float Temp"""
        try:
            lines = self.read_temp_raw(device)
            equals_pos = lines[1].find('t=')
            if equals_pos != -1:
                temp_string = lines[1][equals_pos+2:]
                temp = float(temp_string) / 1000.0
                return(round(temp, 1))
        except:
            return(None)


if __name__ == "__main__":

    temp_sensors = TempSensors()
    while True:
        print(temp_sensors.read_temp(temp_device_one))
        print(temp_sensors.read_temp(temp_device_two))
        print("*********")
        time.sleep(1)
