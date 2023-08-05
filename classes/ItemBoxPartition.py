from datetime import datetime
from classes.Design import Design
from classes.PathStyle import PathStyle
from classes.Direction import Rotation
from classes.ThumbholeStyle import ThumbholeStyle
from classes.ConfigConstants import ConfigConstants as Cc


class C:
    partitions = "partitions"

    tolerance = "tolerance"
    height_reduction = "height reduction"
    separation_width = "separation width"

    tolerance_tdpi = "tolerance_tdpi"
    height_reduction_tdpi = "height reduction_tdpi"
    separation_width_tdpi = "separation width_tdpi"


class ItemBoxPartition(Design):
    __DEFAULT_FILENAME = "ItemBoxPartition"
    __DEFAULT_TEMPLATE = "ItemBoxPartition.svg"

    __DEFAULT_VERTICAL_SEPARATION = 3

    __DEFAULT_THUMBHOLE_SMALL_RADIUS = 2
    __DEFAULT_THUMBHOLE_RADIUS = 10
    __DEFAULT_LONGHOLE_RADIUS = 10
    __DEFAULT_LONGHOLE_REST_HEIGHT = 2

    # default tolerance for slots for better mounting
    __DEFAULT_TOLERANCE = 0.2

    # reducing of the height of the separator
    __DEFAULT_HEIGHT_REDUCTION = 0

    # default length for the slot for mounting the separator in the box
    __DEFAULT_MOUNTING_HOLE_LENGTH = 10

    # default separation width
    __DEFAULT_SEPARATION_WIDTH = 10

    # default style of thumbhole
    __DEFAULT_THUMBHOLE_STYLE = ThumbholeStyle.NONE

    # Default sizes
    __DEFAULT_WIDTH = 60
    __DEFAULT_HEIGHT = 40
    __DEFAULT_THICKNESS = 1.5

    def __init__(self, **kwargs):
        super().__init__(kwargs)

        self.settings.update({'template name': self.__DEFAULT_TEMPLATE})

        self.inner_dimensions = []
        self.outer_dimensions = []
        self.partition_settings = []

        self.corners_bottom_hole = []
        self.corners_side_slot = []

        self.bottom_cut = ""
        self.slot_cut = ""

        thickness = self.__DEFAULT_THICKNESS
        if Cc.thickness in kwargs:
            thickness = kwargs[Cc.thickness]

        width = self.__DEFAULT_WIDTH
        if Cc.width in kwargs:
            width = kwargs[Cc.width]

        height = self.__DEFAULT_HEIGHT
        if Cc.height in kwargs:
            height = kwargs[Cc.height]

        project_name = ""
        if Cc.project_name in kwargs:
            project_name = kwargs[Cc.project_name]

        self.settings.update({Cc.thickness: thickness,
                              Cc.width: width,
                              Cc.height: height,
                              'project name': project_name,
                              'thumbhole style': self.__DEFAULT_THUMBHOLE_STYLE,
                              'thumbhole radius': self.__DEFAULT_THUMBHOLE_RADIUS,
                              'thumbhole small radius': self.__DEFAULT_THUMBHOLE_SMALL_RADIUS,
                              'longhole radius': self.__DEFAULT_LONGHOLE_RADIUS,
                              'longhole rest height': self.__DEFAULT_LONGHOLE_REST_HEIGHT,
                              'vertical separation': self.__DEFAULT_VERTICAL_SEPARATION,
                              'mounting hole length': self.__DEFAULT_MOUNTING_HOLE_LENGTH,
                              'tolerance': self.__DEFAULT_TOLERANCE,
                              'height reduction': self.__DEFAULT_HEIGHT_REDUCTION,
                              C.separation_width: self.__DEFAULT_SEPARATION_WIDTH,
                              C.partitions: ""
                              }
                             )

        self.add_settings_measures(["thickness", "width", "height", "thumbhole radius", "thumbhole small radius",
                                    "longhole radius", "longhole rest height", "vertical separation",
                                    "mounting hole length", "tolerance", "height reduction", C.separation_width])

        self.add_settings_enum({"thumbhole style": ThumbholeStyle,
                                })

        # General settings are loaded. Overwritten later by settings for each separation
        self.load_settings(self.config_file, self.config_section)

        self.settings[
            "title"] = f"{self.__DEFAULT_FILENAME}-W{self.settings['width']}-" \
                       f"H{self.settings['height']}-S{self.settings['thickness']}-" \
                       f"{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.settings[
            "general filename"] = self.settings["title"][:]

        # copy the settings for later use when making the partitions. Before creating a partition
        # the general settings have to be restored
        self.general_settings = self.settings.copy()

        if C.partitions in self.settings:
            self.settings[C.partitions] = self.split_config_lines_to_list(self.settings[C.partitions], 3)

        self.convert_measures_to_tdpi()

    def create(self, output=True):
        # self.__init_design()
        # noinspection DuplicatedCode

        slot_start_x = 0
        slot_start_y = 0
        bottom_hole_start_x = 0
        bottom_hole_start_y = 0

        slot_cut = ""
        bottom_cut = ""
        last_x = 0
        x_offset = 0

        for idx, partition in enumerate(self.settings[C.partitions]):
            config_file, config_section = self.get_config_file_and_section(self.config_file,
                                                                           partition[0])

            # restore the general settings that the settings from the last separator are
            # reverted.
            settings = self.general_settings.copy()
            # to generate different default filenames the index of the partition is added to
            # the default filename
            settings[Cc.filename] = settings["general filename"] + "-" + str(idx + 1)

            # load the settings for the new partition
            settings = self.load_settings(self.config_file, config_section, settings)

            self.__init_design(settings)

            # store the settings for the partitions in an array for later use. This is when
            # the ItemBox requests the settings to create the bottom hole and the side slots

            settings = self.settings.copy()
            settings.update({"corners bottom hole": self.corners_bottom_hole,
                             "corners side slot": self.corners_side_slot})

            x_offset = x_offset + settings[C.separation_width_tdpi]
            last_x, cut = self.__init_bottom_slot(x_offset, 0)
            bottom_cut += " " + cut

            last_x, cut = self.__init_side_slot(x_offset, 0)
            slot_cut += " " + cut
            x_offset = last_x

            # self.partition_settings.append( self.settings.copy())
            self.partition_settings.append(settings)

            if output:
                self.__create_single_partition(settings)

        self.bottom_cut = bottom_cut
        self.slot_cut = slot_cut

    def get_partition_settings(self):
        self.create(False)
        return self.partition_settings

    def __create_single_partition(self, settings=None):

        if len(settings) is None:
            settings = self.settings

        # noinspection DuplicatedCode
        base_cut = Design.draw_lines(self.corners, self.cutlines)

        template = {
            Cc.template: self.__DEFAULT_TEMPLATE,
            Cc.svgpath: base_cut}

        viewbox_x, viewbox_y = self.get_viewbox(self.right_x, self.bottom_y)

        template.update({"VIEWBOX_X": viewbox_x,
                         "VIEWBOX_Y": viewbox_y,
                         "$FOOTER__OVERALL_WIDTH$": self.tpi_to_unit(self.right_x - self.left_x),
                         "$FOOTER_OVERALL_HEIGHT$": self.tpi_to_unit(self.bottom_y - self.top_y),
                         "$FOOTER_INNER_LENGTH$": self.inner_dimensions[0],
                         "$FOOTER_INNER_WIDTH$": self.inner_dimensions[1],
                         "$FOOTER_INNER_HEIGHT$": self.inner_dimensions[2],
                         "$FOOTER_OUTER_LENGTH$": self.outer_dimensions[0],
                         "$FOOTER_OUTER_WIDTH$": self.outer_dimensions[1],
                         "$FOOTER_OUTER_HEIGHT$": self.outer_dimensions[2],
                         })

        self.write_to_file(template, settings)

        print(
            f"Inner Length: {self.inner_dimensions[0]} , "
            f"Inner Width: {self.inner_dimensions[1]} , "
            f"Inner Height: {self.inner_dimensions[2]}")

        print(
            f"Outer Length: {self.outer_dimensions[0]} , "
            f"Outer Width: {self.outer_dimensions[1]} , "
            f"Outer Height: {self.outer_dimensions[2]}")

    def __init_design(self, settings=None):
        if settings is None:
            settings = self.settings
        self.__init_base(settings)
        # self.__init_bottom_slot()
        # self.__init_side_slot()

    def __init_base(self, settings):

        #         a     b    o  c d          e f   p   g     h
        #  i      01--------17-05--------------11-20--------15
        #         |         \   |              |  /          |
        #  q      |           \18              19/           |
        #         |             |              |             |
        #         |             |              |             |
        #         |             |              |             |
        #  j      02---03       |              |       13---16
        #  k            |      06              12      |
        #               |        \            /        |
        #               |         \----------/         |
        #               |                              |
        #               |                              |
        #   m           04--------07        09--------14
        #                          |        |
        #                          |        |
        #   n                      08-------10

        settings.update(self.convert_measures_to_tdpi(settings))

        height = settings['height_tdpi']
        width = settings['width_tdpi']
        thickness = settings['thickness_tdpi']

        thumbhole_radius = settings['thumbhole radius_tdpi']
        longhole_radius = settings['longhole radius_tdpi']
        longhole_rest_height = settings['longhole rest height_tdpi']
        vertical_separation = settings['vertical separation_tdpi']
        mounting_hole_length = settings['mounting hole length_tdpi']
        tolerance = settings['tolerance_tdpi']
        height_reduction = settings['height reduction_tdpi']
        thumbhole_small_radius = settings['thumbhole small radius_tdpi']

        # noinspection DuplicatedCode
        # X - Points
        a = settings["x offset_tdpi"]
        b = int(a + thickness + tolerance)
        if settings['thumbhole style'] is ThumbholeStyle.THUMBHOLE:
            c = int(a + thickness + width / 2 - thumbhole_radius)
        else:
            c = int(a + thickness + width / 2 - longhole_radius)
        d = int(a + thickness + width / 2 - mounting_hole_length / 2)
        h = int(a + width + 2 * thickness)
        e = int(h - thickness - width / 2 + (mounting_hole_length / 2))
        if settings['thumbhole style'] is ThumbholeStyle.THUMBHOLE:
            f = int(h - thickness - width / 2 + thumbhole_radius)
        else:
            f = int(h - thickness - width / 2 + longhole_radius)

        g = h - thickness - tolerance
        o = c - thumbhole_small_radius
        p = f + thumbhole_small_radius

        # noinspection DuplicatedCode
        # Y - Points
        i = settings['y offset_tdpi']

        j = int(i + (height - height_reduction) / 2)
        m = i + height - height_reduction
        k = m - longhole_radius - longhole_rest_height
        n = m + thickness - tolerance
        q = i + thumbhole_small_radius

        # noinspection DuplicatedCode
        self.corners = [[a, i], [a, i], [a, j], [b, j], [b, m], [c, i], [c, k], [d, m], [d, n],
                        [e, m], [e, n], [f, i], [f, k], [g, j], [g, m], [h, i], [h, j],
                        [o, i], [c, q], [f, q], [p, i]
                        ]

        # noinspection DuplicatedCode
        self.inner_dimensions = [self.tpi_to_unit(thickness), self.tpi_to_unit(g - b), self.tpi_to_unit(m - i)]
        self.outer_dimensions = [self.tpi_to_unit(thickness), self.tpi_to_unit(h - a), self.tpi_to_unit(n - i)]

        if settings['thumbhole style'] is ThumbholeStyle.THUMBHOLE:
            self.cutlines = [
                [PathStyle.LINE, [17, 1, 2, 3, 4, 7, 8, 10, 9, 14, 13, 16, 15, 20]],
                [PathStyle.QUARTERCIRCLE_NOMOVE, [20, 19, Rotation.CCW]],
                [PathStyle.HALFCIRCLE_NOMOVE, [19, 18, Rotation.CW]],
                [PathStyle.QUARTERCIRCLE_NOMOVE, [18, 17, Rotation.CCW]]
            ]
        elif settings['thumbhole style'] is ThumbholeStyle.LONGHOLE:
            self.cutlines = [
                [PathStyle.LINE, [17, 1, 2, 3, 4, 7, 8, 10, 9, 14, 13, 16, 15, 20]],
                [PathStyle.QUARTERCIRCLE_NOMOVE, [20, 19, Rotation.CCW]],
                [PathStyle.LINE_NOMOVE, [19, 12]],
                [PathStyle.HALFCIRCLE_NOMOVE, [12, 6, Rotation.CW]],
                [PathStyle.LINE_NOMOVE, [6, 18]],
                [PathStyle.QUARTERCIRCLE_NOMOVE, [18, 17, Rotation.CCW]]
            ]
        else:
            self.cutlines = [
                [PathStyle.LINE, [1, 2, 3, 4, 7, 8, 10, 9, 14, 13, 16, 15, 1]]
            ]

        # detect boundaries of drawing
        self.left_x, self.right_x, self.top_y, self.bottom_y = self.set_bounds(self.corners)
        self.settings = settings

    def __init_side_slot(self, start_x=0, start_y=0) -> (int, str):
        #          A------b
        #          |      |
        #          |      |
        #          |      |
        #          |      |
        #          c------d
        # Start point in caps (A)

        width = self.settings[Cc.thickness_tdpi] + 2 * self.settings[C.tolerance_tdpi]

        height = int(self.settings[C.height_reduction_tdpi]
                     + (self.settings[Cc.height_tdpi] - self.settings[C.height_reduction_tdpi]) / 2
                     + self.settings[C.tolerance_tdpi])

        ax = start_x
        ay = start_y
        bx = ax + width
        by = ay
        cx = ax
        cy = ay + height
        dx = ax
        dy = cy

        corners_side_slot = [[ax, ay], [bx, by], [cx, cy], [dx, dy]]
        cutlines_side_slot = [[PathStyle.LINE, [0, 2, 3, 1]]]
        cut = Design.draw_lines(corners_side_slot, cutlines_side_slot, raw=True)

        return bx, cut

    def __init_bottom_slot(self, start_x=0, start_y=0) -> (int, str):
        #           TOP
        #          A      b
        #          |      |
        #          |      |
        #          |      |
        #          |      |
        #          c------d
        # Start point in caps (A)
        # formatting: off
        width = self.settings[Cc.thickness_tdpi] + 2 * self.settings[C.tolerance_tdpi]
        height = self.settings[Cc.height_tdpi] - self.settings["mounting hole length_tdpi"] + \
                 2 * self.settings[C.tolerance_tdpi]
        # formatting: on

        ax = start_x
        ay = start_y
        bx = ax + width
        by = ay
        cx = ax
        cy = ay + height
        dx = ax
        dy = cy

        corners_bottom_hole = [[ax, ay], [bx, by], [cx, cy], [dx, dy]]
        cutlines_bottom_hole = [[PathStyle.LINE, [0, 1, 2, 3]]]
        cut = Design.draw_lines(corners_bottom_hole, cutlines_bottom_hole, raw=True)

        return bx, cut
