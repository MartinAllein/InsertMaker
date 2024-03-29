import configparser
import os
import sys
from classes.File import File
from classes.ConfigConstants import ConfigConstantsText as c


class C:
    design = 'design'


class Config:

    @classmethod
    # def read_config(cls, filename: str, section: str, defaults=None):
    def read_config(cls, filename_and_section: str, defaults=None):
        """ Read the given section from a configuration file

        :param filename_and_section: config filename with section
        :param defaults:
        :return:
        """

        if defaults is None:
            defaults = []

        config_file, config_section = Config.get_config_file_and_section(filename_and_section)

        # read entries from the configuration file
        # config = configparser.ConfigParser(defaults=defaults)
        config = configparser.ConfigParser()
        config.read(config_file)

        # Test if requested section exists
        if not config.has_section(config_section):
            print(f'Sections in file {config_file}')
            for part in config.sections():
                print(part)
            print('Section ' + config_section + ' in config file ' + config_file)
            if config_section[0] == '"' or config_section[-1] == '"' or config_section[0] == '"' \
                    or config_section[-1] == '"':
                print('Please remove the quotation marks around the section!')
            sys.exit(-1)

        return config

    @classmethod
    # def get_style(cls, filename: str, section: str):
    def get_design(cls, filename_and_section: str) -> str:
        """ Returns the style from a configuration within a configuration file

        :param filename_and_section: configuration file with section
        :return: style of the item (CardSheet, CardBox, ....)
        """
        config = cls.read_config(filename_and_section, C.design)

        filename, section = Config.get_config_file_and_section(filename_and_section)

        style = config.get(section, C.design)

        if style is None:
            print(f'Config file {filename} with Section {section} has no style entry.')
            sys.exit(-1)

        return config.get(section, C.design)

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
                f'Duplicate Section {e.args[0]} in file {e.args[1]} in line {e.args[2]}'
                f'\nPlease correct this line and run configMaker again.')

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
            print('File ' + file + ' does not exist')
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
        with open(filename + 'CR', 'r+') as configfile:
            config.write_config(dict)

    @staticmethod
    def get_config_file_and_section(file_and_section: str, default_filename=None) -> (str, str):
        """ Split configuration with filename and section into separate parts. Also test if the
        file is existing.

        :param file_and_section: configuration file and section in the format filename#section
        :param default_filename: Filename to precede when only section is given.
        :return:
        """

        # If there is a default filename and the first parameter is missing the # separator
        # then this is only the section of the configuration
        # Combine default filename with section and seperator to full config information
        if default_filename is not None and '#' not in file_and_section:
            file_and_section = f'{default_filename}{c.config_separator}{file_and_section}'

        # If the separation character is missing here then there is no valid config information.
        if c.config_separator not in file_and_section:
            print(f'Missing section for config file "{file_and_section}". I.e. /foo/bar#the_section')
            sys.exit(-1)

        # split config informsation at config separator
        split = file_and_section.rsplit(c.config_separator)

        # Only one separation character is allowed.
        if len(split) != 2:
            print(f'There must be only a single separator "{c.config_separator}" in the {file_and_section}.')
            sys.exit(-1)

        filename = split[0]
        section = split[1]

        # if the config file is missing the extension so append it.
        filename = File.path_and_extension('', filename, c.config_file_extension)

        # Test if configuration file exists
        if not os.path.isfile(filename):
            print(f'Config file  {filename} does not exist. ')
            sys.exit(-1)

        return filename, section

    @staticmethod
    def normalize_config_files_and_sections(configs: list, filename: str) -> list:
        """ Complete the items in the list of configurations that they are all in the
        format of filename#section.

        :param configs: List of configurations
        :param filename: filename to prefix to the section.
        :return: list of configurations in the format filename#section
        """
        retval = []
        for config in configs:
            fn, cf = Config.get_config_file_and_section(config, filename)
            retval.append(f"{fn}{c.config_separator}{cf}")

        return retval

    @staticmethod
    def normalize_config_file_and_section(config: str, filename: str) -> str:
        retval = ''
        fn, cf = Config.get_config_file_and_section(config, filename)
        retval = f'{fn}{c.config_separator}{cf}'

        return retval

    @staticmethod
    def split_config_lines_to_list(config_string: str, items_per_line=0) -> list:
        """ Split a string with CR separated elements into a list of elemets. If an element
        has comma separated items in an element so split these and check if there are the correct number of items.

        :param config_string: String with the \n separated Elemets
        :param items_per_line: Number of items per configuration line. 0 means no checking
        :return: list of configuration elements
        """
        retval = []

        if len(config_string) == 0:
            return retval

        items = list(filter(None, (x.strip() for x in config_string.splitlines())))

        for item in items:
            item = item.replace('"', '').replace("'", '')
            # split only when no count of split characters is given or the count of split
            # characters is exactly the requested one
            if "," in item:
                if len(item.split(",")) == items_per_line or items_per_line == 0:
                    retval.append(item.split(","))
                else:
                    print(f"Wrong number of items in line '{item}' (Expect {items_per_line} items).")
            else:
                retval.append(item)
        return retval
