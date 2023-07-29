from datetime import datetime
from enum import Enum
from classes.Design import Design
from classes.PathStyle import PathStyle
from classes.Direction import Rotation
from classes.ThumbholeStyle import ThumbholeStyle
from classes.ConfigConstants import ConfigConstants as C


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

        thickness = self.__DEFAULT_THICKNESS
        if C.thickness in kwargs:
            thickness = kwargs[C.thickness]

        width = self.__DEFAULT_WIDTH
        if C.width in kwargs:
            width = kwargs[C.width]

        height = self.__DEFAULT_HEIGHT
        if C.height in kwargs:
            height = kwargs[C.height]

        project_name = ""
        if "project name" in kwargs:
            project_name = kwargs["project name"]

        self.settings.update({C.thickness: thickness,
                              C.width: width,
                              C.height: height,
                              'project name': self.settings["project name"],
                              'thumbhole style': self.__DEFAULT_THUMBHOLE_STYLE,
                              'thumbhole radius': self.__DEFAULT_THUMBHOLE_RADIUS,
                              'thumbhole small radius': self.__DEFAULT_THUMBHOLE_SMALL_RADIUS,
                              'longhole radius': self.__DEFAULT_LONGHOLE_RADIUS,
                              'longhole rest height': self.__DEFAULT_LONGHOLE_REST_HEIGHT,
                              'vertical separation': self.__DEFAULT_VERTICAL_SEPARATION,
                              'mounting hole length': self.__DEFAULT_MOUNTING_HOLE_LENGTH,
                              'tolerance': self.__DEFAULT_TOLERANCE,
                              'height reduction': self.__DEFAULT_HEIGHT_REDUCTION,
                              'partitions': []
                              }
                             )

        self.add_settings_measures(["thickness", "width", "height", "thumbhole radius", "thumbhole small radius",
                                    "longhole radius", "longhole rest height", "vertical separation",
                                    "mounting hole length", "tolerance", "height reduction"])

        self.add_settings_enum({"thumbhole style": ThumbholeStyle,
                                })

        self.add_settings_boolean(["separated"])

        # General settings are loaded. Overwritten later by settings for each separation
        self.load_settings(self.config_file, self.config_section)

        self.settings[
            "title"] = f"{self.__DEFAULT_FILENAME}-W{self.settings['width']}-" \
                       f"H{self.settings['height']}-S{self.settings['thickness']}-" \
                       f"{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        if "partitions" in self.settings:
            self.settings['partitions'] = self.get_string_or_list(self.settings['partitions'])

        self.convert_measures_to_tdpi()

    def create(self):
        # noinspection DuplicatedCode


        if "partitions" not in self.settings:
            self.__create_single_separation()
        else:
            for partition in self.settings["partitions"]:
                self.load_settings(self.config_file, self.config_section)
                print(partition)
                if isinstance(partition, list):
                    self.load_settings(partition[0], partition[1])
                else:
                    self.load_settings(self.config_file, partition)

                self.convert_measures_to_tdpi()
                self.__create_single_separation()

    def __create_single_separation(self):

        # noinspection DuplicatedCode
        self.__init_design()
        base_cut = Design.draw_lines(self.corners, self.cutlines)

        self.template["TEMPLATE"] = self.__DEFAULT_TEMPLATE
        self.template["$SVGPATH$"] = base_cut

        viewbox_x, viewbox_y = self.set_viewbox(self.right_x, self.bottom_y)

        self.template["VIEWBOX_X"] = viewbox_x
        self.template["VIEWBOX_Y"] = viewbox_y

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

    def __init_design(self):
        self.__init_base()

    def __init_base(self):

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

        self.add_settings_measures(["thickness", "width", "height", "thumbhole radius", "longhole radius",
                                    "longhole rest height", "vertical separation", "mounting hole length",
                                    "tolerance", "height reduction"])

        height = self.settings['height_tdpi']
        width = self.settings['width_tdpi']
        thickness = self.settings['thickness_tdpi']

        thumbhole_radius = self.settings['thumbhole radius_tdpi']
        longhole_radius = self.settings['longhole radius_tdpi']
        longhole_rest_height = self.settings['longhole rest height_tdpi']
        vertical_separation = self.settings['vertical separation_tdpi']
        mounting_hole_length = self.settings['mounting hole length_tdpi']
        tolerance = self.settings['tolerance_tdpi']
        height_reduction = self.settings['height reduction_tdpi']
        thumbhole_small_radius = self.settings['thumbhole small radius_tdpi']

        # noinspection DuplicatedCode
        # X - Points
        a = self.settings["x offset_tdpi"]
        b = int(a + thickness + tolerance)
        if self.settings['thumbhole style'] is ThumbholeStyle.THUMBHOLE:
            c = int(a + thickness + width / 2 - thumbhole_radius)
        else:
            c = int(a + thickness + width / 2 - longhole_radius)
        d = int(a + thickness + width / 2 - mounting_hole_length / 2)
        h = int(a + width + 2 * thickness)
        e = int(h - thickness - width / 2 + (mounting_hole_length / 2))
        if self.settings['thumbhole style'] is ThumbholeStyle.THUMBHOLE:
            f = int(h - thickness - width / 2 + thumbhole_radius)
        else:
            f = int(h - thickness - width / 2 + longhole_radius)

        g = h - thickness - tolerance
        o = c - thumbhole_small_radius
        p = f + thumbhole_small_radius

        # noinspection DuplicatedCode
        # Y - Points
        i = self.settings['y offset_tdpi']

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

        if self.settings['thumbhole style'] is ThumbholeStyle.THUMBHOLE:
            self.cutlines = [
                [PathStyle.LINE, [17, 1, 2, 3, 4, 7, 8, 10, 9, 14, 13, 16, 15, 20]],
                [PathStyle.QUARTERCIRCLE_NOMOVE, [20, 19, Rotation.CCW]],
                [PathStyle.HALFCIRCLE_NOMOVE, [19, 18, Rotation.CW]],
                [PathStyle.QUARTERCIRCLE_NOMOVE, [18, 17, Rotation.CCW]]
            ]
        elif self.settings['thumbhole style'] is ThumbholeStyle.LONGHOLE:
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

    def __do_partitions(self):
        for partition in self.partitions:
            print(partition)
            if len(partition) == 1:
                # Section is in the Project file
                # Single.create(self.project, item[self.__SECTION_ONLY], **self.kwargs)
                self.settings.update({C.config_file: self.config_file, C.config_section: partition})
                ItemBoxPartition(**self.settings)
            elif len(partition) == 2:
                # section is in a separate file
                # Single.create(item[self.__CONFIG], item[self.__SECTION], **self.kwargs)
                pass
