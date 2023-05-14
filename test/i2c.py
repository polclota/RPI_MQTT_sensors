import smbus
import time
from i2csense.bme280 import BME280

# bus = smbus.Bus(1)
bus = smbus.SMBus(1)

BME280_address = BME280(bus)
delta_secs = 10
# Define some constants from the datasheet
BH1750_address     = 0x23 # Default BH1750_address I2C address
POWER_DOWN = 0x00 # No active state
POWER_ON   = 0x01 # Power on
RESET      = 0x07 # Reset data register value
ONE_TIME_HIGH_RES_MODE = 0x20

def convertToNumber(data):
  # Simple function to convert 2 bytes of data
  # into a decimal number
  return ((data[1] + (256 * data[0])) / 1.2)
 
def readLight(addr=BH1750_address):
  data = bus.read_i2c_block_data(addr,ONE_TIME_HIGH_RES_MODE)
  return convertToNumber(data)
 

def main():
 
    BME280_address.update()
    if not BME280_address.sample_ok:
        print("An error has occured")
    else: 
        print("BME280: Temperature: {:0.2f} °C".format(BME280_address._temperature),"Humidity: {:0.2f} %".format(BME280_address._humidity),"Pressure: {:0.2f} mb".format(BME280_address._pressure))
    print(    "BH1750: Light Level: {:0.2f} lux".format(readLight()))
 
if __name__=="__main__":
   main()