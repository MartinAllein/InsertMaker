import sys
import os
import xml.dom.minidom
from abc import ABC, abstractmethod

FILENAME = 'FILENAME'

TEMPLATE = 'TEMPLATE'


class Design(ABC):
    DEFAULT_FILENAME = "Design-"

    XML_LINE = '<line x1="%s"  y1="%s"  x2="%s" y2="%s" />\n'
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
    def convert_coord(coord):
        if coord == 0:
            value = "00000"
        else:
            value = str(coord)

        return value[:-4] + "." + value[-4:]

    @staticmethod
    def line(start: int, end: int):
        start_x = Design.convert_coord(start[0])
        start_y = Design.convert_coord(start[1])
        end_x = Design.convert_coord(end[0])
        end_y = Design.convert_coord(end[1])

        return Design.XML_LINE % (start_x, start_y, end_x, end_y)

    @staticmethod
    def create_xml_lines(corners, lines):
        xml_lines = ""
        for idx_outer, num_outer in enumerate(lines):
            for idx_inner, num_inner in enumerate(num_outer[:-1]):
                xml_lines += Design.line(corners[lines[idx_outer][idx_inner]], corners[lines[idx_outer][idx_inner + 1]])
        return xml_lines

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