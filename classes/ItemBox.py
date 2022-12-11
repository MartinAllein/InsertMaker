import argparse
import configparser
from datetime import datetime
import os
import sys
from classes.Design import Design
from classes.Direction import Direction
from classes.PathStyle import PathStyle

class ItemBox:
    __DEFAULT_FILENAME = "ItemBox"
    __DEFAULT_TEMPLATE = "templates/ItemBox.svg"
    __DEFAULT_TEMPLATE_SEPARATED = "templates/ItemBoxSeparated.svg"

    __DEFAULT_X_OFFSET = Design.x_offset
    __DEFAULT_Y_OFFSET = Design.y_offset

    __DEFAUL_THICKNESS = 1.5

    __DEFAULT_VERTICAL_SEPARATION = 3

    __THUMBHOLE_SMALL_RADIUS = Design.mm_to_thoudpi(2)
    __DEFAULT_THUMBHOLE_RADIUS = 10

    __DEFAULT_SLOT_WIDTH = 10
    __DEFAULT_CORNER_GAP = 10

    __DEFAULT_SMALL_HEIGHT = Design.mm_to_thoudpi(20)

    def __init__(self, arguments=""):
        self.__init_variables()

        # parse vom cli
        self.args = self.parse_arguments(arguments)

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

        temp_name = f"{self.__DEFAULT_FILENAME}-L{self.length}-W{self.width}-H{self.height}-" \
                    f"S{self.thickness}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        if not self.title:
            self.title = temp_name

        if not self.outfile:
            self.outfile = temp_name

        # Set extension of outfile to .svg
        if self.outfile[-4:] != '.svg':
            self.outfile += '.svg'

        if self.verbose:
            self.__print_variables()

        # Convert all measures to thousands dpi
        self.__convert_all_to_thoudpi()

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

        # Project
        if self.args.p:
            self.project = self.args.p

        # Title
        if self.args.t:
            self.title = self.args.t

        # -d Single Thumbhole
        # -D Dual Thumbhole
        if self.args.d:
            self.thumbhole = True
            self.singlethumbhole = True
        elif self.args.D:
            self.thumbhole = True
            self.singlethumbhole = False

        if self.args.e:
            self.enforce_small_design = True

        if self.args.E:
            self.enforce_large_design = True

    def __config_from_file(self, filename: str, section: str):
        defaults = {'x offset': self.__DEFAULT_X_OFFSET,
                    'y offset': self.__DEFAULT_Y_OFFSET,
                    'vertical separation': self.__DEFAULT_VERTICAL_SEPARATION,
                    'slot width': self.__DEFAULT_SLOT_WIDTH, 'corner_gap': self.__DEFAULT_CORNER_GAP,
                    'length': 0,
                    'width': 0,
                    'height': 0,
                    'project name': "",
                    'filename': "",
                    'title': "",
#                    'thumbhole': False,
#                    'thumbhole radius': self.__DEFAULT_THUMBHOLE_RADIUS,
                    }

        config_file = 'config/' + filename + ".config"
        # Read default values from the config file
        if not os.path.isfile(config_file):
            print("Config file config/" + filename + ".config not found")
            sys.exit()

        # read entries from the configuration file
        config = configparser.ConfigParser(defaults=defaults)
        config.read(config_file)

        if not config.has_section(section):
            print("Section " + section + " in config file config/" + filename + ".config not found")
            sys.exit()

        self.project = config[section]['project name'].strip('"')
        self.outfile = config[section]['filename'].strip('"')
        self.title = config[section]['title'].strip('"')
        self.x_offset = int(config[section]['x offset'])
        self.y_offset = int(config[section]['y offset'])
        self.vertical_separation = int(config[section]['vertical separation'])
        self.slot_width = int(config[section]['slot width'])
        self.corner_gap = int(config[section]['corner gap'])
        self.thickness = float(config[section]['thickness'])


        if config.has_option(section, 'thumbhole radius'):
            self.thumbhole = True
            self.singlethumbhole = True
            self.thumbholeradius = float(config[section]['thumbhole radius'])

        if config.has_option(section, 'thumbhole'):
            if config[section]['thumbhole'] == "single":
                self.thumbhole = True
                self.singlethumbhole = True
            elif config[section]['thumbhole'] == 'dual' or config[section]['thumbhole'] == 'double':
                self.thumbhole = True
                self.singlethumbhole = False

        if config.has_option(section, 'enforce design'):
            design = config[section]['enforce design']

            if design == 'small':
                self.enforce_small_design = True
                self.enforce_large_design = False
            elif design == 'large':
                self.enforce_small_design = False
                self.enforce_large_design = True

        self.length = float(config[section]['length'])
        self.width = float(config[section]['width'])
        self.height = float(config[section]['height'])

        self.__print_variables()

    def __init_variables(self):

        self.args_string = ' '.join(sys.argv[1:])

        self.length = 0.0
        self.width = 0.0
        self.height = 0.0
        self.thickness = self.__DEFAUL_THICKNESS
        self.project = ""
        self.outfile = ""
        self.title = ""
        self.outfile = ''
        self.separated = False
        self.thumbhole = False
        self.thumbholeradius = 0.0
        self.singlethumbhole = True
        self.vertical_separation = self.__DEFAULT_VERTICAL_SEPARATION
        self.enforce_small_design = False
        self.enforce_large_design = False

        self.template = {}

        self.corners = []
        self.cutlines = []
        self.left_x = 0
        self.right_x = 0
        self.top_y = 0
        self.bottom_y = 0
        self.inner_dimensions = []
        self.outer_dimensions = []

        self.x_offset = self.__DEFAULT_X_OFFSET
        self.y_offset = self.__DEFAULT_Y_OFFSET

        self.slot_width = self.__DEFAULT_SLOT_WIDTH
        self.corner_gap = self.__DEFAULT_CORNER_GAP
        self.small_height = self.__DEFAULT_SMALL_HEIGHT
        self.thumbholeradius = self.__DEFAULT_THUMBHOLE_RADIUS

        self.verbose = False

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

    def parse_arguments(self, arguments: str):
        parser = argparse.ArgumentParser(add_help=False)

        parser.add_argument('-l', type=float, help="length of the matchbox")
        parser.add_argument('-w', type=float, help="width of the matchbox")
        parser.add_argument('-h', type=float, help="height of the matchbox")
        parser.add_argument('-d', type=float, help="Thumb Hole Radius")
        parser.add_argument('-s', type=float, help="thickness of the material")
        parser.add_argument('-o', type=str, help="output filename")
        parser.add_argument('-t', type=str, help="title of the matchbox")
        parser.add_argument('-v', action="store_true", help="verbose")
        parser.add_argument('-x', action="store_true", help="separated Design")
        parser.add_argument('-c', type=str, help="config File")
        parser.add_argument('-C', type=str, help="config section")
        parser.add_argument('-p', type=str, help="Project Name")
        parser.add_argument('-e', action="store_true", help="Enforce small design")
        parser.add_argument('-E', action="store_true", help="Enforce large design")

        if not arguments:
            return parser.parse_args()

        return parser.parse_args(arguments.split())

    def create(self):
        self.__init_design()

        self.template["FILENAME"] = self.outfile
        self.template["$PROJECT$"] = self.project
        self.template["$TITLE$"] = self.title
        self.template["$FILENAME$"] = self.outfile
        self.template["$LABEL_X$"] = Design.thoudpi_to_dpi(self.left_x)

        ycoord = self.bottom_y + self.vertical_separation

        # self.make_slots([0, 0])

        base_cut = Design.draw_lines(self.corners, self.cutlines)

        self.template["TEMPLATE"] = self.__DEFAULT_TEMPLATE
        self.template["$BASE-CUT$"] = base_cut

        ycoord += 2 * self.vertical_separation
        self.template["$LABEL_PROJECT_Y$"] = Design.thoudpi_to_dpi(ycoord)

        ycoord += self.vertical_separation
        self.template["$LABEL_TITLE_Y$"] = Design.thoudpi_to_dpi(ycoord)

        ycoord += self.vertical_separation
        self.template["$LABEL_FILENAME_Y$"] = Design.thoudpi_to_dpi(ycoord)

        ycoord += self.vertical_separation
        self.template["$LABEL_OVERALL_WIDTH_Y$"] = Design.thoudpi_to_dpi(ycoord)
        self.template["$LABEL_OVERALL_WIDTH$"] = str(round((self.right_x - self.left_x) / Design.FACTOR, 2))

        ycoord += self.vertical_separation
        self.template["$LABEL_OVERALL_HEIGHT_Y$"] = Design.thoudpi_to_dpi(ycoord)
        self.template["$LABEL_OVERALL_HEIGHT$"] = round((self.bottom_y - self.top_y) / Design.FACTOR, 2)

        ycoord += self.vertical_separation
        self.template["$ARGS_STRING_Y$"] = Design.thoudpi_to_dpi(ycoord)
        self.template["$ARGS_STRING$"] = self.args_string

        ycoord += self.vertical_separation
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

        #          a    b    c    d    e     f          g                    h          i     j    k    m    n    o
        #  q                      10--------------------------------------------------------------50
        #                         |                                                                |
        #                         |                                                                |
        #                         |                                                                |
        #                         |                                                                |
        #                         |                                                                |
        #                         |                                                                |
        #  r                      11--22                   length                             44--51
        #                              |                                                      |
        #                              |                                                      |
        #                              |                                                      |
        #  s                      12--23                                                      45--52
        #                         | side-gap                                              side-gap |
        #                         |                                                                |
        #                         |                                                                |
        #                         |                                                                |
        #                         |                                                                |
        #                         |                                                                |
        #                         |                                                                |
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

        slot_width = self.slot_width
        corner_gap = self.corner_gap
        print(f"+++++++{self.thumbholeradius} ---- {Design.thoudpi_to_mm(self.thumbholeradius)}")
        thumbholeradius = self.thumbholeradius

        # noinspection DuplicatedCode
        # X - Points
        a = int(self.x_offset)
        b = a + int(height / 2) - int(slot_width / 2)
        c = a + int(height / 2) + int(slot_width / 2)
        d = a + height
        # d = self.__X_OFFSET
        e = d + thickness
        f = d + corner_gap
        g = f + slot_width
        j = e + length
        k = j + thickness
        i = k - corner_gap
        h = i - slot_width

        m = k + int(height / 2) - int(slot_width / 2)
        n = k + int(height / 2) + int(slot_width / 2)
        o = k + height

        # noinspection DuplicatedCode
        # Y - Points
        q = int(self.y_offset)
        r = q + int(height / 2) - int(slot_width / 2)
        s = q + int(height / 2) + int(slot_width / 2)
        t = q + height
        u = t + thickness
        v = u + int(width / 2) - int(slot_width / 2)
        w = u + int(width / 2) + int(slot_width / 2)
        x = u + width
        y = x + thickness
        z = y + int(height / 2 - slot_width / 2)
        aa = y + int(height / 2 + slot_width / 2)
        ab = y + height
        ac = q + thickness
        ad = t - thickness
        ae = u + int(width / 2 - thumbholeradius - self.__THUMBHOLE_SMALL_RADIUS)
        af = u + int(width / 2 + thumbholeradius + self.__THUMBHOLE_SMALL_RADIUS)
        # ag = q + int(width / 2 - thumbholeradius - self.__THUMBHOLE_SMALL_RADIUS)
        # ah = q + int(width / 2 + thumbholeradius + self.__THUMBHOLE_SMALL_RADIUS)

        if self.verbose:
            print(f"a: {a} / {Design.thoudpi_to_mm(a)}")
            print(f"b: {b}/ {Design.thoudpi_to_mm(b)}")
            print(f"c: {c}/ {Design.thoudpi_to_mm(c)}")
            print(f"d: {d}/ {Design.thoudpi_to_mm(d)}")
            print(f"e: {e}/ {Design.thoudpi_to_mm(e)}")
            print(f"f: {f}/ {Design.thoudpi_to_mm(f)}")
            print(f"g: {g}/ {Design.thoudpi_to_mm(g)}")
            print(f"h: {h}/ {Design.thoudpi_to_mm(h)}")
            print(f"i: {i}/ {Design.thoudpi_to_mm(i)}")
            print(f"j: {j}/ {Design.thoudpi_to_mm(j)}")
            print(f"k: {k}/ {Design.thoudpi_to_mm(k)}")
            print(f"m: {m}/ {Design.thoudpi_to_mm(m)}")
            print(f"n: {n}/ {Design.thoudpi_to_mm(n)}")
            print(f"o: {o}/ {Design.thoudpi_to_mm(o)}")

            print(f"q: {q}/ {Design.thoudpi_to_mm(q)}")
            print(f"r: {r}/ {Design.thoudpi_to_mm(r)}")
            print(f"s: {s}/ {Design.thoudpi_to_mm(s)}")
            print(f"t: {t}/ {Design.thoudpi_to_mm(t)}")
            print(f"u: {u}/ {Design.thoudpi_to_mm(u)}")
            print(f"v: {v}/ {Design.thoudpi_to_mm(v)}")
            print(f"w: {w}/ {Design.thoudpi_to_mm(w)}")
            print(f"x: {x}/ {Design.thoudpi_to_mm(x)}")
            print(f"y: {y}/ {Design.thoudpi_to_mm(y)}")
            print(f"z: {z}/ {Design.thoudpi_to_mm(z)}")
            print(f"aa: {aa}/ {Design.thoudpi_to_mm(aa)}")
            print(f"ab: {ab}/ {Design.thoudpi_to_mm(ab)}")
            print(f"ac: {ac}/ {Design.thoudpi_to_mm(ac)}")
            print(f"ad: {ad}/ {Design.thoudpi_to_mm(ad)}")
            print(f"ae: {ae}/ {Design.thoudpi_to_mm(ae)}")
            print(f"af: {af}/ {Design.thoudpi_to_mm(af)}")

        self.corners = [[a, u], [a, x], [b, t], [b, u], [b, x], [b, y], [c, t], [c, u], [c, x],
                        [c, y], [d, q], [d, r], [d, s], [d, t], [d, u], [d, v], [d, w], [d, x],
                        [d, y], [d, z], [d, aa], [d, ab], [e, r], [e, s], [e, v], [e, w], [e, z],
                        [e, aa], [f, t], [f, u], [f, x], [f, y], [g, t], [g, u], [g, x], [g, y],
                        [h, t], [h, u], [h, x], [h, y], [i, t], [i, u], [i, x], [i, y], [j, r],
                        [j, s], [j, v], [j, w], [j, z], [j, aa], [k, q], [k, r], [k, s], [k, t],
                        [k, u], [k, v], [k, w], [k, x], [k, y], [k, z], [k, aa], [k, ab], [m, t],
                        [m, u], [m, x], [m, y], [n, t], [n, u], [n, x], [n, y], [o, u], [o, x],
                        [k, ac], [k, ad], [m, q], [m, ac], [m, ad], [n, q], [n, ac], [n, ad],
                        [o, ac], [o, ad], [a, ae], [a, af], [o, ae], [o, af],
                        ]

        self.inner_dimensions = [Design.thoudpi_to_mm(j - e), Design.thoudpi_to_mm(x - u), Design.thoudpi_to_mm(d - a)]
        self.outer_dimensions = [Design.thoudpi_to_mm(k - d), Design.thoudpi_to_mm(y - t), Design.thoudpi_to_mm(e - a)]

        # right with no thumbhole
        right_full = [PathStyle.LINE, [54, 63, 62, 66, 67, 70, 71, 68, 69, 65, 64, 57]]
        left_full = [PathStyle.LINE, [14, 7, 6, 2, 3, 0, 1, 4, 5, 9, 8, 17]]

        self.cutlines = [
            # Top upper, middle left and right, Bottom lower
            [PathStyle.LINE,
             [10, 11, 22, 23, 12, 15, 24, 25, 16, 19, 26, 27, 20, 21, 61, 60, 49, 48, 59, 56, 47, 46,
              55, 52, 45,
              44, 51, 50, 10]],
            # middle upper
            [PathStyle.LINE, [13, 28, 29, 33, 32, 36, 37, 41, 40, 53]],
            # middle lower
            [PathStyle.LINE, [18, 31, 30, 34, 35, 39, 38, 42, 43, 58]],
        ]

        if not self.thumbhole:
            self.cutlines.append(left_full)
            self.cutlines.append(right_full)
        else:
            #
            self.cutlines.append(
                [PathStyle.THUMBHOLE, [82, self.__THUMBHOLE_SMALL_RADIUS, self.thumbholeradius, 0, Direction.SOUTH]])
            self.cutlines.append([PathStyle.LINE, [14, 7, 6, 2, 3, 0, 82]])
            self.cutlines.append([PathStyle.LINE, [83, 1, 4, 5, 9, 8, 17]])

            if self.singlethumbhole:
                self.cutlines.append(right_full)
            else:
                self.cutlines.append(
                    [PathStyle.THUMBHOLE, [85, self.__THUMBHOLE_SMALL_RADIUS, self.thumbholeradius, 0, Direction.NORTH]])
                self.cutlines.append([PathStyle.LINE, [54, 63, 62, 66, 67, 70, 84]])
                self.cutlines.append([PathStyle.LINE, [85, 71, 68, 69, 65, 64, 57]])

        # detect boundaries of drawing
        self.left_x, self.right_x, self.top_y, self.bottom_y = Design.get_bounds(self.corners)

    def __draw_slot_hole_line(self, xml_string, start, delta):

        # https://stackoverflow.com/questions/25640628/python-adding-lists-of-numbers-with-other-lists-of-numbers
        stop = [sum(values) for values in zip(start, delta)]

        xml_string += Design.draw_line(start, stop)

        return xml_string, stop

    def __print_variables(self):
        print("-------------")
        print(f"Length: {self.length}\n"
              f"Width: {self.width}"
              f"Height: {self.height}"
              f"X Offset:{self.x_offset}\nY Offset: {self.y_offset}\n"
              f"Vertical Separation: {self.vertical_separation}\nSlot Width: {self.slot_width}\n"
              f"Corner Gap: {self.corner_gap}\n"
              f"Single Thumbhole: {self.singlethumbhole}\n"
              f"Thumbhole Radius: {self.thumbholeradius}\n"
              f"Enforce Small Design: {self.enforce_small_design}\n"
              f"Enforce Large Design: {self.enforce_large_design}\n"
              f"Project: {self.project}\n"
              f"Filename: {self.outfile}\n"
              f"Title: {self.title}\n"
              )

    def __convert_all_to_thoudpi(self):
        # convert all mm to thoudpi
        self.length = Design.mm_to_thoudpi(self.length)
        self.width = Design.mm_to_thoudpi(self.width)
        self.height = Design.mm_to_thoudpi(self.height)
        self.x_offset = Design.mm_to_thoudpi(self.x_offset)
        self.y_offset = Design.mm_to_thoudpi(self.y_offset)
        self.vertical_separation = Design.mm_to_thoudpi(self.vertical_separation)
        self.corner_gap = Design.mm_to_thoudpi(self.corner_gap)
        self.slot_width = Design.mm_to_thoudpi(self.slot_width)
        self.thumbholeradius = Design.mm_to_thoudpi(self.thumbholeradius)
        self.thickness = Design.mm_to_thoudpi(self.thickness)

        # not yet implemented
        # self.bottomhole_radius = Design.mm_to_thoudpi(self.bottomhole_radius)
