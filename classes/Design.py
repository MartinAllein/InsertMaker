from abc import ABC, abstractmethod
from collections import namedtuple


class Design(ABC):

    DEFAULT_FILENAME = "Design-"

    XML_LINE = '<line x1="%s"  y1="%s"  x2="%s" y2="%s" />\n'
    FACTOR = 720000 / 25.4
    X_OFFSET = int(1 * FACTOR)
    Y_OFFSET = int(1 * FACTOR)

    Point = namedtuple('Point', 'x y')

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
    def line(start, end):
        start_x = Design.convert_coord(start.x)
        start_y = Design.convert_coord(start.y)
        end_x = Design.convert_coord(end.x)
        end_y = Design.convert_coord(end.y)

        return Design.XML_LINE % (start_x, start_y, end_x, end_y)
