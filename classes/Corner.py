import os
import sys
import argparse
import configparser
from datetime import datetime
from classes.Design import Design
from classes.Direction import Direction
from classes.PathStyle import PathStyle


class Corner:
    __DEFAULT_FILENAME = "Corner"
    __DEFAULT_TEMPLATE = "templates/Corner.svg"
    __DEFAULT_TEMPLATE_SEPARATED = "templates/CornerSeparated.svg"

    __DEFAULT_X_OFFSET = Design.__DEFAULT_X_OFFSET
    __DEFAULT_Y_OFFSET = Design.__DEFAULT_Y_OFFSET

    __DEFAULT_SLOT_WIDTH = 10
    __DEFAULT_CORNER_GAP = 10
    __DEFAULT_CORNER_RADIUS = 2
    __DEFAULT_THICKNESS = 1.5

    __DEFAULT_VERTICAL_SEPARATION = 3
    __DEFAULT_ENFORCE_SMALL_DESIGN = False
    __DEFAULT_ENFORCE_LARGE_DESIGN = True

    __DEFAULT_SMALL_HEIGHT = Design.mm_to_thoudpi(20)

    def __init__(self, arguments=""):
        self.__init_variables()

        # Parse the cli
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
                    'thumbhole': False,
                    'funnel': 'dual with holes',
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
        self.funnel_top_width = int(config[section]['funnel top width'])
        self.funnel_bottom_width = int(config[section]['funnel bottom width'])
        self.funnel_neck_height = int(config[section]['funnel neck height'])
        self.thickness = float(config[section]['thickness'])
        self.center_nose_width = int(config[section]['center nose width'])

        if config.has_option(section, 'funnel'):
            funnel = config[section]['funnel']
            if funnel == "single with hole" or funnel == "single with holes":
                self.thumbhole = True
                self.singlethumbhole = True
                self.singlefunnel = True
            elif funnel == "dual with hole":
                self.thumbhole = True
                self.singlethumbhole = True
                self.singlefunnel = False
            elif funnel == "dual with holes":
                self.thumbhole = True
                self.singlethumbhole = False
                self.singlefunnel = False

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

    def __init_variables(self):
        # initialization of variables

        # Arguments as String
        self.args_string = ' '.join(sys.argv[1:])

        # command line parameter variables
        self.length = 0.0
        self.width = 0.0
        self.height = 0.0
        self.thickness = self.__DEFAULT_THICKNESS
        self.project = ""
        self.outfile = ""
        self.title = ""
        self.separated = False
        self.corner_radius = self.__DEFAULT_CORNER_RADIUS
        self.rectangular = True
        self.bottom_tile = True
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

        self.x_offset = self.__DEFAULT_X_OFFSET
        self.y_offset = self.__DEFAULT_Y_OFFSET
        self.slot_width = self.__DEFAULT_SLOT_WIDTH
        self.corner_gap = self.__DEFAULT_CORNER_GAP
        self.small_height = self.__DEFAULT_SMALL_HEIGHT
        self.vertical_separation = self.__DEFAULT_VERTICAL_SEPARATION

        # not implemented yet
        # self.bottomhole_radius = CardBox.__DEFAULT_BOTTOM_HOLE_RADIUS

        self.verbose = False

    def parse_arguments(self, arguments: str):
        parser = argparse.ArgumentParser(add_help=False)

        # The config file is mutually exclusive to all other command line parameters
        # and has precedence
        parser.add_argument('-c', type=str, required=True, help="Configuration File")
        parser.add_argument('-C', type=str, required=True, help="Config file section")

        if not arguments:
            return parser.parse_args()

        return parser.parse_args(arguments.split())

    def create(self, separated=False):
        self.__init_design()

        self.template["FILENAME"] = self.outfile
        self.template["$PROJECT$"] = self.project
        self.template["$TITLE$"] = self.title
        self.template["$FILENAME$"] = self.outfile
        self.template["$LABEL_X$"] = Design.thoudpi_to_dpi(self.left_x)

        ycoord = self.bottom_y + self.vertical_separation

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

    def __init_design(self):
        self.__init_base()

    def __init_base(self):


        # -------------------------------------------------------------------------------------
        #
        #    X--X------X     X------X--X
        #    |         |     |         |
        #    |         X-----X         |
        #    X                         X
        #    |                         |
        #    X-X                     X-X
        #      |                     |
        #      |                     |
        #    X-X                     X-X
        #    |                         |
        #    X                         X
        #    |         X-----X         |         X-----X                   X-----X                   X-----X
        #    |         |     |         |         |     |                   |     |                   |     |
        #    X--X------X     X------X--X--X------X     X------X--X--X------X     X------X--X--X------X     X------X--X
        #       |                   |     |                   |     |                   |     |                   |
        #       |                   |     |                   |     |                   |     |                   |
        #       |                   |     |                   |     |                   |     |                   |
        #       |                   |     |                   |     |                   |     |                   |
        #       |                   |     |                   |     |                   |     |                   |
        #       |                   |     |                   |     |                   |     |                   |
        #       |                   |     |                   |     |                   |     |                   |
        #       |                   |     |                   |     |                   |     |                   |
        #       |                   |     |                   |     |                   |     |                   |
        #    X--X------X     X------X--X--X------X     X------X--X--X------X     X------X--X--X------X     X------X--X
        #    |         |     |         |         |     |                   |     |                   |     |
        #    |         X-----X         |         X-----X                   X-----X                   X-----X
        #    X                         X
        #    |                         |
        #    X-X                     X-X
        #      |                     |
        #      |                     |
        #    X-X                     X-X
        #    |                         |
        #    X                         X
        #    |         X-----X         |
        #    |         |     |         |
        #    X--X------X     X------X--X




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
        w = s + int(width / 2 + funnelbottomwidth / 2)
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
            print(f"ba: {ba}/ {Design.thoudpi_to_mm(ba)}")
            print(f"bb: {bb}/ {Design.thoudpi_to_mm(bb)}")
            print(f"bc: {bc}/ {Design.thoudpi_to_mm(bc)}")
            print(f"bd: {bd}/ {Design.thoudpi_to_mm(bd)}")

            print(f"p: {p}/ {Design.thoudpi_to_mm(p)}")
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
            print(f"ca: {ca}/ {Design.thoudpi_to_mm(ca)}")
            print(f"cb: {cb}/ {Design.thoudpi_to_mm(cb)}")
            print(f"cc: {cc}/ {Design.thoudpi_to_mm(cc)}")
            print(f"cd: {cd}/ {Design.thoudpi_to_mm(cd)}")

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

        if (height <= self.small_height or self.enforce_small_design) and not self.enforce_large_design:
            self.cutlines = [
                # left upper
                [PathStyle.LINE, [6, 7, 0, 1, 4, 23, 22, 13, 12]],
                # left lower
                [PathStyle.LINE, [9, 8, 3, 2, 5, 24, 25, 16, 17]],
                # middle upper
                [PathStyle.LINE, [6, 28, 29, 33, 32, 36, 37, 41, 40, 62]],
                # middle lower
                [PathStyle.LINE, [9, 31, 30, 34, 35, 39, 38, 42, 43, 65]],
                # bottom
                [PathStyle.LINE, [26, 27, 18, 19, 61, 60, 51, 50]],
                # top
                [PathStyle.LINE, [21, 20, 11, 10, 52, 53, 44, 45]],

            ]

            if self.singlefunnel:
                # right single wall top cutline
                self.cutlines.append([PathStyle.LINE, [62, 63, 68, 71, 64, 65]])
                # right single wall upper cutline
                self.cutlines.append([PathStyle.LINE, [54, 55, 46, 47, 56]])
                # right single wall lower cutline
                self.cutlines.append([PathStyle.LINE, [59, 58, 49, 48, 57]])
            else:
                # right upper
                self.cutlines.append([PathStyle.LINE, [54, 62, 63, 68, 69, 66, 47, 46, 55, 54]])
                # right lower
                self.cutlines.append([PathStyle.LINE, [59, 65, 64, 71, 70, 67, 48, 49, 58, 59]])
        else:
            # Height is greater than 20
            self.cutlines = [
                # left upper
                [PathStyle.LINE, [82, 77, 76, 72, 73, 0, 1, 4, 23, 22, 13, 81]],
                # left lower
                [PathStyle.LINE, [83, 78, 79, 75, 74, 3, 2, 5, 24, 25, 16, 84]],
                # middle upper
                [PathStyle.LINE, [12, 28, 29, 33, 32, 36, 37, 41, 40, 54]],
                # middle lower
                [PathStyle.LINE, [17, 31, 30, 34, 35, 39, 38, 42, 43, 59]],
                # top
                [PathStyle.LINE, [81, 87, 86, 80, 10, 52, 94, 90, 91, 95]],
                # bottom
                [PathStyle.LINE, [84, 88, 89, 85, 19, 61, 99, 93, 92, 98]],
                # right top
                [PathStyle.LINE, [96, 101, 100, 104, 105, 68]],
                # right bottom
                [PathStyle.LINE, [97, 102, 103, 107, 106, 71]],
                [PathStyle.LINE, [95, 55, 46, 47]],
                [PathStyle.LINE, [98, 58, 49, 48]],
            ]

            if self.singlefunnel:
                # right single wall top
                self.cutlines.append([PathStyle.LINE, [68, 71]])
                self.cutlines.append([PathStyle.LINE, [47, 56]])
                self.cutlines.append([PathStyle.LINE, [48, 57]])
            else:
                self.cutlines.append([PathStyle.LINE, [68, 69, 66, 47]])
                self.cutlines.append([PathStyle.LINE, [71, 70, 67, 48]])

        if self.thumbhole:
            self.cutlines.append([PathStyle.HALFCIRCLE, [14, 15, Direction.VERTICAL]])
            if self.singlethumbhole:
                self.cutlines.append([PathStyle.LINE, [56, 57]])
            else:
                self.cutlines.append([PathStyle.HALFCIRCLE, [57, 56, Direction.VERTICAL]])
        else:
            self.cutlines.append([PathStyle.LINE, [14, 15]])
            self.cutlines.append([PathStyle.LINE, [56, 57]])

        self.fullright = [
            [PathStyle.LINE, [57, 48, 49, 58, 59, 100, 101, 105, 104, 107, 106, 103, 102, 98, 99, 54, 55, 46, 47, 56]]]

        self.cutlines_top = [
            [PathStyle.LINE, [10, 11, 20, 21, 28, 29, 33, 32, 36, 37, 41, 40, 45, 44, 53, 52, 10]]]
        self.cutlines_center = [[PathStyle.LINE,
                                 [12, 13, 22, 23, 14, 15, 24, 25, 16, 17, 31, 30, 34, 35, 39, 38, 42, 43, 59, 58, 49,
                                  48, 57, 56, 47, 46, 55, 54, 40, 41, 37, 36, 32, 33, 29, 28, 12]]]
        self.cutlines_bottom = [[PathStyle.LINE, [26, 27, 18, 19, 61, 60, 51, 50, 43, 42, 383, 9, 35, 34, 30, 31, 26]]]
        self.cutlines_left_top = [[PathStyle.LINE, [12, 6, 7, 0, 1, 4, 23, 22, 13, 12]]]
        self.cutlines_left_bottom = [[PathStyle.LINE, [17, 16, 25, 24, 5, 2, 3, 8, 9, 17]]]
        self.cutlines_right_top = [[PathStyle.LINE, [54, 62, 63, 68, 69, 66, 47, 46, 55, 54]]]
        self.cutlines_right_bottom = [[PathStyle.LINE, [59, 65, 64, 71, 70, 67, 48, 49, 58, 59]]]

        # detect boundaries of drawing

        self.left_x, self.right_x, self.top_y, self.bottom_y = Design.set_bounds(self.corners)

        if self.verbose:
            self.__print_dimensons()

        if self.verbose:
            print(
                f"Left X: {Design.thoudpi_to_mm(self.left_x)}, "
                f"Right X:{Design.thoudpi_to_mm(self.right_x)}, "
                f"Top Y: {Design.thoudpi_to_mm(self.top_y)}, "
                f"Bottom Y: {Design.thoudpi_to_mm(self.bottom_y)}"
            )

    def __make_thumbhole(self, start, end, orientation):
        # startpoint, endpoint, orientation of the circle
        pass

    def __print_variables(self):
        print("-------------")
        print(f"Length: {self.length}")
        print(f"Width: {self.width}")
        print(f"Height: {self.height}")
        print(f"X Offset:{self.x_offset}\nY Offset: {self.y_offset}\n")
        print(f"Vertical Separation: {self.vertical_separation}\nSlot Width: {self.slot_width}")
        print(f"Corner Gap: {self.corner_gap}\nFunnel Top Width: {self.funnel_top_width}")
        print(f"Funnel Bottom Width: {self.funnel_bottom_width}")
        print(f"Funnel Neck Height: {self.funnel_neck_height}\nThickness: {self.thickness}")
        print(f"Center Nose Width: {self.center_nose_width}")
        print(f"Enforce Small Design: {self.enforce_small_design}")
        print(f"Enforce Large Design: {self.enforce_large_design}")
        print(f"Project: {self.project}")
        print(f"Filename: {self.outfile}")
        print(f"Title: {self.title}")

    def __print_dimensons(self):
        print(
            f"Inner Length: {self.inner_dimensions[0]} , "
            f"Inner Width: {self.inner_dimensions[1]} , "
            f"Inner Height: {self.inner_dimensions[2]}")

        print(
            f"Outer Length: {self.outer_dimensions[0]} , "
            f"Outer Width: {self.outer_dimensions[1]} , "
            f"Outer Height: {self.outer_dimensions[2]}")

    def __convert_all_to_thoudpi(self):
        # convert all mm to thoudpi
        self.length = Design.mm_to_thoudpi(self.length)
        self.width = Design.mm_to_thoudpi(self.width)
        self.height = Design.mm_to_thoudpi(self.height)
        self.x_offset = Design.mm_to_thoudpi(self.x_offset)
        self.y_offset = Design.mm_to_thoudpi(self.y_offset)
        self.vertical_separation = Design.mm_to_thoudpi(self.vertical_separation)
        self.slot_width = Design.mm_to_thoudpi(self.slot_width)
        self.corner_gap = Design.mm_to_thoudpi(self.corner_gap)
        self.funnel_top_width = Design.mm_to_thoudpi(self.funnel_top_width)
        self.funnel_bottom_width = Design.mm_to_thoudpi(self.funnel_bottom_width)
        self.funnel_neck_height = Design.mm_to_thoudpi(self.funnel_neck_height)
        self.thickness = Design.mm_to_thoudpi(self.thickness)
        self.center_nose_width = Design.mm_to_thoudpi(self.center_nose_width)
        # not yet implemented
        # self.bottomhole_radius = Design.mm_to_thoudpi(self.bottomhole_radius)

# TODO:
# create empty template --create-template <filename>
# implement bottom hole
# Config Parameter für default small height
