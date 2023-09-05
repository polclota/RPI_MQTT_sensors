import paho.mqtt.client as mqttp
import random
import time
import config as config
if config.general['hardware'].lower() == "opi":
    from pyA20.gpio import gpio
    from pyA20.gpio import port
else:
    import RPi.GPIO as GPIO
    GPIO.setwarnings(False)  # Ignore warning for now
    GPIO.setmode(GPIO.BCM)  # Use physical pin numbering
import sys

done_subs = False

if "mqtt" in config.config:
    mqtt = config.config['mqtt']
    mqttc = mqttp.Client("domIot_RPI_{0}".format(random.random()))
    mqttc.username_pw_set(mqtt["user"], password=mqtt["password"])
else:
    print('MQTT config missing or not found!')
    sys.exit()


def domain_base(s, domain):
    base = (config.device_name + ' ' + mqtt["built_in"]).replace(" ",
                                                                 "_").lower()
    base += '/' + domain + '/'
    base += s["platform"].lower() + "_" + s["name"].lower().replace(" ", "_")
    return base


def on_message(client, userdata, msg):
    m = msg.payload.decode("utf-8")
    t = msg.topic
    print(t + ":" + m)
    for s in config.config["switch"]:
        if s["platform"].lower() == "gpio":
            if domain_base(s, mqtt["switch"]) in t:
                pin = s["pin"]

                if m.lower() == mqtt["payload_on"].lower():
                    s = mqtt["state_on"]
                    if config.general['hardware'].lower() == "opi":
                        gpio.output(getattr(port,pin), gpio.HIGH)
                    else:
                        GPIO.output(pin, GPIO.HIGH)
                elif m.lower() == mqtt["payload_off"].lower():
                    s = mqtt["state_off"]
                    if config.general['hardware'].lower() == "opi":
                        gpio.output(getattr(port,pin), gpio.LOW)
                    else:
                        GPIO.output(pin, GPIO.LOW)

                mqttc.publish(t.replace(mqtt["command"], mqtt["state"]), s)


mqttc.on_message = on_message


def on_connect(client, userdata, flags, rc):
    global done_subs
    print("Connected with result code " + str(rc))
    domain_subs(mqtt["switch"])
    domain_subs(mqtt["binary_sensor"])
    done_subs = True


mqttc.on_connect = on_connect


def mqtt_connect():
    if not mqttc.is_connected():
        print('Connecting to MQTT on {0}'.format(mqtt["host"]), end='')
        try:
            mqttc.connect(mqtt["host"], mqtt["port"])
            if mqttc.is_connected:
                print(", done!\r")
        except Exception as e:
            print("MQTT Error: ", e, '\r')


def mqtt_disconnect():
    # if mqttc.is_connected():
    print('Disconnecting from MQTT\r')
    mqttc.disconnect()


def device_name_f(s, ss, full_dev_name):
    device = '{'
    device += '"identifiers":"' + full_dev_name.replace(' ',
                                                        '_').lower() + '",'
    device += '"name":"' + full_dev_name + '",'
    if 'sw_version' in s[ss]:
        device += '"sw_version":"' + s[ss]["sw_version"] + '"'
    else:
        device += '"sw_version":"' + config.general["sw_version"] + '"'
    device += ','
    if 'manufacturer' in s[ss]:
        device += '"manufacturer":"' + s[ss]["manufacturer"] + '"'
    else:
        device += '"manufacturer":"' + config.general["manufacturer"] + '"'
    device += ','
    if 'model' in s[ss]:
        device += '"model":"' + s[ss]["model"] + '"'
    else:
        device += '"model":"' + config.general["model"] + '"'
    device += '}'
    return device


def all_conditions(delete, s, ss, platform, domain, device_name, sensor_name,
                   retain):
    full_dev_name = config.device_name + ' ' + device_name
    device = device_name_f(s, ss, full_dev_name)
    platform = platform.lower()

    if s[ss]["monitored_conditions"]:
        for c in s[ss]["monitored_conditions"]:
            base = mqtt[
                "discovery_prefix"] + '/' + domain + '/' + device_name.replace(
                    " ", "_").lower() + "_" + platform + "_" + c
            topic = base + "/" + mqtt["config"]
            if not delete:
                name = full_dev_name + ' ' + platform + ' ' + c
                unique_id = name.replace(" ", "_").lower()

                state_topic = full_dev_name.replace(" ", "_").lower()
                state_topic += '/' + domain + '/'
                state_topic += platform + "_" + c
                state_topic += '/' + mqtt["state"]

                pl = '{'
                # pl += '"~": "' + base + '",'
                # pl += '"stat_t": "~/' + mqtt["state"]+ '",'
                pl += '"name": "' + name + '",'
                if device:
                    pl += '"device": ' + device + ','
                pl += '"state_topic": "' + state_topic + '",'
                pl += '"unique_id": "' + unique_id + '",'
                pl += '"device_class":"' + c + '",'
                if config.general.get(c):
                    pl += '"unit_of_measurement": "' + config.general[c][
                        "unit_of_measurement"]
                pl += '"}'

                # print('Setting up:', topic)
                print('as: ', pl, end='')
            else:
                pl = ''
                print('Deleting:', topic, end='')

            # (result1, mid) =
            if mqttc.publish(topic.lower(), pl, retain=retain):
                print(', done!', end='')
            else:
                print(', error!', end='')
            time.sleep(mqtt["mqtt_delay"])

            print()


