import config
import leds
import time
import mqtt_i


if 'onewire' in config.general['platforms']:
    from w1thermsensor import W1ThermSensor  # pip3 install w1thermsensor
    def w1():
        try:
            w1_sensor = W1ThermSensor()
            return round(w1_sensor.get_temperature(), 2)
        except Exception as e:
            print("Error: ", e)

if 'bme280' in config.general['platforms']:
    import smbus
    bus = smbus.SMBus(1)
    from i2csense.bme280 import BME280  # pip3 install i2csense
    def bme280(addr):
        try:
            BME280_address = BME280(bus)
            BME280_address.update()
            if BME280_address.sample_ok:
                return round(BME280_address._temperature,
                             2), round(BME280_address._humidity,
                                       2), round(BME280_address._pressure, 2)
        except Exception as e:
            print("Error: ", e)


# Type of sensor, can be Adafruit_DHT.DHT11, Adafruit_DHT.DHT22, or Adafruit_DHT.AM2302.
if 'dht' in config.general['platforms']:
    import Adafruit_DHT
    def dht_type():
        return Adafruit_DHT.AM2302
    def dht(typ, pin):
        try:
            humidity, temp = Adafruit_DHT.read_retry(typ, pin)
            if humidity: humidity = round(humidity, 2)
            else: humidity = 0
            if temp: temp = round(temp, 2)
            else: temp = 0
            return temp, humidity
        except Exception as e:
            print("Error: ", e)


def convertToNumber(data):
    # Simple function to convert 2 bytes of data
    # into a decimal number
    return ((data[1] + (256 * data[0])) / 1.2)


if 'bh1750' in config.general['platforms']:
    def bh1750(addr):
        ONE_TIME_HIGH_RES_MODE = 0x20
        try:
            data = bus.read_i2c_block_data(addr, ONE_TIME_HIGH_RES_MODE)
            return round(convertToNumber(data), 2)
        except Exception as e:
            print("Error: ", e)

def check_sensors(a, n):
    if a in config.config:
        s = config.config[a]
        for ss in range(0, len(s)):
            full_dev_name = config.device_name
            if 'device' in s[ss]:
                full_dev_name += '_' + a + '_' + s[ss]['device']
            else:
                full_dev_name += '_' + mqtt_i.mqtt["built_in"]
            if 'platform' in s[ss]:
                platform = s[ss]["platform"]
            else:
                return

            r = ' Reading: '
            if s[ss][n]:
                r += s[ss][n] + ', '
            r += platform + ' '
            print(r.center(50, '*'))
            t = 0
            h = 0
            p = 0
            i = 0
            b = 0

            if platform.lower() == "onewire":
                t = w1()
            if platform.lower() == "dht":
                t, h = dht(sensors.dht_type(), s[ss]["pin"])
            if platform.lower() == "bme280":
                t, h, p = bme280(s[ss]["i2c_address"])
            if platform.lower() == "bh1750":
                i = bh1750(s[ss]["i2c_address"])

            if platform.lower() == "lywsd03mmc":
                import LYWSD03MMC
                t, h, b = LYWSD03MMC.LYWSD03MMC(s[ss]["mac"])

            if t + h + p + i != 0 and s[ss]["monitored_conditions"]:
                leds.greenLed()
                for c in s[ss]["monitored_conditions"]:
                    print(c.ljust(15, '.'), end=': ')
                    if t != 0 and c == "temperature":
                        pl = t
                    elif h != 0 and c == "humidity":
                        pl = h
                    elif p != 0 and c == "pressure":
                        pl = p
                    elif i != 0 and c == "illuminance":
                        pl = i
                    elif b != 0 and c == "battery":
                        pl = b
                    else:
                        print()

                    print((str(pl) +
                           config.general[c]["unit_of_measurement"]).rjust(10),
                          end='')

                    state_topic = full_dev_name.replace(" ", "_")
                    state_topic += '/' + mqtt_i.mqtt["sensor"] + '/'
                    state_topic += platform + "_" + c
                    state_topic += '/' + mqtt_i.mqtt["state"]
                    state_topic = state_topic.lower()

                    print(', Publishing', end='')
                    print(' to state_topic:', state_topic, end='')

                    try:
                        mqtt_i.mqttc.publish(state_topic, pl)
                        print(', done!', end='')
                    except Exception as e:
                        print(', error {0} publishing!'.format(e))

                    time.sleep(mqtt_i.mqtt["mqtt_delay"])
                    print()

            else:
                leds.redLed()
                print('No value from sensor!')
