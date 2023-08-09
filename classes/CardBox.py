from enum import Enum
from classes.Design import Design
from datetime import datetime
from classes.PathStyle import PathStyle
from classes.Direction import Rotation
from classes.ConfigConstants import ConfigConstantsText as Ct
from classes.ConfigConstants import ConfigConstantsTemplate as Cm


class C:
    template_card_name = 'template card name'
    thumbhole = 'thumbhole'
    enforce_design = 'enforce design'
    slot_width = 'slot width'
    corner_gap = 'corner gap'
    funnel_top_width = 'funnel top width'
    funnel_bottom_width = 'funnel bottom width'
    funnel_neck_height = 'funnel neck height'
    center_nose_width = 'center nose width'
    funnel = 'funnel'
    small_height = 'small height'

    slot_width_tdpi =  f'{slot_width}{Ct.tdpi}'
    corner_gap_tdpi = f'{corner_gap}{Ct.tdpi}'
    funnel_top_width_tdpi = f'{funnel_top_width}{Ct.tdpi}'
    funnel_bottom_width_tdpi = f'{funnel_bottom_width}{Ct.tdpi}'
    funnel_neck_height_tdpi = f'{funnel_neck_height}{Ct.tdpi}'
    center_nose_width_tdpi = f'{center_nose_width}{Ct.tdpi}'
    funnel = f'{funnel}{Ct.tdpi}'
    small_height = f'{small_height}{Ct.tdpi}'



class EnfordeDesign(Enum):
    NONE = 'none'
    SMALL = 'small'
    LARGE = 'large'
    EMPTY = ''


class Thumbhole(Enum):
    SINGLE = 'single'
    DUAL = 'double'
    NONE = 'none'


class Funnel(Enum):
    SINGLE = "single"
    DUAL = "double"


