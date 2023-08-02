from enum import Enum
from classes.Design import Design
from datetime import datetime
from classes.PathStyle import PathStyle
from classes.Template import Template
from classes.Direction import Rotation


class EnfordeDesign(Enum):
    NONE = "none"
    SMALL = "small"
    LARGE = "large"
    EMPTY = ""


class Thumbhole(Enum):
    SINGLE = "single"
    DUAL = "double"
    NONE = "none"


class Funnel(Enum):
    SINGLE = "single"
    DUAL = "double"


class CardBox(Design):
    __DEFAULT_FILENAME = "CardBox"
    __DEFAULT_TEMPLATE = "CardBox.svg"
    __DEFAULT_TEMPLATE_SEPARATED = "ItemBoxSeparated.svg"

    __DEFAULT_LENGTH = 80.0
    __DEFAULT_WIDTH = 40.0
    __DEFAULT_HEIGHT = 15.0

    __DEFAULT_SLOT_WIDTH = 10.0
    __DEFAULT_CORNER_GAP = 10.0
    __DEFAULT_FUNNEL_TOP_WIDTH = 10.0
    __DEFAULT_FUNNEL_BOTTOM_WIDTH = 10.0
    __DEFAULT_FUNNEL_NECK_HEIGHT = 10.0
    __DEFAULT_VERTICAL_SEPARATION = 3.0
    __DEFAULT_CENTER_NOSE_WIDTH = 5.0
    __DEFAULT_BOTTOM_HOLE_RADIUS = 10.0
    __DEFAULT_ENFORCEDESIGN = EnfordeDesign.NONE
    __DEFAULT_FUNNEL = Funnel.DUAL
    __DEFAULT_THUMBHOLE = Thumbhole.NONE

    __DEFAULT_SMALL_HEIGHT = 20.0

    def __init__(self, config_file: str, section: str, **kwargs):
        super().__init__(kwargs)

        self.settings.update({'template name': self.__DEFAULT_TEMPLATE,
                              'template card name': self.__DEFAULT_TEMPLATE,
                              })

        self.inner_dimensions = []
        self.outer_dimensions = []

        self.settings.update({'length': self.__DEFAULT_LENGTH,
                              'width': self.__DEFAULT_WIDTH,
                              'height': self.__DEFAULT_HEIGHT,
                              'separated': False,
                              'thumbhole': self.__DEFAULT_THUMBHOLE,
                              'enforce design': self.__DEFAULT_ENFORCEDESIGN,
                              'vertical separation': self.__DEFAULT_VERTICAL_SEPARATION,
                              'slot width': self.__DEFAULT_SLOT_WIDTH,
                              'corner gap': self.__DEFAULT_CORNER_GAP,
                              'funnel top width': self.__DEFAULT_FUNNEL_TOP_WIDTH,
                              'funnel bottom width': self.__DEFAULT_FUNNEL_BOTTOM_WIDTH,
                              'funnel neck height': self.__DEFAULT_FUNNEL_NECK_HEIGHT,
                              'center nose width': self.__DEFAULT_CENTER_NOSE_WIDTH,
                              'funnel': self.__DEFAULT_FUNNEL,
                              'small height': self.__DEFAULT_SMALL_HEIGHT,
                              }
                             )

        self.add_settings_measures(["length", "width", "height", "vertical separation", "slot width",
                                    "corner gap", "funnel top width", "funnel bottom width", "funnel neck height",
                                    "center nose width"])

        self.add_settings_enum({"funnel": Funnel,
                                "enforce design": EnfordeDesign,
                                "thumbhole": Thumbhole,
                                })

        self.add_settings_boolean(["separated"])

        self.load_settings(config_file, section)

        self.settings[
            "title"] = f"{self.get_project_name_for_title()}" \
                       f"{self.__DEFAULT_FILENAME}-L{self.settings['length']}-W{self.settings['width']}-" \
                       f"H{self.settings['height']}-S{self.settings['thickness']}-" \
                       f"{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        self.convert_measures_to_tdpi()

    def create(self, separated=False):
        self.__init_design()
        base_cut = ""

        if not self.settings["separated"]:
            if self.settings["funnel"] is Funnel.DUAL:
                # Two funnels
                if self.settings["thumbhole"] is Thumbhole.DUAL:
                    # Two funnels and two thumbholes
                    base_cut = Design.draw_lines(self.corners, self.cutlines_double_funnel_double_thumbholes)
                elif self.settings["thumbhole"] is Thumbhole.SINGLE:
                    # Two funnels and one thumbole
                    base_cut = Design.draw_lines(self.corners, self.cutlines_double_funnel_single_thumbhole)
                else:
                    base_cut = Design.draw_lines(self.corners, self.cutlines_double_funnel_no_thumbholes)

            else:
                # One funnel
                if self.settings["thumbhole"] is Thumbhole.NONE:
                    # One funnel, no thumbholes
                    base_cut = Design.draw_lines(self.corners, self.cutlines_single_funnel_no_thumbholes)
                else:
                    # One funnel, one thumbhole even if two are selected
                    base_cut = Design.draw_lines(self.corners, self.cutlines_single_funnel_single_thumbhole)

            self.template["TEMPLATE"] = self.__DEFAULT_TEMPLATE
            self.template["$SVGPATH$"] = base_cut

        else:
            # TEST FOR SEPARATION
            template = Template.load_template(self.__DEFAULT_TEMPLATE_SEPARATED)

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

        viewbox_x, viewbox_y = self.get_viewbox(self.right_x, self.bottom_y)

        self.template["VIEWBOX_X"] = viewbox_x
        self.template["VIEWBOX_Y"] = viewbox_y

        self.template["$FOOTER__OVERALL_WIDTH$"] = str(
            round((self.right_x - self.left_x) / self.conversion_factor(), 2))

        self.template["$FOOTER_OVERALL_HEIGHT$"] = self.tpi_to_unit(self.bottom_y - self.top_y)
        self.template["$FOOTER_INNER_LENGTH$"] = self.inner_dimensions[0]
        self.template["$FOOTER_INNER_WIDTH$"] = self.inner_dimensions[1]
        self.template["$FOOTER_INNER_HEIGHT$"] = self.inner_dimensions[2]
        self.template["$FOOTER_OUTER_LENGTH$"] = self.outer_dimensions[0]
        self.template["$FOOTER_OUTER_WIDTH$"] = self.outer_dimensions[1]
        self.template["$FOOTER_OUTER_HEIGHT$"] = self.outer_dimensions[2]

        self.write_to_file(self.template)
        print(f"CardBox \"{self.settings['filename']}\" created")

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

        length = self.settings["length_tdpi"]
        height = self.settings["height_tdpi"]
        width = self.settings["width_tdpi"]
        thickness = self.settings["thickness_tdpi"]

        slot_width = self.settings["slot width_tdpi"]
        corner_gap = self.settings["corner gap_tdpi"]
        neckheight = self.settings["funnel neck height_tdpi"]
        funneltopwidth = self.settings["funnel top width_tdpi"]
        funnelbottomwidth = self.settings["funnel bottom width_tdpi"]
        nosewidth = self.settings["center nose width_tdpi"]

        # noinspection DuplicatedCode
        # X - Points
        a = self.settings["x offset_tdpi"]
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
        p = self.settings["y offset_tdpi"]
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

        # noinspection DuplicatedCode
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

        # noinspection DuplicatedCode
        self.inner_dimensions = [self.tpi_to_unit(j - e), self.tpi_to_unit(z - s), self.tpi_to_unit(d - a)]
        self.outer_dimensions = [self.tpi_to_unit(k - d), self.tpi_to_unit(aa - r), self.tpi_to_unit(e - a)]

        if self.settings["enforce design"] is EnfordeDesign.SMALL or \
                (self.tpi_to_unit(height)  <= self.settings["small height"] and
                 not self.settings["enforce design"] is EnfordeDesign.LARGE):

            # small design
            middle_top = [PathStyle.LINE, [21, 28, 29, 33, 32, 36, 37, 41, 40, 45]]
            middle_bottom = [PathStyle.LINE, [26, 31, 30, 34, 35, 39, 38, 42, 43, 50]]
            right_thumbhole = [PathStyle.HALFCIRCLE_NOMOVE, [56, 57, Rotation.CCW]]
            left_thumbhole = [PathStyle.HALFCIRCLE_NOMOVE, [15, 14, Rotation.CCW]]
            path_around_top = [14, 23, 22, 13, 12, 21, 20, 11, 10, 52, 53, 44, 45, 54, 55, 46, 47, 56]
            path_around_bottom = [48, 49, 58, 59, 50, 51, 60, 61, 19, 18, 27, 26, 17, 16, 25, 24, 15]

            # left top flap path
            # in all designs the same
            left_top_path = [12, 6, 7, 0]
            # check if top and bottom funnel width is not equal, so set point 1
            if not self.settings["funnel top width"] == self.settings["funnel bottom width"]:
                # there is really a funnel
                left_top_path.append(1)
            left_top_path += [4, 14]

            # left bottom flap path
            left_bottom_path = [17, 9, 8, 3]
            # check if top and bottom funnel width is not equal, so set point 2
            if not self.settings["funnel top width"] == self.settings["funnel bottom width"]:
                # there is really a funnel
                left_bottom_path.append(2)
            left_bottom_path += [5, 15]

            # right top flap path
            # in all designs the same
            right_top_path = [54, 62, 63, 68]
            # check if top and bottom funnel width is not equal, so set point 69
            if not self.settings["funnel top width"] == self.settings["funnel bottom width"]:
                # there is really a funnel
                right_top_path.append(69)
            right_top_path += [66, 56]

            # left bottom flap path
            right_bottom_path = [59, 65, 64, 71]
            # check if top and bottom funnel width is not equal, so set point 70
            if not self.settings["funnel top width"] == self.settings["funnel bottom width"]:
                # there is really a funnel
                right_bottom_path.append(70)
            right_bottom_path += [67, 57]

            right_no_funnel_path = [54, 62, 63, 68, 71, 64, 65, 59]
        else:
            # Large design
            # in all designs the same
            middle_top = [PathStyle.LINE, [12, 28, 29, 33, 32, 36, 37, 41, 40, 54]]
            middle_bottom = [PathStyle.LINE, [17, 31, 30, 34, 35, 39, 38, 42, 43, 59]]
            left_thumbhole = [PathStyle.HALFCIRCLE_NOMOVE, [15, 14, Rotation.CCW]]
            right_thumbhole = [PathStyle.HALFCIRCLE_NOMOVE, [56, 57, Rotation.CCW]]
            # path around both clockwise
            path_around_top = [14, 23, 22, 13, 81, 87, 86, 80, 10, 52, 94, 90, 91, 95, 55, 46, 47, 56]
            path_around_bottom = [48, 49, 58, 98, 92, 93, 99, 61, 19, 85, 89, 88, 84, 16, 25, 24, 15]

            # left top flap path
            # in all designs the same
            left_top_path = [82, 77, 76, 72, 73, 0]
            # check if top and bottom funnel width is not equal, so set point 1
            if not self.settings["funnel top width"] == self.settings["funnel bottom width"]:
                # there is really a funnel
                left_top_path.append(1)
            left_top_path += [4, 14]

            # left bottom flap path
            left_bottom_path = [83, 78, 79, 75, 74, 3]
            # check if top and bottom funnel width is not equal, so set point 2
            if not self.settings["funnel top width"] == self.settings["funnel bottom width"]:
                # there is really a funnel
                left_bottom_path.append(2)
            left_bottom_path += [5, 15]

            # right top flap path
            # in all designs the same
            right_top_path = [96, 101, 100, 104, 105, 68]
            # check if top and bottom funnel width is not equal, so set point 69
            if not self.settings["funnel top width"] == self.settings["funnel bottom width"]:
                # there is really a funnel
                right_top_path.append(69)
            right_top_path += [66, 56]

            # left bottom flap path
            right_bottom_path = [97, 102, 103, 107, 106, 71]
            # check if top and bottom funnel width is not equal, so set point 70
            if not self.settings["funnel top width"] == self.settings["funnel bottom width"]:
                # there is really a funnel
                right_bottom_path.append(70)
            right_bottom_path += [67, 57]

            right_no_funnel_path = [96, 101, 100, 104, 105, 68, 71, 106, 107, 103, 102, 97]

        self.cutlines_double_funnel_no_thumbholes = [
            middle_top,
            middle_bottom,
            [PathStyle.LINE, left_top_path],
            [PathStyle.LINE, left_bottom_path],
            [PathStyle.LINE, right_top_path],
            [PathStyle.LINE, right_bottom_path],
            [PathStyle.LINE, path_around_top],
            [PathStyle.LINE_NOMOVE, [57]],
            [PathStyle.LINE_NOMOVE, path_around_bottom],
            [PathStyle.LINE_NOMOVE, [14]],
        ]

        self.cutlines_double_funnel_single_thumbhole = [
            middle_top,
            middle_bottom,
            [PathStyle.LINE, left_top_path],
            [PathStyle.LINE, left_bottom_path],
            [PathStyle.LINE, right_top_path],
            [PathStyle.LINE, right_bottom_path],
            [PathStyle.LINE, path_around_top],
            [PathStyle.LINE_NOMOVE, [57]],
            [PathStyle.LINE_NOMOVE, path_around_bottom],
            left_thumbhole
        ]

        self.cutlines_double_funnel_double_thumbholes = [
            middle_top,
            middle_bottom,
            [PathStyle.LINE, left_top_path],
            [PathStyle.LINE, left_bottom_path],
            [PathStyle.LINE, right_top_path],
            [PathStyle.LINE, right_bottom_path],
            [PathStyle.LINE, path_around_top],
            right_thumbhole,
            [PathStyle.LINE_NOMOVE, path_around_bottom],
            left_thumbhole
        ]

        self.cutlines_single_funnel_no_thumbholes = [
            middle_top,
            middle_bottom,
            [PathStyle.LINE, left_top_path],
            [PathStyle.LINE, left_bottom_path],
            [PathStyle.LINE, right_no_funnel_path],
            [PathStyle.LINE, path_around_top],
            [PathStyle.LINE_NOMOVE, [57]],
            [PathStyle.LINE_NOMOVE, path_around_bottom],
            [PathStyle.LINE_NOMOVE, [14]],
        ]

        self.cutlines_single_funnel_single_thumbhole = [
            middle_top,
            middle_bottom,
            [PathStyle.LINE, left_top_path],
            [PathStyle.LINE, left_bottom_path],
            [PathStyle.LINE, right_no_funnel_path],
            [PathStyle.LINE, path_around_top],
            [PathStyle.LINE_NOMOVE, [57]],
            [PathStyle.LINE_NOMOVE, path_around_bottom],
            left_thumbhole
        ]

        # detect boundaries of drawing

        self.left_x, self.right_x, self.top_y, self.bottom_y = self.set_bounds(self.corners)

        if self.verbose:
            self.__print_dimensons()

    def __make_thumbhole(self, start, end, orientation):
        # startpoint, endpoint, orientation of the circle
        pass

    def __print_dimensons(self):
        print(
            f"Inner Length: {self.inner_dimensions[0]} , "
            f"Inner Width: {self.inner_dimensions[1]} , "
            f"Inner Height: {self.inner_dimensions[2]}")

        print(
            f"Outer Length: {self.outer_dimensions[0]} , "
            f"Outer Width: {self.outer_dimensions[1]} , "
            f"Outer Height: {self.outer_dimensions[2]}")

# TODO:
# create empty template --create-template <filename>
# implement bottom hole
# Config Parameter für default small height
