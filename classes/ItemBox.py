import argparse
import configparser
from datetime import datetime
import os
import sys
from enum import Enum, auto
from classes.Design import Design
from classes.Direction import Direction
from classes.PathStyle import PathStyle


class EnfordeDesign(Enum):
    NONE = "none"
    SMALL = "small"
    LARGE = "large"
    EMPTY = ""


class Thumbhole(Enum):
    SINGLE = "single"
    DUAL = "dual"
    NONE = "none"


class ItemBox(Design):
    __DEFAULT_FILENAME = "ItemBox"
    __DEFAULT_TEMPLATE = "ItemBox.svg"
    __DEFAULT_TEMPLATE_SEPARATED = "ItemBoxSeparated.svg"

    __DEFAULT_VERTICAL_SEPARATION = 3

    __DEFAULT_THUMBHOLE_SMALL_RADIUS = 2
    __DEFAULT_THUMBHOLE_RADIUS = 10

    __DEFAULT_SLOT_WIDTH = 10
    __DEFAULT_CORNER_GAP = 10

    __DEFAULT_SMALL_HEIGHT = 20

    __DEFAULT_LENGTH = 60
    __DEFAULT_WIDTH = 40
    __DEFAULT_HEIGHT = 25

    __DEFAULT_ENFORCEDESIGN = EnfordeDesign.NONE
    __DEFAULT_THUMBHOLE = Thumbhole.NONE

    def __init__(self, config_file: str, section: str, verbose=False, **kwargs):
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
                              'enforcedesign': self.__DEFAULT_ENFORCEDESIGN,
                              'vertical separation': self.__DEFAULT_VERTICAL_SEPARATION,
                              'slot width': self.__DEFAULT_SLOT_WIDTH,
                              'corner gap': self.__DEFAULT_CORNER_GAP,
                              'small height': self.__DEFAULT_SMALL_HEIGHT,
                              }
                             )

        self.add_settings_measures(["length", "width", "height", "vertical separation", "slot width",
                                    "corner gap", "center nose width"])

        self.add_settings_enum({"enforcedesign": EnfordeDesign,
                                "thumbhole": Thumbhole,
                                })

        self.add_settings_boolean(["separated"])

        self.load_settings(config_file, section, verbose)

        self.settings[
            "title"] = f"{self.__DEFAULT_FILENAME}-L{self.settings['length']}-W{self.settings['width']}-" \
                       f"H{self.settings['height']}-S{self.settings['thickness']}-" \
                       f"{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        self.convert_measures_to_tdpi()

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
        ae = u + int(width / 2 - thumbholeradius - self.__DEFAULT_THUMBHOLE_SMALL_RADIUS)
        af = u + int(width / 2 + thumbholeradius + self.__DEFAULT_THUMBHOLE_SMALL_RADIUS)
        # ag = q + int(width / 2 - thumbholeradius - self.__DEFAULT_THUMBHOLE_SMALL_RADIUS)
        # ah = q + int(width / 2 + thumbholeradius + self.__DEFAULT_THUMBHOLE_SMALL_RADIUS)

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
                [PathStyle.THUMBHOLE,
                 [82, self.__DEFAULT_THUMBHOLE_SMALL_RADIUS, self.thumbholeradius, 0, Direction.SOUTH]])
            self.cutlines.append([PathStyle.LINE, [14, 7, 6, 2, 3, 0, 82]])
            self.cutlines.append([PathStyle.LINE, [83, 1, 4, 5, 9, 8, 17]])

            if self.singlethumbhole:
                self.cutlines.append(right_full)
            else:
                self.cutlines.append(
                    [PathStyle.THUMBHOLE,
                     [85, self.__DEFAULT_THUMBHOLE_SMALL_RADIUS, self.thumbholeradius, 0, Direction.NORTH]])
                self.cutlines.append([PathStyle.LINE, [54, 63, 62, 66, 67, 70, 84]])
                self.cutlines.append([PathStyle.LINE, [85, 71, 68, 69, 65, 64, 57]])

        # detect boundaries of drawing
        self.left_x, self.right_x, self.top_y, self.bottom_y = Design.set_bounds(self.corners)

    def __draw_slot_hole_line(self, xml_string, start, delta):

        # https://stackoverflow.com/questions/25640628/python-adding-lists-of-numbers-with-other-lists-of-numbers
        stop = [sum(values) for values in zip(start, delta)]

        xml_string += Design.draw_line(start, stop)

        return xml_string, stop
