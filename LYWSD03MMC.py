#!/usr/bin/python3 -u

from bluepy import btle
import os
import re
from dataclasses import dataclass
from collections import deque
import threading
import time
import math

debug = False

@dataclass
class Measurement:
    temperature: float
    humidity: int
    voltage: float
    battery: int = 0

myMeasurement = Measurement(0, 0, 0, 0)

class MyDelegate(btle.DefaultDelegate):
    def __init__(self, params):
        btle.DefaultDelegate.__init__(self)
        # ... initialise here

    def handleNotification(self, cHandle, data):
        try:
            if debug: print('Got data:', data)
            myMeasurement.temperature = int.from_bytes(
                data[0:2], byteorder='little', signed=True) / 100.
            myMeasurement.humidity = int.from_bytes(data[2:3],
                                                    byteorder='little')
            voltage = int.from_bytes(data[3:5], byteorder='little') / 1000.
            # 3.1 or above --> 100% 2.1 --> 0 %
            myMeasurement.battery = min(int(round((voltage - 2.1), 2) * 100),
                                        100)
            myMeasurement.voltage = voltage

        except Exception as e:
            print(e)


# Initialisation  -------
def connect(address):
    p = btle.Peripheral(address)
    p.withDelegate(MyDelegate("abc"))
    return p


def LYWSD03MMC(address):
    connected = False
    try:
        if not connected:
            if debug: print("Connecting to BLE: " + address)
            p = connect(address)
            connected = True

        if p.waitForNotifications(4000):
            if debug: print("End of BLE notification")
            p.disconnect()

        return myMeasurement.temperature, myMeasurement.humidity, myMeasurement.battery

    except Exception as e:
        if debug: print("Connection lost: ", e)
        if connected is True:  # First connection abort after connected
            connected = False
        return 0, 0, 0


def main(m):
    print('Reading MAC.:', m)
    t, h, b = LYWSD03MMC(m)

    print('temperature.: '+str(t)+'°')
    print('humidity....: '+str(h)+'%')
    print('battery.....: '+str(b)+'%')


if __name__ == "__main__":
    main('58:2D:34:51:B7:FB')

# gatttool -I -b 58:2D:34:51:B7:FB
# char-read-uuid ebe0ccc1-7a0a-4b0c-8a1a-6ff2997da3a6
# characteristics
