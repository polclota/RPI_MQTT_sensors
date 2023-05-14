import yaml
import socket
import os
dirname = os.path.dirname(__file__)

printAllowed = True

with open(dirname + '/config-' + socket.gethostname() + '.yaml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)
    general = config["general"]
    device_name = general["device_name"]
    device_name = device_name.replace('hostname', socket.gethostname())

if __name__ == "__main__":
    print(dirname)
    print(general['company_name'], device_name, general['model'])

    # bme280', 'bh1750', 'dht', 'onewire'

