import sys
import argparse
from classes.Design import Design

from datetime import datetime


class CardBox(Design):
    __DEFAULT_FILENAME = "CardBox"
    __DEFAULT_TEMPLATE = "templates/CardBox.svg"
    __DEFAULT_TEMPLATE_SEPARATED = "templates/ItemBoxSeparated.svg"

    __X_OFFSET = Design.X_OFFSET
    __Y_OFFSET = Design.Y_OFFSET

    __DEFAULT_SLOT_WIDTH = int(float(10 * Design.FACTOR))
    __DEFAULT_SIDE_GAP = int(float(10 * Design.FACTOR))
    __DEFAULT_FUNNEL_TOP_WIDTH = int(float(20 * Design.FACTOR))
    __DEFAULT_FUNNELBOTTOMWIDTH = int(float(10 * Design.FACTOR))
    __DEFAULT_NECKHEIGHT = int(float(10 * Design.FACTOR))
    __DEFAULT_THICKNESS = 1.5
    __DEFAULT_SEPARATION = int(float(3 * Design.FACTOR))
    __DEFAULT_NOSEWIDTH = int(float(5 * Design.FACTOR))
    __DEFAULT_BOTTOMHOLE_RADIUS = int(float(10 * Design.FACTOR))

    __SMALL_HEIGHT = int(20 * Design.FACTOR)

    def __init__(self):

        self.length = 0.0
        self.width = 0.0
        self.height = 0.0
        self.thickness = 0.0
        self.outfile = ""
        self.title = ""
        self.outfile = ''
        self.foo = {}
        self.separated = False
        self.thumbhole = False
        self.singlethumbhole = True
        self.singlefunnel = False

        self.left_x = 0
        self.right_x = 0
        self.top_y = 0
        self.bottom_y = 0

        self.inner_dimensions = []
        self.outer_dimensions = []

        self.args = self.parse_arguments()
        self.args_string = ' '.join(sys.argv[1:])
        self.corners = []
        self.cutlines = []

        error = ""

        self.length = self.args.l
        self.width = self.args.w
        self.height = self.args.h

        if not self.args.s:
            self.thickness = self.__DEFAULT_THICKNESS
        else:
            self.thickness = self.args.s

        self.separated = self.args.x

        temp_filename = f"{CardBox.__DEFAULT_FILENAME}-L{self.length}-W{self.width}-H{self.height}-" \
                        f"S{self.thickness}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        # here are the inner measurements on the command line => calculate outer lines
        self.length += 2 * self.thickness
        self.width += 2 * self.thickness

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

        if self.args.F:
            self.funnel_top = self.args.F
        else:
            self.funnel_top = self.__DEFAULT_FUNNEL_TOP_WIDTH

        if self.args.f:
            self.funnel_bottom = self.args.f
        else:
            self.funnel_bottom = self.__DEFAULT_FUNNELBOTTOMWIDTH

        # -n neck height of funnel
        if self.args.n:
            self.neckheight = self.args.n
        else:
            self.neckheight = self.__DEFAULT_NECKHEIGHT

        # -u width of nose at bottom of funnel
        if self.args.u:
            self.nosewidth = self.args.u
        else:
            self.nosewidth = self.__DEFAULT_NOSEWIDTH

        # -d Single Thumbhole
        # -D Dual Thumbhole
        if self.args.d:
            self.thumbhole = True
            self.singlethumbhole = True
        elif self.args.D:
            self.thumbhole = True
            self.singlethumbhole = False
        else:
            self.thumbhole = False

        # -b Funnel only on one side
        if self.args.b:
            self.singlefunnel = True
            self.singlethumbhole = True

        # Convert int 123.5 to 1235000 to avoid decimal places. 4 decimal places used
        self.length = int(float(self.length) * Design.FACTOR)
        self.width = int(float(self.width) * Design.FACTOR)
        self.height = int(float(self.height) * Design.FACTOR)
        self.thickness = int(float(self.thickness) * Design.FACTOR)
        self.funnel_bottom = int(float(self.funnel_bottom) * Design.FACTOR)
        self.funnel_top = int(float(self.funnel_top) * Design.FACTOR)
        self.neckheight = int(float(self.neckheight) * Design.FACTOR)
        self.nosewidth = int(float(self.nosewidth) * Design.FACTOR)

        error += self.__check_length(self.length)
        error += self.__check_width(self.width)
        error += self.__check_height(self.height)
        error += self.__check_thickness(self.height)

        if not error:
            print(error)

    @staticmethod
    def __check_length(value):
        return CardBox.__check_value('Length', value)

    @staticmethod
    def __check_width(value):
        return CardBox.__check_value('Width', value)

    @staticmethod
    def __check_height(value):
        return CardBox.__check_value('Height', value)

    @staticmethod
    def __check_thickness(value):
        return CardBox.__check_value('Thickness', value)

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
        parser.add_argument('-s', type=float, help="Thickness")

        group = parser.add_mutually_exclusive_group()
        group.add_argument('-d', action="store_true", help="Single Thumbhole")
        group.add_argument('-D', action="store_true", help="Double Thumbhole")
        parser.add_argument('-b', action="store_true", help="Funnel on both sides")

        parser.add_argument('-f', type=float, help="Funnel Bottom Width")
        parser.add_argument('-F', type=str, help="Funnel Bottom width")
        parser.add_argument('-n', type=int, help="Funnel Neck Height")
        parser.add_argument('-u', type=int, help="Nose width")
        parser.add_argument('-t', type=int, help="Drawing Title")
        parser.add_argument('-x', action="store_true", help="separated Design")
        parser.add_argument('-o', type=str, help="output filename")

        print(parser.parse_args())

        return parser.parse_args()

    def create(self, separated=False):
        self.__init_design()

        self.foo["FILENAME"] = self.outfile
        self.foo["$TITLE$"] = self.title
        self.foo["$FILENAME$"] = self.outfile
        self.foo["$LABEL_X$"] = Design.convert_coord(self.left_x)

        ycoord = self.bottom_y + Design.Y_LINE_SEPARATION

        # self.make_slots([0, 0])

        if not self.separated:
            base_cut = Design.create_xml_cutlines(self.corners, self.cutlines)

            # if self.thumbholeradius:
            #     base_cut = Design.create_xml_cutlines(self.corners, self.cutlines_with_thumbhole)

            self.foo["TEMPLATE"] = self.__DEFAULT_TEMPLATE
            self.foo["$BASE-CUT$"] = base_cut

        else:
            # TEST FOR SEPARATION
            separation = self.__DEFAULT_SEPARATION + self.thickness

            y1 = 0
            self.foo["TEMPLATE"] = self.__DEFAULT_TEMPLATE_SEPARATED

            # TOP CUT
            self.foo[
                '$TRANSLATE_TOP$'] = f"{Design.convert_coord(self.corners[0][0] - self.corners[10][0])}, 0"
            top_cut = Design.create_xml_cutlines(self.corners, self.cutlines_top)
            self.foo["$TOP-CUT$"] = top_cut

            # CENTER CUT
            self.foo[
                '$TRANSLATE_CENTER$'] = f"{Design.convert_coord(self.corners[0][0] - self.corners[13][0])}, " \
                                        + f"{Design.convert_coord(self.thickness + separation)}"

            center_cut = Design.create_xml_cutlines(self.corners, self.cutlines_center)
            self.foo["$CENTER-CUT$"] = center_cut

            # Bottom Cut
            self.foo[
                '$TRANSLATE_BOTTOM$'] = f"{Design.convert_coord(self.corners[0][0] - self.corners[18][0])}, " \
                                        + f"{Design.convert_coord(2 * (self.thickness + separation))}"
            bottom_cut = Design.create_xml_cutlines(self.corners, self.cutlines_bottom)
            self.foo["$BOTTOM-CUT$"] = bottom_cut

            # LEFT CUT
            self.foo[
                '$TRANSLATE_LEFT$'] = f"{Design.convert_coord(self.length + self.thickness + separation)}, " \
                                      + f"-{Design.convert_coord(self.height)}"
            left_cut = Design.create_xml_cutlines(self.corners, self.cutlines_left)
            self.foo["$LEFT-CUT$"] = left_cut

            # RIGHT CUT
            self.foo[
                '$TRANSLATE_RIGHT$'] = f"-{Design.convert_coord(self.height - self.thickness - separation)}, " \
                                       + f" {Design.convert_coord(-self.height + self.width + self.thickness + separation)}"
            # + f" {Design.convert_coord(self.thickness + separation)}"
            right_cut = Design.create_xml_cutlines(self.corners, self.cutlines_right)
            self.foo["$RIGHT-CUT$"] = right_cut

            ycoord += 2 * Design.Y_LINE_SEPARATION

        self.foo["$LABEL_TITLE_Y$"] = Design.convert_coord(ycoord)

        ycoord += Design.Y_LINE_SEPARATION
        self.foo["$LABEL_FILENAME_Y$"] = Design.convert_coord(ycoord)

        ycoord += Design.Y_LINE_SEPARATION
        self.foo["$LABEL_OVERALL_WIDTH_Y$"] = Design.convert_coord(ycoord)
        self.foo["$LABEL_OVERALL_WIDTH$"] = str(round((self.right_x - self.left_x) / Design.FACTOR, 2))

        ycoord += Design.Y_LINE_SEPARATION
        self.foo["$LABEL_OVERALL_HEIGHT_Y$"] = Design.convert_coord(ycoord)
        self.foo["$LABEL_OVERALL_HEIGHT$"] = str(round((self.bottom_y - self.top_y) / Design.FACTOR, 2))

        # ycoord += Design.Y_LINE_SEPARATION
        # self.foo["$LABEL_FLAP_WIDTH_Y$"] = Design.convert_coord(ycoord)

        ycoord += Design.Y_LINE_SEPARATION
        self.foo["$ARGS_STRING_Y$"] = Design.convert_coord(ycoord)
        self.foo["$ARGS_STRING$"] = self.args_string

        ycoord += round(ycoord + Design.Y_LINE_SEPARATION)
        self.foo["$VIEWPORT$"] = f"{Design.convert_coord(round(self.right_x + 2 * Design.FACTOR))}," \
                                 f" {Design.convert_coord(ycoord)}"

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
        #            a b   c      d    e      f         g                    h          i     j    k      m   n o
        #
        # p                       10--------------------------------------------------------------52
        #                         |                                                                |
        #                         |                                                                |
        # q                       11--20                                                      44--53
        #                              |                                                      |
        #                              |                                                      |
        # r                6------12--21----28          32------------------36          40----45--54-----62
        #                  |      |          |          |thickness           |          |          |      |
        #                  |      |          |          |                    |          |          |      |
        # s          0-----7      |          29--------33                    37--------41          |      63---68
        #            |            |           slot_width                                           |            |
        #            |            |                                                                |            |
        # t          1            |                                                                |            69
        # u          \            13--22                                                      46--55            /
        #             \                |  nosewidth                                           |                /
        # v            4----------14--23                                                      47---56--------66     w
        #        w     neckheight |                                                                |                i
        #        i                |                                                                |                d
        #        d funnel         |  funnelbottomwidth                                             |                d
        #        t top width      |                                                                |                t
        #        h                |                                                                |                h
        # w            5----------15--24                                                      48---57--------67
        #             /                |  nosewidth                                           |                \
        # x          /            16--25                                                      49--58            \
        # y          2            |                                                                |            70
        #            |            |                                                                |            |
        #            |            |                                                                |            |
        # z          3-----8      |          30--------34                    38--------42          |      64---71
        #                  |      |          |          |                    |          |          |      |
        #                  |      |          |          |                    |          |          |      |
        #  aa              9------17--26----31          35------------------39          43----50---59----65
        #                              |                                                      |
        #                              |                                                      |
        #  ab                     18--27                                                      51--60
        #                         |                                                                |
        #                         |                          length                                |
        #  ac                     19--------------------------------------------------------------61

        #            a b   c      d    e      f         g                    h          i     j    k      m   n o
        #                ba   bb       bc                                                     bd       be   bf
        # p                       10--------------------------------------------------------------52
        #                         |                                                                |
        #                         |                                                                |
        #                         |                                                                |
        #    ca                   82--86                                                      90--94
        #                              |                                                      |
        #                              |                                                      |
        #    cb                   83--87                                                      91--95
        #                         |                                                                |
        #    cc          74--78   |                                                                |   98--A2
        #                |    |   |                                                                |   |    |
        # r          72-75    79--12--21----28          32------------------36          40----45--54--99    A3--A6
        #            |            |          |          |thickness           |          |          |            |
        #            |            |          |          |                    |          |          |            |
        # s          0            |          29--------33                    37--------41          |           68
        #            |            |           slot_width                                           |            |
        #            |            |                                                                |            |
        # t          1            |                                                                |            69
        # u          \            13--22                                                      46--55            /
        #             \                |  nosewidth                                           |                /
        # v            4----------14--23                                                      47---56--------66     w
        #        w     neckheight |                                                                |                i
        #        i                |                                                                |                d
        #        d funnel         |  funnelbottomwidth                                             |                d
        #        t top width      |                                                                |                t
        #        h                |                                                                |                h
        # w            5----------15--24                                                      48---57--------67
        #             /                |  nosewidth                                           |                \
        # x          /            16--25                                                      49--58            \
        # y          2            |                                                                |            70
        #            |            |                                                                |            |
        #            |            |                                                                |            |
        # z          3            |          30--------34                    38--------42          |           71
        #            |            |          |          |                    |          |          |            |
        #            |            |          |          |                    |          |          |            |
        #  aa        73-76    80--17--26----31          35------------------39          43----50---59-A0    A4-A7
        #                |    |   |                                                                |   |    |
        #     cd         77--81   |                                                                |   A1--A5
        #                         |                                                                |
        #     ce                  84--88                                                      92--96
        #                              |                                                      |
        #                              |                                                      |
        #     cf                  85--89                                                      93--97
        #                         |                                                                |
        #                         |                          length                                |
        #                         |                          length                                |
        #  ac                     19--------------------------------------------------------------61

        length = self.length
        height = self.height
        width = self.width
        thickness = self.thickness

        slot_width = self.__DEFAULT_SLOT_WIDTH
        side_gap = self.__DEFAULT_SIDE_GAP
        neckheight = self.neckheight
        funneltopwidth = self.funnel_top
        funnelbottomwidth = self.funnel_bottom
        nosewidth = self.nosewidth

        # noinspection DuplicatedCode
        # X - Points
        a = self.__X_OFFSET
        b = a + height - neckheight
        c = a + int(height / 2)
        d = a + height
        e = d + thickness
        f = d + side_gap
        g = f + slot_width
        k = d + length
        j = k - thickness
        i = k - side_gap
        h = i - slot_width
        m = k + int(height / 2)
        o = k + height
        n = k + neckheight
        ba = a + int(height / 2 - slot_width / 2)
        bb = a + int(height / 2 + slot_width / 2)
        bc = d + thickness
        bd = k - thickness
        be = k + int(height / 2 - slot_width / 2)
        bf = k + int(height / 2 + slot_width / 2)

        # noinspection DuplicatedCode
        # Y - Points
        p = self.__Y_OFFSET
        q = p + int(height / 2)
        r = p + height
        s = r + thickness
        t = s + int(width / 2 - funneltopwidth / 2)
        v = s + int(width / 2 - funnelbottomwidth / 2)
        u = v - nosewidth
        w = r + int(width / 2 + funnelbottomwidth / 2)
        x = w + nosewidth
        z = s + width
        y = z - int(width / 2 - funneltopwidth / 2)
        aa = z + thickness
        ab = aa + int(height / 2)
        ac = aa + height

        ca = p + int(height / 2 - slot_width / 2)
        cb = p + int(height / 2 + slot_width / 2)
        cc = r - thickness
        cd = aa + thickness
        ce = aa + int(height / 2 - slot_width / 2)
        cf = aa + int(height / 2 + slot_width / 2)

        self.corners = [[a, s], [a, t], [a, y], [a, z], [b, v], [b, w], [c, r], [c, s], [c, z],
                        [c, aa], [d, p], [d, q], [d, r], [d, u], [d, v], [d, w], [d, x], [d, aa],
                        [d, ab], [d, ac], [e, q], [e, r], [e, u], [e, v], [e, w], [e, x], [e, aa],
                        [e, ab], [f, r], [f, s], [f, z], [f, aa], [g, r], [g, s], [g, z], [g, aa],
                        [h, r], [h, s], [h, z], [h, aa], [i, r], [i, s], [i, z], [i, aa], [j, q],
                        [j, r], [j, u], [j, v], [j, w], [j, x], [j, aa], [j, ab], [k, p], [k, q],
                        [k, r], [k, u], [k, v], [k, w], [k, x], [k, aa], [k, ab], [k, ac], [m, r],
                        [m, s], [m, z], [m, aa], [n, v], [n, w], [o, s], [o, t], [o, y], [o, z],
                        [a, r], [a, aa], [ba, cc], [ba, r], [ba, aa], [ba, cd], [bb, cc], [bb, r], [bb, aa],
                        [bb, cd], [d, ca], [d, cb], [d, ce], [d, cf], [bc, ca], [bc, cb], [bc, ce], [bc, cf],
                        [bd, ca], [bd, cb], [bd, ce], [bd, cf], [k, ca], [k, cb], [k, ce], [k, cf], [be, cc],
                        [be, r], [be, aa], [be, cd], [bf, cc], [bf, r], [bf, aa], [bf, cd], [o, r], [o, aa]
                        ]

        self.inner_dimensions = [Design.to_numeral(self.corners[46][0] - self.corners[22][0]),
                                 Design.to_numeral(self.corners[30][1] - self.corners[29][1]),
                                 Design.to_numeral(self.corners[14][0] - self.corners[0][0])]

        self.outer_dimensions = [Design.to_numeral(self.corners[54][0] - self.corners[12][0]),
                                 Design.to_numeral(self.corners[17][1] - self.corners[12][1]),
                                 Design.to_numeral(self.corners[15][0] - self.corners[3][0])]

        if height <= self.__SMALL_HEIGHT:
            self.cutlines = [
                # left upper
                [Design.LINE, [6, 7, 0, 1, 4, 23, 22, 13, 12]],
                # left lower
                [Design.LINE, [9, 8, 3, 2, 5, 24, 25, 16, 17]],
                # middle upper
                [Design.LINE, [6, 28, 29, 33, 32, 36, 37, 41, 40, 62]],
                # middle lower
                [Design.LINE, [9, 31, 30, 34, 35, 39, 38, 42, 43, 65]],
                # bottom
                [Design.LINE, [26, 27, 18, 19, 61, 60, 51, 50]],
                # top
                [Design.LINE, [21, 20, 11, 10, 52, 53, 44, 45]],
            ]

            if self.singlefunnel:
                # right single wall top cutline
                self.cutlines.append([Design.LINE, [62, 63, 68, 71, 64, 65]])
                # right single wall upper cutline
                self.cutlines.append([Design.LINE, [54, 55, 46, 47, 56]])
                # right single wall lower cutline
                self.cutlines.append([Design.LINE, [59, 58, 49, 48, 57]])
            else:
                # right upper
                self.cutlines.append([Design.LINE, [54, 62, 63, 68, 69, 66, 47, 46, 55, 54]])
                # right lower
                self.cutlines.append([Design.LINE, [59, 65, 64, 71, 70, 67, 48, 49, 58, 59]])


        else:
            # Height is greater than 20
            self.cutlines = [
                # left upper
                [Design.LINE, [12, 79, 78, 74, 75, 72, 1, 4, 23, 22, 13, 83]],
                # left lower
                [Design.LINE, [84, 16, 25, 24, 5, 2, 73, 76, 77, 81, 80, 17]],
                # middle upper
                [Design.LINE, [79, 28, 29, 33, 32, 36, 37, 41, 40, 99]],
                # middle lower
                [Design.LINE, [80, 31, 30, 34, 35, 39, 38, 42, 43, 100]],
                # top
                [Design.LINE, [83, 87, 86, 82, 10, 52, 94, 90, 91, 95]],
                # bottom
                [Design.LINE, [84, 88, 89, 85, 19, 61, 97, 93, 92, 96]],
            ]

            if self.singlefunnel:
                # right single wall top
                self.cutlines.append([Design.LINE, [99, 98, 102, 103, 106, 107, 104, 105, 101, 100]])
                # right single wall upper cutline
                self.cutlines.append([Design.LINE, [95, 55, 46, 47, 56]])
                # right single wall lower cutline
                self.cutlines.append([Design.LINE, [96, 58, 49, 48, 57]])
            else:
                self.cutlines.append([Design.LINE, [54, 99, 98, 102, 103, 106, 69, 66, 47, 46, 55, 95]])
                self.cutlines.append([Design.LINE, [59, 100, 101, 105, 104, 107, 70, 67, 48, 49, 58, 96]])

        if self.thumbhole:
            self.cutlines.append([Design.HALFCIRCLE, [14, 15, Design.VERTICAL]])
            if self.singlethumbhole:
                self.cutlines.append([Design.LINE, [56, 57]])
            else:
                self.cutlines.append([Design.HALFCIRCLE, [57, 56, Design.VERTICAL]])
