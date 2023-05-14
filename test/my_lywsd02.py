from lywsd02 import Lywsd02Client


def main(m):
    print('Reading MAC:', m)

    client = Lywsd02Client(m)
    data = client.data

    with client.connect():
        data = client.data
        print('Temperature.:', data.temperature)
        print('Humidity....:', data.humidity)
        print('Battery.....:', client.battery)

if __name__ == "__main__":
    main('A4:C1:38:89:F7:CA')
