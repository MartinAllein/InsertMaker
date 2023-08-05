import argparse
import json
import sys

import classes.Project
from classes.Single import Single
from classes.Config import Config
from classes.ConfigConstants import ConfigConstants as Cc


class Project:
    __PROJECT_SECTION = "Project"
    __CONFIG = 0
    __SECTION = 1
    __SECTION_ONLY = 0

    def __init__(self, **kwargs):

        self.project_config_file = ""
        if Cc.config_file in kwargs:
            self.project_config_file = kwargs[Cc.config_file]

        project_config_file = self.project_config_file
        self.kwargs = kwargs

        if project_config_file == "":
            print("No project file.\n-p <config_file-file>")
            sys.exit(-1)

        # Test if "Project" section exists in project file
        sections = Config.get_sections(project_config_file)
        if not Config.section_exists(sections, self.__PROJECT_SECTION):
            print(f"Missing section Project in file {project_config_file}")

        self.__read_config(f"{project_config_file}{Cc.config_separator}{self.__PROJECT_SECTION}")

    @staticmethod
    def parse_arguments():
        parser = argparse.ArgumentParser(add_help=False)

        parser.add_argument('-p', type=str, help="Project File")
        parser.add_argument('-P', type=str, help="Project section")
        parser.add_argument('-v', action="store_true", help="verbose")

        return parser.parse_args()

    def __read_config(self, filename_and_section: str):
        # load built in default values
        self.__set_defaults()

        config = Config.read_config(filename_and_section)

        if not config.has_option(self.__PROJECT_SECTION, 'items'):
            print(f"Project configuration {filename_and_section} has no items!")
            sys.exit(-1)

        self.items = config.get(self.__PROJECT_SECTION, 'items')

        self.options = {}

        if config.has_option(self.__PROJECT_SECTION, Cc.project_name):
            self.name = config.get(self.__PROJECT_SECTION, Cc.project_name)
            self.options[Cc.project_name]  = self.options.get(Cc.project_name, "")

        if config.has_option(self.__PROJECT_SECTION, Cc.x_offset):
            self.x_offset = float(config.get(self.__PROJECT_SECTION, Cc.x_offset))
            self.options[Cc.x_offset] = self.x_offset

        if config.has_option(self.__PROJECT_SECTION, Cc.y_offset):
            self.y_offset = float(config.get(self.__PROJECT_SECTION, Cc.y_offset))
            self.options[Cc.y_offset] = self.y_offset

        if config.has_option(self.__PROJECT_SECTION, Cc.thickness):
            self.thickness = float(config.get(self.__PROJECT_SECTION, Cc.thickness))
            self.options[Cc.thickness] = self.thickness

        if config.has_option(self.__PROJECT_SECTION, Cc.y_text_spacing):
            self.y_text_spacing = float(config.get(self.__PROJECT_SECTION, Cc.y_text_spacing))
            self.options[Cc.y_text_spacing] = self.y_text_spacing

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
        items = json.loads(self.items)
        self.kwargs["options"] = self.options

        items = Config.beautify_config_array(items, self.project_config_file)

        # iterate over all items in the project file
        for item in items:
            if len(item) == 1:
                # Section is in the Project file
                Single.create(**self.kwargs)
            elif len(item) == 2:
                # config_section is in a separate file
                Single.create(**self.kwargs)
