import smbus
 
# Define some constants from the datasheet
BH1750_address     = 0x23 # Default BH1750_address I2C address
ONE_TIME_HIGH_RES_MODE = 0x20
 
bus = smbus.SMBus(1)  # Rev 2 Pi uses 1
 
def convertToNumber(data):
  # Simple function to convert 2 bytes of data
  # into a decimal number
  return ((data[1] + (256 * data[0])) / 1.2)
 
def readLight(addr=BH1750_address):
  data = bus.read_i2c_block_data(addr,ONE_TIME_HIGH_RES_MODE)
  return round(convertToNumber(data),2)
 
def main():
  print("Light Level : " + str(readLight()) + " lux")
 
if __name__=="__main__":
   main()