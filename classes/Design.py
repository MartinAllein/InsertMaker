import re
import sys
import os
import xml.dom.minidom
from datetime import datetime
from abc import ABC, abstractmethod
from classes.Config import Config
from classes.Direction import Direction
from classes.PathStyle import PathStyle
from classes.Template import Template
from classes.File import File
import json

FILENAME = '$FILENAME$'
TEMPLATE = 'TEMPLATE'

""" Order of Configuration is
    Default configuration in insertmaker.config
    Project configuration
    Item configuration

    """


class Design(ABC):
    __initialized = False

    # XML element definitions
    __DEFAULT_XML_LINE = '<line x1="%s" y1="%s"  x2="%s" y2="%s" />\n'
    __DEFAULT_XML_PATH = '<path d="M %s %s A %s %s 0 0 %s %s %s"/>\n'

    # Default filename and section for the InsertMaker configuration file
    __DEFAULT_SECTION_NAME = "STANDARD"
    __DEFAULT_CONFIG_FILE = "InsertMaker.config"

    # Fallback settings when InsertMaker.config is missing
    __DEFAULT_X_OFFSET = 1.0
    __DEFAULT_Y_OFFSET = 2.0
    __DEFAULT_Y_TEXT_SPACING = 7
    __DEFAULT_THICKNESS = 1.5
    __DEFAULT_STROKE_COLOR = "#aaaaaa"
    __DEFAULT_STROKE_DASHARRAY = "20, 20"
    __DEFAULT_STROKE_WIDTH = 2

    # Default path  and extension definitions
    __CONFIG_EXTENSION = "config"
    __TEMPLATE_PATH = "templates"

    # unit definitions
    __UNIT_MM_TEXT = 'mm'
    __UNIT_MIL_TEXT = 'mil'
    __DEFAULT_UNIT = __UNIT_MM_TEXT

    xml_line = __DEFAULT_XML_LINE
    xml_path = __DEFAULT_XML_PATH
    # unit_mm = True

    # Default measure keys, text keys
    __config_standard_measures = ["x offset", "y offset", "y text spacing", "thickness", "stroke width"]
    __config_standard_texts = ["unit", "stroke color", "stroke dasharray"]

    # The nonstandard keys are design dependend and cannot be in the global settings InsertMaker.config
    __config_nonstandards = ["title", "outfile", "project name", "name", "template name"]

    # all measure keys
    __settings_measures = __config_standard_measures

    # all text keys. Standard and nonstandard
    __config_texts = __config_standard_texts + __config_nonstandards

    # FACTOR = 720000 / 25.4

    # conversion values for mm<->tdpi and mil <-> tdpi
    __factor = {"mm": 720000 / 25.4,
                "mil": 720000
                }

    __default_configuration = {}

    measures = {}

    def __init__(self, args):
        options = {}
        if 'options' in args:
            options = args["options"]

        self.settings = {'x offset': self.__DEFAULT_X_OFFSET,
                         'y offset': self.__DEFAULT_Y_OFFSET,
                         'y text spacing': self.__DEFAULT_Y_TEXT_SPACING,
                         'thickness': self.__DEFAULT_THICKNESS,
                         'title': "",
                         'outfile': "",
                         'project name': "",
                         'name': "",
                         'template name': "",
                         'unit': self.__DEFAULT_UNIT,
                         'stroke color': self.__DEFAULT_STROKE_COLOR,
                         'stroke width': self.__DEFAULT_STROKE_WIDTH,
                         'stroke dasharray': self.__DEFAULT_STROKE_DASHARRAY,
                         }

        self.__read_config(self.__DEFAULT_CONFIG_FILE, self.__DEFAULT_SECTION_NAME)

        # Overwrite the default settings with the ones from the command line

        self.__update_settings_with_options(options)

        self.verbose: bool = False
        self.default_name: str = ""

        # corner points for the designs
        self.corners: list[float] = []

        # lines for cutting/drawing
        self.cutlines: list[float] = []

        # x and y positions for the boundaries
        self.left_x: float = 0
        self.right_x: float = 0
        self.top_y: float = 0
        self.bottom_y: float = 0

        # content for the template
        self.template = {}

        # command line as string
        self.args_string: str = ' '.join(sys.argv[1:])

        print(self.settings)

    @abstractmethod
    def create(self):
        """ Create the design
        """
        pass

    def __update_settings_with_options(self, options: dict):
        """ Updates the settings with the items from the options
        :param options: Options from the command line
        :return:
        """
        self.settings = self.settings | options
        return

    def convert_measures_to_tdpi(self):
        """ Shift comma of dpi four digits to the right to get acceptable accuracy and only integer numbers"""

        # remove all keys ending with '_tdpi'
        # https://stackoverflow.com/questions/11358411/silently-removing-key-from-a-python-dict
        for k in self.__settings_measures:
            self.settings.pop(k + '_tdpi', None)

        # convert all keys to tdpi and add '_tdpi' to the key
        self.settings.update(
            {k + "_tdpi": self.to_tdpi(self.settings[k]) for k in self.__settings_measures})

        return

    def to_tdpi(self, value: float) -> int:
        """ Convert mm/mil to thousand DPI depending in the selected unit

        :param value:
        :return:
        """
        return int(float(value) * Design.__factor[self.settings['unit']])

    @staticmethod
    def __divide_dpi(coord: str) -> str:
        if coord == 0:
            value = "00000"
        else:
            value = str(coord)

        return value[:-4] + "." + value[-4:]

    @staticmethod
    def thoudpi_to_dpi(coord) -> str:

        if type(coord) is list:
            result = []
            for item in coord:
                result.append(Design.__divide_dpi(item))
        else:
            result = Design.__divide_dpi(coord)
        return result

    @staticmethod
    def draw_line(start, end):
        start_x, start_y = Design.thoudpi_to_dpi(start)
        end_x, end_y = Design.thoudpi_to_dpi(end)
        return Design.__DEFAULT_XML_LINE % (start_x, start_y, end_x, end_y)

    @staticmethod
    def draw_halfcircle(corners, path):
        """Draws a half circle SVG path"""
        start_x, start_y = corners[path[0]]
        end_x, end_y = corners[path[1]]
        orientation = path[2]

        diameter = 0
        if orientation == Direction.VERTICAL:
            diameter = abs(end_y - start_y)
        else:
            diameter = abs(end_x - start_x)

        if diameter == 0:
            return ""

        return Design.__draw_arc(start_x, start_y, int(diameter / 2), Direction.CW, end_x, end_y)

    @staticmethod
    def draw_quartercircle(corners, path):
        """Draws a quarter circle SVG path"""
        start_x, start_y = corners[path[0]]
        end_x, end_y = corners[path[1]]
        orientation = path[2]

        diameter = 0
        if orientation == Direction.VERTICAL:
            radius = abs(end_y - start_y)
        else:
            radius = abs(end_x - start_x)

        if radius == 0:
            return ""

        return Design.__draw_arc(start_x, start_y, int(radius), 1, end_x, end_y)

    @staticmethod
    def draw_thumbhole_path(corners, path):
        start_x, start_y = corners[path[0]]
        smallradius, thumbholeradius, direction, orientation = path[1:]

        delta = {
            Direction.NORTH: [[-smallradius, -smallradius, direction], [0, -2 * thumbholeradius, 1 - direction],
                              [smallradius, -smallradius, direction]],
            Direction.SOUTH: [[smallradius, smallradius, direction], [0, 2 * thumbholeradius, 1 - direction],
                              [-smallradius, smallradius, direction]],
            Direction.WEST: [[-smallradius, -smallradius, 1 - direction], [-2 * thumbholeradius, 0, direction],
                             [-smallradius, +smallradius, 1 - direction]],
            Direction.EAST: [[smallradius, smallradius, 1 - direction], [2 * thumbholeradius, 0, direction],
                             [smallradius, -smallradius, 1 - direction]],
        }

        xmlstring = ""
        for values in delta[orientation]:
            end_x = start_x + values[0]
            end_y = start_y + values[1]
            outstring = Design.__draw_arc(start_x, start_y, smallradius, values[2], end_x, end_y)
            xmlstring += outstring
            start_x = end_x
            start_y = end_y

        return xmlstring

    @staticmethod
    def __draw_arc(start_x, start_y, radius, direction, end_x, end_y):
        return Design.__DEFAULT_XML_PATH % (
            Design.thoudpi_to_dpi(start_x), Design.thoudpi_to_dpi(start_y), Design.thoudpi_to_dpi(radius),
            Design.thoudpi_to_dpi(radius), direction, Design.thoudpi_to_dpi(end_x), Design.thoudpi_to_dpi(end_y))

    @staticmethod
    def draw_lines(corners, lines):
        xml_lines = ""
        for command, values in lines:
            if command == PathStyle.LINE:
                for start, end in zip(values[:-1], values[1:]):
                    xml_lines += Design.draw_line(corners[start], corners[end])
            elif command == PathStyle.THUMBHOLE:
                xml_lines += Design.draw_thumbhole_path(corners, values)
            elif command == PathStyle.PAIR:
                for start, end in zip(values[::2], values[1::2]):
                    xml_lines += Design.draw_line(corners[start], corners[end])
            elif command == PathStyle.HALFCIRCLE:
                xml_lines += Design.draw_halfcircle(corners, values)
            elif command == PathStyle.QUARTERCIRCLE:
                xml_lines += Design.draw_quartercircle(corners, values)

        return xml_lines

    def set_bounds(self, corners):

        self.left_x = min(a for (a, b) in corners)
        self.top_y = min(b for (a, b) in corners)
        self.right_x = max(a for (a, b) in corners)
        self.bottom_y = max(b for (a, b) in corners)

        return self.left_x, self.right_x, self.top_y, self.bottom_y

    def write_to_file(self, items: dict):

        if self.settings["outfile"] == "":
            raise "No filename given"

        if self.settings["template_name"]:
            items['TEMPLATE'] = self.settings["template_name"]

        if TEMPLATE not in items:
            raise " No tamplate given"

        if 'VIEWBOX_X' not in items:
            raise "VIEWBOX X is missing"

        if 'VIEWBOX_Y' not in items:
            raise "VIEWBOX Y is missing"

        template = Template.load_template(items[TEMPLATE])

        # modify FILENAME with leading and trailing $
        self.template["$FOOTER_PROJECT_NAME$"] = self.settings["project_name"]
        self.template["$FOOTER_TITLE$"] = self.settings["title"]
        self.template["$HEADER_TITLE$"] = self.settings["title"]

        self.template["$FOOTER_FILENAME$"] = self.settings["outfile"]
        self.template["$FOOTER_ARGS_STRING$"] = self.args_string
        self.template['$FOOTER_OVERALL_WIDTH$'] = self.template['VIEWBOX_X']
        self.template['$FOOTER_OVERALL_HEIGHT'] = self.template['VIEWBOX_Y']

        self.template["$LABEL_X$"] = self.thoudpi_to_dpi(self.left_x)

        ycoord = self.template['VIEWBOX_Y']
        self.template["$LABEL_PROJECT_Y$"] = self.thoudpi_to_dpi(ycoord + self.y_text_spacing)
        self.template["$LABEL_Y_SPACING$"] = self.thoudpi_to_dpi(self.y_text_spacing)

        all_footers = [i for i in self.template if i.startswith('$FOOTER_')]
        self.template['$VIEWBOX$'] = f"{self.thoudpi_to_dpi(self.template['VIEWBOX_X'])} " \
                                     f" {self.thoudpi_to_dpi(self.template['VIEWBOX_Y'] + (len(all_footers) + 2) * self.y_text_spacing)} "

        for key in items:
            template = template.replace(key, str(items[key]))

        dom = xml.dom.minidom.parseString(template)
        template = dom.toprettyxml(newl='')

        with open(f"{self.settings['outfile']}", 'w') as f:
            f.write(template)

    @classmethod
    def read_template(cls, template: str, template_path: str) -> str:
        """Import the template"""
        string = ""
        if not template:
            raise "No template name given"

        template_file = os.path.join(cls.__TEMPLATE_PATH, template)
        if not os.path.isfile(template_file):
            raise f"Template file {template_file} does not exist"

        with open(template_file, 'r') as f:
            string = f.read()

        return string

    def tpi_to_unit(self, value: float) -> float:
        """
        Convert values from tdpi to the unit from the settings

        :param value: tdpi to convert
        :return: unit
        """

        return round(value / self.__factor[self.settings["unit"]], 2)

    def to_dpi(self, value: float) -> float:
        """
        convert measure from settings unit to DPI
        :param value: value to convert
        :return: DPI value
        """
        return int(value * self.__factor[self.settings["unit"]]) / 10000

    @staticmethod
    def validate_config_and_section(classname, config: str, section: str):
        if config is None or config == "":
            print(f"No configuration file for Design {classname}")
            sys.exit(-1)

        if section is None or section == "":
            print(f"No section for configuration file {config}")
            sys.exit(-1)

    @staticmethod
    def get_options(value):
        options = {}
        if 'options' in value:
            options = value['options']

        return options

    def add_settings_measures(self, measures: list):
        """
        Add list of config measure keys to standard measure keys for converting unit -> tdpi
        :param measures: list of keys
        :return:
        """
        self.__settings_measures = self.__settings_measures + measures

    def add_config_texts(self, texts: list):
        """
        Add list of text config text keys. These are nonstandard keys
        :param texts:
        :return:
        """
        self.__config_texts += texts

    def set_title_and_outfile(self, name: str):
        """
        Set the title of the sheet and the filename for the output
        :param name:
        :return:
        """
        if name is None or name == "":
            return

        if not self.settings["title"]:
            # set default title
            self.settings['title'] = name

        # set default filename for output
        self.settings["outfile"] = name

        if self.settings["outfile"]:
            self.settings['outfile'] = File.set_svg_extension(self.settings["outfile"])

    def load_settings(self, config_file: str, section: str, verbose: bool):
        """
        Reads in a section from a configuration file.
        :param config_file: filename with path of the config file
        :param section: section from the config file to read
        :param verbose: be verbose of the import
        :param payload: default and optional values
        :return: config object
        """
        self.validate_config_and_section(__class__.__name__, config_file, section)

        self.set_title_and_outfile(f"{self.__class__.__name__}-{datetime.now().strftime('%Y%m%d-%H%M%S')}")

        self.verbose = verbose
        self.__read_config(config_file, section)

        return

    def __read_config(self, filename: str, section: str):
        """ Read configuration from file and convert numbers from string to int/float

        """

        config = Config.read_config(filename, section)

        # copy values of all key in the config to the settings. Convert numbers from string to int/float
        self.settings.update({k: self.try_float(config.get(section, k)) for k in config.options(section) if
                              config.has_option(section, k)})

        print(json.dumps(self.settings, indent=4))
        return config

    @staticmethod
    def is_float(value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    @staticmethod
    def try_float(value):

        try:
            float(value)
            return float(value)
        except ValueError:
            return value

# found things to consider in later designs
#     self.measures.update({k: args['options'][k] for k in keys if k in args['options']})

# https://stackoverflow.com/questions/23662280/how-to-log-the-contents-of-a-configparser
# print({section: dict(config[section]) for section in config.sections()})

# How to pretty print nested dictionaries?
# https://stackoverflow.com/questions/3229419/how-to-pretty-print-nested-dictionaries
