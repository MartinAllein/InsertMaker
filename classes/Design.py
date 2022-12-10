import sys
import os
import xml.dom.minidom
from abc import ABC, abstractmethod
from classes.Config import Config
from classes.Direction import Direction
from classes.PathStyle import PathStyle
from classes.Template import Template

import configparser

FILENAME = 'FILENAME'

TEMPLATE = 'TEMPLATE'


class Design(ABC):
    __initialized = False

    # XML element definitions
    __DEFAULT_XML_LINE = '<line x1="%s" y1="%s"  x2="%s" y2="%s" />\n'
    __DEFAULT_XML_PATH = '<path d="M %s %s A %s %s 0 0 %s %s %s"/>\n'

    __DEFAULT_SECTION_NAME = "STANDARD"

    __DEFAULT_CONFIG_FILE = "config/InsertMaker.config"
    __DEFAULT_X_ORIGIN = 0
    __DEFAULT_Y_ORIGIN = 0

    # Fallback settings when InsertMaker.config is missing
    __DEFAULT_X_OFFSET = 0
    __DEFAULT_Y_OFFSET = 0
    __DEFAULT_Y_LINE_SEPARATION = 7
    __DEFAULT_THICKNESS = 1.5

    # Default path  and extension definitions
    __CONFIG_EXTENSION = "config"
    __TEMPLATE_PATH = "templates"

    # Names for Configuration file elements
    __X_ORIGIN_CONFIG_NAME = "x origin"
    __Y_ORIGIN_CONFIG_NAME = "y origin"
    __X_OFFSET_CONFIG_NAME = "x offset"
    __Y_OFFSET_CONFIG_NAME = "y offset"
    __THICKNESS_CONFIG_NAME = "thickness"
    __Y_LINE_SEPARATION_NAME = "y line separation"
    __UNIT_CONFIG_NAME = "unit"
    __XML_LINE_CONFIG_NAME = "xml line"
    __XML_PATH_CONFIG_NAME = "xml path"

    __UNIT_MM_TEXT = 'mm'
    __UNIT_MIL_TEXT = 'mil'
    __DEFAULT_UNIT = __UNIT_MM_TEXT

    xml_line = __DEFAULT_XML_LINE
    xml_path = __DEFAULT_XML_PATH
    x_origin = __DEFAULT_X_ORIGIN
    y_origin = __DEFAULT_Y_ORIGIN
    x_offset = __DEFAULT_X_OFFSET
    y_offset = __DEFAULT_Y_OFFSET
    thickness = __DEFAULT_THICKNESS
    y_line_separation = __DEFAULT_Y_LINE_SEPARATION
    unit_mm = True

    FACTOR = 720000 / 25.4
    __default_configuration = {}

    @abstractmethod
    def create(self):
        pass

    @abstractmethod
    def parse_arguments(self):
        pass

    @staticmethod
    def __divide_dpi(coord: str):
        if coord == 0:
            value = "00000"
        else:
            value = str(coord)

        return value[:-4] + "." + value[-4:]

    @staticmethod
    def thoudpi_to_dpi(coord):

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

    @staticmethod
    def get_bounds(corners):

        left_x = min(a for (a, b) in corners)
        top_y = min(b for (a, b) in corners)
        right_x = max(a for (a, b) in corners)
        bottom_y = max(b for (a, b) in corners)

        return left_x, right_x, top_y, bottom_y

    @classmethod
    def write_to_file(cls, items):

        if FILENAME not in items:
            raise "No filename given"

        if TEMPLATE not in items:
            raise " No tamplate given"

        template = Template.load_template(items[TEMPLATE])

        # modify FILENAME with leading and trailing $
        items["$FILENAME$"] = items[FILENAME]
        filename = items[FILENAME]
        del items[FILENAME]

        for key in items:
            template = template.replace(key, str(items[key]))

        dom = xml.dom.minidom.parseString(template)
        template = dom.toprettyxml(newl='')

        with open(f"{filename}", 'w') as f:
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

    @staticmethod
    def thoudpi_to_mm(value: float) -> float:
        """ Convert values from tenthousandth of dpi to dpi """
        return round(value / Design.FACTOR, 2)

    @staticmethod
    def mm_to_thoudpi(value: float) -> int:
        return int(float(value) * Design.FACTOR)

    @classmethod
    def read_config(cls, filename: str, section: str = None, defaults: str = None):
        """ Read configuration from file"""

        # if the filename does not have the extension config, then add ist to the filename
        # +1 because of the dot in front of the extension
        if filename[-len(cls.__CONFIG_EXTENSION + 1):] != "." + cls.__CONFIG_EXTENSION:
            filename += cls.__CONFIG_EXTENSION

        # Read default values from the config file
        if not os.path.isfile(filename):
            print("Config file " + filename + " not found")
            sys.exit()

        # read entries from the configuration file
        configuration = configparser.RawConfigParser(defaults=defaults)
        configuration.read(filename)

        if section:
            if not configuration.has_section(section):
                print("Section " + section + " in config file " + filename + " not found")
                sys.exit()

        return configuration

    @classmethod
    def default_config(cls):
        if cls.__initialized:
            return

        defaults = {cls.__X_ORIGIN_CONFIG_NAME: 0,
                    cls.__Y_ORIGIN_CONFIG_NAME: 0,
                    cls.__X_OFFSET_CONFIG_NAME: 0,
                    cls.__Y_OFFSET_CONFIG_NAME: 0,
                    cls.__DEFAULT_THICKNESS: cls.__DEFAULT_THICKNESS,
                    cls.__Y_LINE_SEPARATION_NAME: cls.__DEFAULT_Y_LINE_SEPARATION,
                    cls.__XML_LINE_CONFIG_NAME: cls.__DEFAULT_XML_LINE,
                    cls.__XML_PATH_CONFIG_NAME: cls.__DEFAULT_XML_PATH,
                    cls.__UNIT_CONFIG_NAME: cls.__DEFAULT_UNIT
                    }

        configuration = Config.read_config(cls.__DEFAULT_CONFIG_FILE, cls.__DEFAULT_SECTION_NAME, defaults)

        cls.x_origin = int(configuration.get(cls.__DEFAULT_SECTION_NAME, cls.__X_ORIGIN_CONFIG_NAME))
        cls.y_origin = int(configuration.get(cls.__DEFAULT_SECTION_NAME, cls.__Y_ORIGIN_CONFIG_NAME))
        cls.x_offset = int(configuration.get(cls.__DEFAULT_SECTION_NAME, cls.__X_OFFSET_CONFIG_NAME))
        cls.y_offset = int(configuration.get(cls.__DEFAULT_SECTION_NAME, cls.__Y_OFFSET_CONFIG_NAME))
        cls.thickness = float(configuration.get(cls.__DEFAULT_SECTION_NAME, cls.__THICKNESS_CONFIG_NAME))
        cls.y_line_separation = int(configuration.get(cls.__DEFAULT_SECTION_NAME, cls.__Y_LINE_SEPARATION_NAME))
        cls.xml_line = configuration.get(cls.__DEFAULT_SECTION_NAME, cls.__XML_LINE_CONFIG_NAME)
        cls.xml_line = configuration.get(cls.__DEFAULT_SECTION_NAME, cls.__XML_LINE_CONFIG_NAME)

        if configuration[cls.__DEFAULT_SECTION_NAME][cls.__UNIT_CONFIG_NAME] == cls.__UNIT_MIL_TEXT:
            cls.unit_mm = False

        cls.__initialized = True


Design.default_config()