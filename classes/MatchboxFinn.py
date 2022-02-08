import argparse
from classes.Design import Design

from datetime import datetime


class MatchboxFinn(Design):
    __DEFAULT_FILENAME = "MatchboxFinn"
    __DEFAULT_TEMPLATE = "templates/MatchboxFinn.svg"

    __X_OFFSET = Design.X_OFFSET
    __Y_OFFSET = Design.Y_OFFSET

    __SLOT_WIDTH = int(float(10 * Design.FACTOR))
    __SIDE_GAP = int(float(10 * Design.FACTOR))

    __DEFAUL_THICKNESS = 1.5

    def __init__(self):

        self.length = 0.0
        self.width = 0.0
        self.height = 0.0
        self.thickness = 0.0
        self.outfile = ""
        self.title = ""
        self.outfile = ''
        self.foo = {}

        self.left_x = 0
        self.right_x = 0
        self.top_y = 0
        self.bottom_y = 0

        self.args = self.parse_arguments()
        self.corners = []

        error = ""

        self.length = self.args.l
        self.width = self.args.w
        self.height = self.args.h

        if not self.args.s:
            self.thickness = self.__DEFAUL_THICKNESS
        else:
            self.thickness = self.args.s

        # here are the inner measurements on the command line => calculate outer lines
        self.length += 2 * self.thickness
        self.width += 2 * self.thickness
        self.height += self.thickness

        temp_filename = f"{MatchboxFinn.__DEFAULT_FILENAME}-L{self.length}-W{self.width}-H{self.height}-" \
                        f"S{self.thickness}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        if not self.args.o:
            self.outfile = temp_filename
        else:
            self.outfile = self.args.o

        if not self.args.t:
            self.title = temp_filename
        else:
            self.title = self.args.t

        if self.outfile[-4:] != '.svg':
            self.outfile += '.svg'

        # Convert int 123.5 to 1235000 to avoid decimal places. 4 decimal places used
        self.length = int(float(self.length) * Design.FACTOR)
        self.width = int(float(self.width) * Design.FACTOR)
        self.height = int(float(self.height) * Design.FACTOR)
        self.thickness = int(float(self.thickness) * Design.FACTOR)

        error += self.__check_length(self.length)
        error += self.__check_width(self.width)
        error += self.__check_height(self.height)
        error += self.__check_thickness(self.height)

        if not error:
            print(error)

    @staticmethod
    def __check_length(value):
        return MatchboxFinn.__check_value('Length', value)

    @staticmethod
    def __check_width(value):
        return MatchboxFinn.__check_value('Width', value)

    @staticmethod
    def __check_height(value):
        return MatchboxFinn.__check_value('Height', value)

    @staticmethod
    def __check_thickness(value):
        return MatchboxFinn.__check_value('Thickness', value)

    @staticmethod
    def __check_value(description, value):
        string = ""
        if not value:
            string += f" missing {description}\n"
        elif int(value) <= 0:
            string += f"{description} must be greater than zero (Is:{value})"

        return string

    def __str__(self):
        return self.width, self.length, self.height, self.thickness, self.outfile

    def parse_arguments(self):
        parser = argparse.ArgumentParser(add_help=False)

        parser.add_argument('-l', type=float, required=True, help="length of the matchbox")
        parser.add_argument('-w', type=float, required=True, help="width of the matchbox")
        parser.add_argument('-h', type=float, required=True, help="height of the matchbox")
        parser.add_argument('-s', type=float, help="thickness of the material")
        parser.add_argument('-o', type=str, help="output filename")
        parser.add_argument('-t', type=str, help="title of the matchbox")

        return parser.parse_args()

    # noinspection DuplicatedCode
    def create(self):
        self.__init_design()
        # base_cut = self.__create_cutline()
        base_cut = Design.create_xml_cutlines(self.corners, self.cutlines)

        self.foo["TEMPLATE"] = self.__DEFAULT_TEMPLATE
        self.foo["FILENAME"] = self.outfile
        self.foo["$BASE-CUT$"] = base_cut
        self.foo["$TITLE$"] = self.title
        self.foo["$FILENAME$"] = self.outfile
        self.foo["$LABEL_X$"] = Design.convert_coord(self.left_x)

        ycoord = self.bottom_y + Design.Y_LINE_SEPARATION
        self.foo["$LABEL_TITLE_Y$"] = Design.convert_coord(ycoord)

        ycoord += Design.Y_LINE_SEPARATION
        self.foo["$LABEL_FILENAME_Y$"] = Design.convert_coord(ycoord)

        ycoord += Design.Y_LINE_SEPARATION
        self.foo["$LABEL_OVERALL_WIDTH_Y$"] = Design.convert_coord(str(ycoord))

        ycoord += Design.Y_LINE_SEPARATION
        self.foo["$LABEL_FLAP_WIDTH_Y$"] = Design.convert_coord(str(ycoord))

        self.foo["$LABEL_OVERALL_WIDTH$"] = str(
            round((self.right_x - self.left_x) / Design.FACTOR, 2))

        self.foo["$VIEWPORT$"] = f"{Design.convert_coord(round(self.right_x + 2 * Design.FACTOR))}," \
                                 f" {Design.convert_coord(ycoord + Design.Y_LINE_SEPARATION)}"

        Design.write_to_file(self.foo)

    def __init_design(self):
        self.__init_base()

    def __init_base(self):

        #          a    b    c    d    e     f          g                    h          i     j    k    m   n     o
        #  q                      10--------------------------------------------------------------50
        #                         |                        length                                  |
        #  r                      11--22                   length                             44--51
        #                              |                                                      |
        #  s                      12--23                                                      45--52
        #                         | side-gap                                              side-gap |
        #                         |                                                                |
        #  t            2--- 6    13--------28          32------------------36          40--------53    62--66
        #               |    |    |          |          |thickness           |          |          |    |    |
        #               |    |    |          |          |                    |          |          |    |    |
        #  u       0----3    7---14          29--------33                    37--------41          54--63    67--70
        #          |              |           slot_width                                           |              |
        #          |              | side-gap                                                       |              |
        #          |              |                                                                |              |
        #  v     w |              15--24                                                      46--55              | w
        #        i |                   |                                                      |                   | i
        #        d |                   |                                                      |                   | d
        #        t |                   |                                                      |                   | t
        #        h |                   |                                                      |                   | h
        #  w       |              16--25                                                      47--56              |
        #          |              |                                                                |              |
        #          |              |                                                                |              |
        #          |              |                                                                |              |
        #  x       1----4    8---17          30--------34                    38--------42          57--64    68--71
        #               |    |    |          |          |                    |          |          |    |    |
        #               |    |    |          |          |                    |          |          |    |    |
        #  y            5----9    18--------31          35------------------39          43--------58    65--69
        #                         |                                                                |
        #                         |                                                                |
        #  z                      19--26                                                      48--59
        #                              |                                                      |
        #  aa                     20--27                                                      49--60
        #                         |                          length                                |
        #  ab                     21--------------------------------------------------------------61

        length = self.length
        height = self.height
        width = self.width
        thickness = self.thickness

        slot_width = self.__SLOT_WIDTH
        side_gap = self.__SIDE_GAP

        # noinspection DuplicatedCode
        # X - Points
        a = self.__X_OFFSET
        b = a + int(height / 2) - int(slot_width / 2)
        c = a + int(height / 2) + int(slot_width / 2)
        d = a + height
        e = d + thickness
        f = d + side_gap
        g = f + slot_width
        k = d + length
        i = k - side_gap
        j = k - thickness
        h = i - slot_width
        m = k + int(height / 2) - int(slot_width / 2)
        n = k + int(height / 2) + int(slot_width / 2)
        o = k + height

        # noinspection DuplicatedCode
        # Y - Points
        q = self.__Y_OFFSET
        r = q + int(height / 2) - int(slot_width / 2)
        s = q + int(height / 2) + int(slot_width / 2)
        t = q + height
        u = t + thickness
        v = t + int(width / 2) - int(slot_width / 2)
        w = t + int(width / 2) + int(slot_width / 2)
        y = t + width
        x = y - thickness
        z = y + int(height / 2) - int(slot_width / 2)
        aa = y + int(height / 2) + int(slot_width / 2)
        ab = y + height

        self.corners = [[a, u], [a, x], [b, t], [b, u], [b, x], [b, y], [c, t], [c, u], [c, x],
                        [c, y], [d, q], [d, r], [d, s], [d, t], [d, u], [d, v], [d, w], [d, x],
                        [d, y], [d, z], [d, aa], [d, ab], [e, r], [e, s], [e, v], [e, w], [e, z],
                        [e, aa], [f, t], [f, u], [f, x], [f, y], [g, t], [g, u], [g, x], [g, y],
                        [h, t], [h, u], [h, x], [h, y], [i, t], [i, u], [i, x], [i, y], [j, r],
                        [j, s], [j, v], [j, w], [j, z], [j, aa], [k, q], [k, r], [k, s], [k, t],
                        [k, u], [k, v], [k, w], [k, x], [k, y], [k, z], [k, aa], [k, ab], [m, t],
                        [m, u], [m, x], [m, y], [n, t], [n, u], [n, x], [n, y], [o, u], [o, x]]

        self.cutlines = [
            [13, 15, 24, 25, 16, 18, 31, 30, 34, 35, 39, 38, 42, 43, 58, 56, 47, 46, 55, 53, 40, 41, 37, 36, 32, 33, 29,
             28, 13],
            [14, 7, 6, 2, 3, 0, 1, 4, 5, 9, 8, 17],
            [18, 19, 26, 27, 20, 21, 61, 60, 49, 48, 59, 58],
            [57, 64, 65, 69, 68, 71, 70, 67, 66, 62, 63, 54],
            [53, 52, 45, 44, 51, 50, 10, 11, 22, 23, 12, 13]
        ]

        # detect boundaries of drawing
        self.left_x, self.right_x, self.top_y, self.bottom_y = Design.get_bounds(self.corners)
