import sys
import json
from json import JSONDecodeError
from xml.etree import ElementTree
from xml.dom import minidom
from datetime import datetime
from abc import ABC, abstractmethod
from classes.Config import Config
from classes.Direction import Direction, Rotation
from classes.PathStyle import PathStyle
from classes.Template import Template
from classes.File import File
from classes.ConfigConstants import ConfigConstants as C

FILENAME = '$FILENAME$'
TEMPLATE = 'TEMPLATE NAME'

""" Order of Configuration is
    Default configuration in insertmaker.config
    Project configuration
    Item configuration
    """


class Design(ABC):
    __initialized = False

    # number of decimal places for tdpi values
    __PRECISION = 4

    # resolution of the SVG drawing. Standard for the Cricut is 72dpi
    __RESOLUTION = 72

    # XML element definitions
    __DEFAULT_XML_LINE = '<line x1="%s" y1="%s"  x2="%s" y2="%s" />\n'
    __DEFAULT_XML_PATH = '<path d="M %s %s A %s %s 0 0 %s %s %s"/>\n'
    __DEFAULT_XML_PATH_NOMOVE = '<path d="A %s %s 0 0 %s %s %s"/>\n'

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
    # x offset       : left offset of the whole SVG drawing
    # y offset       : top offset of the whole SVG drawing
    # y text spacing : vertical spacing of the describing text lines at the bottom of the drawing
    # thickness      : thickness of the uses material
    # stroke width   : stroke width of the lines in the SVG drawing
    __settings_standard_measures = ["x offset", "y offset", "y text spacing", "thickness", "stroke width"]

    # unit             : used unit in the settings (mm or mil)
    # stroke color     : color of the lines drawn in the SVG image
    # stroke dasharray : pattern of the lines drawn in the SVG image
    # resolution       : resolution of the SVG drawing
    __settings_standard_texts = ["unit", "stroke color", "stroke dasharray", "resolution"]

    # The nonstandard keys are design dependend and cannot be in the global settings InsertMaker.config
    # title         : title of the drawing
    # filename      : filename of the utput file
    # project name  : project (i.e. boardgame) to which the design belongs
    # template name : SVG template to use for the design
    __settings_nonstandards = ["title", "filename", "project name", "template name"]

    # all measure keys
    __settings_measures = __settings_standard_measures

    # all text keys. Standard and nonstandard
    __settings_texts = __settings_standard_texts + __settings_nonstandards

    # boolean configuration keys
    __settings_boolean = []

    # enumerations in config
    __settings_enum = {}

    # conversion values for mm<->tdpi and mil <-> tdpi
    __conversion_factor = {"mm": (__RESOLUTION * 10000) / 25.4,
                           "mil": (__RESOLUTION * 10000)
                           }

    __default_configuration = {}

    measures = {}

    def __init__(self, args):
        if C.config_file in args:
            self.config_file = args[C.config_file]

        if C.config_section in args:
            self.config_section = args[C.config_section]

        options = {}
        if 'options' in args:
            options = args["options"]

        # default settings
        self.settings = {'x offset': self.__DEFAULT_X_OFFSET,
                         'y offset': self.__DEFAULT_Y_OFFSET,
                         'y text spacing': self.__DEFAULT_Y_TEXT_SPACING,
                         'thickness': self.__DEFAULT_THICKNESS,
                         'title': f"{__class__.__name__}-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                         'filename': "",
                         'project name': "",
                         'template name': "",
                         'unit': self.__DEFAULT_UNIT,
                         'resolution': self.__RESOLUTION,
                         'stroke color': self.__DEFAULT_STROKE_COLOR,
                         'stroke width': self.__DEFAULT_STROKE_WIDTH,
                         'stroke dasharray': self.__DEFAULT_STROKE_DASHARRAY,
                         }

        # Overwrite the default config with the settings from the Insertmaker.config
        self.__read_config(self.__DEFAULT_CONFIG_FILE, self.__DEFAULT_SECTION_NAME)

        # Overwrite the combined default/InsertMaker settings with the ones from the command line
        self.__update_settings_with_options(options)

        self.verbose: bool = False
        self.noprint: bool = False

        if "verbose" in args and args["verbose"] is True:
            self.verbose = True

        if "noprint" in args and args["noprint"] is True:
            self.noprint = True

        # corner points for the designs
        self.corners: list[float] = []

        # lines for cutting/drawing
        self.cutlines: list[float] = []

        # x and y positions for the boundaries
        self.left_x: float = 0
        self.right_x: float = 0
        self.top_y: float = 0
        self.bottom_y: float = 0

        # command line as string
        self.args_string: str = ' '.join(sys.argv[1:])

    @abstractmethod
    def create(self) -> None:
        """ Create the design. Has to be overridden by the Designs
        """
        pass

    def __update_settings_with_options(self, options: dict) -> None:
        """ Updates the settings with the items from the options
        :param options: Options from the command line
        :return:
        """
        self.settings = self.settings | options
        return

    def convert_measures_to_tdpi(self, settings=None) -> dict:
        """
            Convert the measures from their nativ unint (mm/mil) to dpi * 10000 (tdpi)
        :return: nothing
        """
        if settings is None:
            settings = self.settings

        # remove all keys ending with '_tdpi'.
        # https://stackoverflow.com/questions/11358411/silently-removing-key-from-a-python-dict
        for k in self.__settings_measures:
            # with pop missing keys will not raise an exception
            settings.pop(k + '_tdpi', None)

        # convert all keys to tdpi and add '_tdpi' to the key from the list of measures to be converted
        settings.update(
            {k + "_tdpi": self.to_tdpi(self.settings[k]) for k in self.__settings_measures})

        return settings

    def conversion_factor(self) -> float:
        """
        Delivers the factor for a unit to tdpi conversion
        :return: conversion factor
        """
        return Design.__conversion_factor[self.settings['unit']]

    def to_tdpi(self, value: float) -> int:
        """ Converts a native unit (mm/mil) to tdpi

        :param value: value to be converted
        :return: converted value
        """
        return int(float(value) * self.conversion_factor())

    @staticmethod
    def __tdpi_to_dpi(value: str) -> str:
        """
        Converts tdpi to dpi
        :param value: convert to dpi with 4 decimals
        :return: dpi representation of value
        """
        value = str(value)

        # if the length of the string, add leading 0 for the division
        if len(value) < Design.__PRECISION + 1:
            value = ("00000" + value)[-Design.__PRECISION - 1:]

        # add decimal point
        return value[:-Design.__PRECISION] + "." + value[-Design.__PRECISION:]

    @staticmethod
    def thoudpi_to_dpi(value) -> str:
        """
        Convert tdpi to dpi
        :param value: item or list to convert to dpi
        :return: list of converted values
        """
        if type(value) is list:
            result = [Design.__tdpi_to_dpi(item) for item in value]
        else:
            result = Design.__tdpi_to_dpi(value)
        return result

    @staticmethod
    def draw_line(corners: list, points: list, move_to=True) -> str:
        # TODO:
        """
        Draws a line from the start to the end coordinates
        :return: path string with
        """
        path = ""

        start = 1
        if move_to:
            path = f"M {Design.thoudpi_to_dpi(corners[points[0]][0])} {Design.thoudpi_to_dpi(corners[points[0]][1])} "
        else:
            start = 0

        if start > len(points):
            return ""

        for point in points[start:]:
            x = Design.thoudpi_to_dpi(corners[point][0])
            y = Design.thoudpi_to_dpi(corners[point][1])
            path += f"L {x} {y} "

        return path

    @staticmethod
    def draw_halfcircle(corners: list, points: list, move_to=True) -> str:
        """
        Draws a half circle SVG path
        :param corners: all points of the drawing
        :param path: start and end points, directon of arc
        :param move_to
        :return: XML string with <path />
        """
        path = ""
        start_x, start_y, end_x, end_y, diameter, rotation = Design.get_coords_for_arc(corners, points)
        radius = int(diameter / 2)

        if diameter == 0:
            return ""

        if move_to:
            path += f"M {Design.thoudpi_to_dpi(start_x)} {Design.thoudpi_to_dpi(start_y)} "

        path += f"A {Design.thoudpi_to_dpi(radius)} {Design.thoudpi_to_dpi(radius)} 0 0 {rotation} " \
                f"{Design.thoudpi_to_dpi(end_x)} {Design.thoudpi_to_dpi(end_y)} "

        return path

    @staticmethod
    def draw_quartercircle(corners: list, points: list, move_to=True):
        """
        Draws a quarter circle SVG path
        :param corners: all points of the drawing
        :param move_to:
        :param points:
        :return: XML string with <path />
        """
        path = ""
        start_x, start_y, end_x, end_y, radius, rotation = Design.get_coords_for_arc(corners, points)
        # print(start_x , start_y, end_x, end_y)

        if radius == 0:
            return ""

        if move_to:
            path += f"M {Design.thoudpi_to_dpi(start_x)} {Design.thoudpi_to_dpi(start_y)} "

        path += f"A {Design.thoudpi_to_dpi(radius)} {Design.thoudpi_to_dpi(radius)} 0 0 {rotation} " \
                f"{Design.thoudpi_to_dpi(end_x)} {Design.thoudpi_to_dpi(end_y)} "

        return path

    @staticmethod
    def get_coords_for_arc(corners: list, path: list):
        """
        Extracts start and end coordinates and radius for drawing an arc or arc segment
        :param corners: all corners of drawings
        :param path: start and end points, direction of arc
        :return:
        """
        start_x, start_y = corners[path[0]]
        end_x, end_y = corners[path[1]]

        rotation = path[2]

        radius = abs(end_y - start_y)
        if start_y == end_y:
            radius = abs(end_x - start_x)

        return start_x, start_y, end_x, end_y, radius, rotation.value

    @staticmethod
    def draw_thumbhole_path(corners, path):
        """
        Creates an --\\----/--- for thumb retrieve
        :param corners: Corners of design
        :param path: path for the thumb hole
        :return:
        """
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
    def __draw_arc(start_x, start_y, radius, direction, end_x, end_y, move_to=True):
        return Design.__DEFAULT_XML_PATH % (
            Design.thoudpi_to_dpi(start_x), Design.thoudpi_to_dpi(start_y), Design.thoudpi_to_dpi(radius),
            Design.thoudpi_to_dpi(radius), direction, Design.thoudpi_to_dpi(end_x), Design.thoudpi_to_dpi(end_y))

    @staticmethod
    def __draw_arc_nomove(radius, direction, end_x, end_y, plainpath=False):
        output = ""
        if plainpath:
            output = f"A {Design.thoudpi_to_dpi(radius)} {Design.thoudpi_to_dpi(radius)} 0 0 {direction} " \
                     f"{Design.thoudpi_to_dpi(end_x)}{Design.thoudpi_to_dpi(end_y)} "
        else:
            output = Design.__DEFAULT_XML_PATH_NOMOVE % (
                Design.thoudpi_to_dpi(radius), Design.thoudpi_to_dpi(radius), direction, Design.thoudpi_to_dpi(end_x),
                Design.thoudpi_to_dpi(end_y))
        return output

    @staticmethod
    def draw_lines(corners: list, lines: list, raw=False) -> str:
        xml_lines = ""
        for command, values in lines:
            if command == PathStyle.LINE:
                xml_lines += Design.draw_line(corners, values)
            elif command == PathStyle.LINE_NOMOVE:
                xml_lines += Design.draw_line(corners, values, move_to=False)
            elif command == PathStyle.QUARTERCIRCLE:
                xml_lines += Design.draw_quartercircle(corners, values)
            elif command == PathStyle.QUARTERCIRCLE_NOMOVE:
                xml_lines += Design.draw_quartercircle(corners, values, move_to=False)
            elif command == PathStyle.HALFCIRCLE:
                xml_lines += Design.draw_halfcircle(corners, values)
            elif command == PathStyle.HALFCIRCLE_NOMOVE:
                xml_lines += Design.draw_halfcircle(corners, values, move_to=False)

            elif command == PathStyle.THUMBHOLE:
                xml_lines += Design.draw_thumbhole_path(corners, values)
            elif command == PathStyle.PAIR:
                for start, end in zip(values[::2], values[1::2]):
                    xml_lines += Design.draw_line(corners[start], corners[end])
            elif command == PathStyle.QUARTERCIRCLE:
                xml_lines += Design.draw_quartercircle(corners, values)

        retval = xml_lines.strip()

        if not raw:
            retval = f'<path d="{xml_lines.strip()}"/>'

        return retval

    def set_bounds(self, corners):
        """
        Extracts the top left and bottom right corner of all corner points
        :param corners: all corners of the design
        :return: min x, max x, min y, max y
        """
        self.left_x = min(a for (a, b) in corners)
        self.top_y = min(b for (a, b) in corners)
        self.right_x = max(a for (a, b) in corners)
        self.bottom_y = max(b for (a, b) in corners)

        return self.left_x, self.right_x, self.top_y, self.bottom_y

    def write_to_file(self, template_values: dict, settings={}):
        """
        Fills the template with the values from the dict and writes it to a file
        :param template_values:
        :return:
        """

        if not settings:
            settings = self.settings.copy()

        if settings[C.filename] == "":
            raise "No filename given"

        if settings["template name"]:
            template_values['TEMPLATE NAME'] = settings["template name"]

        if TEMPLATE not in template_values:
            raise " No template given"

        # if 'VIEWBOX_X' not in template_values:
        #     raise "VIEWBOX X is missing"

        # if 'VIEWBOX_Y' not in template_values:
        #     raise "VIEWBOX Y is missing"

        template_string = Template.load_template(template_values[TEMPLATE])

        template_values["$UNIT$"] = settings.get("unit", "unknown")

        # modify FILENAME with leading and trailing $
        template_values["$FOOTER_PROJECT_NAME$"] = settings.get("project name", "")
        template_values["$FOOTER_TITLE$"] = settings.get("title", "")
        template_values["$HEADER_TITLE$"] = settings.get("title", "")

        template_values["$FOOTER_FILENAME$"] = settings.get("filename", "NO FILENAME")
        template_values["$FOOTER_ARGS_STRING$"] = self.args_string
        template_values['$FOOTER_OVERALL_WIDTH$'] = round(
            template_values.get('VIEWBOX_X', 0) / self.conversion_factor(), 2)
        template_values['$FOOTER_OVERALL_HEIGHT$'] = round(
            template_values.get('VIEWBOX_Y', 0) / self.conversion_factor(), 2)

        template_values["$LABEL_X$"] = self.thoudpi_to_dpi(self.left_x)

        ycoord = template_values['VIEWBOX_Y']
        template_values["$LABEL_PROJECT_Y$"] = self.thoudpi_to_dpi(ycoord + settings["y text spacing_tdpi"])
        template_values["$LABEL_Y_SPACING$"] = self.thoudpi_to_dpi(settings["y text spacing_tdpi"])

        all_footers = [i for i in template_values if i.startswith('$FOOTER_')]
        template_values['$VIEWBOX$'] = f"{self.thoudpi_to_dpi(template_values.get('VIEWBOX_X', 0))} " \
                                       f" {self.thoudpi_to_dpi(template_values.get('VIEWBOX_Y', 0) + (len(all_footers) + 2) * self.settings['y text spacing_tdpi'])} "

        for key in template_values:
            template_string = template_string.replace(key, str(template_values[key]))

        template_string = self.remove_xml_labels(template_string)
        template_string = self.remove_xml_labels(template_string)

        with open(f"{settings['filename']}", 'w') as f:
            f.write(template_string)

    def remove_xml_labels(self, template_string):
        if self.noprint is False:
            return template_string

        root = ElementTree.fromstring(template_string)
        for elem in root.iter():
            if 'id' in elem.attrib and elem.attrib["id"] == "document-labels":
                root.remove(elem)

        ElementTree.register_namespace("", "http://www.w3.org/2000/svg")
        newdom = minidom.parseString(ElementTree.tostring(root))
        xmlstr = '\n'.join([line for line in newdom.toprettyxml(indent=' ' * 2).split('\n') if line.strip()])

        return xmlstr

    def tpi_to_unit(self, value: float) -> float:
        """
        Convert values from tdpi to the unit from the settings

        :param value: tdpi to convert
        :return: unit
        """

        return round(value / self.__conversion_factor[self.settings["unit"]], 2)

    def to_dpi(self, value: float) -> float:
        """
        convert measure from settings unit to DPI
        :param value: value to convert
        :return: DPI value
        """
        return int(value * self.__conversion_factor[self.settings["unit"]]) / 10000

    @staticmethod
    def validate_config_and_section(classname, config: str, section: str) -> None:
        """
        Verifies if a configuration file and section is set.
        :param classname: class to verify. Only needed for output
        :param config: config file name
        :param section: section name
        :return:
        """
        if config is None or config == "":
            print(f"No configuration file for Design {classname}")
            sys.exit(-1)

        if section is None or section == "":
            print(f"No section for configuration file {config}")
            sys.exit(-1)

    @staticmethod
    def get_options(value: dict) -> dict:
        options = {}
        if 'options' in value:
            options = value['options']

        return options

    def add_settings_boolean(self, keys: list) -> None:
        """
        Add list of config keys that represent a boolean value

        :param keys: keys to add to boolean config list
        :return:
        """
        self.__settings_boolean = self.__settings_boolean + keys

    def add_settings_enum(self, keys: dict) -> None:
        """
        Add list of config keys that represent an enum value

        :param keys: keys to add to enum config list
        :return:
        """
        self.__settings_enum.update(keys)

    def convert_to_json(self, keys):
        for key in keys:
            self.settings[key] = self.get_string_or_list(self.settings[key])

    def add_settings_measures(self, keys: list) -> None:
        """
        Add list of config measure keys to standard measure keys for converting unit -> tdpi
        :param keys: list of keys
        :return:
        """
        self.__settings_measures = self.__settings_measures + keys

    def add_config_texts(self, texts: list) -> None:
        """
        Add list of text config text keys. These are nonstandard keys
        :param texts:
        :return:
        """
        self.__settings_texts += texts

    def set_title_and_outfile(self, name: str) -> None:
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
        if not self.settings["filename"]:
            self.settings["filename"] = name

        if self.settings["filename"]:
            self.settings['filename'] = File.set_svg_extension(self.settings["filename"])

    def load_settings(self, config_file: str, section: str, settings=None) -> None:
        """
        Reads in a section from a configuration file.
        :param config_file: filename with path of the config file
        :param section: section from the config file to read
        :param verbose: be verbose of the import
        :param payload: default and optional values
        :return: config object
        """
        if settings is None:
            settings = self.settings
        self.validate_config_and_section(__class__.__name__, config_file, section)

        settings =self.__read_config(config_file, section, settings)

        self.set_title_and_outfile(f"{self.__class__.__name__}-{datetime.now().strftime('%Y%m%d-%H%M%S')}")

        return settings

    def __read_config(self, filename: str, section: str, settings=None):
        """ Read configuration from file and convert numbers from string to int/float

        """
        if settings is None:
            settings = self.settings

        error = ""
        config = Config.read_config(filename, section)

        # copy values of all key in the config to the settings. Convert numbers from string to int/float
        settings.update({k: self.try_float(config.get(section, k)) for k in config.options(section) if
                         config.has_option(section, k) and section not in self.__settings_enum})

        foo = self.__settings_enum
        # iterate through all enums of the settings
        for key in self.__settings_enum:
            # enum_item is a dict with settings name as the key and the enm as value
            # test if the config file has the key
            if config.has_option(section, key):
                # retrieve the data from the config
                value = config.get(section, key)
                try:
                    # convert the config data into an enum by string
                    settings[key] = self.__settings_enum[key](value)
                except ValueError as e:
                    error += f"Unknown value for {key} in {filename} section {section}. Current value \"{value}\". " \
                             f"Allowed values are {[e.value for e in self.__settings_enum[key]]}"

        # iterate through all boolean settings
        for key in self.__settings_boolean:
            if config.has_option(section, key):
                settings[key] = False
                value = config.get(section, key)
                if value.lower() in ["y", "yes", "1", "t", "true"]:
                    settings[key] = True

        if len(error) != 0:
            print(error)
            sys.exit(1)

        # print(json.dumps(self.settings, indent=4))

        return settings

    @staticmethod
    def is_float(value) -> bool:
        try:
            float(value)
            return True
        except ValueError:
            return False

    @staticmethod
    def try_float(value: str):

        try:
            if value.__contains__("."):
                float(value)
                return float(value)
            else:
                int(value)
                return int(value)
        except ValueError:
            return value

    def get_project_name_for_title(self, prefix="", postfix="-") -> str:
        return f"{'' if len(self.settings['project name']) == 0 else prefix + self.settings['project name'] + postfix}"

    def get_viewbox(self, x: int, y: int) -> (int, int):
        return round(self.settings["x offset_tdpi"] + x), round(self.settings["y offset_tdpi"] + y)

    @staticmethod
    def get_string_or_list(value) -> str:
        try:
            retval = json.loads(value)
        except JSONDecodeError as e:
            retval = value

        return retval

    @staticmethod
    def split_config_lines_to_list(config_array: str, item_count: int) -> list:
        retval = []

        if len(config_array) == 0:
            return retval

        items = list(filter(None, (x.strip() for x in config_array.splitlines())))

        for item in items:
            item = item.replace('"', '')
            if len(item.split(",")) == item_count:
                retval.append(item.split(","))

        return retval

    def get_config_file_and_section(self, default_filename: str, file_and_section: str) -> (str, str):
        filename = default_filename
        section = ""
        split = file_and_section.rsplit("/", 1)
        if len(split) == 2:
            filename = split[0]
            section = split[1]
        else:
            section = split[0]
        return filename, section

# found things to consider in later designs
#     self.measures.update({k: args['options'][k] for k in keys if k in args['options']})

# https://stackoverflow.com/questions/23662280/how-to-log-the-contents-of-a-configparser
# print({section: dict(config[section]) for section in config.sections()})

# How to pretty print nested dictionaries?
# https://stackoverflow.com/questions/3229419/how-to-pretty-print-nested-dictionaries
