#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import datetime
import config
import sensors
import mqtt_i
import leds

if config.general['hardware'].lower() == "opi":
    from pyA20.gpio import gpio as GPIO
else:
    import RPi.GPIO as GPIO
if 'lora' in config.config:
    import lora

import keys

print(config.general['company_name'], config.device_name)
print('Date: {0}'.format(time.strftime('%d-%m-%Y %H:%M:%S')))
if "status_leds" in config.general: 
    leds.config_leds()
    leds.blinkLeds()
print('Logging sensor measurements to MQTT every {0} seconds.'.format(
config.general["scan_interval"]))

print('Press ctrl-C to quit.')
try:

    mqtt_i.mqtt_connect()
    if mqtt_i.mqtt["auto_configure"]:
        mqtt_i.define_MQTT_sensors(retain=True)

    mqtt_i.mqttc.loop_start()
    while True:
        if mqtt_i.done_subs: 
            break

    if 'lora' in config.config:
        kb = keys.KBHit()
        i = config.config['lora']
        for d in range(0, len(i)):
            if 'scan_interval' in i[d]:
                lora.lora.send('timer ' + str(i[d]['scan_interval']))
        keys.help()

    tp = 0
    tpp = 0
    d = False
    n = False
    c = chr(0)
    while True:
        mqtt_i.binary_sensor_loop()
        if n:
            n = False
            target = datetime.datetime.fromtimestamp(
                tp + config.general["scan_interval"])
            print(target.strftime('%H:%M:%S'), 'next update', end='')
            if 'lora' in config.config: print(', listening to LoRa messages')
            else: print()

        if d:
            if int(datetime.datetime.now().timestamp()
                   ) > tpp and config.printAllowed:
                tpp = int(datetime.datetime.now().timestamp())
                # print("\r", end='', flush=True)
                currenttime = time.strftime('%H:%M:%S')
                # print(currenttime, end=' ', flush=True)

        d = True

        if tp == 0 or int(datetime.datetime.now().timestamp()
                          ) > tp + config.general["scan_interval"]:
            n = True
            tp = int(datetime.datetime.now().timestamp())
            print('*'.ljust(50, "*"))

            # builtin sensors loop
            if "sensor" in config.config:
                sensors.check_sensors("sensor", "name")

            # ble loop
            if "ble" in config.config:
                sensors.check_sensors("ble", "device")

        if 'lora' in config.config:
            if kb.kbhit():
                ch = kb.GetCh()
                if ch in [chr(3), chr(27)]:
                    break
                ch = ch.lower()
                if ch == 'h':
                    keys.help()
                else:
                    s, r = keys.option(ch)
                    if s:
                        lora.lora.send(r)
                    else:
                        print(r)

        # if 'switch' in config.config:

except Exception as e:
    print('Error: {0}'.format(e))
    if "mqtt" in config.config:
        mqtt_i.mqtt_disconnect()
    GPIO.cleanup()
except KeyboardInterrupt as k:
    print('Program exited with: {0}'.format(k))
    if "mqtt" in config.config:
        if "switch" in config.config: 
            mqtt_i.unaval(mqtt_i.mqtt["switch"])
        if "binary_sensor" in config.config: 
            mqtt_i.unaval(mqtt_i.mqtt["binary_sensor"])
        mqtt_i.mqtt_disconnect()
    if config.general['hardware'].lower() == "opi":
        pass
    else:    
        GPIO.cleanup()
