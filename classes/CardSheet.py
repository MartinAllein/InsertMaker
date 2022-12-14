import argparse
import sys
from typing import Any, List
from datetime import datetime
from classes.Design import Design
from classes.Direction import Direction
from classes.PathStyle import PathStyle
from classes.Template import Template


class CardSheet(Design):
    __DEFAULT_FILENAME = "CardSheet"
    __DEFAULT_TEMPLATE = "CardSheet.svg"
    __DEFAULT_TEMPLATE_CARD = "Card.svg"

    __DEFAULT_COLUMNS = 1
    __DEFAULT_ROWS = 1

    __DEFAULT_X_SEPARATION = 0
    __DEFAULT_Y_SEPARATION = 0

    # __DEFAULT_VERTICAL_SEPARATION = 6

    __DEFAULT_CORNER_RADIUS = 3

    __DEFAULT_X_MEASURE = 89
    __DEFAULT_Y_MEASURE = 55

    __CUTLINES_CARD_FULL = int(0)
    __CUTLINES_CARD_LEFT_OPEN = int(1)
    __CUTLINES_CARD_TOP_OPEN = int(2)
    __CUTLINES_CARD_TOPLEFT_OPEN = int(3)

    def __init__(self, config_file: str, section: str, verbose=False, **kwargs):
        super().__init__()

        # load built in default values
        self.__set_defaults()

        payload = {}

        if 'options' in kwargs:
            payload['options'] = kwargs['options']

        project_name = ""
        if 'project name' in payload['options']:
            project_name = f"{payload['options']['project name']}-"

        payload['default_name'] = f"{project_name}{self.__DEFAULT_FILENAME}-L{self.x_measure}-W{self.y_measure}-" \
                                  f"{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        payload['convert_values'] = ["x_measure", "y_measure", "x_separation",
                                     "y_separation", "corner_radius"]

        payload['default_values'] = {'x separation': self.x_separation,
                                     'y separation': self.y_separation,
                                     'rows': self.column_count,
                                     'columns': self.row_count,
                                     'x measure': self.x_measure,
                                     'y measure': self.y_measure,
                                     'corner radius': self.corner_radius,
                                     'project name': "",
                                     'filename': "",
                                     'title': "",
                                     }

        config = super().configuration(config_file, section, verbose, payload)

        self.x_separation = float(config.get(section, 'x separation'))
        self.y_separation = float(config.get(section, 'y separation'))
        self.row_count = int(config.get(section, 'rows'))
        self.column_count = int(config.get(section, 'columns'))
        self.x_measure = float(config.get(section, 'x measure'))
        self.y_measure = float(config.get(section, 'y measure'))
        self.corner_radius = float(config.get(section, 'corner radius'))

        # Convert all measures to thousands dpi
        to_convert = ["x_measure", "y_measure", "x_separation",
                      "y_separation", "corner_radius"]

        self.convert_all_to_thoudpi(to_convert)

    def __set_defaults(self):
        """ Set default values for all variables from built in values"""

        self.args_string = ' '.join(sys.argv[1:])

        self.x_measure = 0.0
        self.y_measure = 0.0
        self.corner_radius = 0.0

        self.x_separation = self.__DEFAULT_X_SEPARATION
        self.y_separation = self.__DEFAULT_Y_SEPARATION
        self.row_count = self.__DEFAULT_COLUMNS
        self.column_count = self.__DEFAULT_ROWS

        self.inner_dimensions = []
        self.outer_dimensions = []

    def create(self):
        # noinspection DuplicatedCode
        self.__init_design()

        self.template["FILENAME"] = self.outfile
        self.template["$FILENAME$"] = self.outfile
        self.template["$PROJECT$"] = self.project_name
        self.template["$TITLE$"] = self.title
        self.template["$LABEL_X$"] = self.thoudpi_to_dpi(self.left_x)

        card_template = Template.load_template(self.__DEFAULT_TEMPLATE_CARD)

        base_cut = [self.draw_lines(self.corners, self.cutlines[self.__CUTLINES_CARD_FULL]),
                    self.draw_lines(self.corners, self.cutlines[self.__CUTLINES_CARD_TOP_OPEN]),
                    self.draw_lines(self.corners, self.cutlines[self.__CUTLINES_CARD_LEFT_OPEN]),
                    self.draw_lines(self.corners, self.cutlines[self.__CUTLINES_CARD_TOPLEFT_OPEN])
                    ]

        output = ""
        for row in range(self.row_count):
            for col in range(self.column_count):
                cut = base_cut[self.__CUTLINES_CARD_FULL]

                if self.x_separation == 0.0 and self.y_separation != 0.0 and col != 0:
                    # Cards are ordered in rows. Left is full others left open
                    cut = base_cut[self.__CUTLINES_CARD_LEFT_OPEN]

                if self.x_separation != 0.0 and self.y_separation == 0.0 and row != 0:
                    # Cards are ordered in columns. Top is full others left open
                    cut = base_cut[self.__CUTLINES_CARD_TOP_OPEN]

                if self.x_separation == 0.0 and self.y_separation == 0.0:
                    # No Separation
                    if row == 0 and col != 0:
                        cut = base_cut[self.__CUTLINES_CARD_LEFT_OPEN]
                    elif row != 0 and col == 0:
                        cut = base_cut[self.__CUTLINES_CARD_TOP_OPEN]
                    elif row != 0 and col != 0:
                        cut = base_cut[self.__CUTLINES_CARD_TOPLEFT_OPEN]

                template = {'$ID$': f"{row} - {col}",
                            '$CUT$': cut,
                            '$TRANSLATE$': str(
                                self.thoudpi_to_dpi((self.x_measure + self.x_separation) * col)) + ", " + str(
                                self.thoudpi_to_dpi((self.y_measure + self.y_separation) * row))
                            }

                temp = card_template
                for key in template:
                    temp = temp.replace(key, str(template[key]))

                output += temp

        self.template["TEMPLATE"] = self.__DEFAULT_TEMPLATE
        self.template["$CUT$"] = output

        ycoord = self.bottom_y + self.y_text_spacing + (self.row_count - 1) * (self.y_measure + self.y_separation)

        ycoord += 2 * self.y_text_spacing
        self.template["$LABEL_PROJECT_Y$"] = self.thoudpi_to_dpi(ycoord)

        ycoord += self.y_text_spacing
        self.template["$LABEL_TITLE_Y$"] = self.thoudpi_to_dpi(ycoord)

        ycoord += self.y_text_spacing
        self.template["$LABEL_FILENAME_Y$"] = self.thoudpi_to_dpi(ycoord)

        ycoord += self.y_text_spacing
        self.template["$LABEL_OVERALL_WIDTH_Y$"] = self.thoudpi_to_dpi(ycoord)
        self.template["$LABEL_OVERALL_WIDTH$"] = str(round((self.right_x - self.left_x) / self.FACTOR, 2))

        ycoord += self.y_text_spacing
        self.template["$LABEL_OVERALL_HEIGHT_Y$"] = self.thoudpi_to_dpi(ycoord)
        self.template["$LABEL_OVERALL_HEIGHT$"] = round((self.bottom_y - self.top_y) / self.FACTOR, 2)

        ycoord += self.y_text_spacing
        self.template["$ARGS_STRING_Y$"] = self.thoudpi_to_dpi(ycoord)
        self.template["$ARGS_STRING$"] = self.args_string

        ycoord += self.y_text_spacing

        viewport_x = self.thoudpi_to_dpi(
            round(self.right_x + (self.column_count - 1) * self.x_separation + 2 * self.FACTOR))
        viewport_y = self.thoudpi_to_dpi(ycoord + (int(self.row_count) - 1) * int(self.y_separation))
        self.template[
            "$VIEWPORT$"] = f"{viewport_x}," \
                            f" {viewport_y}"

        self.write_to_file(self.template)
        print(f"CardSheet \"{self.outfile}\" created")

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

        x_measure = self.x_measure
        y_meaure = self.y_measure
        corner_radius = self.corner_radius

        # X - Points
        a = int(self.x_offset)
        b = a + corner_radius
        d = a + x_measure
        c = d - corner_radius

        # Y - Points
        m = int(self.y_offset)
        n = m + corner_radius
        p = m + y_meaure
        o = p - corner_radius

        if self.verbose:
            values_mil = [self.thoudpi_to_mm(s) for s in [a, b, c, d, m, n, o, p]]
            print(f"a: {a} / {values_mil[0]}")
            print(f"b: {b} / {values_mil[1]}")
            print(f"c: {c} / {values_mil[2]}")
            print(f"d: {d} / {values_mil[3]}")

            print(f"m: {m} / {values_mil[4]}")
            print(f"n: {n} / {values_mil[5]}")
            print(f"o: {o} / {values_mil[6]}")
            print(f"q: {p} / {values_mil[7]}")

        self.corners = [[a, m], [a, n], [a, o], [a, p],
                        [b, m], [b, n], [d, o], [b, p],
                        [c, m], [c, n], [c, o], [c, p],
                        [d, m], [d, n], [d, o], [d, p]
                        ]

        self.cutlines = [
            [
                # Top upper, middle left and right, Bottom lower
                [PathStyle.PAIR,
                 [1, 2, 4, 8, 13, 14, 7, 11]],
                [PathStyle.QUARTERCIRCLE, [1, 4, Direction.NORTH]],
                [PathStyle.QUARTERCIRCLE, [8, 13, Direction.EAST]],
                [PathStyle.QUARTERCIRCLE, [14, 11, Direction.SOUTH]],
                [PathStyle.QUARTERCIRCLE, [7, 2, Direction.WEST]]
            ],
            [
                # Top upper, middle left and right, Bottom lower
                [PathStyle.PAIR,
                 [1, 2, 13, 14, 7, 11]],
                [PathStyle.QUARTERCIRCLE, [1, 4, Direction.NORTH]],
                [PathStyle.QUARTERCIRCLE, [8, 13, Direction.EAST]],
                [PathStyle.QUARTERCIRCLE, [14, 11, Direction.SOUTH]],
                [PathStyle.QUARTERCIRCLE, [7, 2, Direction.WEST]]
            ],
            [
                # Top upper, middle left and right, Bottom lower
                [PathStyle.PAIR,
                 [4, 8, 13, 14, 7, 11]],
                [PathStyle.QUARTERCIRCLE, [1, 4, Direction.NORTH]],
                [PathStyle.QUARTERCIRCLE, [8, 13, Direction.EAST]],
                [PathStyle.QUARTERCIRCLE, [14, 11, Direction.SOUTH]],
                [PathStyle.QUARTERCIRCLE, [7, 2, Direction.WEST]]
            ],
            [
                # Top upper, middle left and right, Bottom lower
                [PathStyle.PAIR,
                 [13, 14, 7, 11]],
                [PathStyle.QUARTERCIRCLE, [1, 4, Direction.NORTH]],
                [PathStyle.QUARTERCIRCLE, [8, 13, Direction.EAST]],
                [PathStyle.QUARTERCIRCLE, [14, 11, Direction.SOUTH]],
                [PathStyle.QUARTERCIRCLE, [7, 2, Direction.WEST]]
            ]
        ]

        # detect boundaries of drawing
        self.set_bounds(self.corners)

    def __print_variables(self):
        print(self.__dict__)
