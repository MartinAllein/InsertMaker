import configparser
import os
import sys
from classes.File import File


class Config:
    __CONFIG_EXTENSION = "config"

    @classmethod
    def read_config(cls, filename: str, section: str, defaults=None):
        """ Read the given section from a configuration file

        :param filename: config filename
        :param section: section of config file to read
        :param defaults:
        :return:
        """

        if defaults is None:
            defaults = []

        config_file = File.path_and_extension("", filename, cls.__CONFIG_EXTENSION)

        # Test if configuration file exists
        if not os.path.isfile(config_file):
            print("Config file " + config_file + " does not exist")
            sys.exit(-1)

        # read entries from the configuration file
        config = configparser.ConfigParser(defaults=defaults)
        config.read(config_file)

        # Test if requested section exists
        if not config.has_section(section):
            print("Section " + section + " in config file " + config_file + " not found")
            sys.exit(-1)

        return config


    @classmethod
    def get_style(cls, filename: str, section: str):
        """ Returns the style from a configuration within a configuration file

        :param filename: configuration file
        :param section: section of the configuration file where to look for the style
        :return: style of the item (CardSheet, CardBox, ....)
        """
        defaults = {'style': ""}

        config = cls.read_config(filename, section, defaults=defaults)

        style = config.get(section, 'style')

        if style is None:
            print(f"Config file {filename} with Section {section} has no style entry.")
            sys.exit(-1)

        return config.get(section, 'style')

    @classmethod
    def get_sections(cls, file_and_path: str):
        """ Returns a list of all sections in a config file

        :param file_and_path: filename and path of the config file to get all the sections
        :return: list of section names that are in the given config file
        """
        cls.file_exists(file_and_path)
        config = configparser.ConfigParser()
        try:
            config.read(file_and_path)

        except configparser.DuplicateSectionError as e:
            print(
                f"Duplicate Section {e.args[0]} in file {e.args[1]} in line {e.args[2]}"
                f"\nPlease correct this line and run configMaker again.")

            sys.exit(-1)

        # return all sections in the project file
        return config.sections()

    @staticmethod
    def section_exists(sections, section):
        """ Test if a section exists in a list of sections

        :param sections: list of sections
        :param section: section to test
        :return: true if found, fals if not found
        """
        if section in sections:
            return True
        return False

    @staticmethod
    def file_exists(file):
        """ Test if file exists

        :param file: file with path to test
        :return: true if exists, false if not
        """
        # Test if configuration file exists
        if not os.path.isfile(file):
            print("File " + file + " does not exist")
            sys.exit(-1)
        return True

    @staticmethod
    def read_config_list(file, section, items, with_empty=False, textmode=False):
        """ Read all entries from list items from config file

        """
        # self.measures.update({k: args['options'][k] for k in keys if k in args['options']})
        # https://stackoverflow.com/questions/10308939/list-comprehensions-splitting-loop-variable
        # foo = [(x[1], x[2]) for x in (x.split(";") for x in items.split("\n")) if x[1] != 5]

        # create dictionary with empty values as defaults
        defaults = {k: "" for k in items}
        config = Config.read_config(file, section, defaults)
        if with_empty:
            # keep empty entries
            result = {k: Config.cast_config(config.get(section, k), textmode) for k in items}
        else:
            # remove empty entries
            result = {k: Config.cast_config(config.get(section, k), textmode) for k in items if
                      config.get(section, k) != ''}
        return result

    @staticmethod
    def cast_config(a: str, textmode=True):
        # https://stackoverflow.com/questions/33645965/configparser-integers
        if textmode:
            return a

        try:
            # First, we try to convert to integer.
            # (Note, that all integer can be interpreted as float and hex number.)
            return int(a)
        except Exception:
            # The integer convertion has failed because `a` contains others than digits [0-9].
            # Next try float, because the normal form (eg: 1E3 = 1000) can be converted to hex also.
            # But if we need hex we will write 0x1E3 (= 483) starting with 0x
            try:
                return float(a)
            except Exception:
                try:
                    return int(a, 16)
                except Exception:
                    return 0

    @staticmethod
    def write_config(filename: str, section: str, values: dict):
        config = configparser.ConfigParser()
        with open(filename+"CR", "r+") as configfile:
            config.write_config(dict)

