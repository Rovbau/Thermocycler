#! python
# -*- coding: utf-8 -*-

# Controller for Thermocycling


from time import *
from threading import *
import atexit
import sys
import logging

class Cycler():

    EVT_CYCLER_STATUS = "EVT_CYCLER_STATUS"
    EVT_TEMP = "EVT_TEMP"

    def __init__(self):
        self.run_cycler = False
        self.observers = {}

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

    def start_test(self, run_status):
        self.run_cycler = True
        print("Cycler: Starting")
        ThreadEncoder=Thread(target=self.reading)
        ThreadEncoder.daemon=True
        ThreadEncoder.start()

    def stop_test(self):
        self.run_cycler = False

    def user_inputs(self, inputs):
        self.user_data = inputs

    def reading(self):
        dict_temp_values = {"TEMP-1": 14, "TEMP-2": 12.3}

        while self.run_cycler == True:
            print(self.user_data)
            self._notifyObservers(Cycler.EVT_CYCLER_STATUS, "PUMP_ERROR")
            
            self._notifyObservers(Cycler.EVT_TEMP, dict_temp_values)

            print("Its HOT ..no.. Cold")
            sleep(5)

        print("Cycler: Ending cycling")
        return()
     
if __name__ == "__main__":
    cycler = Cycler()
    cycler.reading()
    pass