import RPi.GPIO as GPIO
import config
import time

GPIO.setmode(GPIO.BCM)  # Use physical pin numbering
GPIO.setwarnings(False)  # Ignore warning for now
GPIO.setup(21, GPIO.OUT, initial=0)
GPIO.output(21, GPIO.HIGH)
