# Controlls the main funktion of Thermo-Cycle

import atexit
from threading import *
from time import sleep, time
import logging


logging.basicConfig(level=logging.DEBUG,
                    filename='thermocycler.log',
                    filemode="w",
                    format='%(asctime)s.%(msecs)03d %(levelname)-6s %(module)-15s %(funcName)-20s: %(message)s',
                    datefmt='%H:%M:%S')

try:    
    import RPi.GPIO as GPIO
except:
    #Use FakeGPIO if no Raspberry-Pi is available
    import FakeGPIO as GPIO
    GPIO.VERBOSE = False


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

class Cycler():
    EVT_CYCLER_STATUS = "EVT_CYCLER_STATUS"
    EVT_CYCLES = "EVT_CYCLES"

    def __init__(self):
        self.run_cycler = True
        self.observers = {}
        self.current_medium = None
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

    def attach(self, evt, observer):
        if not evt in self.observers:
            self.observers[evt] = set()
        self.observers[evt].add(observer)

    def detach(self, evt, observer):
        if not evt in self.observers:
            return
        self.observers[evt].discard(observer)

    def _notifyObservers(self, evt, data):
        if not evt in self.observers:
            return
        for observer in self.observers[evt]:
            observer(data)
    
    def debounce_levelsensor(self):
        counter = 3
        while True:
            if GPIO.input(self.level_indicator_port) == 1:
              counter += 1
            else:
              counter -= 1
            if counter >= 6:
              return(1)
            if counter <= 0:
              return(0)
            sleep(0.1)

    def start_test(self):
        self.run_cycler = True
        print("Cycler: Starting")
        logging.info("Cycler: Starting")
        ThreadLoop=Thread(target=self.loop)
        ThreadLoop.daemon=True
        ThreadLoop.start()
        self._notifyObservers(Cycler.EVT_CYCLER_STATUS, "TEST START")
        

    def stop_test(self):
        """Set machine to a save state"""
        self.run_cycler = False
        GPIO.output(self.pump_2, 0)
        GPIO.output(self.pump_1, 0)
        GPIO.output(self.valve_cleaning, 0)

        if self.current_medium == "Medium-1":
            GPIO.output(self.valve_in_med1,  1)
            GPIO.output(self.valve_out_med1, 1)
        elif self.current_medium == "Medium-2":
            GPIO.output(self.valve_in_med2,  1)
            GPIO.output(self.valve_out_med2, 1)
        else:
            print("Stop-Error: wrong Medium name")
            logging.error("Stop-Error: wrong Medium name")
        self._notifyObservers(Cycler.EVT_CYCLER_STATUS, "STOPPING")


    def user_inputs(self, inputs):
        self.user_data = inputs

    def set_valves(self, medium):
        """Sets valves On/Off for Medium"""
        if self.run_cycler == False:
            return()
        if medium == "Medium-1":
            self.current_medium = "Medium-1"
            GPIO.output(self.valve_in_med1,  1)
            GPIO.output(self.valve_out_med1, 0)
            GPIO.output(self.valve_in_med2,  0)
            GPIO.output(self.valve_out_med2, 0)
            print("Valves for Med-1...")
            logging.debug("Valves for Med-1...")

        elif medium == "Medium-2":
            self.current_medium = "Medium-2"
            GPIO.output(self.valve_in_med1,  0)
            GPIO.output(self.valve_out_med1, 0)
            GPIO.output(self.valve_in_med2,  1)
            GPIO.output(self.valve_out_med2, 0)           
            print("Valves for Med-2...")
            logging.debug("Valves for Med-2...")
        else:
            self.current_medium = None
            print("Valve-Error: wrong Medium name")
            logging.error("Valve-Error: wrong Medium name")


    def fill(self, medium):
        """Run Pump until level is reached, stops if fill_time to long"""
        fill_time_exceed = False
        start_fill_time = time()

        if self.run_cycler == False:
            return()

        if medium == "Medium-1" and self.current_medium == "Medium-1":
            GPIO.output(self.valve_in_med1,  1)
            GPIO.output(self.valve_out_med1, 0)
            GPIO.output(self.pump_1, 1)
            print("Fill Med-1...")
            logging.debug("Fill Med-1")

        elif medium == "Medium-2" and self.current_medium == "Medium-2":
            GPIO.output(self.valve_in_med2,  1)
            GPIO.output(self.valve_out_med2, 0)
            GPIO.output(self.pump_2, 1)
            print("Fill Med-2...")
            logging.debug("Fill Med-2")
        else:
            print("Pump-Error: wrong Medium name or false valve settings")
            logging.error("Pump-Error: wrong Medium name or false valve settings")

        while (self.debounce_levelsensor() == 0) and (fill_time_exceed == False):
            if time() - start_fill_time > 50:
                fill_time_exceed = True
                print("Filling takes to long ERROR")
                logging.error("Filling takes to long ERROR")
                self._notifyObservers(Cycler.EVT_CYCLER_STATUS, "PUMP_ERROR")
                self.stop_test()
            if self.run_cycler == False:
                return()
            sleep(0.1)
        print("Full " + str(self.current_medium))
        logging.debug("Full " + str(self.current_medium))

        GPIO.output(self.pump_1, 0)
        GPIO.output(self.pump_2, 0)


    def flush(self, medium, flush_time, haltezeit):
        """Flush for flush_time, between rest for time: 'haltezeit' then open outlet-valve for secs"""
        flush_time_exceed = False
        start_flush_time = time()

        if self.run_cycler == False:
            return()

        if medium == "Medium-1" and self.current_medium == "Medium-1":
            print("Flush Med-1...")
            logging.debug("Flush Med-1...")
            GPIO.output(self.valve_in_med1,  1)
            pump = self.pump_1
            outlet_valve = self.valve_out_med1 
        elif medium == "Medium-2" and self.current_medium == "Medium-2":
            print("Flush Med-2...")
            logging.debug("Flush Med-2...")
            GPIO.output(self.valve_in_med2,  1)
            pump = self.pump_2
            outlet_valve = self.valve_out_med2
        else:
            print("Pump-Error: wrong Medium name or false valve settings")
            logging.error("Pump-Error: wrong Medium name or false valve settings")
 
        start_haltezeit = time()

        while (time() - start_flush_time) < flush_time:
            start_haltezeit = time()

            print("Flush Haltezeit")
            logging.debug("Flush Haltezeit")
            while (time() - start_haltezeit) < haltezeit:           
                if self.run_cycler == False:
                    return
                if (time() - start_flush_time) > flush_time:
                    break
                sleep(0.1)

            GPIO.output(outlet_valve, 1)
            sleep(2)
            GPIO.output(outlet_valve, 0)

            start_fill_time = time()
            flush_time_exceed = False

            while (self.debounce_levelsensor() == 0) and (flush_time_exceed == False):              
                print("Refill")
                if (time() - start_fill_time) > 50:
                    flush_time_exceed = False
                    print("Flushing takes to long ERROR")
                    logging.error("Flushing takes to long ERROR")
                    self._notifyObservers(Cycler.EVT_CYCLER_STATUS, "PUMP_ERROR")
                    self.stop_test()
                if self.run_cycler == False:
                    return()
                if (time() - start_flush_time) > flush_time:
                    break
                GPIO.output(pump, 1)
                sleep(0.1)
                    
            GPIO.output(pump, 0)

        GPIO.output(self.pump_2, 0)
        GPIO.output(self.pump_1, 0)
        GPIO.output(self.valve_in_med1,  0)
        GPIO.output(self.valve_in_med2,  0)


    def clean_container(self, medium, clean_time):
        """Open Air-Valve for cleaning during clean_time
           INPUT: int clean_time"""
        if self.run_cycler == False:
            return()
    
        if medium == "Medium-1" and self.current_medium == "Medium-1":
            print("Clean Med-1")
            logging.debug("Clean Med-1")
            GPIO.output(self.valve_out_med1, 1)
            sleep(2)
            GPIO.output(self.valve_cleaning, 1)
            sleep(clean_time)
        elif medium == "Medium-2" and self.current_medium == "Medium-2":
            print("Clean Med-2")
            logging.debug("Clean Med-2")
            GPIO.output(self.valve_out_med2, 1)
            sleep(2)
            GPIO.output(self.valve_cleaning, 1)
            sleep(clean_time)
        else:
            print("Clean-Error: wrong Medium name") 
            logging.error("Clean-Error: wrong Medium name")

        GPIO.output(self.valve_cleaning, 0)
        sleep(2)
        GPIO.output(self.valve_cleaning, 1)
        sleep(2)

        GPIO.output(self.valve_cleaning, 0)
        GPIO.output(self.valve_in_med1,  0)
        GPIO.output(self.valve_out_med1, 0)
        GPIO.output(self.valve_in_med2,  0)
        GPIO.output(self.valve_out_med2, 0)

    def loop(self):
        """Main loop for cycling. Controls Pump, valves, ... """      
        counter = 0
       
        max_cycles =     int(self.user_data["cycles"])
        clean_time =     int(self.user_data["reinigungszeit"])
        haltezeit =      int(self.user_data["haltezeit"])
        flush_time_1 =   int(self.user_data["dauer_links"])
        flush_time_2 =   int(self.user_data["dauer_rechts"])
        storage_medium = self.user_data["testend"]

        while (self.run_cycler == True) and (counter < max_cycles):               
            counter = counter + 1
            print("Cycles: " + str(counter))
            logging.debug("Cycles: " + str(counter))

            self._notifyObservers(Cycler.EVT_CYCLES, counter)
            self._notifyObservers(Cycler.EVT_CYCLER_STATUS, "UPDATE TEMP DATA")

            self.set_valves("Medium-1")
            self.fill("Medium-1")
            self.flush("Medium-1", flush_time_1, haltezeit)
            self.clean_container("Medium-1" ,clean_time)

            self.set_valves("Medium-2")
            self.fill("Medium-2")
            self.flush("Medium-2", flush_time_2, haltezeit)
            self.clean_container("Medium-2", clean_time)

        self._notifyObservers(Cycler.EVT_CYCLER_STATUS, "CYCLING END")

        #After testend store at Medium..
        if storage_medium == "STORAGE NONE":
            self._notifyObservers(Cycler.EVT_CYCLER_STATUS, "STORAGE NONE")
        elif storage_medium == "STORAGE 1":
            self._notifyObservers(Cycler.EVT_CYCLER_STATUS, "STORAGE 1")
            self.set_valves("Medium-1")
            self.fill("Medium-1")
            self.flush("Medium-1", 999999, haltezeit)
        elif storage_medium == "STORAGE 2":
            self._notifyObservers(Cycler.EVT_CYCLER_STATUS, "STORAGE 2")
            self.set_valves("Medium-2")
            self.fill("Medium-2")
            self.flush("Medium-2", 999999, haltezeit)
        else:
            print("Error wrong storage type")
            logging.debug("Error wrong storage type")
            
        
        self.stop_test()
        print("Cycler: All done")
        logging.debug("Cycler: All done")
        self._notifyObservers(Cycler.EVT_CYCLER_STATUS, "TEST END")


if __name__ == "__main__":
    cycler = Cycler()
    cycler.user_data                   = {}
    cycler.user_data["cycles"]         = "3"
    cycler.user_data["reinigungszeit"] = "2"
    cycler.user_data["haltezeit"]      = "5"
    cycler.user_data["dauer_links"]    = "25"
    cycler.user_data["dauer_rechts"]   = "15"
    cycler.user_data["testend"]        = "STORAGE 1"

    atexit.register(cycler.stop_test)
    cycler.loop()
