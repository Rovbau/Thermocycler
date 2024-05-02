import RPi.GPIO as GPIO
from time import sleep, time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO.setup(40, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

while (True):

    print (GPIO.input(40))


GPIO.setup(22,  GPIO.OUT)
GPIO.output(22,  0)
sleep ( 5)
GPIO.output(22,  1)