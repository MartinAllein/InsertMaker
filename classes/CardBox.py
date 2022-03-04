import os
import sys
import argparse
import configparser
from classes.Design import Design
from pathlib import Path

from datetime import datetime


class CardBox(Design):
    __DEFAULT_FILENAME = "CardBox"
    __DEFAULT_TEMPLATE = "templates/CardBox.svg"
    __DEFAULT_TEMPLATE_SEPARATED = "templates/ItemBoxSeparated.svg"

    __DEFAULT_X_OFFSET = Design.X_OFFSET
    __DEFAULT_Y_OFFSET = Design.Y_OFFSET

    __DEFAULT_SLOT_WIDTH = 10
    __DEFAULT_CORNER_GAP = 10
    __DEFAULT_FUNNEL_TOP_WIDTH = 20
    __DEFAULT_FUNNEL_BOTTOM_WIDTH = 10
    __DEFAULT_FUNNEL_NECK_HEIGHT = 10
    __DEFAULT_THICKNESS = 1.5
    __DEFAULT_VERTICAL_SEPARATION = 3
    __DEFAULT_CENTER_NOSE_WIDTH = 5
    __DEFAULT_BOTTOM_HOLE_RADIUS = 10
    __DEFAULT_ENFORCE_SMALL_DESIGN = False
    __DEFAULT_ENFORCE_LARGE_DESIGN = True

    __DEFAULT_SMALL_HEIGHT = 20

    def __init__(self):
        self.__init_variables()

        # Parse
        self.args = self.parse_arguments()

        error = ""

        if self.args.v:
            self.verbose = True

        if self.args.c:
            # config file was chosen
            if not self.args.C:
                print("No section of config file\n-c <config-file> -C <section of config file>")
                sys.exit()
            self.__config_from_file(self.args.c, self.args.C)
        else:
            # CLI was chosen
            self.__config_from_cli()

        temp_name = f"{CardBox.__DEFAULT_FILENAME}-L{self.length}-W{self.width}-H{self.height}-" \
                    f"S{self.thickness}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        if not self.title:
            self.title = temp_name

        if not self.outfile:
            self.outfile = temp_name

        # Set extension of outfile to .svg
        if self.outfile[-4:] != '.svg':
            self.outfile += '.svg'

        # Convert int 123.5 to 1235000 to avoid decimal places. 4 decimal places used
        # self.length = int(float(self.length) * Design.FACTOR)
        # self.width = int(float(self.width) * Design.FACTOR)
        # self.height = int(float(self.height) * Design.FACTOR)
        # self.thickness = int(float(self.thickness) * Design.FACTOR)
        # self.funnel_bottom = int(float(self.funnel_bottom) * Design.FACTOR)
        # self.funnel_top = int(float(self.funnel_top) * Design.FACTOR)
        # self.neckheight = int(float(self.neckheight) * Design.FACTOR)
        # self.nosewidth = int(float(self.nosewidth) * Design.FACTOR)

        # error += self.__check_length(self.length)
        # error += self.__check_width(self.width)
        # error += self.__check_height(self.height)
        # error += self.__check_thickness(self.height)

        # if not error:
        #    print(error)

    def __config_from_cli(self):

        self.length = self.args.l
        self.width = self.args.w
        self.height = self.args.h

        if self.args.s:
            self.thickness = self.args.s

        self.separated = self.args.x

        # Outfile
        if self.args.o:
            self.outfile = self.args.o

        # Title
        if self.args.t:
            self.title = self.args.t

        # Top funnel width
        if self.args.F:
            self.funnel_top_width = self.args.F

        # Bottom funnel width
        if self.args.f:
            self.funnel_bottom_width = self.args.f

        # funnel neck height
        if self.args.n:
            self.funnel_neck_height = self.args.n

        # width of nose at bottom of funnel
        if self.args.u:
            self.center_nose_width = self.args.u

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

        if self.args.e:
            self.enforce_small_design = True

        if self.args.E:
            self.enforce_large_design = True

    def __config_from_file(self, filename: str, section: str):
        defaults = {'x_offset': self.__DEFAULT_X_OFFSET, 'y_offset': self.__DEFAULT_Y_OFFSET,
                    'vertical_separation': self.__DEFAULT_VERTICAL_SEPARATION,
                    'slot_width': self.__DEFAULT_SLOT_WIDTH, 'corner_gap': self.__DEFAULT_CORNER_GAP,
                    'funnel_top_width': self.__DEFAULT_FUNNEL_TOP_WIDTH,
                    'funnel_bottom_width': self.__DEFAULT_FUNNEL_BOTTOM_WIDTH,
                    'funnel_neck_height': self.__DEFAULT_FUNNEL_NECK_HEIGHT, 'thickness': self.__DEFAULT_THICKNESS,
                    'center_nose_width': self.__DEFAULT_CENTER_NOSE_WIDTH,
                    'enforce_small_design': self.__DEFAULT_ENFORCE_SMALL_DESIGN,
                    'enforce_large_design': self.__DEFAULT_ENFORCE_LARGE_DESIGN}

        config_file = 'config/' + filename + ".config"
        # Read default values from the config file
        if os.path.isfile(config_file):
            # read entries from the configuration file
            config = configparser.ConfigParser(defaults=defaults)
            config.read(config_file)
            print("-------------")
            print(config.sections())
            print("-------------")

            if not config.has_section(section):
                print("Section " + section + " in config file config/" + filename + ".config not found")
                sys.exit()

            self.x_offset = int(config[section]['x_offset'])
            self.y_offset = int(config[section]['y_offset'])
            self.vertical_separation = int(config[section]['vertical_separation'])
            self.slot_width = int(config[section]['slot_width'])
            self.corner_gap = int(config[section]['corner_gap'])
            self.funnel_top_width = int(config[section]['funnel_top_width'])
            self.funnel_bottom_width = int(config[section]['funnel_bottom_width'])
            self.funnel_neck_height = int(config[section]['funnel_neck_height'])
            self.thickness = float(config[section]['thickness'])
            self.center_nose_width = int(config[section]['center_nose_width'])
            self.enforce_small_design = bool(config[section]['enforce_small_design'])
            self.enforce_large_design = bool(config[section]['enforce_large_design'])
        else:
            print("Config file config/" + filename + ".config not found")
            sys.exit()

    def __init_variables(self):
        # initialization of variables

        # Arguments as String
        self.args_string = ' '.join(sys.argv[1:])

        # command line parameter variables
        self.length = 0.0
        self.width = 0.0
        self.height = 0.0
        self.thickness = self.__DEFAULT_THICKNESS
        self.outfile = ""
        self.title = ""
        self.outfile = ''
        self.separated = False
        self.thumbhole = False
        self.singlethumbhole = True
        self.singlefunnel = False
        self.enforce_small_design = False
        self.enforce_large_design = False

        self.template = {}

        # geometry variables
        self.corners = []
        self.cutlines = []
        self.left_x = 0
        self.right_x = 0
        self.top_y = 0
        self.bottom_y = 0
        self.inner_dimensions = []
        self.outer_dimensions = []

        self.x_offset = Design.X_OFFSET
        self.y_offset = Design.Y_OFFSET
        self.slot_width = CardBox.__DEFAULT_SLOT_WIDTH
        self.funnel_top_width = CardBox.__DEFAULT_FUNNEL_TOP_WIDTH
        self.funnel_bottom_width = CardBox.__DEFAULT_FUNNEL_BOTTOM_WIDTH
        self.funnel_neck_height = CardBox.__DEFAULT_FUNNEL_NECK_HEIGHT
        self.center_nose_width = CardBox.__DEFAULT_CENTER_NOSE_WIDTH
        self.corner_gap = CardBox.__DEFAULT_CORNER_GAP
        self.bottomhole_radius = CardBox.__DEFAULT_BOTTOM_HOLE_RADIUS
        self.small_height = CardBox.__DEFAULT_SMALL_HEIGHT

        self.verbose = False

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

        group_thumbhole = parser.add_mutually_exclusive_group()
        group_thumbhole.add_argument('-d', action="store_true", help="Single Thumbhole")
        group_thumbhole.add_argument('-D', action="store_true", help="Double Thumbhole")
        parser.add_argument('-b', action="store_true", help="Funnel on both sides")

        parser.add_argument('-f', type=float, help="Funnel Bottom Width")
        parser.add_argument('-F', type=str, help="Funnel Bottom width")
        parser.add_argument('-n', type=int, help="Funnel Neck Height")
        parser.add_argument('-u', type=int, help="Nose width")
        parser.add_argument('-t', type=int, help="Drawing Title")
        parser.add_argument('-x', action="store_true", help="separated Design")
        parser.add_argument('-o', type=str, help="output filename")

        group_enforce = parser.add_mutually_exclusive_group()
        group_enforce.add_argument('-e', action="store_true", help="Enforce small design")
        group_enforce.add_argument('-E', action="store_true", help="Enforce large design")

        parser.add_argument('-v', action="store_true", help="verbose output")


        # The config file is mutually exclusive to all other command line parameters
        # and has precedence
        parser.add_argument('-c', type=str, required=True, help="Configuration File")
        parser.add_argument('-C', type=str, required=True, help="Config file section")

        return parser.parse_args()

    def create(self, separated=False):
        self.__init_design()

        self.template["FILENAME"] = self.outfile
        self.template["$TITLE$"] = self.title
        self.template["$FILENAME$"] = self.outfile
        self.template["$LABEL_X$"] = Design.thoudpi_to_dpi(self.left_x)

        ycoord = self.bottom_y + Design.Y_LINE_SEPARATION

        # self.make_slots([0, 0])

        if not self.separated:
            base_cut = Design.draw_lines(self.corners, self.cutlines)

            # if self.thumbholeradius:
            #     base_cut = Design.create_xml_cutlines(self.corners, self.cutlines_with_thumbhole)

            self.template["TEMPLATE"] = self.__DEFAULT_TEMPLATE
            self.template["$BASE-CUT$"] = base_cut

        else:
            # TEST FOR SEPARATION
            separation = self.vertical_separation + self.thickness

            y1 = 0
            self.template["TEMPLATE"] = self.__DEFAULT_TEMPLATE_SEPARATED

            # TOP CUT
            self.template[
                '$TRANSLATE_TOP$'] = f"{Design.thoudpi_to_dpi(self.corners[0][0] - self.corners[10][0])}, 0"
            top_cut = Design.draw_lines(self.corners, self.cutlines_top)
            self.template["$TOP-CUT$"] = top_cut

            # CENTER CUT
            self.template[
                '$TRANSLATE_CENTER$'] = f"{Design.thoudpi_to_dpi(self.corners[0][0] - self.corners[13][0])}, " \
                                        + f"{Design.thoudpi_to_dpi(self.thickness + separation)}"

            center_cut = Design.draw_lines(self.corners, self.cutlines_center)
            self.template["$CENTER-CUT$"] = center_cut

            # Bottom Cut
            self.template[
                '$TRANSLATE_BOTTOM$'] = f"{Design.thoudpi_to_dpi(self.corners[0][0] - self.corners[18][0])}, " \
                                        + f"{Design.thoudpi_to_dpi(2 * (self.thickness + separation))}"
            bottom_cut = Design.draw_lines(self.corners, self.cutlines_bottom)
            self.template["$BOTTOM-CUT$"] = bottom_cut

            # LEFT CUT
            self.template[
                '$TRANSLATE_LEFT$'] = f"{Design.thoudpi_to_dpi(self.length + self.thickness + separation)}, " \
                                      + f"-{Design.thoudpi_to_dpi(self.height)}"
            left_cut = Design.draw_lines(self.corners, self.cutlines_left)
            self.template["$LEFT-CUT$"] = left_cut

            # RIGHT CUT
            self.template[
                '$TRANSLATE_RIGHT$'] = f"-{Design.thoudpi_to_dpi(self.height - self.thickness - separation)}, " \
                                       + f" {Design.thoudpi_to_dpi(-self.height + self.width + self.thickness + separation)}"
            # + f" {Design.convert_coord(self.thickness + separation)}"
            right_cut = Design.draw_lines(self.corners, self.cutlines_right)
            self.template["$RIGHT-CUT$"] = right_cut

            ycoord += 2 * Design.Y_LINE_SEPARATION

        self.template["$LABEL_TITLE_Y$"] = Design.thoudpi_to_dpi(ycoord)

        ycoord += Design.Y_LINE_SEPARATION
        self.template["$LABEL_FILENAME_Y$"] = Design.thoudpi_to_dpi(ycoord)

        ycoord += Design.Y_LINE_SEPARATION
        self.template["$LABEL_OVERALL_WIDTH_Y$"] = Design.thoudpi_to_dpi(ycoord)
        self.template["$LABEL_OVERALL_WIDTH$"] = str(round((self.right_x - self.left_x) / Design.FACTOR, 2))

        ycoord += Design.Y_LINE_SEPARATION
        self.template["$LABEL_OVERALL_HEIGHT_Y$"] = Design.thoudpi_to_dpi(ycoord)
        self.template["$LABEL_OVERALL_HEIGHT$"] = round((self.bottom_y - self.top_y) / Design.FACTOR, 2)

        ycoord += Design.Y_LINE_SEPARATION
        self.template["$ARGS_STRING_Y$"] = Design.thoudpi_to_dpi(ycoord)
        self.template["$ARGS_STRING$"] = self.args_string

        ycoord += Design.Y_LINE_SEPARATION
        self.template["$VIEWPORT$"] = f"{Design.thoudpi_to_dpi(round(self.right_x + 2 * Design.FACTOR))}," \
                                      f" {Design.thoudpi_to_dpi(ycoord)}"

        Design.write_to_file(self.template)

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
        #                ba   bb                                                                       be   bf
        # p                       10--------------------------------------------------------------52
        #                         |                                                                |
        #                         |                                                                |
        #                         |                                                                |
        #    ca                   80--86                                                      90--94
        #                              |                                                      |
        #                              |                                                      |
        #    cb                   81--87                                                      91--95
        #                         |                                                                |
        #                         |                                                                |
        #                         |                                                                |
        # r              72---76  12--21----28          32------------------36          40----45--54  A0----A4
        #                |     |  |          |          |thickness           |          |          |   |    |
        #                |     |  |          |          |                    |          |          |   |    |
        # s          0--73    77-82          29--------33                    37--------41          96-A1    A5-68
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
        # z          3--74    78-83          30--------34                    38--------42          97-A2    A6-71
        #                |     |  |          |          |                    |          |          |   |    |
        #                |     |  |          |          |                    |          |          |   |    |
        #  aa            75---79  17--26----31          35------------------39          43----50---59 A3----A7
        #                         |                                                                |
        #                         |                                                                |
        #                         |                                                                |
        #     cc                  84--88                                                      92--98
        #                              |                                                      |
        #                              |                                                      |
        #     cd                  85--89                                                      93--99
        #                         |                                                                |
        #                         |                          length                                |
        #                         |                          length                                |
        #  ac                     19--------------------------------------------------------------61

        print(self.thickness)

        length = self.length
        height = self.height
        width = self.width
        thickness = self.thickness

        slot_width = self.slot_width
        corner_gap = self.corner_gap
        neckheight = self.funnel_neck_height
        funneltopwidth = self.funnel_top_width
        funnelbottomwidth = self.funnel_bottom_width
        nosewidth = self.center_nose_width

        # noinspection DuplicatedCode
        # X - Points
        a = self.x_offset
        b = a + height - neckheight
        c = a + int(height / 2)
        d = a + height
        e = d + thickness
        f = d + corner_gap
        g = f + slot_width
        k = d + length + 2 * thickness
        j = k - thickness
        i = k - corner_gap
        h = i - slot_width
        m = k + int(height / 2)
        o = k + height
        n = k + neckheight

        ba = a + int(height / 2 - slot_width / 2)
        bb = a + int(height / 2 + slot_width / 2)
        bc = k + int(height / 2 - slot_width / 2)
        bd = k + int(height / 2 + slot_width / 2)

        # noinspection DuplicatedCode
        # Y - Points
        p = self.y_offset
        q = p + int(height / 2)
        r = p + height
        s = r + thickness
        t = s + int(width / 2 - funneltopwidth / 2)
        v = s + int(width / 2 - funnelbottomwidth / 2)
        u = v - nosewidth
        w = r + int(width / 2 + funnelbottomwidth / 2)
        x = w + nosewidth
        aa = r + width + 2 * thickness
        z = aa - thickness
        y = z - int(width / 2 - funneltopwidth / 2)
        ab = aa + int(height / 2)
        ac = aa + height

        ca = p + int(height / 2 - slot_width / 2)
        cb = p + int(height / 2 + slot_width / 2)
        cc = aa + int(height / 2 - slot_width / 2)
        cd = aa + int(height / 2 + slot_width / 2)

        print(thickness)

        print(Design.thoudpi_to_mm(p), Design.thoudpi_to_mm(ca), Design.thoudpi_to_mm(cb), Design.thoudpi_to_mm(r),
              Design.thoudpi_to_mm(s), Design.thoudpi_to_mm(z))

        self.corners = [[a, s], [a, t], [a, y], [a, z], [b, v], [b, w], [c, r], [c, s], [c, z],
                        [c, aa], [d, p], [d, q], [d, r], [d, u], [d, v], [d, w], [d, x], [d, aa],
                        [d, ab], [d, ac], [e, q], [e, r], [e, u], [e, v], [e, w], [e, x], [e, aa],
                        [e, ab], [f, r], [f, s], [f, z], [f, aa], [g, r], [g, s], [g, z], [g, aa],
                        [h, r], [h, s], [h, z], [h, aa], [i, r], [i, s], [i, z], [i, aa], [j, q],
                        [j, r], [j, u], [j, v], [j, w], [j, x], [j, aa], [j, ab], [k, p], [k, q],
                        [k, r], [k, u], [k, v], [k, w], [k, x], [k, aa], [k, ab], [k, ac], [m, r],
                        [m, s], [m, z], [m, aa], [n, v], [n, w], [o, s], [o, t], [o, y], [o, z],
                        [ba, r], [ba, s], [ba, z], [ba, aa], [bb, r], [bb, s], [bb, z], [bb, aa], [d, ca],
                        [d, cb], [d, s], [d, z], [d, cc], [d, cd], [e, ca], [e, cb], [e, cc], [e, cd],
                        [j, ca], [j, cb], [j, cc], [j, cd], [k, ca], [k, cb], [k, s], [k, z], [k, cc],
                        [k, cd], [bc, r], [bc, s], [bc, z], [bc, aa], [bd, r], [bd, s], [bd, z], [bd, aa]
                        ]

        #        self.inner_dimensions = [Design.to_numeral(self.corners[46][0] - self.corners[22][0]),
        #                                 Design.to_numeral(self.corners[30][1] - self.corners[29][1]),
        #                                 Design.to_numeral(self.corners[14][0] - self.corners[0][0])]

        #        self.outer_dimensions = [Design.to_numeral(self.corners[54][0] - self.corners[12][0]),
        #                                 Design.to_numeral(self.corners[17][1] - self.corners[12][1]),
        #                                 Design.to_numeral(self.corners[15][0] - self.corners[3][0])]
        self.inner_dimensions = [Design.thoudpi_to_mm(j - e), Design.thoudpi_to_mm(z - s), Design.thoudpi_to_mm(d - a)]
        self.outer_dimensions = [Design.thoudpi_to_mm(k - d), Design.thoudpi_to_mm(aa - r), Design.thoudpi_to_mm(e - a)]

        if height <= self.small_height:
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
                [Design.LINE, [82, 77, 76, 72, 73, 0, 1, 4, 23, 22, 13, 81]],
                # left lower
                [Design.LINE, [83, 78, 79, 75, 74, 3, 2, 5, 24, 25, 16, 84]],
                # middle upper
                [Design.LINE, [12, 28, 29, 33, 32, 36, 37, 41, 40, 54]],
                # middle lower
                [Design.LINE, [17, 31, 30, 34, 35, 39, 38, 42, 43, 59]],
                # top
                [Design.LINE, [81, 87, 86, 80, 10, 52, 94, 90, 91, 95]],
                # bottom
                [Design.LINE, [84, 88, 89, 85, 19, 61, 99, 93, 92, 98]],
                # right top
                [Design.LINE, [96, 101, 100, 104, 105, 68]],
                # right bottom
                [Design.LINE, [97, 102, 103, 107, 106, 71]],
                [Design.LINE, [95, 55, 46, 47]],
                [Design.LINE, [98, 58, 49, 48]],
            ]

            if self.singlefunnel:
                # right single wall top
                self.cutlines.append([Design.LINE, [68, 71]])
                self.cutlines.append([Design.LINE, [47, 56]])
                self.cutlines.append([Design.LINE, [48, 57]])
            else:
                self.cutlines.append([Design.LINE, [68, 69, 66, 47]])
                self.cutlines.append([Design.LINE, [71, 70, 67, 48]])

        if self.thumbhole:
            self.cutlines.append([Design.HALFCIRCLE, [14, 15, Design.VERTICAL]])
            if self.singlethumbhole:
                self.cutlines.append([Design.LINE, [56, 57]])
            else:
                self.cutlines.append([Design.HALFCIRCLE, [57, 56, Design.VERTICAL]])
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

    def __setup(self):
        pass

# convert all mm to thoudpi
# CardBox.x_offset = Design.mm_to_thoudpi(CardBox.x_offset)
# CardBox.y_offset = Design.mm_to_thoudpi(CardBox.y_offset)
# CardBox.vertical_separation = Design.mm_to_thoudpi(CardBox.vertical_separation)
# CardBox.slot_width = Design.mm_to_thoudpi(CardBox.slot_width)
# CardBox.side_gap = Design.mm_to_thoudpi(CardBox.side_gap)
# CardBox.funnel_top_width = Design.mm_to_thoudpi(CardBox.funnel_top_width)
# CardBox.funnel_bottom_width = Design.mm_to_thoudpi(CardBox.funnel_bottom_width)
# CardBox.neck_height = Design.mm_to_thoudpi(CardBox.neck_height)
# CardBox.thickness = Design.mm_to_thoudpi(CardBox.thickness)
# CardBox.nose_width = Design.mm_to_thoudpi(CardBox.nose_width)
# CardBox.bottomhole_radius = Design.mm_to_thoudpi(CardBox.bottomhole_radius)
