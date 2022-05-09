import configparser
import os
import sys
from classes.File import File


class Config:

    __CONFIG_EXTENSION = "config"
    __CONFIG_PATH = os.path.sep + "config" + os.path.sep

    @classmethod
    def read_config(cls, defaults: [], filename: str, section: str):
        """ Read configuration from file"""

        config_file = cls.__config_path_and_extension(filename)

        # Test if configuration file exists
        if not os.path.isfile(config_file):
            print("Config file " + cls.__CONFIG_PATH + filename + " not found")
            sys.exit()

        # read entries from the configuration file
        config = configparser.ConfigParser(defaults=defaults)
        config.read(config_file)

        # Test if requested section exists
        if not config.has_section(section):
            print("Section " + section + " in config file " + config_file + " not found")
            sys.exit()

        return config

    @classmethod
    def __config_path_and_extension(cls, filename: str) -> str:
        return cls.__CONFIG_PATH + File.set_file_extenstion(filename, cls.__CONFIG_EXTENSION)
