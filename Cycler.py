# Controlls the main funtkon of Thermo-Cycle

import RPi.GPIO as GPIO
from time import sleep, time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

class Cycler():
    def __init__(self):
        self.run = True
        self.valve_status = None
        self.pump_1 = 36
        self.pump_2 = 38
        self.valve_in_med1 = 12
        self.valve_in_med2 = 16
        self.valve_out_med1 = 18
        self.valve_out_med2 = 22
        self.valve_cleaning = 32
        self.level_indicator_port = 40

        GPIO.setup(self.pump_1,         GPIO.OUT)
        GPIO.setup(self.pump_2,         GPIO.OUT)
        GPIO.setup(self.valve_in_med1,  GPIO.OUT)
        GPIO.setup(self.valve_in_med2,  GPIO.OUT)
        GPIO.setup(self.valve_out_med1, GPIO.OUT)
        GPIO.setup(self.valve_out_med2, GPIO.OUT)
        GPIO.setup(self.valve_cleaning, GPIO.OUT)

        GPIO.setup(self.level_indicator_port, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)


    def set_valves(self, medium):
        """Sets valves On/Off for Medium"""
        if medium == "Medium-1":
            GPIO.output(self.valve_in_med1,  1)
            GPIO.output(self.valve_out_med1, 1)
            GPIO.output(self.valve_in_med2,  0)
            GPIO.output(self.valve_out_med2, 0)
            self.valve_status = "Medium-1"
            print("Valves for Med-1...")
        elif medium == "Medium-2":
            GPIO.output(self.valve_in_med1,  0)
            GPIO.output(self.valve_out_med1, 0)
            GPIO.output(self.valve_in_med2,  1)
            GPIO.output(self.valve_out_med2, 1)
            self.valve_status = "Medium-2"
            print("Valves for Med-2...")
        else:
            self.valve_status = None
            print("Valve-Error: wrong Medium name")


    def fill(self, medium):
        """Run Pump until level is reached, stops if fill_time to long"""
        fill_time_exceed = False
        start_fill_time = time()

        if medium == "Medium-1" and self.valve_status == "Medium-1":
            GPIO.output(self.pump_1, 1)
            print("Fill Med-1...")
        elif medium == "Medium-2" and self.valve_status == "Medium-2":
            GPIO.output(self.pump_2, 1)
            print("Fill Med-2...")
        else:
            print("Pump-Error: wrong Medium name or false valve settings")

        self.level_indicator = GPIO.input(self.level_indicator_port)

        while (self.level_indicator == 0) and (fill_time_exceed == False):
            self.level_indicator = GPIO.input(self.level_indicator_port)
            if time() - start_fill_time > 5:
                fill_time_exceed = True
            print("Not full yet")
            sleep(0.5)

        GPIO.output(self.pump_2, 0)
        GPIO.output(self.pump_1, 0)
        GPIO.output(self.valve_in_med1,  0)
        GPIO.output(self.valve_out_med1, 0)
        GPIO.output(self.valve_in_med2,  0)
        GPIO.output(self.valve_out_med2, 0)


    def clean_container(self, clean_time):
        """Open Air-Valve for cleaning during clean_time
           INPUT: int clean_time"""
        print("Cleaning...")
        GPIO.output(self.valve_cleaning, 1)
        sleep(clean_time)
        GPIO.output(self.valve_cleaning, 0)


    def loop(self):
        """Main loop for cycling. Controls Pump, valves, ... """
        while (self.run == True):

            print("Cycling...")

            self.set_valves("Medium-1")
            self.fill("Medium-1")
            self.clean_container(3)
            self.set_valves("Medium-2")
            self.fill("Medium-2")
            self.clean_container(3)



if __name__ == "__main__":

    cycler = Cycler()
    cycler.loop()



