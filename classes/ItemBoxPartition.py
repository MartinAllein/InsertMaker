from datetime import datetime
from classes.Design import Design
from classes.PathStyle import PathStyle
from classes.Direction import Rotation
from classes.ThumbholeStyle import ThumbholeStyle
from classes.Config import Config
from classes.ConfigConstants import ConfigConstantsText as Ct
from classes.ConfigConstants import ConfigConstantsTemplate as Cm


class C:
    partitions = 'partitions'
    thumbhole_radius = 'thumbhole radius'
    thumbhole_small_radius = 'thumbhole small radius'
    longhole_radius = 'longhole radius'
    longhole_rest_height = 'longhole rest height'
    mounting_hole_length = 'mounting hole length'
    tolerance = 'tolerance'
    height_reduction = 'height reduction'
    thumbhole_style = 'thumbhole style'
    general_filename = 'general filename'

    thumbhole_radius_tdpi = f'{thumbhole_radius}{Ct.tdpi}'
    thumbhole_small_radius_tdpi = f'{thumbhole_small_radius}{Ct.tdpi}'
    longhole_radius_tdpi = f'{longhole_radius}{Ct.tdpi}'
    longhole_rest_height_tdpi = f'{longhole_rest_height}{Ct.tdpi}'
    mounting_hole_length_tdpi = f'{mounting_hole_length}{Ct.tdpi}'
    tolerance_tdpi = f'{tolerance}{Ct.tdpi}'
    height_reduction_tdpi = f'{height_reduction}{Ct.tdpi}'


