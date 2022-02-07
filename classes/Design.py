from datetime import datetime
from abc import ABC, abstractmethod


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

