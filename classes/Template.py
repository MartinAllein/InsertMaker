import os
from classes.File import File


class Template:

    __TEMPLATE_EXTENSION = "svg"
    __TEMPLATE_PATH = "templates"

    @classmethod
    def load_template(cls, template: str) -> str:
        """Import the template"""

        string = ""
        if not template:
            raise "No template name given"

        template_file = File.path_and_extension(cls.__TEMPLATE_PATH, template, cls.__TEMPLATE_EXTENSION)

        if not os.path.isfile(template_file):
            raise "Template file " + template_file + " does not exist"

        with open(template_file, 'r') as f:
            string = f.read()

        return string
