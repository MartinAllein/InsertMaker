import argparse
import os
import sys

from classes.Single import Single
from classes.Config import Config
from classes.ConfigConstants import ConfigConstantsText as Ct


class C:
    designs = 'designs'
    project = 'Project'


class Project:

    def __init__(self, **kwargs):

        # A keyword argument for the project settings file is mandatory. If it does not
        # exist create an empty entry
        project_config_file = kwargs.setdefault(Ct.config_file, '')

        self.kwargs = kwargs

        # Terminate if project file does not exist.
        if not os.path.isfile(project_config_file):
            print(f'Project file "{project_config_file}" does not exist.')
            sys.exit(-1)

        # Test if 'Project' section exists in project file
        sections = Config.get_sections(project_config_file)

        # [Project] section is madatory for projects. Terminate if it is not existing
        if not Config.section_exists(sections, C.project):
            print(f'Missing section [{C.project}] in file {project_config_file}')
            sys.exit(-1)

        # read the Project configuration from the settings
        self.__read_config(f"{project_config_file}{Ct.config_separator}{C.project}")

    @staticmethod
    def parse_arguments():
        parser = argparse.ArgumentParser(add_help=False)

        parser.add_argument('-p', type=str, help='Project File')
        parser.add_argument('-v', action='store_false', help='verbose')

        return parser.parse_args()

    def __read_config(self, filename_and_section: str):
        # load built in default values
        self.__set_defaults()

        config = Config.read_config(filename_and_section)

        # A project has to have a "designs" entry with the list of designs to create
        if not config.has_option(C.project, C.designs):
            print(f'Project configuration {filename_and_section} has no designs!')
            sys.exit(-1)

        # the designes are read as a string with \n separation between the designs
        self.designs = config.get(C.project, C.designs)

        # Split the line at the \n character and get the list of designs
        self.designs = Config.split_config_lines_to_list(self.designs)

        # The designs refer to sections in configuration files. Complete every entry that
        # it has the format config_file#section. If the file is missing, complete the entry
        # with the project file name
        project_file, _ = Config.get_config_file_and_section(filename_and_section)
        self.designs = Config.normalize_config_files_and_sections(self.designs, project_file)

        if config.has_option(C.project, Ct.project_name):
            self.options[Ct.project_name] = config.get(C.project, Ct.project_name)

        if config.has_option(C.project, Ct.x_offset):
            self.options[Ct.x_offset] = config.get(C.project, Ct.x_offset)

        if config.has_option(C.project, Ct.y_offset):
            self.options[Ct.y_offset] = config.get(C.project, Ct.y_offset)

        if config.has_option(C.project, Ct.thickness):
            self.options[Ct.thickness] = config.get(C.project, Ct.thickness)

        if config.has_option(C.project, Ct.y_text_spacing):
            self.options[Ct.y_text_spacing] = config.get(C.project, Ct.y_text_spacing)

        if config.has_option(C.project, Ct.resolution):
            self.options[Ct.thickness] = config.get(C.project, Ct.resolution)

    def __set_defaults(self):
        """ Set default values for all variables from built in values"""
        self.designs = []
        self.options = {}

    def create(self):
        """ Create the designs of the project

        :return: None
        """
        self.kwargs[Ct.options] = self.options

        # iterate over all designs in the project file
        for design in self.designs:
            config = self.kwargs.copy()
            config[Ct.config_file_and_section] = design
            Single.create(**config)
