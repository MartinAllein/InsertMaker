import sys
import os
import pathlib
from classes.File import File


class Template:
    __TEMPLATE_EXTENSION = "svg"
    __TEMPLATE_PATH = os.path.join(pathlib.Path(os.path.dirname(__file__)).parent, "templates")

    @classmethod
    def load_template(cls, template: str) -> str:
        """Import the template"""

        string = ""
        if not template:
            print("No template name given")
            sys.exit()

        template_file = File.path_and_extension(cls.__TEMPLATE_PATH, template, cls.__TEMPLATE_EXTENSION)

        if not os.path.isfile(template_file):
            print(f"Template file {template_file} does not exist!")
            sys.exit()

        with open(template_file, 'r') as f:
            string = f.read()

        return string

    @classmethod
    def load_and_create(cls, template: str, variables) -> str:
        pass
