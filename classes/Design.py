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
    X_OFFSET = int(1 * FACTOR)
    Y_OFFSET = int(1 * FACTOR)
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
    def set_dot(coord: str):
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
                result.append(Design.set_dot(item))
        else:
            result = Design.set_dot(coord)
        return result

    @staticmethod
    def line(start: int, end: int):
        start_x, start_y = Design.convert_coord(start)
        end_x, end_y = Design.convert_coord(end)
        return Design.__XML_LINE % (start_x, start_y, end_x, end_y)

    @staticmethod
    def thumbholepath(corners, path):
        start_x, start_y = corners[path[0]]
        smallradius, thumbholeradius, direction, orientation = path[1:]

        end_x = start_x - smallradius
        end_y = start_y - smallradius
        xmlstring = Design.__XML_PATH % (
            Design.convert_coord(start_x), Design.convert_coord(start_y), Design.convert_coord(smallradius),
            Design.convert_coord(smallradius), direction, Design.convert_coord(end_x), Design.convert_coord(end_y))

        start_x = end_x
        start_y = end_y
        end_x = end_x
        end_y = start_y - 2 * thumbholeradius
        xmlstring += Design.__XML_PATH % (
            Design.convert_coord(start_x), Design.convert_coord(start_y), Design.convert_coord(thumbholeradius),
            Design.convert_coord(thumbholeradius), 1 - direction, Design.convert_coord(end_x),
            Design.convert_coord(end_y))

        start_x = end_x
        start_y = end_y
        end_x = start_x + smallradius
        end_y = start_y - smallradius
        xmlstring += Design.__XML_PATH % (
            Design.convert_coord(start_x), Design.convert_coord(start_y), Design.convert_coord(smallradius),
            Design.convert_coord(smallradius), direction, Design.convert_coord(end_x), Design.convert_coord(end_y))

        return xmlstring

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
    def create_xpl_paths(corners, points):
        pass

    @staticmethod
    def get_bounds(corners):
        left_x = sys.maxsize - 1
        right_x = -sys.maxsize - 1
        top_y = sys.maxsize - 1
        bottom_y = -sys.maxsize - 1

        for key, value in enumerate(corners):

            # check left_x
            if value[0] < left_x:
                left_x = value[0]

            # check right_x
            if value[0] > right_x:
                right_x = value[0]

            # check top_y
            if value[1] < top_y:
                top_y = value[1]

            # check bottom_y
            if value[1] > bottom_y:
                bottom_y = value[1]

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
