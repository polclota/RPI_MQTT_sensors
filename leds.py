import RPi.GPIO as GPIO
import config
import time
import config

GPIO.setwarnings(False)  # Ignore warning for now
GPIO.setmode(GPIO.BCM)  # Use physical pin numbering


def config_leds():
    if "status_leds" in config.general:
        for p in config.general["status_leds"]:
            if p["pin"]:
                GPIO.setup(p["pin"], GPIO.OUT, initial=0)
                print("Set up LED at pin:", p["pin"])


def blinkLeds():
    if "status_leds" in config.general:
        for p in config.general["status_leds"]:
            if p["pin"]:
                GPIO.output(p["pin"], GPIO.HIGH)
                time.sleep(p["interval"])
                GPIO.output(p["pin"], GPIO.LOW)
                time.sleep(p["interval"])


def greenLed():
    if "status_leds" in config.general:
        for p in config.general["status_leds"]:
            if p["name"].lower() == 'green':
                GPIO.output(p["pin"], GPIO.HIGH)
                time.sleep(p["interval"])
                GPIO.output(p["pin"], GPIO.LOW)
                time.sleep(p["interval"])


def redLed():
    if "status_leds" in config.general:
        for p in config.general["status_leds"]:
            if p["name"].lower() == 'red':
                GPIO.output(p["pin"], GPIO.HIGH)
                time.sleep(p["interval"])
                GPIO.output(p["pin"], GPIO.LOW)
                time.sleep(p["interval"])


def main():
    config_leds()
    blinkLeds()
    greenLed()
    redLed()


if __name__ == "__main__":
    main()