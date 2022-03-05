import sys
import os
import xml.dom.minidom
from abc import ABC, abstractmethod
import configparser

FILENAME = 'FILENAME'

TEMPLATE = 'TEMPLATE'


class Design(ABC):
    __XML_LINE = '<line x1="%s" y1="%s"  x2="%s" y2="%s" />\n'
    __XML_PATH = '<path d="M %s %s A %s %s 0 0 %s %s %s"/>\n'
    __CONFIG_FILE = 'config/Design.config'

    # Line Types
    LINE = "Line"
    THUMBHOLE = "Path"
    HALFCIRCLE = "Halfcircle"
    PAIR = "Pair"

    # Drawing directions
    SOUTH = "South"
    NORTH = "North"
    EAST = "East"
    WEST = "West"
    VERTICAL = "Vertical"
    HORIZONTAL = "Horizontal"
    CW = 1
    CCW = 0

    FACTOR = 720000 / 25.4

    # Fallback settings when Design.config is missing
    X_OFFSET = 5
    Y_OFFSET = 5
    Y_LINE_SEPARATION = 7

    @classmethod
    def config_file(cls):
        return cls.__CONFIG_FILE

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
    def thoudpi_to_dpi(coord: int):

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
        return Design.__XML_LINE % (start_x, start_y, end_x, end_y)

    @staticmethod
    def draw_halfcircle(corners, path):
        start_x, start_y = corners[path[0]]
        end_x, end_y = corners[path[1]]
        orientation = path[2]

        diameter = 0
        if orientation == Design.VERTICAL:
            diameter = abs(end_y - start_y)
        else:
            diameter = abs(end_x - start_x)

        return Design.__draw_arc(start_x, start_y, int(diameter / 2), Design.CW, end_x, end_y)

    @staticmethod
    def draw_thumbhole_path(corners, path):
        start_x, start_y = corners[path[0]]
        smallradius, thumbholeradius, direction, orientation = path[1:]

        delta = {
            Design.NORTH: [[-smallradius, -smallradius, direction], [0, -2 * thumbholeradius, 1 - direction],
                           [smallradius, -smallradius, direction]],
            Design.SOUTH: [[smallradius, smallradius, direction], [0, 2 * thumbholeradius, 1 - direction],
                           [-smallradius, smallradius, direction]],
            Design.WEST: [[-smallradius, -smallradius, 1 - direction], [-2 * thumbholeradius, 0, direction],
                          [-smallradius, +smallradius, 1 - direction]],
            Design.EAST: [[smallradius, smallradius, 1 - direction], [2 * thumbholeradius, 0, direction],
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
        return Design.__XML_PATH % (
            Design.thoudpi_to_dpi(start_x), Design.thoudpi_to_dpi(start_y), Design.thoudpi_to_dpi(radius),
            Design.thoudpi_to_dpi(radius), direction, Design.thoudpi_to_dpi(end_x), Design.thoudpi_to_dpi(end_y))

    @staticmethod
    def draw_lines(corners, lines):
        xml_lines = ""
        for command, values in lines:
            if command == Design.LINE:
                for start, end in zip(values[:-1], values[1:]):
                    xml_lines += Design.draw_line(corners[start], corners[end])
            elif command == Design.THUMBHOLE:
                xml_lines += Design.draw_thumbhole_path(corners, values)
            elif command == Design.PAIR:
                for start, end in zip(values[::2], values[1::2]):
                    xml_lines += Design.draw_line(corners[start], corners[end])
            elif command == Design.HALFCIRCLE:
                xml_lines += Design.draw_halfcircle(corners, values)

        return xml_lines

    @staticmethod
    def get_bounds(corners):

        left_x = min(a for (a, b) in corners)
        top_y = min(b for (a, b) in corners)
        right_x = max(a for (a, b) in corners)
        bottom_y = max(b for (a, b) in corners)

        return left_x, right_x, top_y, bottom_y

    @staticmethod
    def write_to_file(items):

        if FILENAME not in items:
            raise "No filename given"

        if TEMPLATE not in items:
            raise " No tamplate given"

        if not os.path.isfile(items[TEMPLATE]):
            raise "Template file does not exist"

        with open(items[TEMPLATE], 'r') as f:
            template = f.read()

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

    @staticmethod
    def thoudpi_to_mm(value):
        return round(value / Design.FACTOR, 2)

    @staticmethod
    def mm_to_thoudpi(value):
        return int(float(value) * Design.FACTOR)


# Read default values from the config file
if os.path.isfile(Design.config_file()):
    # read entries from the configuration file
    config = configparser.ConfigParser()
    config.read(Design.config_file())
    Design.X_OFFSET = config['DESIGN']['X_OFFSET']
    Design.Y_OFFSET = config['DESIGN']['Y_OFFSET']
    Design.Y_LINE_SEPARATION = config['DESIGN']['Y_LINE_SEPARATION']

