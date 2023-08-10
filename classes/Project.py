import argparse
import json
import sys

from classes.Single import Single
from classes.Config import Config
from classes.ConfigConstants import ConfigConstantsText as Ct


class Project:
    __PROJECT_SECTION = 'Project'
    __CONFIG = 0
    __SECTION = 1
    __SECTION_ONLY = 0

    def __init__(self, **kwargs):

        self.project_config_file = ''
        if Ct.config_file in kwargs:
            self.project_config_file = kwargs[Ct.config_file]

        project_config_file = self.project_config_file
        self.kwargs = kwargs

        if project_config_file == '':
            print('No project file.\n-p <config_file-file>')
            sys.exit(-1)

        # Test if 'Project' section exists in project file
        sections = Config.get_sections(project_config_file)
        if not Config.section_exists(sections, self.__PROJECT_SECTION):
            print(f'Missing section Project in file {project_config_file}')

        self.__read_config(f"{project_config_file}{Ct.config_separator}{self.__PROJECT_SECTION}")

    @staticmethod
    def parse_arguments():
        parser = argparse.ArgumentParser(add_help=False)

        parser.add_argument('-p', type=str, help='Project File')
        parser.add_argument('-v', action='store_true', help='verbose')

        return parser.parse_args()

    def __read_config(self, filename_and_section: str):
        # load built in default values
        self.__set_defaults()

        config = Config.read_config(filename_and_section)

        if not config.has_option(self.__PROJECT_SECTION, 'items'):
            print(f'Project configuration {filename_and_section} has no items!')
            sys.exit(-1)

        self.items = config.get(self.__PROJECT_SECTION, 'items')
        self.items = Config.split_config_lines_to_list(self.items)
        self.items = Config.normalize_config_file_and_section(self.items, self.project_config_file)

        self.options = {}

        if config.has_option(self.__PROJECT_SECTION, Ct.project_name):
            self.name = config.get(self.__PROJECT_SECTION, Ct.project_name)
            self.options[Ct.project_name] = self.options.get(Ct.project_name, "")

        if config.has_option(self.__PROJECT_SECTION, Ct.x_offset):
            self.x_offset = float(config.get(self.__PROJECT_SECTION, Ct.x_offset))
            self.options[Ct.x_offset] = self.x_offset

        if config.has_option(self.__PROJECT_SECTION, Ct.y_offset):
            self.y_offset = float(config.get(self.__PROJECT_SECTION, Ct.y_offset))
            self.options[Ct.y_offset] = self.y_offset

        if config.has_option(self.__PROJECT_SECTION, Ct.thickness):
            self.thickness = float(config.get(self.__PROJECT_SECTION, Ct.thickness))
            self.options[Ct.thickness] = self.thickness

        if config.has_option(self.__PROJECT_SECTION, Ct.y_text_spacing):

            self.y_text_spacing = float(config.get(self.__PROJECT_SECTION, Ct.y_text_spacing))
            self.options[Ct.y_text_spacing] = self.y_text_spacing

    def __set_defaults(self):
        """ Set default values for all variables from built in values"""
        self.name = None
        self.thickness = None
        self.x_offset = None
        self.y_offset = None
        self.y_text_spacing = None
        self.items = []
        self.options = None
        self.config_path = None

    def create(self):
        # items = json.loads(self.items)
        self.kwargs[Ct.options] = self.options

        # Split string with \n separated items into an array
        # self.items = Config.split_config_lines_to_list(self.items)

        # add the configuration file to the configuration section
        # self.items = Config.beautify_config_array(self.items, self.project_config_file)

        # iterate over all items in the project file
        for item in self.items:
            config = self.kwargs.copy()
            config[Ct.config_file_and_section] = item
            Single.create(**config)
