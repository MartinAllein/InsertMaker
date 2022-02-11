import sys
import os
import xml.dom.minidom
from abc import ABC, abstractmethod

FILENAME = 'FILENAME'

TEMPLATE = 'TEMPLATE'


class Design(ABC):
    DEFAULT_FILENAME = "Design-"

    __XML_LINE = '<line x1="%s"  y1="%s"  x2="%s" y2="%s" />\n'
    __XML_PATH = '<path d="M %s %s A %s %s 0 0 %s %s %s"/>\n'

    LINE = "Line"
    THUMBHOLE = "Path"
    SOUTH = "South"
    NORTH = "North"
    EAST = "East"
    WEST = "West"

    FACTOR = 720000 / 25.4
    X_OFFSET = int(5 * FACTOR)
    Y_OFFSET = int(5 * FACTOR)
    FLAP_RETRACT = int(2 * FACTOR)
    X_DRAWING_DELTA = int(2 * FACTOR)
    Y_DRAWING_DELTA = int(2 * FACTOR)
    Y_LINE_SEPARATION = int(7 * FACTOR)

    @abstractmethod
    def create(self):
        pass

    @abstractmethod
    def parse_arguments(self):
        pass

    @staticmethod
    def __set_dot(coord: str):
        if coord == 0:
            value = "00000"
        else:
            value = str(coord)

        return value[:-4] + "." + value[-4:]

    @staticmethod
    def convert_coord(coord: str):

        if type(coord) is list:
            result = []
            for item in coord:
                result.append(Design.__set_dot(item))
        else:
            result = Design.__set_dot(coord)
        return result

    @staticmethod
    def line(start, end):
        start_x, start_y = Design.convert_coord(start)
        end_x, end_y = Design.convert_coord(end)
        return Design.__XML_LINE % (start_x, start_y, end_x, end_y)

    @staticmethod
    def thumbholepath(corners, path):
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
            outstring = Design.__make_arc(start_x, start_y, smallradius, values[2], end_x, end_y)
            xmlstring += outstring
            start_x = end_x
            start_y = end_y

        return xmlstring

    @staticmethod
    def __make_arc(start_x, start_y, radius, direction, end_x, end_y):
        return Design.__XML_PATH % (
            Design.convert_coord(start_x), Design.convert_coord(start_y), Design.convert_coord(radius),
            Design.convert_coord(radius), direction, Design.convert_coord(end_x), Design.convert_coord(end_y))

    @staticmethod
    def create_xml_lines(corners, lines):
        xml_lines = ""
        for command, values in lines:
            if command == Design.LINE:
                for start, end in zip(values[:-1], values[1:]):
                    xml_lines += Design.line(corners[start], corners[end])
            elif command == Design.THUMBHOLE:
                xml_lines += Design.thumbholepath(corners, values)
                pass

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
            template = template.replace(key, items[key])

        dom = xml.dom.minidom.parseString(template)
        template = dom.toprettyxml(newl='')

        with open(f"{filename}", 'w') as f:
            f.write(template)

    @staticmethod
    def create_xml_cutlines(corners, lines):
        return Design.create_xml_lines(corners, lines)

    @staticmethod
    def to_numeral(value):
        return round(value / Design.FACTOR, 2)
