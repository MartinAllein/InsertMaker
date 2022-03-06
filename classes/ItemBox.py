import argparse
from classes.Design import Design

from datetime import datetime


class ItemBox(Design):
    __DEFAULT_FILENAME = "MatchboxFinn"
    __DEFAULT_TEMPLATE = "templates/ItemBox.svg"
    __DEFAULT_TEMPLATE_SEPARATED = "templates/ItemBoxSeparated.svg"

    __X_OFFSET = Design.X_OFFSET
    __Y_OFFSET = Design.Y_OFFSET

    __SLOT_WIDTH = int(float(10 * Design.FACTOR))
    __SIDE_GAP = int(float(10 * Design.FACTOR))

    __DEFAUL_THICKNESS = 1.5

    __SEPARATION = int(float(3 * Design.FACTOR))

    __THUMBHOLE_SMALL_RADIUS = int(2 * Design.FACTOR)

    def __init__(self, arguments=""):

        self.length = 0.0
        self.width = 0.0
        self.height = 0.0
        self.thickness = 0.0
        self.outfile = ""
        self.title = ""
        self.outfile = ''
        self.foo = {}
        self.separated = False
        self.thumbholeradius = 0.0
        self.walls = []

        self.left_x = 0
        self.right_x = 0
        self.top_y = 0
        self.bottom_y = 0

        self.inner_dimensions = []
        self.outer_dimensions = []

        self.args = self.parse_arguments(arguments)
        self.corners = []
        self.cutlines = []

        error = ""

        self.length = self.args.l
        self.width = self.args.w
        self.height = self.args.h

        if not self.args.s:
            self.thickness = self.__DEFAUL_THICKNESS
        else:
            self.thickness = self.args.s

        self.separated = self.args.x

        # here are the inner measurements on the command line => calculate outer lines
        self.length += 2 * self.thickness
        self.width += 2 * self.thickness

        temp_filename = f"{ItemBox.__DEFAULT_FILENAME}-L{self.length}-W{self.width}-H{self.height}-" \
                        f"S{self.thickness}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        if not self.args.o:
            self.outfile = temp_filename
        else:
            self.outfile = self.args.o

        if not self.args.t:
            self.title = temp_filename
        else:
            self.title = self.args.t

        if self.args.W:
            self.walls = self.args.W

        if self.outfile[-4:] != '.svg':
            self.outfile += '.svg'

        if self.args.d:
            self.thumbholeradius = self.args.d

        print(self.walls)

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
        return ItemBox.__check_value('Length', value)

    @staticmethod
    def __check_width(value):
        return ItemBox.__check_value('Width', value)

    @staticmethod
    def __check_height(value):
        return ItemBox.__check_value('Height', value)

    @staticmethod
    def __check_thickness(value):
        return ItemBox.__check_value('Thickness', value)

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

    def parse_arguments(self, arguments):
        parser = argparse.ArgumentParser(add_help=False)

        parser.add_argument('-l', type=float, required=True, help="length of the matchbox")
        parser.add_argument('-w', type=float, required=True, help="width of the matchbox")
        parser.add_argument('-h', type=float, required=True, help="height of the matchbox")
        parser.add_argument('-d', type=float, help="Thumb Hole Radius")
        parser.add_argument('-s', type=float, help="thickness of the material")
        parser.add_argument('-o', type=str, help="output filename")
        parser.add_argument('-t', type=str, help="title of the matchbox")
        parser.add_argument('-x', action="store_true", help="separated Design")
        parser.add_argument('-W', type=int, nargs='+', help="Walls")

        if not arguments:
            return parser.parse_args()

        return parser.parse_args(arguments.split())



    def create(self):
        self.__init_design()

        self.foo["FILENAME"] = self.outfile
        self.foo["$TITLE$"] = self.title
        self.foo["$FILENAME$"] = self.outfile
        self.foo["$LABEL_X$"] = Design.thoudpi_to_dpi(self.left_x)

        ycoord = self.bottom_y +int( Design.Y_LINE_SEPARATION)

        # self.make_slots([0, 0])

        if not self.separated:
            if self.thumbholeradius:
                base_cut = Design.draw_lines(self.corners, self.cutlines_with_thumbhole)
            else:
                base_cut = Design.draw_lines(self.corners, self.cutlines)

            self.foo["TEMPLATE"] = self.__DEFAULT_TEMPLATE
            self.foo["$BASE-CUT$"] = base_cut

        else:
            # TEST FOR SEPARATION
            separation = self.__SEPARATION + self.thickness

            y1 = 0
            self.foo["TEMPLATE"] = self.__DEFAULT_TEMPLATE_SEPARATED

            # TOP CUT
            self.foo[
                '$TRANSLATE_TOP$'] = f"{Design.thoudpi_to_dpi(self.corners[0][0] - self.corners[10][0])}, 0"
            top_cut = Design.create_xml_cutlines(self.corners, self.cutlines_top)
            self.foo["$TOP-CUT$"] = top_cut

            # CENTER CUT
            self.foo[
                '$TRANSLATE_CENTER$'] = f"{Design.thoudpi_to_dpi(self.corners[0][0] - self.corners[13][0])}, " \
                                        + f"{Design.thoudpi_to_dpi(self.thickness + separation)}"

            center_cut = Design.create_xml_cutlines(self.corners, self.cutlines_center)
            self.foo["$CENTER-CUT$"] = center_cut

            # Bottom Cut
            self.foo[
                '$TRANSLATE_BOTTOM$'] = f"{Design.thoudpi_to_dpi(self.corners[0][0] - self.corners[18][0])}, " \
                                        + f"{Design.thoudpi_to_dpi(2 * (self.thickness + separation))}"
            bottom_cut = Design.create_xml_cutlines(self.corners, self.cutlines_bottom)
            self.foo["$BOTTOM-CUT$"] = bottom_cut

            # LEFT CUT
            self.foo[
                '$TRANSLATE_LEFT$'] = f"{Design.thoudpi_to_dpi(self.length + self.thickness + separation)}, " \
                                      + f"-{Design.thoudpi_to_dpi(self.height)}"
            left_cut = Design.create_xml_cutlines(self.corners, self.cutlines_left)
            self.foo["$LEFT-CUT$"] = left_cut

            # RIGHT CUT
            self.foo[
                '$TRANSLATE_RIGHT$'] = f"-{Design.thoudpi_to_dpi(self.height - self.thickness - separation)}, " \
                                       + f" {Design.thoudpi_to_dpi(-self.height + self.width + self.thickness + separation)}"
            # + f" {Design.convert_coord(self.thickness + separation)}"
            right_cut = Design.create_xml_cutlines(self.corners, self.cutlines_right)
            self.foo["$RIGHT-CUT$"] = right_cut

            ycoord += 2 * Design.Y_LINE_SEPARATION

        temp = round(3 * (self.height + 3 * int( self.__SEPARATION) + int(Design.Y_LINE_SEPARATION)))
        self.foo["$VIEWPORT$"] = f"{Design.thoudpi_to_dpi(round(self.right_x + 2 * Design.FACTOR))}," \
                                 f" {Design.thoudpi_to_dpi(temp)}"

        self.foo["$LABEL_TITLE_Y$"] = Design.thoudpi_to_dpi(ycoord)

        ycoord += int( Design.Y_LINE_SEPARATION)
        self.foo["$LABEL_FILENAME_Y$"] = Design.thoudpi_to_dpi(ycoord)

        ycoord += int( Design.Y_LINE_SEPARATION)
        self.foo["$LABEL_OVERALL_WIDTH_Y$"] = Design.thoudpi_to_dpi(ycoord)

        ycoord += int( Design.Y_LINE_SEPARATION)
        self.foo["$LABEL_FLAP_WIDTH_Y$"] = Design.thoudpi_to_dpi(ycoord)

        self.foo["$LABEL_OVERALL_WIDTH$"] = str(round((self.right_x - self.left_x) / Design.FACTOR, 2))

        Design.write_to_file(self.foo)

        print(
            f"Inner Length: {self.inner_dimensions[0]} , "
            f"Inner Width: {self.inner_dimensions[1]} , "
            f"Inner Height: {self.inner_dimensions[2]}")

        print(
            f"Outer Length: {self.outer_dimensions[0]} , "
            f"Outer Width: {self.outer_dimensions[1]} , "
            f"Outer Height: {self.outer_dimensions[2]}")

    def __init_design(self):
        self.__init_base()

    def __init_base(self):

        #          a    b    c    d    e     f          g                    h          i     j    k    m    n    o
        #  q                      10--------------------------------------------------------------50    74--77
        #                         |                                                                |    |    |
        #                         |                                                                |    |    |
        #  ac                     |                                                                72--75    78--80
        #                         |                                                                |              |
        #                         |                                                                |              |
        #  ag                     |                                                                |           /-86
        #  r                      11--22                   length                             44--51          /   |
        #                              |                                                      |              /    |
        #                              |                                                      |              |    |
        #                              |                                                      |              |    |
        #  s                      12--23                                                      45--52         \    |
        #                         | side-gap                                              side-gap |          \   |
        #                         |                                                                |           \-87
        #  ah                     |                                                                |              |
        #                         |                                                                |              |
        #  ad                     |                                                                73--76    79--81
        #                         |                                                                |    |    |
        #                         |                                                                |    |    |
        #  t            2--- 6    13--------28          32------------------36          40--------53    62--66
        #               |    |    |          |          |thickness           |          |          |    |    |
        #               |    |    |          |          |                    |          |          |    |    |
        #  u       0----3    7---14          29--------33                    37--------41          54--63    67--70
        #          |              |           slot_width                                           |              |
        #          |              | side-gap                                                       |              |
        #  ae      82-\           |                                                                |           /-84
        #  v       |   \          15--24                                                      46--55          /   | w
        #        w |    \              |                                                      |              /    | i
        #        i |     |             |                                                      |              |    | d
        #        d |     |             |                                                      |              |    | d
        #        t |     |             |                                                      |              |    | t
        #        h |    /              |                                                      |              \    | h
        #  w       |   /          16--25                                                      47--56          \   |
        #  af      83-/           |                                                                |           \-85
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
        height = int(self.height)
        width = self.width
        thickness = self.thickness

        slot_width = int(self.__SLOT_WIDTH)
        side_gap = self.__SIDE_GAP

        # noinspection DuplicatedCode
        # X - Points
        a = int(self.__X_OFFSET)
        b = a + int(height / 2) - int(slot_width / 2)
        c = a + int(height / 2) + int(slot_width / 2)
        d = a + height
        # d = self.__X_OFFSET
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
        q = int(self.__Y_OFFSET)
        r = q + int(height / 2) - int(slot_width / 2)
        s = q + int(height / 2) + int(slot_width / 2)
        t = q + height
        u = t + thickness
        v = t + int(width / 2) - int(slot_width / 2)
        w = t + int(width / 2) + int(slot_width / 2)
        y = t + width
        x = y - thickness
        z = y + int(height / 2 - slot_width / 2)
        aa = y + int(height / 2 + slot_width / 2)
        ab = y + height
        ac = q + thickness
        ad = t - thickness
        ae = t + int(width / 2 - self.thumbholeradius - self.__THUMBHOLE_SMALL_RADIUS)
        af = t + int(width / 2 + self.thumbholeradius + self.__THUMBHOLE_SMALL_RADIUS)
        ag = q + int(width / 2 - self.thumbholeradius - self.__THUMBHOLE_SMALL_RADIUS)
        ah = q + int(width / 2 + self.thumbholeradius + self.__THUMBHOLE_SMALL_RADIUS)

        self.corners = [[a, u], [a, x], [b, t], [b, u], [b, x], [b, y], [c, t], [c, u], [c, x],
                        [c, y], [d, q], [d, r], [d, s], [d, t], [d, u], [d, v], [d, w], [d, x],
                        [d, y], [d, z], [d, aa], [d, ab], [e, r], [e, s], [e, v], [e, w], [e, z],
                        [e, aa], [f, t], [f, u], [f, x], [f, y], [g, t], [g, u], [g, x], [g, y],
                        [h, t], [h, u], [h, x], [h, y], [i, t], [i, u], [i, x], [i, y], [j, r],
                        [j, s], [j, v], [j, w], [j, z], [j, aa], [k, q], [k, r], [k, s], [k, t],
                        [k, u], [k, v], [k, w], [k, x], [k, y], [k, z], [k, aa], [k, ab], [m, t],
                        [m, u], [m, x], [m, y], [n, t], [n, u], [n, x], [n, y], [o, u], [o, x],
                        [k, ac], [k, ad], [m, q], [m, ac], [m, ad], [n, q], [n, ac], [n, ad],
                        [o, ac], [o, ad], [a, ae], [a, af], [o, ae], [o, af], [o, ag], [o, ah]
                        ]

        self.inner_dimensions = [Design.thoudpi_to_mm(self.corners[46][0] - self.corners[24][0]),
                                 Design.thoudpi_to_mm(self.corners[1][1] - self.corners[0][1]),
                                 Design.thoudpi_to_mm(self.corners[14][0] - self.corners[0][0])]

        self.outer_dimensions = [Design.thoudpi_to_mm(self.corners[50][0] - self.corners[10][0]),
                                 Design.thoudpi_to_mm(self.corners[18][1] - self.corners[13][1]),
                                 Design.thoudpi_to_mm(self.corners[24][0] - self.corners[0][0])]

        self.cutlines = [
            [Design.LINE,
             [10, 11, 22, 23, 12, 15, 24, 25, 16, 19, 26, 27, 20, 21, 61, 60, 49, 48, 59, 56, 47, 46, 55, 52, 45, 44,
              51, 50, 10]],
            [Design.LINE, [13, 28, 29, 33, 32, 36, 37, 41, 40, 53]],
            [Design.LINE, [18, 31, 30, 34, 35, 39, 38, 42, 43, 58]],
            [Design.LINE, [54, 63, 62, 66, 67, 70, 71, 68, 69, 65, 64, 57]],
            [Design.LINE, [14, 7, 6, 2, 3, 0, 1, 4, 5, 9, 8, 17]],
        ]

        self.cutlines_with_thumbhole = [
            [Design.THUMBHOLE, [85, self.__THUMBHOLE_SMALL_RADIUS, self.thumbholeradius, 0, Design.NORTH]],
            [Design.THUMBHOLE, [82, self.__THUMBHOLE_SMALL_RADIUS, self.thumbholeradius, 0, Design.SOUTH]],
            [Design.LINE,
             [10, 11, 22, 23, 12, 15, 24, 25, 16, 19, 26, 27, 20, 21, 61, 60, 49, 48, 59, 56, 47, 46, 55, 52, 45, 44,
              51, 50, 10]],
            [Design.LINE, [13, 28, 29, 33, 32, 36, 37, 41, 40, 53]],
            [Design.LINE, [18, 31, 30, 34, 35, 39, 38, 42, 43, 58]],
            [Design.LINE, [54, 63, 62, 66, 67, 70, 84]],
            [Design.LINE, [85, 71, 68, 69, 65, 64, 57]],
            # [Design.LINE, [73, 76, 62]],
            # [Design.LINE, [72, 75, 74, 77, 78, 80, 86]],
            # [Design.LINE, [87, 81, 79, 66]]
            [Design.LINE, [14, 7, 6, 2, 3, 0, 82]],
            [Design.LINE, [83, 1, 4, 5, 9, 8, 17]]
        ]

        self.cutlines_top = [
            [Design.LINE, [10, 11, 22, 23, 12, 13, 28, 29, 33, 32, 36, 37, 41, 40, 53, 52, 45, 44, 51, 50, 10]]]
        self.cutlines_center = [[Design.LINE,
                                 [13, 15, 24, 25, 16, 18, 31, 30, 34, 35, 39, 38, 42, 43, 58, 56, 47, 46, 55, 53, 40,
                                  41, 37, 36, 32, 33, 29, 28, 13]]]
        self.cutlines_bottom = [[Design.LINE,
                                 [18, 19, 26, 27, 20, 21, 61, 60, 49, 48, 59, 58, 43, 42, 38, 39, 35, 34, 30, 31, 18]]]
        self.cutlines_left = [[Design.LINE, [0, 1, 4, 5, 9, 8, 17, 16, 25, 24, 15, 14, 7, 6, 2, 3, 0]]]
        self.cutlines_right = [[Design.LINE, [54, 55, 46, 47, 56, 57, 64, 65, 69, 68, 71, 70, 67, 66, 62, 63, 54]]]

        # detect boundaries of drawing
        self.left_x, self.right_x, self.top_y, self.bottom_y = Design.get_bounds(self.corners)

    def __draw_slot_hole_line(self, xml_string, start, delta):

        # https://stackoverflow.com/questions/25640628/python-adding-lists-of-numbers-with-other-lists-of-numbers
        stop = [sum(values) for values in zip(start, delta)]

        xml_string += Design.draw_line(start, stop)

        return xml_string, stop
