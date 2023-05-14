import sys

import socket
import config
import time
import datetime
import mqtt_i


def main():

    try:
        mqtt_i.mqtt_connect()

        while True:
            print()

    except Exception as e:
        mqtt_i.mqtt_disconnect()
        print('Error: {0}'.format(e))

if __name__ == "__main__":
    main()