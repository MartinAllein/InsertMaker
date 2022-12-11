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
    _DEFAULT_X_OFFSET = 1.0
    _DEFAULT_Y_OFFSET = 2.0
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
    thickness = __DEFAULT_THICKNESS
    y_line_separation = __DEFAULT_Y_LINE_SEPARATION
    unit_mm = True

    FACTOR = 720000 / 25.4
    __default_configuration = {}

    def __init__(self):
        self.outfile = ""
        self.title = ""
        self.x_offset = self._DEFAULT_X_OFFSET
        self.y_offset = self._DEFAULT_Y_OFFSET
        self.project_name = ""
        self.verbose = False
        self.options = None
        self.default_name = ""

    @abstractmethod
    def create(self):
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

    def banane(self):
        print(self.x_offset)

    @staticmethod
    def validate_config_and_section(classname, config: str, section: str):
        if config is None or config == "":
            print(f"No configuration file for Design {classname}")
            sys.exit()

        if section is None or section == "":
            print(f"No section for configuration file {config}")
            sys.exit()

    @staticmethod
    def get_options(value):
        options = {}
        if 'options' in value:
            options = value['options']

        return options

    def convert_all_to_thoudpi(self, to_convert):
        """ Shift comma of dpi four digits to the right to get acceptable accuracy and only integer numbers"""

        for item in to_convert:
            setattr(self, item, Design.mm_to_thoudpi(getattr(self, item)))

    def import_from_config(self, config, section, options):
        # Set all configuration values
        if 'project name' in options:
            self.project_name = options['project name']
        else:
            self.project_name = config.get(section, 'project name')

        self.outfile = config.get(section, 'filename')

        self.title = config.get(section, 'title').strip('"')

        if 'x offset' in options:
            self.x_offset = options['x offset']
        else:
            self.x_offset = float(config.get(section, 'x offset'))

        if 'y offset' in options:
            self.y_offset = options['y offset']
        else:
            self.y_offset = float(config.get(section, 'y offset'))

    def set_title_and_outfile(self, name: str):
        if name is None or name == "":
            return

        if not self.title:
            self.title = name

        if not self.outfile:
            self.outfile = name

        self.outfile = File.set_svg_extension(self.outfile)

    def configuration(self, config: str, section: str, verbose: bool, payload=None):
        self.validate_config_and_section(__class__.__name__, config, section)

        if payload is None:
            payload = {}

        options = {}
        if 'options' in payload:
            options = payload['options']

        default_values = []
        if 'default_values' in payload:
            default_values = payload['default_values']

        config = self.__read_config(config, section, default_values, options)

        default_name = ""
        if 'default_name' in payload:
            default_name = payload['default_name']
        else:
            default_name = f"{self.__class__.__name__}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.set_title_and_outfile(default_name)

        self.verbose = verbose

        return config

    def __read_config(self, filename: str, section: str, defaults=None, options=None):
        """ Read configuration from file"""
        if defaults is None:
            defaults = {}

        if options is None:
            options = {}

        config = Config.read_config(filename, section, defaults)
        self.import_from_config(config, section, options)
        return config


Design.default_config()