class ItemBoxPartition(Design):
    __DEFAULT_FILENAME = 'ItemBoxPartition'
    __DEFAULT_TEMPLATE = 'ItemBoxPartition.svg'

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

        self.settings.update({Ct.template_name: self.__DEFAULT_TEMPLATE})

        self.inner_dimensions = []
        self.outer_dimensions = []
        self.partition_settings = []

        # ensure that option exists in kwargs
        _ = kwargs.setdefault(Ct.options, {})

        self.settings.update({Ct.thickness: kwargs[Ct.options].get(Ct.thickness, self.__DEFAULT_THICKNESS),
                              Ct.width: kwargs[Ct.options].get(Ct.width, self.__DEFAULT_WIDTH),
                              Ct.height: kwargs[Ct.options].get(Ct.height, self.__DEFAULT_HEIGHT),
                              Ct.project_name: kwargs[Ct.options].get(Ct.project_name, ''),
                              C.thumbhole_style: self.__DEFAULT_THUMBHOLE_STYLE,
                              C.thumbhole_radius: self.__DEFAULT_THUMBHOLE_RADIUS,
                              C.thumbhole_small_radius: self.__DEFAULT_THUMBHOLE_SMALL_RADIUS,
                              C.longhole_radius: self.__DEFAULT_LONGHOLE_RADIUS,
                              C.longhole_rest_height: self.__DEFAULT_LONGHOLE_REST_HEIGHT,
                              Ct.vertical_separation: self.__DEFAULT_VERTICAL_SEPARATION,
                              C.mounting_hole_length: self.__DEFAULT_MOUNTING_HOLE_LENGTH,
                              C.tolerance: self.__DEFAULT_TOLERANCE,
                              C.height_reduction: self.__DEFAULT_HEIGHT_REDUCTION,
                              C.partitions: ''
                              }
                             )

        self.add_settings_measures([Ct.thickness, Ct.width, Ct.height, C.thumbhole_radius, C.thumbhole_small_radius,
                                    C.longhole_radius, C.longhole_rest_height, Ct.vertical_separation,
                                    C.longhole_rest_height, C.tolerance, C.height_reduction])

        self.add_settings_enum({C.thumbhole_style: ThumbholeStyle,
                                })

        self.add_settings_boolean([Ct.separated])

        # General settings are loaded. Overwritten later by settings for each separation
        self.load_settings(self.config_file_and_section)

        self.settings[
            Ct.title] = f'{self.__DEFAULT_FILENAME}-W{self.settings[Ct.width]}-' \
                        f'H{self.settings[Ct.height]}-S{self.settings[Ct.thickness]}-' \
                        f'{datetime.now().strftime("%Y%m%d-%H%M%S")}'
        self.settings[C.general_filename] = self.settings.get(Ct.title)

        # copy the settings for later use when making the partitions. Before creating a partition
        # the general settings must be restored
        self.general_settings = self.settings.copy()

        if C.partitions in self.settings:
            self.settings[C.partitions] = Config.split_config_lines_to_list(self.settings[C.partitions], 3)

        self.convert_settings_measures_to_tdpi()

    def create(self, output=True):
        # noinspection DuplicatedCode

        for idx, partition in enumerate(self.settings[C.partitions]):

            main_file, _ = Config.get_config_file_and_section(self.config_file_and_section)
            config_file, config_section = Config.get_config_file_and_section(partition, main_file)

            # restore the general settings that the settings from the last separator are
            # reverted.
            self.settings = self.general_settings.copy()
            self.settings[Ct.filename] = self.settings[C.general_filename] + '-' + str(idx + 1)

            # load the settings for the new partition
            self.load_settings(f'{config_file}{Ct.config_separator}{config_section}')
            # self.convert_settings_measures_to_tdpi()
            # self.partition_settings.append(self.settings)

            if output:
                self.__create_single_separation()

    def __create_single_separation(self):

        # noinspection DuplicatedCode
        self.__init_design()
        base_cut = Design.draw_paths(self.corners, self.cutlines)

        self.template_variables[Cm.template] = self.__DEFAULT_TEMPLATE
        self.template_variables[Cm.svgpath] = base_cut

        viewbox_x, viewbox_y = self.get_viewbox(self.right_x, self.bottom_y)

        self.template_variables[Cm.viewbox_x] = viewbox_x
        self.template_variables[Cm.viewbox_y] = viewbox_y

        self.template_variables[Cm.footer_overall_width] = self.tdpi_to_unit(self.right_x - self.left_x)
        self.template_variables[Cm.footer_overall_height] = self.tdpi_to_unit(self.bottom_y - self.top_y)

        self.template_variables['$FOOTER_INNER_LENGTH$'], self.template_variables['$FOOTER_INNER_WIDTH$'], \
            self.template_variables['$FOOTER_INNER_HEIGHT$'] = self.inner_dimensions

        self.template_variables['$FOOTER_OUTER_LENGTH$'], self.template_variables['$FOOTER_OUTER_WIDTH$'], \
        self.template_variables['$FOOTER_OUTER_HEIGHT$'] = self.outer_dimensions

        self.write_to_file(self.template_variables)

        print(
            f'Inner Length: {self.inner_dimensions[0]} , '
            f'Inner Width: {self.inner_dimensions[1]} , '
            f'Inner Height: {self.inner_dimensions[2]}')

        print(
            f'Outer Length: {self.outer_dimensions[0]} , '
            f'Outer Width: {self.outer_dimensions[1]} , '
            f'Outer Height: {self.outer_dimensions[2]}')

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

        self.add_settings_measures([Ct.thickness, Ct.width, Ct.height, C.thumbhole_radius, C.longhole_radius,
                                    C.longhole_rest_height, C.mounting_hole_length,
                                    C.tolerance, C.height_reduction, C.thumbhole_small_radius])

        self.convert_settings_measures_to_tdpi()

        height = self.settings.get(Ct.height_tdpi)
        width = self.settings.get(Ct.width_tdpi)
        thickness = self.settings.get(Ct.thickness_tdpi)

        thumbhole_radius = self.settings.get(C.thumbhole_radius_tdpi)
        longhole_radius = self.settings.get(C.longhole_radius_tdpi)
        longhole_rest_height = self.settings.get(C.longhole_rest_height_tdpi)
        mounting_hole_length = self.settings[C.mounting_hole_length_tdpi]
        tolerance = self.settings.get(C.tolerance_tdpi)
        height_reduction = self.settings.get(C.height_reduction_tdpi)
        thumbhole_small_radius = self.settings.get(C.thumbhole_small_radius_tdpi)

        print(self.settings.get(C.thumbhole_style))
        # noinspection DuplicatedCode
        # X - Points
        a = self.settings.get(Ct.x_offset_tdpi)
        b = int(a + thickness + tolerance)
        if self.settings.get(C.thumbhole_style) is ThumbholeStyle.THUMBHOLE:
            c = int(a + thickness + width / 2 - thumbhole_radius)
        else:
            c = int(a + thickness + width / 2 - longhole_radius)
        d = int(a + thickness + width / 2 - mounting_hole_length / 2)
        h = int(a + width + 2 * thickness)
        e = int(h - thickness - width / 2 + (mounting_hole_length / 2))
        if self.settings.get(C.thumbhole_style) is ThumbholeStyle.THUMBHOLE:
            f = int(h - thickness - width / 2 + thumbhole_radius)
        else:
            f = int(h - thickness - width / 2 + longhole_radius)

        g = h - thickness - tolerance
        o = c - thumbhole_small_radius
        p = f + thumbhole_small_radius

        # noinspection DuplicatedCode
        # Y - Points
        i = self.settings.get(Ct.y_offset_tdpi)

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
        self.inner_dimensions = [self.tdpi_to_unit(thickness), self.tdpi_to_unit(g - b), self.tdpi_to_unit(m - i)]
        self.outer_dimensions = [self.tdpi_to_unit(thickness), self.tdpi_to_unit(h - a), self.tdpi_to_unit(n - i)]

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
