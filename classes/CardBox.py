from classes.Design import Design
from datetime import datetime
from classes.Direction import Direction
from classes.PathStyle import PathStyle


class CardBox(Design):
    __DEFAULT_FILENAME = "CardBox"
    __DEFAULT_TEMPLATE = "CardBox.svg"
    __DEFAULT_TEMPLATE_SEPARATED = "ItemBoxSeparated.svg"

    __DEFAULT_LENGTH = 80.0
    __DEFAULT_WIDTH = 40.0
    __DEFAULT_HEIGHT = 15.0

    __DEFAULT_SLOT_WIDTH = 10.0
    __DEFAULT_CORNER_GAP = 10.0
    __DEFAULT_FUNNEL_TOP_WIDTH = 20.0
    __DEFAULT_FUNNEL_BOTTOM_WIDTH = 10.0
    __DEFAULT_FUNNEL_NECK_HEIGHT = 10.0
    __DEFAULT_THICKNESS = 1.5
    __DEFAULT_VERTICAL_SEPARATION = 3.0
    __DEFAULT_CENTER_NOSE_WIDTH = 5.0
    __DEFAULT_BOTTOM_HOLE_RADIUS = 10.0
    __DEFAULT_ENFORCE_SMALL_DESIGN = False
    __DEFAULT_ENFORCE_LARGE_DESIGN = True
    __DEFAULT_ENFORCEDESIGN = ""
    __DEFAULT_FUNNEL = "dual with holes"

    __DEFAULT_SMALL_HEIGHT = 20.0

    def __init__(self, config_file: str, section: str, verbose=False, **kwargs):
        super().__init__(kwargs)

        self.inner_dimensions = []
        self.outer_dimensions = []

        self.settings.update({'length': self.__DEFAULT_LENGTH,
                              'width': self.__DEFAULT_WIDTH,
                              'height': self.__DEFAULT_HEIGHT,
                              'separated': False,
                              'thumbhole': False,
                              'singlethumbhole': False,
                              'singlefunnel': False,
                              # small
                              #   self.enforce_small_design = True
                              #   self.enforce_large_design = False
                              # large
                              #   self.enforce_small_design = False
                              #   self.enforce_large_design = True
                              'enforcedesign': self.__DEFAULT_ENFORCEDESIGN,
                              'vertical separation': self.__DEFAULT_VERTICAL_SEPARATION,
                              'slot width': self.__DEFAULT_SLOT_WIDTH,
                              'corner gap': self.__DEFAULT_CORNER_GAP,
                              'funnel top width': self.__DEFAULT_FUNNEL_TOP_WIDTH,
                              'funnel bottom width': self.__DEFAULT_FUNNEL_BOTTOM_WIDTH,
                              'funnel neck height': self.__DEFAULT_FUNNEL_NECK_HEIGHT,
                              'thickness': self.__DEFAULT_THICKNESS,
                              'center nose width': self.__DEFAULT_CENTER_NOSE_WIDTH,
                              # single with hole/single with holes
                              #   self.thumbhole = True
                              #   self.singlethumbhole = True
                              #   self.singlefunnel = True
                              # dual with hole
                              #   self.thumbhole = True
                              #   self.singlethumbhole = True
                              #   self.singlefunnel = False
                              # dual with holes
                              #   self.thumbhole = True
                              #   self.singlethumbhole = False
                              #   self.singlefunnel = False
                              'funnel': self.__DEFAULT_FUNNEL,
                              'small height': self.__DEFAULT_SMALL_HEIGHT
                              }
                             )

        # not yet implemented
        # self.bottomhole_radius = Design.mm_to_thoudpi(self.bottomhole_radius)
        self.add_settings_measures(["length", "width", "height", "vertical separation", "slot width",
                                    "corner gap", "funnel top width", "funnel bottom width", "funnel neck height",
                                    "center nose width"])

        self.settings[
            "title"] = f"{'' if self.settings['project name'] is None else self.settings['project name'] + '-'}" \
                       f"{self.__DEFAULT_FILENAME}-L{self.length}-W{self.width}-H{self.height}-" \
                       f"S{self.thickness}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        self.load_settings(config_file, section, verbose)

        self.convert_measures_to_tdpi()

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