def pins(delete, s, ss, domain, device_name, retain):
    full_dev_name = config.device_name + ' ' + device_name
    device = device_name_f(s, ss, full_dev_name)
    platform = s[ss]["platform"].lower()

    if s[ss]["name"]:
        c = s[ss]["name"].lower().replace(" ", "_")
        base = mqtt[
            "discovery_prefix"] + '/' + domain + '/' + device_name.replace(
                " ", "_").lower() + "_" + platform + "_" + c
        topic = base + "/" + mqtt["config"]
        if not delete:
            name = full_dev_name + ' ' + platform + ' ' + c
            unique_id = name.replace(" ", "_").lower()

            state_topic = full_dev_name.replace(" ", "_").lower()
            state_topic += '/' + domain + '/'
            state_topic += platform + "_" + c
            state_topic += '/' + mqtt["state"]

            cmd_topic = full_dev_name.replace(" ", "_").lower()
            cmd_topic += '/' + domain + '/'
            cmd_topic += platform + "_" + c
            cmd_topic += '/' + mqtt["command"]

            availability_topic = full_dev_name.replace(" ", "_").lower()
            availability_topic += '/' + domain + '/'
            availability_topic += platform + "_" + c
            availability_topic += '/' + mqtt["availability"]

            pl = '{'
            pl += '"name": "' + name + '",'
            if device:
                pl += '"device": ' + device + ','
            if "payload_on" in mqtt:
                pl += '"payload_on":"' + mqtt["payload_on"] + '",'
            if "payload_off" in mqtt:
                pl += '"payload_off":"' + mqtt["payload_off"] + '",'

            if domain == mqtt['switch']:
                pl += '"command_topic": "' + cmd_topic + '",'
                if "state_on" in mqtt:
                    pl += '"state_on":"' + mqtt["state_on"] + '",'
                if "state_off" in mqtt:
                    pl += '"state_off":"' + mqtt["state_off"] + '",'

            elif domain == mqtt['binary_sensor']:
                # if "payload_available" in mqtt:
                #     pl += '"payload_available":"' + mqtt["payload_available"] + '",'
                # if "payload_not_available" in mqtt:
                #     pl += '"payload_not_available":"' + mqtt["payload_not_available"] + '",'
                if "device_class" in s[ss]:
                    pl += '"device_class":"' + s[ss]["device_class"] + '",'

            if "icon" in s[ss]:
                pl += '"icon":"' + s[ss]["icon"] + '",'
            pl += '"state_topic": "' + state_topic + '",'
            pl += '"availability_topic": "' + availability_topic + '",'
            pl += '"unique_id": "' + unique_id
            pl += '"}'

            # print('Setting up:', topic)
            print('as: ', pl, end='')
        else:
            pl = ''
            print('Deleting:', topic, end='')

        # (result1, mid) =
        if mqttc.publish(topic.lower(), pl, retain=retain):
            print(', done!', end='')
        else:
            print(', error!', end='')
        time.sleep(mqtt["mqtt_delay"])

        print()


pinStatus = {}
buttonEventHandlerBusy = False
buttonEventHandlerDone = False
c = 0


def payload(s, p):
    r = ''
    inverted = 'inverted' in s and s['inverted']
    if p:
        if inverted:
            r = mqtt['payload_on']
        else: r = mqtt['payload_off']
    else:
        if inverted:
            r = mqtt['payload_off']
        else: r = mqtt['payload_on']
    return r

def buttonEventHandler(channel):
    global pinStatus, buttonEventHandlerBusy, buttonEventHandlerDone, c
    buttonEventHandlerDone = False
    cc = config.config['binary_sensor']
    if buttonEventHandlerBusy: return
    buttonEventHandlerBusy = True
    for s in cc:
        if s['pin'] == channel:
            if s["platform"].lower() == "gpio":
                # time.sleep(.1)
                p = GPIO.input(s["pin"])
                r = payload(s, p)
                t = domain_base(s, mqtt["binary_sensor"]) + '/' + mqtt["state"]
                c +=1
                print(c,'1-Publishig:', s['name'], r, end='')
                if mqttc.publish(t, r):
                    print(', done!')
                else:
                    print(', error!')
                pinStatus[s["pin"]] = p
    buttonEventHandlerBusy = False

