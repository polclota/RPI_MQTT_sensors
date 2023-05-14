import RPi.GPIO as GPIO  # Allows us to call our GPIO pins and names it just GPIO
import config
import time

mqtt = config.config['mqtt']

c = 0

def buttonEventHandler(channel):
    s = []
    for ss in config.config['binary_sensor']:
        if ss['pin'] == channel: 
            s = ss
    # time.sleep(0.1)
    p = GPIO.input(s["pin"])
    if p:
        r = mqtt['payload_off']
    else:
        r = mqtt['payload_on']
    global c
    c +=1    
    print('{0}-{1}, {2}'.format(c, s['name'], r))


GPIO.setmode(GPIO.BCM)  # Set's GPIO pins to BCM GPIO numbering
for s in config.config['binary_sensor']:
    print(s['pin'])
    GPIO.setup(s['pin'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Set our input pin to be an input
    GPIO.add_event_detect(s['pin'],
                          GPIO.BOTH,
                          callback=buttonEventHandler,
                          bouncetime=200)

# Wait for the input to go low, run the function when it does

while True:
    pass
GPIO.cleanup()