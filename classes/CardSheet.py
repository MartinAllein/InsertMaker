from datetime import datetime
from classes.Design import Design
from classes.PathStyle import PathStyle
from classes.Template import Template
from classes.Direction import Rotation
from classes.ConfigConstants import ConfigConstantsText as Ct
from classes.ConfigConstants import ConfigConstantsTemplate as Cm


class C:
    x_measure = 'x measure'
    y_measure = 'y measure'
    corner_radius = 'corner radius'
    x_separation = 'x separation'
    y_separation = 'y separation'

    x_measure_tdpi = f'{x_measure}{Ct.tdpi}'
    y_measure_tdpi = f'{y_measure}{Ct.tdpi}'
    corner_radius_tdpi = f'{corner_radius}{Ct.tdpi}'
    x_separation_tdpi = f'{x_separation}{Ct.tdpi}'
    y_separation_tdpi = f'{y_separation}{Ct.tdpi}'

    rows = 'rows'
    columns = 'columns'
    # template_name = 'template name'
    template_card_name = 'template card name'


class T:
    footer_card_width = '$FOOTER_CARD_WIDTH$'
    footer_card_height = '$FOOTER_CARD_HEIGHT$'


class CardSheet(Design):
    # Default values
    __DEFAULT_FILENAME: str = 'CardSheet'
    __DEFAULT_TEMPLATE: str = 'CardSheet.svg'
    __DEFAULT_TEMPLATE_CARD: str = 'Card.svg'

    # number of rows and columns of cards per sheet
    __DEFAULT_COLUMNS: int = 2
    __DEFAULT_ROWS: int = 4

    # distance between single rows and columns
    __DEFAULT_X_SEPARATION: float = 0.0
    __DEFAULT_Y_SEPARATION: float = 0.0

    # corner radius of the cards. 0.0 produces rectangular cards
    __DEFAULT_CORNER_RADIUS: float = 3.0

    # standard size of cards is European
    __DEFAULT_X_MEASURE: float = 89.0
    __DEFAULT_Y_MEASURE: float = 55.0

    # Enums
    # TODO: Inner class enums?
    __CUTLINES_CARD_FULL: int = 0
    __CUTLINES_CARD_LEFT_OPEN: int = 1
    __CUTLINES_CARD_TOP_OPEN: int = 2
    __CUTLINES_CARD_TOPLEFT_OPEN: int = 3

    def __init__(self,  **kwargs):
        super().__init__(kwargs)

        self.settings.update({C.x_measure: self.__DEFAULT_X_MEASURE,
                              C.y_measure: self.__DEFAULT_Y_MEASURE,
                              C.corner_radius: self.__DEFAULT_CORNER_RADIUS,
                              C.x_separation: self.__DEFAULT_X_SEPARATION,
                              C.y_separation: self.__DEFAULT_Y_SEPARATION,
                              C.rows: self.__DEFAULT_ROWS,
                              C.columns: self.__DEFAULT_COLUMNS,
                              Ct.template_name: self.__DEFAULT_TEMPLATE,
                              C.template_card_name: self.__DEFAULT_TEMPLATE,

                              })
        self.add_settings_measures([C.x_measure, C.y_measure, C.corner_radius, C.x_separation, C.y_separation])

        # : encloses config values to replace
        self.settings[
            Ct.title] = f'{self.get_project_name_for_title()}' \
                        f'{self.__DEFAULT_FILENAME}-{self.settings.get(C.x_measure)}-{self.settings.get(C.y_measure)}' \
                        f'-{datetime.now().strftime("%Y%m%d-%H%M%S")}'

        self.load_settings(self.config_file_and_section)

        self.convert_settings_measures_to_tdpi()

    def create(self):
        # noinspection DuplicatedCode
        self.__init_design()

        card_template = Template.load_template(self.__DEFAULT_TEMPLATE_CARD)

        if self.settings[C.corner_radius] == 0:
            base_cut = [self.draw_paths(self.corners, self.cutlines_nocorners[self.__CUTLINES_CARD_FULL]),
                        self.draw_paths(self.corners, self.cutlines_nocorners[self.__CUTLINES_CARD_TOP_OPEN]),
                        self.draw_paths(self.corners, self.cutlines_nocorners[self.__CUTLINES_CARD_LEFT_OPEN]),
                        self.draw_paths(self.corners, self.cutlines_nocorners[self.__CUTLINES_CARD_TOPLEFT_OPEN])
                        ]
        else:
            base_cut = [self.draw_paths(self.corners, self.cutlines[self.__CUTLINES_CARD_FULL]),
                        self.draw_paths(self.corners, self.cutlines[self.__CUTLINES_CARD_TOP_OPEN]),
                        self.draw_paths(self.corners, self.cutlines[self.__CUTLINES_CARD_LEFT_OPEN]),
                        self.draw_paths(self.corners, self.cutlines[self.__CUTLINES_CARD_TOPLEFT_OPEN])
                        ]

        rows = self.settings.get(C.rows)
        columns = self.settings.get(C.columns)
        x_separation = self.settings.get(C.x_separation)
        y_separation = self.settings.get(C.y_separation)
        x_measure = self.settings.get(C.x_measure)
        y_measure = self.settings[C.y_measure]

        output = ''
        for row in range(rows):
            for col in range(columns):
                svgpath = base_cut[self.__CUTLINES_CARD_FULL]

                if x_separation == 0.0 and y_separation != 0.0 and col != 0:
                    # Cards are ordered in rows. Left is full others left open
                    svgpath = base_cut[self.__CUTLINES_CARD_LEFT_OPEN]

                if x_separation != 0.0 and y_separation == 0.0 and row != 0:
                    # Cards are ordered in columns. Top is full others left open
                    svgpath = base_cut[self.__CUTLINES_CARD_TOP_OPEN]

                if x_separation == 0.0 and y_separation == 0.0:
                    # No Separation
                    if row == 0 and col != 0:
                        svgpath = base_cut[self.__CUTLINES_CARD_LEFT_OPEN]
                    elif row != 0 and col == 0:
                        svgpath = base_cut[self.__CUTLINES_CARD_TOP_OPEN]
                    elif row != 0 and col != 0:
                        svgpath = base_cut[self.__CUTLINES_CARD_TOPLEFT_OPEN]

                template = {Cm.id: f'{row} - {col}',
                            Cm.svgpath: svgpath,
                            Cm.translate: str(
                                self.unit_to_dpi(
                                    self.settings.get(Ct.x_offset) + (x_measure + x_separation) * col)) + ', ' + str(
                                self.unit_to_dpi(self.settings.get(Ct.y_offset) + (y_measure + y_separation) * row))
                            }

                temp = card_template
                for key in template:
                    temp = temp.replace(key, str(template[key]))

                output += temp

        self.template_variables['TEMPLATE'] = self.__DEFAULT_TEMPLATE
        self.template_variables[Cm.svgpath] = output

        self.template_variables[T.footer_card_width] = str(self.settings.get(C.x_measure)) + ' ' + self.settings.get(Ct.unit)
        self.template_variables[T.footer_card_height] = str(self.settings.get(C.y_measure)) + ' ' + self.settings.get(Ct.unit)

        viewbox_x = round(self.settings.get(Ct.x_offset_tdpi) + (self.right_x - self.left_x) * columns
                          + x_separation * self.conversion_factor() * (columns - 1))
        viewbox_y = round(self.settings.get(Ct.y_offset_tdpi) + (self.bottom_y - self.top_y) * rows
                          + y_separation * self.conversion_factor() * (rows - 1))

        self.template_variables[Cm.viewbox_x] = viewbox_x
        self.template_variables[Cm.viewbox_y] = viewbox_y

        self.write_to_file(self.template_variables)
        print(f'CardSheet "{self.settings.get(Ct.filename)}" created')

    def __init_design(self):

        # -----------------------------------------------------------------------------
        #       a  b                        c  d
        #
        #  m    0--4------------------------8-12
        #       |                              |
        #       |                              |
        #  n    1  5                        9 13
        #       |                              |
        #       |                              |
        #       |                              |
        #       |                              |
        #  o    2  6                       10 14
        #       |                              |
        #       |                              |
        #  p    3--7-----------------------11-15

        # Separation x = 0
        # |--------|--------|
        # |  F     |  LO    |
        # |--------|--------|
        #
        # |--------|--------|
        # |  F     |  LO    |
        # |--------|--------|

        # Separation y = 0
        # |--------| |--------|
        # |   F    | |   F    |
        # |--------| |--------|
        # |   TO   | |   TO   |
        # |--------| |--------|

        # Separation x = 0, y = 0
        # |--------|--------|
        # |   F    |  LO    |
        # |--------|--------|
        # |   TO   |  TLO   |
        # |--------|--------|

        x_measure = self.settings.get(C.x_measure_tdpi)
        y_meaure = self.settings.get(C.y_measure_tdpi)
        corner_radius = self.settings.get(C.corner_radius_tdpi)
        x_offset = self.settings.get(Ct.x_offset)
        y_offset = self.settings.get(Ct.y_offset)

        # X - Points
        a = x_offset
        b = a + corner_radius
        d = a + x_measure
        c = d - corner_radius

        # Y - Points
        m = y_offset
        n = m + corner_radius
        p = m + y_meaure
        o = p - corner_radius

        self.corners = [[a, m], [a, n], [a, o], [a, p],
                        [b, m], [b, n], [d, o], [b, p],
                        [c, m], [c, n], [c, o], [c, p],
                        [d, m], [d, n], [d, o], [d, p]
                        ]

        self.cutlines = [
            [
                # Full Card
                [PathStyle.LINE, [4, 8]],
                [PathStyle.QUARTERCIRCLE_NOMOVE, [8, 13, Rotation.CW]],
                [PathStyle.LINE_NOMOVE, [14]],
                [PathStyle.QUARTERCIRCLE_NOMOVE, [14, 11, Rotation.CW]],
                [PathStyle.LINE_NOMOVE, [11, 7]],
                [PathStyle.QUARTERCIRCLE_NOMOVE, [7, 2, Rotation.CW]],
                [PathStyle.LINE_NOMOVE, [2, 1]],
                [PathStyle.QUARTERCIRCLE_NOMOVE, [1, 4, Rotation.CW]],
            ],
            [
                # Top open
                [PathStyle.QUARTERCIRCLE, [8, 13, Rotation.CW]],
                [PathStyle.LINE_NOMOVE, [14]],
                [PathStyle.QUARTERCIRCLE_NOMOVE, [14, 11, Rotation.CW]],
                [PathStyle.LINE_NOMOVE, [11, 7]],
                [PathStyle.QUARTERCIRCLE_NOMOVE, [7, 2, Rotation.CW]],
                [PathStyle.LINE_NOMOVE, [2, 1]],
                [PathStyle.QUARTERCIRCLE_NOMOVE, [1, 4, Rotation.CW]],
            ],
            [
                # Left open
                [PathStyle.QUARTERCIRCLE, [1, 4, Rotation.CW]],
                [PathStyle.LINE_NOMOVE, [8]],
                [PathStyle.QUARTERCIRCLE_NOMOVE, [8, 13, Rotation.CW]],
                [PathStyle.LINE_NOMOVE, [14]],
                [PathStyle.QUARTERCIRCLE_NOMOVE, [14, 11, Rotation.CW]],
                [PathStyle.LINE_NOMOVE, [11, 7]],
                [PathStyle.QUARTERCIRCLE_NOMOVE, [7, 2, Rotation.CW]],
            ],
            [
                # Top and left open
                [PathStyle.QUARTERCIRCLE, [8, 13, Rotation.CW]],
                [PathStyle.LINE_NOMOVE, [14]],
                [PathStyle.QUARTERCIRCLE_NOMOVE, [14, 11, Rotation.CW]],
                [PathStyle.LINE_NOMOVE, [11, 7]],
                [PathStyle.QUARTERCIRCLE_NOMOVE, [7, 2, Rotation.CW]],
                [PathStyle.LINE_NOMOVE, [2, 1]],
                [PathStyle.QUARTERCIRCLE_NOMOVE, [1, 4, Rotation.CW]],
            ],
        ]

        self.cutlines_nocorners = [
            [
                # Full Card
                [PathStyle.LINE, [0, 12, 15, 3, 0]],
            ],
            [
                # Top open
                [PathStyle.LINE, [12, 15, 3, 0]],
            ],
            [
                # Left open
                [PathStyle.LINE, [0, 12, 15, 3]],
            ],
            [
                # Top and left open
                [PathStyle.LINE, [12, 15, 3]],
            ],

        ]

        # detect boundaries of drawing
        self.set_bounds(self.corners)


def __print_variables(self):
    print(self.__dict__)