class CardBox(Design):
    __DEFAULT_FILENAME = 'CardBox'
    __DEFAULT_TEMPLATE = 'CardBox.svg'
    __DEFAULT_TEMPLATE_SEPARATED = 'ItemBoxSeparated.svg'

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

    def __init__(self, **kwargs):
        super().__init__(kwargs)

        self.settings.update({Ct.template_name: self.__DEFAULT_TEMPLATE,
                              C.template_card_name: self.__DEFAULT_TEMPLATE,
                              })

        self.inner_dimensions = []
        self.outer_dimensions = []

        self.settings.update({Ct.length: self.__DEFAULT_LENGTH,
                              Ct.width: self.__DEFAULT_WIDTH,
                              Ct.height: self.__DEFAULT_HEIGHT,
                              # 'separated': False,
                              C.thumbhole: self.__DEFAULT_THUMBHOLE,
                              C.enforce_design: self.__DEFAULT_ENFORCEDESIGN,
                              Ct.vertical_separation: self.__DEFAULT_VERTICAL_SEPARATION,
                              C.slot_width: self.__DEFAULT_SLOT_WIDTH,
                              C.corner_gap: self.__DEFAULT_CORNER_GAP,
                              C.funnel_top_width: self.__DEFAULT_FUNNEL_TOP_WIDTH,
                              C.funnel_bottom_width: self.__DEFAULT_FUNNEL_BOTTOM_WIDTH,
                              C.funnel_neck_height: self.__DEFAULT_FUNNEL_NECK_HEIGHT,
                              C.center_nose_width: self.__DEFAULT_CENTER_NOSE_WIDTH,
                              C.funnel: self.__DEFAULT_FUNNEL,
                              C.small_height: self.__DEFAULT_SMALL_HEIGHT,
                              }
                             )

        self.add_settings_measures([Ct.length, Ct.width, Ct.height, Ct.vertical_separation, C.slot_width,
                                    C.corner_gap, C.funnel_top_width, C.funnel_bottom_width, C.funnel_neck_height,
                                    C.center_nose_width])

        self.add_settings_enum({C.funnel: Funnel,
                                C.enforce_design: EnfordeDesign,
                                C.thumbhole: Thumbhole,
                                })

        self.add_settings_boolean([Ct.separated])

        self.load_settings(self.config_file_and_section)

        self.settings[
            'title'] = f'{self.get_project_name_for_title()}' \
                       f'{self.__DEFAULT_FILENAME}-L{self.settings.get(Ct.length)}-W{self.settings.get(Ct.width)}-' \
                       f'H{self.settings.get(Ct.height)}-S{self.settings.get(Ct.thickness)}-' \
                       f'{datetime.now().strftime("%Y%m%d-%H%M%S")}'

        self.convert_measures_to_tdpi()

    def create(self, separated=False):
        self.__init_design()
        base_cut = ''

        if self.settings.get(C.funnel) is Funnel.DUAL:
            # Two funnels
            if self.settings.get(C.thumbhole) is Thumbhole.DUAL:
                # Two funnels and two thumbholes
                base_cut = Design.draw_lines(self.corners, self.cutlines_double_funnel_double_thumbholes)
            elif self.settings.get(C.thumbhole) is Thumbhole.SINGLE:
                # Two funnels and one thumbole
                base_cut = Design.draw_lines(self.corners, self.cutlines_double_funnel_single_thumbhole)
            else:
                base_cut = Design.draw_lines(self.corners, self.cutlines_double_funnel_no_thumbholes)

        else:
            # One funnel
            if self.settings.get(C.thumbhole) is Thumbhole.NONE:
                # One funnel, no thumbholes
                base_cut = Design.draw_lines(self.corners, self.cutlines_single_funnel_no_thumbholes)
            else:
                # One funnel, one thumbhole even if two are selected
                base_cut = Design.draw_lines(self.corners, self.cutlines_single_funnel_single_thumbhole)

        self.template['TEMPLATE'] = self.__DEFAULT_TEMPLATE
        self.template[Cm.svgpath] = base_cut

        viewbox_x, viewbox_y = self.set_viewbox(self.right_x, self.bottom_y)

        self.template[Cm.viewbox_x] = viewbox_x
        self.template[Cm.viewbox_y] = viewbox_y

        self.template[Cm.footer_overall_width] = str(
            round((self.right_x - self.left_x) / self.conversion_factor(), 2))

        self.template[Cm.footer_overall_height] = self.tpi_to_unit(self.bottom_y - self.top_y)
        self.template['$FOOTER_INNER_LENGTH$'] = self.inner_dimensions[0]
        self.template['$FOOTER_INNER_WIDTH$'] = self.inner_dimensions[1]
        self.template['$FOOTER_INNER_HEIGHT$'] = self.inner_dimensions[2]
        self.template['$FOOTER_OUTER_LENGTH$'] = self.outer_dimensions[0]
        self.template['$FOOTER_OUTER_WIDTH$'] = self.outer_dimensions[1]
        self.template['$FOOTER_OUTER_HEIGHT$'] = self.outer_dimensions[2]

        self.write_to_file(self.template)
        print(f'CardBox \'{self.settings.get(Ct.filename)}\' created')

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

        length = self.settings.get(Ct.length_tdpi)
        height = self.settings.get(Ct.height_tdpi)
        width = self.settings.get(Ct.width_tdpi)
        thickness = self.settings.get(Ct.thickness_tdpi)

        slot_width = self.settings.get(C.slot_width_tdpi)
        corner_gap = self.settings.get(C.corner_gap_tdpi)
        neckheight = self.settings.get(C.funnel_neck_height_tdpi)
        funneltopwidth = self.settings.get(C.funnel_top_width_tdpi)
        funnelbottomwidth = self.settings.get(C.funnel_top_width_tdpi)
        nosewidth = self.settings.get(C.center_nose_width_tdpi)

        # noinspection DuplicatedCode
        # X - Points
        a = self.settings.get(Ct.x_offset_tdpi)
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
        p = self.settings.get(Ct.y_offset_tdpi)
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

        if self.settings.get(C.enforce_design) is EnfordeDesign.SMALL or \
                (self.tpi_to_unit(height) <= self.settings.get(C.small_height) and
                 not self.settings.get(C.enforce_design) is EnfordeDesign.LARGE):

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
            if not self.settings.get(C.funnel_top_width) == self.settings.get(C.funnel_bottom_width):
                # there is really a funnel
                left_top_path.append(1)
            left_top_path += [4, 14]

            # left bottom flap path
            left_bottom_path = [17, 9, 8, 3]
            # check if top and bottom funnel width is not equal, so set point 2
            if not self.settings.get(C.funnel_top_width) == self.settings.get(C.funnel_bottom_width):
                # there is really a funnel
                left_bottom_path.append(2)
            left_bottom_path += [5, 15]

            # right top flap path
            # in all designs the same
            right_top_path = [54, 62, 63, 68]
            # check if top and bottom funnel width is not equal, so set point 69
            if not self.settings.get(C.funnel_top_width) == self.settings.get(C.funnel_bottom_width):
                # there is really a funnel
                right_top_path.append(69)
            right_top_path += [66, 56]

            # left bottom flap path
            right_bottom_path = [59, 65, 64, 71]
            # check if top and bottom funnel width is not equal, so set point 70
            if not self.settings.get(C.funnel_top_width) == self.settings.get(C.funnel_bottom_width):
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
            if not self.settings.get(C.funnel_top_width) == self.settings.get(C.funnel_bottom_width):
                # there is really a funnel
                left_top_path.append(1)
            left_top_path += [4, 14]

            # left bottom flap path
            left_bottom_path = [83, 78, 79, 75, 74, 3]
            # check if top and bottom funnel width is not equal, so set point 2
            if not self.settings.get(C.funnel_top_width) == self.settings.get(C.funnel_bottom_width):
                # there is really a funnel
                left_bottom_path.append(2)
            left_bottom_path += [5, 15]

            # right top flap path
            # in all designs the same
            right_top_path = [96, 101, 100, 104, 105, 68]
            # check if top and bottom funnel width is not equal, so set point 69
            if not self.settings.get(C.funnel_top_width) == self.settings.get(C.funnel_bottom_width):
                # there is really a funnel
                right_top_path.append(69)
            right_top_path += [66, 56]

            # left bottom flap path
            right_bottom_path = [97, 102, 103, 107, 106, 71]
            # check if top and bottom funnel width is not equal, so set point 70
            if not self.settings.get(C.funnel_top_width) == self.settings.get(C.funnel_bottom_width):
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

    def __print_dimensons(self):
        print(
            f'Inner Length: {self.inner_dimensions[0]} , '
            f'Inner Width: {self.inner_dimensions[1]} , '
            f'Inner Height: {self.inner_dimensions[2]}')

        print(
            f'Outer Length: {self.outer_dimensions[0]} , '
            f'Outer Width: {self.outer_dimensions[1]} , '
            f'Outer Height: {self.outer_dimensions[2]}')

# TODO:
# create empty template --create-template <filename>
# implement bottom hole
# Config Parameter für default small height
