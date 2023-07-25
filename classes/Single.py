import importlib
import sys
from classes.Config import Config


class Single:

    @classmethod
    def create(cls, config, section, **kwargs):
        """ Single config file design

        :return:
        """

        # configuration section is mandatory
        if not config or config == "":
            print(f"No section for config file {config}\n-c <config-file> -C <section of config file>")
            sys.exit(-1)

        # read config file and extract the style to dynamically load the class
        style = Config.get_style(config, section)

        # Import the style from the config file and load the same named class
        try:
            module = importlib.import_module("classes." + style)
            class_ = getattr(module, style)
        except ModuleNotFoundError:
            print(f"Unknown style \"{style}\" in config file {config} section {section}")
            sys.exit(-1)
        except Exception as inst:
            print("Unknown Error")
            print(type(inst))  # the exception instance
            print(inst.args)  # arguments stored in .args
            print(inst)
            sys.exit(-1)

            # invoke creation of the item
        design = class_(config, section, **kwargs)

        # execute the content
        design.create()
