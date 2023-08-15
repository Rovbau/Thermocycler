# Controlls the main funktion of Thermo-Cycle

import atexit
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

        atexit.register(self.stop)

        GPIO.setup(self.pump_1,         GPIO.OUT)
        GPIO.setup(self.pump_2,         GPIO.OUT)
        GPIO.setup(self.valve_in_med1,  GPIO.OUT)
        GPIO.setup(self.valve_in_med2,  GPIO.OUT)
        GPIO.setup(self.valve_out_med1, GPIO.OUT)
        GPIO.setup(self.valve_out_med2, GPIO.OUT)
        GPIO.setup(self.valve_cleaning, GPIO.OUT)
        GPIO.setup(self.level_indicator_port, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)


    def stop(self):
        """Set machine to a save state"""
        GPIO.output(self.valve_in_med1,  0)
        GPIO.output(self.valve_out_med1, 1)
        GPIO.output(self.valve_in_med2,  0)
        GPIO.output(self.valve_out_med2, 1)
        GPIO.output(self.valve_cleaning, 0)
        GPIO.output(self.pump_2, 0)
        GPIO.output(self.pump_1, 0)
        print("Stop done")


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


    def fill(self, medium, flush_time):
        """Run Pump until level is reached, stops if fill_time to long"""
        fill_time_exceed = False
        flush_time_exceed = False
        start_fill_time = time()

        if medium == "Medium-1" and self.valve_status == "Medium-1":
            GPIO.output(self.valve_in_med1,  1)
            GPIO.output(self.valve_out_med1, 0)
            GPIO.output(self.pump_1, 1)
            print("Fill Med-1...")
        elif medium == "Medium-2" and self.valve_status == "Medium-2":
            GPIO.output(self.valve_in_med2,  1)
            GPIO.output(self.valve_out_med2, 0)
            GPIO.output(self.pump_2, 1)
            print("Fill Med-2...")
        else:
            print("Pump-Error: wrong Medium name or false valve settings")

        while (GPIO.input(self.level_indicator_port) == 0) and (fill_time_exceed == False):
            if time() - start_fill_time > 50:
                fill_time_exceed = True
            print("Not full yet")
            sleep(0.5)
        print("Full")

        GPIO.output(self.pump_1, 0)
        GPIO.output(self.pump_2, 0)

        #  Flush with Level control
        start_flush_time = time()

        if medium == "Medium-1" and self.valve_status == "Medium-1":
            GPIO.output(self.valve_in_med1,  1)
            GPIO.output(self.valve_out_med1, 1)
            GPIO.output(self.pump_1, 1)
            print("Flush Med-1...")
            while (flush_time_exceed == False):
                if GPIO.input(self.level_indicator_port) == 1:
                    GPIO.output(self.pump_1, 0)
                    print("stopping")
                    sleep(3)
                else:
                    GPIO.output(self.pump_1, 1)

                if (time() - start_flush_time) > flush_time:
                        flush_time_exceed = True
                sleep(0.5)
        elif medium == "Medium-2" and self.valve_status == "Medium-2":
            GPIO.output(self.valve_in_med2,  1)
            GPIO.output(self.valve_out_med2, 1)
            GPIO.output(self.pump_2, 1)
            print("Flush Med-2...")
            while (flush_time_exceed == False):
                if GPIO.input(self.level_indicator_port) == 1:
                    GPIO.output(self.pump_2, 0)
                    print("stopping")
                    sleep(3)
                else:
                    GPIO.output(self.pump_2, 1)

                if (time() - start_flush_time) > flush_time:
                        flush_time_exceed = True
                sleep(0.5)
        else:
            print("Pump-Error: wrong Medium name or false valve settings")

        GPIO.output(self.pump_2, 0)
        GPIO.output(self.pump_1, 0)
        GPIO.output(self.valve_in_med1,  0)
        GPIO.output(self.valve_out_med1, 0)
        GPIO.output(self.valve_in_med2,  0)
        GPIO.output(self.valve_out_med2, 0)

    def clean_container(self, medium, clean_time):
        """Open Air-Valve for cleaning during clean_time
           INPUT: int clean_time"""
        print("Cleaning...")
        if medium == "Medium-1":
            GPIO.output(self.valve_out_med1, 1)
            sleep(3)
            GPIO.output(self.valve_cleaning, 1)
            sleep(clean_time)
        elif medium == "Medium-2":
            GPIO.output(self.valve_out_med2, 1)
            sleep(3)
            GPIO.output(self.valve_cleaning, 1)
            sleep(clean_time)
        else:
            print("Clean-Error: wrong Medium name")

        print("Close clean valve")
        GPIO.output(self.valve_cleaning, 0)

    def harware_test(self):
        for i in range(5):
            #GPIO.output(self.valve_cleaning, 1)
            print(GPIO.input(self.level_indicator_port))
            print("On")
            sleep(2)
            #GPIO.output(self.valve_cleaning, 0)
            print("Off")
            sleep(2)


    def loop(self):
        """Main loop for cycling. Controls Pump, valves, ... """

        flush_time = 120
        clean_time = 10

        while (self.run == True):
            print("Cycling...")
            self.set_valves("Medium-1")
            self.fill("Medium-1", flush_time)
            self.clean_container("Medium-1" ,clean_time)
            self.set_valves("Medium-2")
            self.fill("Medium-2", flush_time)
            self.clean_container("Medium-2", clean_time)



if __name__ == "__main__":

    cycler = Cycler()
    #cycler.harware_test()
    cycler.loop()