def binary_sensor_loop():
    global buttonEventHandlerBusy, buttonEventHandlerDone

    if not buttonEventHandlerBusy and not buttonEventHandlerDone:
        global pinStatus, c
        cc = config.config['binary_sensor']
        for s in cc:
            if config.general['hardware'].lower() == "opi":
                pass
            else:
                p = GPIO.input(s["pin"])
                if pinStatus[s["pin"]] != p and pinStatus[s["pin"]] != 3:
                    buttonEventHandlerDone = True
                    pinStatus[s["pin"]] = p
                    r = payload(s, p)
                    print(c,'2-Publishig:', s['name'], r, end='')
                    t = domain_base(s, mqtt["binary_sensor"]) + '/' + mqtt["state"]
                    if mqttc.publish(t, r):
                        print(', done!')
                    else:
                        print(', error!')


def setupPins(domain, direction):
    global pinStatus
    for s in config.config[domain]:
        if s["platform"].lower() == "gpio":
            if config.general['hardware'].lower() == "opi":
                pass
            else:
                GPIO.setup(s["pin"], direction)
                if domain == mqtt['binary_sensor']:
                    pinStatus[s["pin"]] = 3
                    if 'bouncetime' in s:
                        bt = s['bouncetime']
                    else:
                        bt = 200
                    GPIO.add_event_detect(s['pin'],
                                        GPIO.BOTH,
                                        callback=buttonEventHandler,
                                        bouncetime=bt)


def domain_subs(domain):
    for s in config.config[domain]:
        if s["platform"].lower() == "gpio":
            cmd_topic = domain_base(s, domain) + '/' + mqtt["command"]
            aval_topic = domain_base(s, domain) + '/' + mqtt["availability"]
            print('Subscribing to:', cmd_topic, end='')

            if mqttc.subscribe(cmd_topic):
                print(', done!')
            else:
                print(', error!')

            print('Publishig availability to:', aval_topic, end='')
            if mqttc.publish(aval_topic, mqtt["online"], retain=True):
                print(', done!')
            else:
                print(', error!')
            time.sleep(mqtt["mqtt_delay"])


def unaval(domain):
    for s in config.config[domain]:
        if s["platform"].lower() == "gpio":
            aval_topic = domain_base(s, domain) + '/' + mqtt["availability"]

            p = mqtt["offline"]
            print('Publishig', p, 'to:', aval_topic, end='')
            if mqttc.publish(aval_topic, p, retain=True):
                print(', done!')
            else:
                print(', error!')
            time.sleep(mqtt["mqtt_delay"])


def define_MQTT_sensors(delete=False, retain=False):
    if "lora" in config.config:
        s = config.config["lora"]
        for ss in range(0, len(s)):
            dev_name = s[ss]['device']
            if 'sensors' in s[ss]:
                l = s[ss]['sensors']
                for m in range(0, len(l)):
                    sens = l[m][mqtt["sensor"]]
                    all_conditions(delete, l, m, sens, mqtt["sensor"],
                                   'lora ' + dev_name, dev_name, retain)

    if "ble" in config.config:
        s = config.config["ble"]
        for ss in range(0, len(s)):
            dev_name = s[ss]['device']
            platform = s[ss]['platform'].lower()
            all_conditions(delete, s, ss, platform, mqtt["sensor"],
                           'ble ' + dev_name, dev_name, retain)

    if "sensor" in config.config:
        s = config.config["sensor"]
        for ss in range(0, len(s)):
            dev_name = s[ss]["name"]
            platform = s[ss]["platform"].lower()
            all_conditions(delete, s, ss, platform, mqtt["sensor"],
                           mqtt["built_in"], dev_name, retain)

    if "switch" in config.config:
        s = config.config["switch"]
        for ss in range(0, len(s)):
            pins(delete, s, ss, mqtt["switch"], mqtt["built_in"], retain)

    if "binary_sensor" in config.config:
        s = config.config["binary_sensor"]
        for ss in range(0, len(s)):
            pins(delete, s, ss, mqtt["binary_sensor"], mqtt["built_in"],
                 retain)


if config.general['hardware'].lower() == "opi":
    setupPins(mqtt["switch"], gpio.OUTPUT)
    setupPins(mqtt["binary_sensor"], gpio.INPUT)
else:
    setupPins(mqtt["switch"], GPIO.OUT)
    setupPins(mqtt["binary_sensor"], GPIO.IN)


def main():
    try:
        # mqtt_connect()
        # define_MQTT_sensors()
        # define_MQTT_sensors(
        #     delete=True,
        #     retain=True)  # d, deletes configuration, r = retained message
        # mqttc.loop_start()
        while True:
            binary_sensor_loop()
    except KeyboardInterrupt as k:
        print('Program exited with: {0}'.format(k))
        mqttc.loop_stop()
        if config.general['hardware'].lower() == "opi":
            pass
        else:
            GPIO.cleanup()



if __name__ == "__main__":
    main()