#                self.cutlines.append([Design.LINE, [62, 63, 68, 69, 66, 47, 46, 55, 54]])
#                self.cutlines.append([Design.LINE, [65, 64, 71, 70, 67, 48, 49, 58, 59]])
        else:
            self.cutlines.append([Design.LINE, [14, 15]])
            self.cutlines.append([Design.LINE, [56, 57]])

        self.fullright = [
            [Design.LINE, [57, 48, 49, 58, 59, 100, 101, 105, 104, 107, 106, 103, 102, 98, 99, 54, 55, 46, 47, 56]]]

        self.cutlines_top = [
            [Design.LINE, [10, 11, 20, 21, 28, 29, 33, 32, 36, 37, 41, 40, 45, 44, 53, 52, 10]]]
        self.cutlines_center = [[Design.LINE,
                                 [12, 13, 22, 23, 14, 15, 24, 25, 16, 17, 31, 30, 34, 35, 39, 38, 42, 43, 59, 58, 49,
                                  48, 57, 56, 47, 46, 55, 54, 40, 41, 37, 36, 32, 33, 29, 28, 12]]]
        self.cutlines_bottom = [[Design.LINE, [26, 27, 18, 19, 61, 60, 51, 50, 43, 42, 383, 9, 35, 34, 30, 31, 26]]]
        self.cutlines_left_top = [[Design.LINE, [12, 6, 7, 0, 1, 4, 23, 22, 13, 12]]]
        self.cutlines_left_bottom = [[Design.LINE, [17, 16, 25, 24, 5, 2, 3, 8, 9, 17]]]
        self.cutlines_right_top = [[Design.LINE, [54, 62, 63, 68, 69, 66, 47, 46, 55, 54]]]
        self.cutlines_right_bottom = [[Design.LINE, [59, 65, 64, 71, 70, 67, 48, 49, 58, 59]]]

        # detect boundaries of drawing

        self.left_x, self.right_x, self.top_y, self.bottom_y = Design.get_bounds(self.corners)

    def __make_thumbhole(self, start, end, orientation):
        # startpoint, endpoint, orientation of the circle
        pass
