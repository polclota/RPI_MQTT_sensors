import paho.mqtt.client as mqtt
import config as config

c_mqtt = mqtt_i.mqtt

mqttc = mqtt.Client("domIot_RPI_{0}".format(99))
mqttc.username_pw_set(mqtt_i.mqtt["user"],
                      password=mqtt_i.mqtt["password"])

print('Connecting to MQTT on {0}'.format(c_mqtt["host"]), end='')
mqttc.connect(c_mqtt["host"], c_mqtt["port"])
if mqttc.is_connected:
    print(", done!")

tp = "officerpi_built_in/sensor/bme280_temperature/state"
pl = 89
if mqttc.publish(tp, pl):
    print(tp, pl)

mqttc.disconnect()
