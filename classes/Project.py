import argparse
import json
import sys
from classes.Single import Single
from classes.Config import Config
from classes.ConfigConstants import ConfigConstants as C

class Project:
    __PROJECT_SECTION = "Project"
    __CONFIG = 0
    __SECTION = 1
    __SECTION_ONLY = 0

    def __init__(self, **kwargs):

        self.project_config = ""
        if C.config_file in kwargs:
            self.project_config = kwargs[C.config_file]

        self.kwargs = kwargs

        if self.project_config == "":
            print("No project file.\n-p <config_file-file>")
            sys.exit(-1)

        # Test if "Project" section exists in project file
        sections = Config.get_sections(self.project_config)
        if not Config.section_exists(sections, self.__PROJECT_SECTION):
            print(f"Missing section Project in file {project}")

        self.__read_config(self.project_config, self.__PROJECT_SECTION)

    @staticmethod
    def parse_arguments():
        parser = argparse.ArgumentParser(add_help=False)

        parser.add_argument('-p', type=str, help="Project File")
        parser.add_argument('-P', type=str, help="Project section")
        parser.add_argument('-v', action="store_true", help="verbose")

        return parser.parse_args()

    def __read_config(self, filename: str, section: str):
        # load built in default values
        self.__set_defaults()

        config = Config.read_config(filename, section)

        if not config.has_option(self.__PROJECT_SECTION, 'items'):
            print(f"Project configuration {filename} has no items!")
            sys.exit(-1)

        self.items = config.get(self.__PROJECT_SECTION, 'items')

        self.options = {}

        if config.has_option(self.__PROJECT_SECTION, 'name'):
            self.name = config.get(self.__PROJECT_SECTION, 'name')
            self.options["project name"] = self.name

        if config.has_option(self.__PROJECT_SECTION, 'x offset'):
            self.x_offset = float(config.get(section, 'x offset'))
            self.options['x offset'] = self.x_offset

        if config.has_option(self.__PROJECT_SECTION, 'y offset'):
            self.y_offset = float(config.get(section, 'y offset'))
            self.options['y offset'] = self.y_offset

        if config.has_option(self.__PROJECT_SECTION, 'thickness'):
            self.thickness = float(config.get(section, 'thickness'))
            self.options['thickness'] = self.thickness

        if config.has_option(self.__PROJECT_SECTION, 'y text spacing'):
            self.y_text_spacing = float(config.get(section, 'y text spacing'))
            self.options['y text spacing '] = self.y_text_spacing

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

        # iterate over all items in the project file
        for item in items:
            if len(item) == 1:
                # Section is in the Project file
                Single.create(**self.kwargs)
            elif len(item) == 2:
                # config_section is in a separate file
                Single.create(**self.kwargs)
