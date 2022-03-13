import configparser
import importlib
import sys


def dynamicallyLoadModule():
    # -l141 - w97 - h 17.5 - d 5 - s 1.5 - o mbox
    # https://stackoverflow.com/questions/547829/how-to-dynamically-load-a-python-class

    config = configparser.ConfigParser()
    print(sys.argv[1])
    config.read(sys.argv[1])

    if not config.sections():
        print(f"Konfigurationsdatei {sys.argv[1]} nicht gefunden oder leer")
        sys.exit(-1)

    error = ""
    for config_set in config.sections():
        try:

            module_name = config[config_set]['type']
            module = importlib.import_module("classes." + module_name)
            class_ = getattr(module, config[config_set]['type'])
            instance = class_()
        except Exception as e:
            print(e)

    print(config_set)
    print(config.items(config_set))
