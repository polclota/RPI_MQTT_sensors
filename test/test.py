from bluepy import btle
import time

class MyDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)
        # ... initialise here

    def handleNotification(self, cHandle, data):
        try:
            temp = int.from_bytes(
                data[0:2], byteorder='little', signed=True)/100
            humidity = int.from_bytes(data[2:3], byteorder='little')
            voltage = int.from_bytes(data[3:5], byteorder='little') / 1000.
            bat = min(int(round((voltage - 2.1), 2) * 100), 100)

            j = 12
            print()
            print('temp:'.ljust(j,"."), temp)
            print('humidity:'.ljust(j,"."), humidity)
            print('voltage:'.ljust(j,"."), voltage)
            print('battery:'.ljust(j,"."), bat)
            print()

        except Exception as e:
            print(e)
            # ... perhaps check cHandle
            # ... process 'data'

            # Initialisation  -------


add = "A4:C1:38:89:F7:CA"
print("domIoT BLE notifications for:", add)

# Setup to turn notifications on, e.g.
#   svc = p.getServiceByUUID( service_uuid )
#   ch = svc.getCharacteristics( char_uuid )[0]
#   ch.write( setup_data )

# Main loop --------

secs = 10

while True:
    try:
        p = btle.Peripheral(add)
        p.setDelegate(MyDelegate())
        if p.waitForNotifications(1.0):
            continue
        # print("Disconecting")
        # if p.disconnect(): print("Done!")
    except Exception as e:
        print(e)
    print("Waiting for next read: ", secs, "secs")
    time.sleep(secs)
    # Perhaps do something else here
