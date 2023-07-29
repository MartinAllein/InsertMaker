import json
from datetime import datetime
from enum import Enum
from classes.Design import Design
from classes.PathStyle import PathStyle
from classes.Direction import Rotation
from classes.ThumbholeStyle import ThumbholeStyle
from classes.ItemBoxPartition import ItemBoxPartition
from classes.ConfigConstants import ConfigConstants as C


class EnfordeDesign(Enum):
    NONE = "none"
    SMALL = "small"
    LARGE = "large"
    EMPTY = ""


class Thumbhole(Enum):
    SINGLE = "single"
    DOUBLE = "double"
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

    __DEFAULT_PARTITIONS = []

    __DEFAULT_PARTITION_THUMBHOLE_SMALL_RADIUS = 2
    __DEFAULT_PARTITION_THUMBHOLE_RADIUS = 10
    __DEFAULT_PARTITION_LONGHOLE_RADIUS = 12
    __DEFAULT_PARTITION_LONGHOLE_REST_HEIGHT = 2

    # default tolerance for slots for better mounting
    __DEFAULT_PARTITION_TOLERANCE = 0.5

    # reducing of the height of the separator
    __DEFAULT_PARTITION_HEIGHT_REDUCTION = 2

    # default length for the slot for mounting the separator in the box
    __DEFAULT_PARTITION_MOUNTING_HOLE_LENGTH = 10

    # default separation width
    __DEFAULT_PARTITION_SEPARATION_WIDTH = 10

    # default style of thumbhole
    __DEFAULT_PARTITION_THUMBHOLE_STYLE = ThumbholeStyle.LONGHOLE

    def __init__(self, **kwargs):
        super().__init__(kwargs)

        self.settings.update({'template name': self.__DEFAULT_TEMPLATE})

        self.inner_dimensions = []
        self.outer_dimensions = []

        self.settings.update({'length': self.__DEFAULT_LENGTH,
                              'width': self.__DEFAULT_WIDTH,
                              'height': self.__DEFAULT_HEIGHT,
                              'separated': False,
                              'thumbhole': self.__DEFAULT_THUMBHOLE,
                              'thumbhole radius': self.__DEFAULT_THUMBHOLE_RADIUS,
                              'enforce design': self.__DEFAULT_ENFORCEDESIGN,
                              'vertical separation': self.__DEFAULT_VERTICAL_SEPARATION,
                              'slot width': self.__DEFAULT_SLOT_WIDTH,
                              'corner gap': self.__DEFAULT_CORNER_GAP,
                              'small height': self.__DEFAULT_SMALL_HEIGHT,
                              'partitions config': self.__DEFAULT_PARTITIONS,
                              'partitions single config': []
                              }
                             )

        self.add_settings_measures(["length", "width", "height", "vertical separation", "thumbhole radius",
                                    "corner gap", "slot width",
                                    ])

        self.add_settings_enum({"enforce design": EnfordeDesign,
                                "thumbhole": Thumbhole,
                                })

        self.add_settings_boolean(["separated"])

        self.load_settings(self.config_file, self.config_section)

        self.settings[
            "title"] = f"{self.__DEFAULT_FILENAME}-L{self.settings[C.length]}-W{self.settings[C.width]}-" \
                       f"H{self.settings[C.height]}-S{self.settings[C.thickness]}-" \
                       f"{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        self.convert_measures_to_tdpi()

    def create(self):
        # noinspection DuplicatedCode
        self.__init_design()

        base_cut = Design.draw_lines(self.corners, self.cutlines)

        self.template["TEMPLATE"] = self.__DEFAULT_TEMPLATE
        self.template["$SVGPATH$"] = base_cut

        viewbox_x, viewbox_y = self.set_viewbox(self.right_x, self.bottom_y)

        self.template["VIEWBOX_X"] = viewbox_x
        self.template["VIEWBOX_Y"] = viewbox_y

        # self.template["$FOOTER__OVERALL_WIDTH$"] = str(
        #     round((self.right_x - self.left_x) / self.conversion_factor(), 2))

        self.template["$FOOTER__OVERALL_WIDTH$"] = self.tpi_to_unit(self.right_x - self.left_x)
        self.template["$FOOTER_OVERALL_HEIGHT$"] = self.tpi_to_unit(self.bottom_y - self.top_y)

        self.template["$FOOTER_INNER_LENGTH$"] = self.inner_dimensions[0]
        self.template["$FOOTER_INNER_WIDTH$"] = self.inner_dimensions[1]
        self.template["$FOOTER_INNER_HEIGHT$"] = self.inner_dimensions[2]
        self.template["$FOOTER_OUTER_LENGTH$"] = self.outer_dimensions[0]
        self.template["$FOOTER_OUTER_WIDTH$"] = self.outer_dimensions[1]
        self.template["$FOOTER_OUTER_HEIGHT$"] = self.outer_dimensions[2]

        self.write_to_file(self.template)

        print(
            f"Inner Length: {self.inner_dimensions[0]} , "
            f"Inner Width: {self.inner_dimensions[1]} , "
            f"Inner Height: {self.inner_dimensions[2]}")

        print(
            f"Outer Length: {self.outer_dimensions[0]} , "
            f"Outer Width: {self.outer_dimensions[1]} , "
            f"Outer Height: {self.outer_dimensions[2]}")

        # stop creation when Itembox has no separators
        if "partitions config" not in self.settings:
            return

        foo = self.settings['partitions config']
        bar = json.loads(foo)

        partitions_config = self.get_string_or_list(self.settings["partitions config"])

        if isinstance(partitions_config, list) and len(partitions_config) == 0 or \
                partitions_config == "":
            return

        itembox_separation_arguments = {}
        if isinstance(partitions_config, list):
            itembox_separation_arguments.update({C.config_file: partitions_config[0]})
            itembox_separation_arguments.update({C.config_section: partitions_config[1]})
        else:
            itembox_separation_arguments.update({C.config_file: self.config_file,
                                                 C.config_section: partitions_config})

        itembox_separation_arguments.update(
            {
                C.width: self.settings[C.width],
                C.height: self.settings[C.height],
                C.thickness: self.settings[C.thickness],
                'options': {'project name': self.settings['project name']}
            }
        )

        itemboxpartition = ItemBoxPartition(**itembox_separation_arguments)
        itemboxpartition.create()

    def __init_design(self):
        self.__init_base()

    def __init_base(self):
        #          a    b    c    d    e     f          g                    h          i     j    k    m    n    o
        #                ag                                                                                 ah
        #  q                      10--------------------------------------------------------------50
        #                         |                                                                |
        #                         |                                                                |
        #                         |                                                                |
        #                         |                                                                |
        #                         |                                                                |
        #                         |                                                                |
        #  r                      |                        length                                  |
        #                         |                                                                |
        #  ai                     90---92                                                    96---A0
        #                              |                                                      |
        #  s                           |                                                      |
        #                              |                                                      |
        #                              |                                                      |
        #                              |                                                      |
        #                              |                                                      |
        #                              |                                                      |
        #                              |                                                      |
        #                              |                                                      |
        #  t             86-------13---93---28          32------------------36          40---97---53-------A2
        #                |        |          |          |thickness           |          |          |        |
        #                |        |          |          |                    |          |          |        |
        #  u       0-----87       |          29--------33                    37--------41          |       A3----70
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
        #  x       1-----88       |          30--------34                    38--------42          |       A4----71
        #                |        |          |          |                    |          |          |        |
        #                |        |          |          |                    |          |          |        |
        #  y             89-------18---94---31          35------------------39          43----98--58-------A5
        #                              |                                                      |
        #                              |                                                      |
        #  z                           |                                                      |
        #  aj                     91---95                                                    99---A1
        #  aa                     |                                                                |
        #                         |                          length                                |
        #  ab                     21--------------------------------------------------------------61

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

        length = self.settings['length_tdpi']
        height = self.settings['height_tdpi']
        width = self.settings['width_tdpi']
        thickness = self.settings['thickness_tdpi']

        slot_width = self.settings['slot width_tdpi']
        thumbholeradius = self.settings['thumbhole radius_tdpi']
        corner_gap = self.settings['corner gap_tdpi']

        # noinspection DuplicatedCode
        # X - Points
        a = self.settings["x offset_tdpi"]
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
        q = self.settings['y offset_tdpi']
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

        ag = a + int(height / 2)
        ah = k + int(height / 2)
        ai = q + int(height / 2)
        aj = y + int(height / 2)

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
                        [ag, t], [ag, u], [ag, x], [ag, y], [d, ai], [d, aj], [e, ai], [e, t], [e, y], [e, aj],
                        [j, ai], [j, t], [j, y], [j, aj], [k, ai], [k, aj], [ah, t], [ah, u], [ah, x], [ah, y]
                        ]

        # noinspection DuplicatedCode
        self.inner_dimensions = [self.tpi_to_unit(j - e), self.tpi_to_unit(x - u), self.tpi_to_unit(d - a)]
        self.outer_dimensions = [self.tpi_to_unit(k - d), self.tpi_to_unit(y - t), self.tpi_to_unit(e - a)]
        self.cutlines = []

        if self.settings["enforce design"] is EnfordeDesign.SMALL or \
                (self.tpi_to_unit(height) <= self.settings["small height"] and
                 not self.settings["enforce design"] is EnfordeDesign.LARGE):

            # right with no thumbhole
            right_full = [PathStyle.LINE, [53, 102, 103, 70, 71, 104, 105, 58]]

            # left with no thumbhole
            left_full = [PathStyle.LINE, [13, 86, 87, 0, 1, 88, 89, 18]]

            # left with thumbhole
            left_thumbhole_top = [PathStyle.LINE, [13, 86, 87, 0, 82]]
            left_thumbhole_bottom = [PathStyle.LINE, [83, 1, 88, 89, 18]]

            # right with thumbhole
            right_thumbhole_top = [PathStyle.LINE, [53, 102, 103, 70, 84]]
            right_thumbhole_bottom = [PathStyle.LINE, [85, 71, 104, 105, 58]]

            # upper
            self.cutlines.append([PathStyle.LINE, [93, 92, 90, 10, 50, 100, 96, 97]])
            # middle top
            self.cutlines.append([PathStyle.LINE, [13, 28, 29, 33, 32, 36, 37, 41, 40, 53]])
            # middle bottom
            self.cutlines.append([PathStyle.LINE, [18, 31, 30, 34, 35, 39, 38, 42, 43, 58]])
            # lower
            self.cutlines.append([PathStyle.LINE, [94, 95, 91, 21, 61, 101, 99, 98]])
            # middle left
            self.cutlines.append([PathStyle.LINE, [13, 15, 24, 25, 16, 18]])
            # middle right
            self.cutlines.append([PathStyle.LINE, [53, 55, 46, 47, 56, 58]])
        else:
            # right with no thumbhole
            right_full = [PathStyle.LINE, [54, 63, 62, 66, 67, 70, 71, 68, 69, 65, 64, 57]]

            # left with no thumbhole
            left_full = [PathStyle.LINE, [14, 7, 6, 2, 3, 0, 1, 4, 5, 9, 8, 17]]

            # left with thumbhole
            left_thumbhole_top = [PathStyle.LINE, [14, 7, 6, 2, 3, 0, 82]]
            left_thumbhole_bottom = [PathStyle.LINE, [83, 1, 4, 5, 9, 8, 17]]

            # right with thumbhole
            right_thumbhole_top = [PathStyle.LINE, [53, 54, 63, 62, 66, 67, 70, 84]]
            right_thumbhole_bottom = [PathStyle.LINE, [85, 71, 68, 69, 65, 64, 57]]

            # Top upper, middle left and right, Bottom lower
            self.cutlines.append([PathStyle.LINE,
                                  [10, 11, 22, 23, 12, 15, 24, 25, 16, 19, 26, 27, 20, 21, 61, 60, 49, 48, 59, 56, 47,
                                   46, 55, 52, 45, 44, 51, 50, 10]])

            # middle upper
            self.cutlines.append([PathStyle.LINE, [13, 28, 29, 33, 32, 36, 37, 41, 40, 53]])

            # middle lower
            self.cutlines.append([PathStyle.LINE, [18, 31, 30, 34, 35, 39, 38, 42, 43, 58]])

        if not self.settings['thumbhole']:
            self.cutlines.append(left_full)
            self.cutlines.append(right_full)
        else:
            if self.settings['thumbhole'] is Thumbhole.SINGLE:
                self.cutlines.append(left_thumbhole_top)
                self.cutlines.append(left_thumbhole_bottom)
                self.cutlines.append([PathStyle.HALFCIRCLE, [83, 82, Rotation.CCW]]),
                self.cutlines.append(right_full)
            elif self.settings['thumbhole'] is Thumbhole.DOUBLE:
                self.cutlines.append(left_thumbhole_top)
                self.cutlines.append(left_thumbhole_bottom)
                self.cutlines.append([PathStyle.HALFCIRCLE, [83, 82, Rotation.CCW]]),
                self.cutlines.append(right_thumbhole_top)
                self.cutlines.append(right_thumbhole_bottom)
                self.cutlines.append([PathStyle.HALFCIRCLE, [84, 85, Rotation.CCW]]),
            else:
                self.cutlines.append(right_full)
                self.cutlines.append(left_full)

        # detect boundaries of drawing
        self.left_x, self.right_x, self.top_y, self.bottom_y = self.set_bounds(self.corners)
