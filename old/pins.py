GPIO.setwarnings(False)  # Ignore warning for now
GPIO.setmode(GPIO.BCM)  # Use physical pin numbering

pins = [13, 6, 26, 19]
value = ["1", "2", "3", "4"]

for p in pins:
    GPIO.setup(p, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(p, GPIO.IN)
