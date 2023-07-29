import importlib
import sys
from classes.Config import Config
from classes.ConfigConstants import ConfigConstants as C


class Single:

    @classmethod
    def create(cls, **kwargs):
        """ Single config file design

        :return:
        """
        config_file = kwargs[C.config_file]
        config_section = kwargs[C.config_section]

        # configuration section is mandatory
        if not config_file or config_file == "":
            print(f"No section for config file {config_file}\n-c <config_file-file> -C <section of config_file file>")
            sys.exit(-1)

        # read config file and extract the style to dynamically load the class
        style = Config.get_style(config_file, config_section)

        # Import the style from the config file and load the same named class
        try:
            module = importlib.import_module("classes." + style)
            class_ = getattr(module, style)
        except ModuleNotFoundError:
            print(f"Unknown style \"{style}\" in config file {config_file} section {config_section}")
            sys.exit(-1)
        except Exception as inst:
            print("Unknown Error")
            print(type(inst))  # the exception instance
            print(inst.args)  # arguments stored in .args
            print(inst)
            sys.exit(-1)

            # invoke creation of the item
        # design = class_(config, section, **kwargs)
        design = class_(**kwargs)

        # execute the content
        design.create()
