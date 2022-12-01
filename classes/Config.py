import configparser
import os
import sys
from classes.File import File


class Config:
    __CONFIG_EXTENSION = "config"
    __CONFIG_PATH = "config" + os.path.sep

    @classmethod
    def read_config(cls, filename: str, section: str, defaults=None):
        """ Read configuration from file"""

        if defaults is None:
            defaults = []

        config_file = File.path_and_extension(cls.__CONFIG_PATH, filename, cls.__CONFIG_EXTENSION)

        # Test if configuration file exists
        if not os.path.isfile(config_file):
            print("Config file " + config_file + " does not exist")
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
    def get_style(cls, filename: str, section: str):
        defaults = {'style': ""}

        config = cls.read_config(filename, section, defaults=defaults)

        style = config.get(section, 'style')

        if style is None:
            print(f"Config file {filename} with Section {section} has no style entry.")
            sys.exit()

        return config.get(section, 'style')

    @classmethod
    def get_sections(cls, file_and_path: str):
        cls.file_exists(file_and_path)
        config = configparser.ConfigParser()
        try:
            config.read(file_and_path)

        except configparser.DuplicateSectionError as e:
            print(
                f"Duplicate Section {e.args[0]} in file {e.args[1]} in line {e.args[2]}"
                f"\nPlease correct this line and run configMaker again.")

            sys.exit()

        return config.sections()

    @staticmethod
    def section_exists(sections, section):
        if section in sections:
            return True
        return False

    @staticmethod
    def file_exists(file):
        # Test if configuration file exists
        if not os.path.isfile(file):
            print("Config file " + file + " does not exist")
            sys.exit()
        return True
