import importlib
import sys
from classes.Config import Config
from classes.ConfigConstants import ConfigConstantsText as Ct


class Single:

    @classmethod
    def create(cls, **kwargs):
        """ Single config file design

        :return:
        """
        config_file_and_section = kwargs.setdefault(Ct.config_file_and_section, '')

        # read config file and extract the design to dynamically load the class
        design = Config.get_design(config_file_and_section)

        # Import the design from the config file and load the same named class
        try:
            module = importlib.import_module(f'classes.{design}')
            class_ = getattr(module, design)
        except ModuleNotFoundError:
            print(f'Unknown design "{design}" in config file {config_file_and_section}.')
            sys.exit(-1)
        except Exception as inst:
            print('Unknown Error')
            print(type(inst))  # the exception instance
            print(inst.args)  # arguments stored in .args
            print(inst)
            sys.exit(-1)

            # invoke creation of the item
        design = class_(**kwargs)

        # execute the content
        design.create()
