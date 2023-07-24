import config
if config.general['hardware'].lower() == "opi":
    from pyA20.gpio import gpio
    from pyA20.gpio import port
else:
    import RPi.GPIO as GPIO
    GPIO.setwarnings(False)  # Ignore warning for now
    GPIO.setmode(GPIO.BCM)  # Use physical pin numbering
import time
import config

def config_leds():
    if "status_leds" in config.general:
        for p in config.general["status_leds"]:
            if p["pin"]:
                if config.general['hardware'].lower() == "opi":
                    gpio.setcfg(getattr(port,p["pin"]), gpio.OUTPUT)
                else:
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