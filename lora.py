#!/usr/bin/env python3

from SX127x.LoRa import *
import time
import config
from SX127x.board_config import BOARD
import leds
import mqtt_i
import json

BOARD.setup()
BOARD.reset()


class mylora(LoRa):
    def publish_lora_sensors(self, pl, a='lora', n='device'):
        if a in config.config:
            s = config.config[a]
            try:
                plj = json.loads(pl.lower())
            except ValueError as error:
                # print("invalid json: %s" % error, '\r')
                return False
            for ss in range(0, len(s)):
                full_dev_name = config.device_name
                if n in s[ss]:
                    full_dev_name += '_' + a + '_' + s[ss][n]
                else:
                    full_dev_name += '_' + mqtt_i.mqtt["built_in"]
                if 'sensors' in s[ss]:
                    mqtt_i.mqtt_connect()
                    sensors = s[ss]["sensors"]
                    for sss in range(0, len(sensors)):
                        sensor = sensors[sss]["sensor"]
                        r = ' Reading: '
                        if s[ss][n]:
                            r += s[ss][n] + ', '
                        r += sensor + ' '
                        print(r.center(50, '*'), '\r')
                        mc = sensors[sss]["monitored_conditions"]

                        if mc:
                            leds.greenLed()
                            for c in mc:
                                if plj[n] == s[ss][n] and sensor.lower(
                                ) in plj:
                                    print(c.ljust(15, '.'), end=': ')
                                    pl = str(plj[sensor.lower()][c])
                                    print((pl + config.general[c]
                                           ["unit_of_measurement"]).rjust(10),
                                          end='')

                                    state_topic = full_dev_name.replace(
                                        " ", "_")
                                    state_topic += '/' + mqtt_i.mqtt[
                                        "sensor"] + '/'
                                    state_topic += sensor + "_" + c
                                    state_topic += '/' + mqtt_i.mqtt[
                                        "state"]
                                    state_topic = state_topic.lower()

                                    config.printAllowed = False
                                    print(', Publishing', end='')
                                    print(' to state_topic:',
                                          state_topic,
                                          end='')

                                    try:
                                        mqtt_i.mqttc.publish(state_topic, pl)
                                        print(', done!', end='')
                                    except Exception as e:
                                        print(
                                            ', error {0} publishing!'.format(
                                                e), '\r')

                                    time.sleep(
                                        mqtt_i.mqtt["mqtt_delay"])
                                    print('\r')

                                else:
                                    leds.redLed()
                                    print('no data!', '\r')
                        else:
                            leds.redLed()
                            print('No value from sensor!', '\r')
                else:
                    leds.redLed()
                    print('No sensors!', '\r')
        mqtt_i.mqtt_disconnect()
        config.printAllowed = True

    def __init__(self, verbose=False):
        super(mylora, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0] * 6)

    def on_rx_done(self):
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        pl = bytes(payload).decode("utf-8", 'ignore')
        print("Received:", pl, '\r')  # Receive DATA
        time.sleep(1)  # Wait for the client be ready
        self.publish_lora_sensors(pl)
        pl = [255, 255, 0, 0, 65, 67, 75, 0]
        print("Sending: ACK\r")
        self.write_payload(pl)  # Send ACK
        self.set_mode(MODE.TX)
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)  # Receiver mode

    def on_tx_done(self):
        print("TxDone", self.get_irq_flags())

    def on_cad_done(self):
        print("on_CadDone, ", self.get_irq_flags())

    def on_rx_timeout(self):
        print("on_RxTimeout, ", self.get_irq_flags())

    def on_valid_header(self):
        print("on_ValidHeader, ", self.get_irq_flags())

    def on_payload_crc_error(self):
        print("on_PayloadCrcError, ", self.get_irq_flags())

    def on_fhss_change_channel(self):
        print("on_FhssChangeChannel, ", self.get_irq_flags())

    def send(self, pl):
        b_pl = []
        b_pl.extend(map(ord, pl))
        print("Sending payload:", pl)
        self.write_payload(b_pl)  # Send INF
        self.set_mode(MODE.TX)
        time.sleep(0.5)
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)  # Receiver mode

    def start(self):
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)  # Receiver mode


lora = mylora(verbose=False)
lora.set_pa_config(pa_select=1, max_power=21, output_power=15)
lora.set_bw(BW.BW125)
lora.set_coding_rate(CODING_RATE.CR4_7)
lora.set_spreading_factor(9)
lora.set_rx_crc(True)

assert (lora.get_agc_auto_on() == 1)

lora.start()

if __name__ == "__main__":
    leds.config_leds()
    lora.publish_lora_sensors(
        '{"Count":13,"device":"node_mcu_25794f","DHT22":{"Temperature":15.150,"Humidity":66.66}}'
    )
