import yaml

with open(r'config.yaml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

    print(config["general"]["company_name"], config["general"]["device_name"],
          config["general"]["version"])

    # print(config["mqtt"]["port"])
    # print("sensor_component:", config["mqtt"]["sensor_component"])

# if config["sensor"]:
#     for s in config["sensor"]:
#         if "platform" in s:
#             print("Setting up:", s["name"], ",", s["platform"])

if config["general"]["status_leds"]:
    for p in config["general"]["status_leds"]:
        # print(p)
        print(p["pin"])
        # if p["pin"]:
        # if "platform" in s:
        #     print("Setting up:", s["name"], ",", s["platform"])
