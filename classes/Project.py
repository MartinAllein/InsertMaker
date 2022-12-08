import argparse
import json
import sys
from classes.Single import Single
from classes.Config import Config
from classes.Design import Design


class Project:
    __DEFAULT_X_OFFSET = Design.x_offset
    __DEFAULT_Y_OFFSET = Design.y_offset
    __PROJECT_SECTION = "Project"
    __CONFIG = 0
    __SECTION = 1
    __SECTION_ONLY = 0

    def __init__(self, project: str, verbose=False):

        self.verbose = verbose
        self.project = project

        if project is None or project == "":
            print("No project file.\n-p <project-file>")
            sys.exit()

        # Test if "Project" section exists in project file
        sections = Config.get_sections(project)
        if not Config.section_exists(sections, self.__PROJECT_SECTION):
            print(f"Missing section Project in file {project}")

        self.__read_config(project, self.__PROJECT_SECTION)

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

        # set default values for reading the config file
        defaults = {'x offset': self.x_offset,
                    'y offset': self.y_offset,
                    'name': self.name,
                    'items': self.items,
                    }
        config = Config.read_config(filename, section, defaults)

        self.name = config.get(self.__PROJECT_SECTION, 'name')
        self.items = config.get(self.__PROJECT_SECTION, 'items')
        self.x_offset = int(config.get(section, 'x offset'))
        self.y_offset = int(config.get(section, 'y offset'))
        print(self.items)
        print(self.name)
        print(self.x_offset)
        print(self.y_offset)

    def __set_defaults(self):
        """ Set default values for all variables from built in values"""
        self.name = ""
        self.x_offset = self.__DEFAULT_X_OFFSET
        self.y_offset = self.__DEFAULT_Y_OFFSET
        self.items = []

    def create(self):
        items = json.loads(self.items)

        # iterate over all items in the project file
        for item in items:
            if len(item) == 1:
                # Section is in the Project file
                Single.create(self.project, item[self.__SECTION_ONLY], self.verbose)
            elif len(item) == 2:
                # section is in a separate file
                Single.create(item[self.__CONFIG], item[self.__SECTION], self.verbose)
