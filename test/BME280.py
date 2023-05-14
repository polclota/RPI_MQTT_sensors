import smbus
import time
from i2csense.bme280 import BME280

bus = smbus.SMBus(1)

sensor = BME280(bus)

def main():
    sensor.update()
    if sensor.sample_ok:
        print(sensor.current_state_str)
    else: 
        print("An error has occured")

if __name__=="__main__":
   main()