import argparse
import configparser
from datetime import datetime
import os
import sys
from classes.Design import Design
from classes.Direction import Direction
from classes.PathStyle import PathStyle
from classes.Config import Config


class CardSheet:
    __DEFAULT_FILENAME = "CardSheet"
    __DEFAULT_TEMPLATE = "templates/CardSheet.svg"
    __DEFAULT_TEMPLATE_CARD = "Card.svg"
    __DEFAULT_TEMPLATE_SEPARATED = "templates/CardSheet.svg"

    __DEFAULT_X_OFFSET = Design.x_offset
    __DEFAULT_Y_OFFSET = Design.y_offset

    __DEFAULT_COLUMNS = 1
    __DEFAULT_ROWS = 1

    __DEFAULT_X_SEPARATION = 0
    __DEFAULT_Y_SEPARATION = 0

    __DEFAULT_VERTICAL_SEPARATION = 6

    __DEFAULT_CORNER_RADIUS = 3

    __DEFAULT_X_MEASURE = 89
    __DEFAULT_Y_MEASURE = 55

    def __init__(self):

        # parse vom cli
        self.args = self.parse_arguments()

        # Verbose output
        if self.args.v:
            self.verbose = True

        # configuration file
        if self.args.c:
            # configuration section
            if not self.args.C:
                print("No section of config file\n-c <config-file> -C <section of config file>")
                sys.exit()
            self.__read_config(self.args.c, self.args.C)

        temp_name = f"{self.__DEFAULT_FILENAME}-L{self.x_measure}-W{self.y_measure}-" \
                    f"-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        if not self.title:
            self.title = temp_name

        if not self.outfile:
            self.outfile = temp_name

        self.outfile = Design.set_svg_extension(self.outfile)

        if self.verbose:
            self.__print_variables()

        # Convert all measures to thousands dpi
        self.__convert_all_to_thoudpi()

    def __read_config(self, filename: str, section: str):
        """ Read configuration from file"""

        # load built in default values
        self.__set_defaults()

        # set default values for reading the config file
        defaults = {'x offset': self.x_offset,
                    'y offset': self.y_offset,
                    'x separation': self.x_separation,
                    'y separation': self.y_separation,
                    'rows': self.column_count,
                    'columns': self.row_count,
                    'x measure': self.x_measure,
                    'y measure': self.y_measure,
                    'corner radius': self.corner_radius,
                    'vertical separation': self.vertical_separation,
                    'project': "",
                    'filename': "",
                    'title': "",
                    }

        config = Config.read_config(defaults, filename, section)

        # Set all configuration values
        self.project = config.get(section, 'project')
        self.outfile = config.get(section, 'filename')
        self.title = config.get(section, 'title').strip('"')
        self.x_offset = int(config.get(section, 'x offset'))
        self.y_offset = int(config.get(section, 'y offset'))
        self.x_separation = int(config.get(section, 'x separation'))
        self.y_separation = int(config.get(section, 'y separation'))
        self.row_count = int(config.get(section, 'rows'))
        self.column_count = int(config.get(section, 'columns'))
        self.x_measure = int(config.get(section, 'x measure'))
        self.y_measure = int(config.get(section, 'y measure'))
        self.corner_radius = int(config.get(section, 'corner radius'))
        self.vertical_separation = int(config.get(section, 'vertical separation'))

        # if verbose, then print all variables to the console
        if self.verbose:
            self.__print_variables()

    def __set_defaults(self):
        """ Set default values for all variables from built in values"""

        self.args_string = ' '.join(sys.argv[1:])

        self.x_measure = 0.0
        self.y_measure = 0.0
        self.corner_radius = 0.0
        self.project = ""
        self.outfile = ""
        self.title = ""

        self.x_offset = self.__DEFAULT_X_OFFSET
        self.y_offset = self.__DEFAULT_Y_OFFSET
        self.x_separation = self.__DEFAULT_X_SEPARATION
        self.y_separation = self.__DEFAULT_Y_SEPARATION
        self.row_count = self.__DEFAULT_COLUMNS
        self.column_count = self.__DEFAULT_ROWS
        self.vertical_separation = self.__DEFAULT_VERTICAL_SEPARATION

        self.template = {}

        self.corners = []
        self.cutlines = []
        self.left_x = 0
        self.right_x = 0
        self.top_y = 0
        self.bottom_y = 0
        self.inner_dimensions = []
        self.outer_dimensions = []

        self.verbose = False

    @staticmethod
    def parse_arguments():
        parser = argparse.ArgumentParser(add_help=False)

        parser.add_argument('-c', type=str, help="config File")
        parser.add_argument('-C', type=str, help="config section")
        parser.add_argument('-v', action="store_true", help="verbose")

        return parser.parse_args()

    def create(self):
        self.__init_design()

        self.template["FILENAME"] = self.outfile
        self.template["$PROJECT$"] = self.project
        self.template["$TITLE$"] = self.title
        self.template["$FILENAME$"] = self.outfile
        self.template["$LABEL_X$"] = Design.thoudpi_to_dpi(self.left_x)

        card_template = Design.read_template(self.__DEFAULT_TEMPLATE_CARD)
        base_cut = Design.draw_lines(self.corners, self.cutlines)

        output = ""
        for row in range(self.row_count):
            for col in range(self.column_count):
                template = {'$ID$': row * self.column_count + col,
                            '$CUT$': base_cut,
                            '$TRANSLATE$': str(
                                Design.thoudpi_to_dpi((self.x_measure + self.x_separation) * col)) + ", " + str(
                                Design.thoudpi_to_dpi((self.y_measure + self.y_separation) * row))
                            }

                temp = card_template
                for key in template:
                    temp = temp.replace(key, str(template[key]))

                output += temp

        self.template["TEMPLATE"] = self.__DEFAULT_TEMPLATE
        self.template["$CUT$"] = output

        ycoord = self.bottom_y + self.vertical_separation + (self.row_count - 1) * (self.y_measure + self.y_separation)

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

        viewport_x = Design.thoudpi_to_dpi(
            round(self.right_x + (self.column_count - 1) * self.x_separation + 2 * Design.FACTOR))
        viewport_y = Design.thoudpi_to_dpi(ycoord + (int(self.row_count) - 1) * int(self.y_separation))
        self.template[
            "$VIEWPORT$"] = f"{viewport_x}," \
                            f" {viewport_y}"

        Design.write_to_file(self.template)

    def __init_design(self):
        self.__init_base()

    def __init_base(self):

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

        x_measure = self.x_measure
        y_meaure = self.y_measure
        corner_radius = self.corner_radius

        # noinspection DuplicatedCode
        # X - Points
        a = int(self.x_offset)
        b = a + corner_radius
        d = a + x_measure
        c = d - corner_radius

        # noinspection DuplicatedCode
        # Y - Points
        m = int(self.y_offset)
        n = m + corner_radius
        p = m + y_meaure
        o = p - corner_radius

        if self.verbose:
            print(f"a: {a} / {Design.thoudpi_to_mm(a)}")
            print(f"b: {b}/ {Design.thoudpi_to_mm(b)}")
            print(f"c: {c}/ {Design.thoudpi_to_mm(c)}")
            print(f"d: {d}/ {Design.thoudpi_to_mm(d)}")

            print(f"m: {m}/ {Design.thoudpi_to_mm(m)}")
            print(f"n: {n}/ {Design.thoudpi_to_mm(n)}")
            print(f"o: {o}/ {Design.thoudpi_to_mm(o)}")
            print(f"q: {p}/ {Design.thoudpi_to_mm(p)}")

        self.corners = [[a, m], [a, n], [a, o], [a, p],
                        [b, m], [b, n], [d, o], [b, p],
                        [c, m], [c, n], [c, o], [c, p],
                        [d, m], [d, n], [d, o], [d, p]
                        ]

        self.cutlines = [
            # Top upper, middle left and right, Bottom lower
            [PathStyle.PAIR,
             [1, 2, 4, 8, 13, 14, 7, 11]],
            [PathStyle.QUARTERCIRCLE, [1, 4, Direction.NORTH]],
            [PathStyle.QUARTERCIRCLE, [8, 13, Direction.EAST]],
            [PathStyle.QUARTERCIRCLE, [14, 11, Direction.SOUTH]],
            [PathStyle.QUARTERCIRCLE, [7, 2, Direction.WEST]]
        ]

        # detect boundaries of drawing
        self.left_x, self.right_x, self.top_y, self.bottom_y = Design.get_bounds(self.corners)

    @staticmethod
    def __draw_slot_hole_line(xml_string, start, delta):

        # https://stackoverflow.com/questions/25640628/python-adding-lists-of-numbers-with-other-lists-of-numbers
        stop = [sum(values) for values in zip(start, delta)]

        xml_string += Design.draw_line(start, stop)

        return xml_string, stop

    def __print_variables(self):
        print(self.__dict__)

    def __convert_all_to_thoudpi(self):
        """ Shift comma of dpi four digits to the right to get acceptable accuracy and only integer numbers"""

        to_convert = ["x_offset", "y_offset", "x_measure", "y_measure", "x_separation", "y_separation", "corner_radius",
                      "vertical_separation"]

        for item in to_convert:
            setattr(self, item, Design.mm_to_thoudpi(getattr(self, item)))
