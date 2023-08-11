import argparse
import xml.dom.minidom
from classes.Design import Design

from datetime import datetime


class Matchbox(Design):
    __DEFAULT_FILENAME = "Matchbox"

    __DEFAULT_TEMPLATE = "Matchbox.svg"

    __DEFAULT_VERTICAL_SEPARATION = 3

    __DEFAULT_SLOT_WIDTH = 10
    __DEFAULT_CORNER_GAP = 10

    __DEFAULT_LENGTH = 60
    __DEFAULT_WIDTH = 40
    __DEFAULT_HEIGHT = 25

    __DEFAULT_FLAP_SPACE = 5

    def __init__(self, **kwargs):
        super().__init__(kwargs)

        self.settings.update({'template name': self.__DEFAULT_TEMPLATE})


        self.length = 0
        self.width = 0
        self.height = 0
        self.outfile = ""
        self.title = ""
        self.outfile = ''

        self.args = self.parse_arguments()
        self.base_corners = []
        self.base_cutlines = []
        self.base_foldlines = []

        error = ""

        self.length = self.args.l
        self.width = self.args.w
        self.height = self.args.h

        temp_filename = f"{Matchbox.__DEFAULT_FILENAME}-L{self.length}-W{self.width}-H{self.height}-" \
                        f"{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        if not self.args.o:
            self.outfile = temp_filename
        else:
            self.outfile = self.args.o

        if not self.args.t:
            self.title = temp_filename
        else:
            self.title = self.args.t

        if self.outfile[-4:] != '.svg':
            self.outfile += '.svg'

        # Convert int 123.5 to 1235000 to avoid decimal places. 4 decimal places used
        self.length = int(float(self.length) * Design.FACTOR)
        self.width = int(float(self.width) * Design.FACTOR)
        self.height = int(float(self.height) * Design.FACTOR)

        error += self.__check_length(self.length)
        error += self.__check_width(self.width)
        error += self.__check_height(self.height)

        if not error:
            print(error)

    @staticmethod
    def __check_length(value):
        return Matchbox.__check_value('Length', value)

    @staticmethod
    def __check_width(value):
        return Matchbox.__check_value('Width', value)

    @staticmethod
    def __check_height(value):
        return Matchbox.__check_value('Height', value)

    @staticmethod
    def __check_value(description, value):
        string = ""
        if not value:
            string += f" missing {description}\n"
        elif int(value) <= 0:
            string += f"{description} must be greater than zero (Is:{value})"

        return string

    def __str__(self):
        return self.width, self.length, self.height, self.outfile

    def parse_arguments(self):
        parser = argparse.ArgumentParser(add_help=False)

        parser.add_argument('-l', type=float, required=True, help="length of the matchbox")
        parser.add_argument('-w', type=float, required=True, help="width of the matchbox")
        parser.add_argument('-h', type=float, required=True, help="height of the matchbox")
        parser.add_argument('-o', type=str, help="output filename")
        parser.add_argument('-t', type=str, help="title of the matchbox")

        return parser.parse_args()

    def create(self):
        self.__init_design()
        base_cut = self.__create_base_cutline()
        base_fold = self.__create_base_foldline()
        wrap_cut = self.__create_wrap_cutline()
        wrap_fold = self.__create_wrap_foldline()

        with open('templates/Matchbox.svg', 'r') as f:
            template = f.read()

        template = template.replace("$BASE-CUT$", base_cut)
        template = template.replace("$BASE-FOLD$", base_fold)
        template = template.replace("$WRAP-CUT$", wrap_cut)
        template = template.replace("$WRAP-FOLD$", wrap_fold)
        template = template.replace("$TITLE$", self.title)
        template = template.replace("$FILENAME$", self.outfile)

        template = template.replace("$LABEL_X$", Design.tdpi_to_dpi(self.base_corners[0][0]))

        ycoord = self.wrap_corners[1][1] + Design.__DEFAULT_Y_LINE_SEPARATION
        template = template.replace("$LABEL_TITLE_Y$", Design.tdpi_to_dpi(ycoord))
        ycoord += Design.__DEFAULT_Y_LINE_SEPARATION
        template = template.replace("$LABEL_FILENAME_Y$", Design.tdpi_to_dpi(ycoord))
        ycoord += Design.__DEFAULT_Y_LINE_SEPARATION
        template = template.replace("$LABEL_BASE_WIDTH_Y$", Design.tdpi_to_dpi(ycoord))
        ycoord += Design.__DEFAULT_Y_LINE_SEPARATION
        template = template.replace("$LABEL_FLAP_WIDTH_Y$", Design.tdpi_to_dpi(ycoord))

        template = template.replace("$LABEL_BASE_WIDTH_X$",
                                    round((self.base_corners[34][0] - self.base_corners[0][0]) / Design.FACTOR, 2))

        template = template.replace("$LABEL_WRAP_WIDTH_X$",
                                    round((self.wrap_corners[10][0] - self.wrap_corners[0][0]) / Design.FACTOR, 2))

        template = template.replace("$TRANSLATE-WRAP$", "0 " + Design.tdpi_to_dpi(self.base_corners[25][1]))

        temp = self.base_corners[25][1] + self.wrap_corners[1][1] + 2 * Design.FACTOR + 4 * Design.__DEFAULT_Y_LINE_SEPARATION
        viewport = f"{Design.tdpi_to_dpi(int(self.base_corners[34][0] + 2 * Design.FACTOR))}," \
                   f" {Design.tdpi_to_dpi(int(temp))}"

        template = template.replace("$VIEWPORT$", viewport)

        dom = xml.dom.minidom.parseString(template)
        template = dom.toprettyxml(newl='')

        with open(f"{self.outfile}", 'w') as f:
            f.write(template)

    def __init_design(self):
        self.__init_base()
        self.__init_wrap()

    def __init_base(self):

        #    a      b     c    d                                    e   f      g       h
        #
        # i                    10----------------------------------18
        #                      |                                    |
        # j               6---11                                    19--26
        #                 |    x                                    x    |
        #                 |    x                                    x    |
        #                 |    x  h                             h   x    |
        #                 |    x                                    x    |
        #                 |    x                                    x    |
        # k               7---12                                    20--27
        #                      |                                    |
        # m         2----------13xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx21---------30
        #           |     h    x                 l                  x          x
        # n  0------3          x                                    x          31----34
        #    |      X          x                                    x          x      |
        #    |      X          x  b                             b   x          x      |
        #    |      X          x                                    x          x      |
        # o  1------4          x                                    x          32----35
        #           |     h    x                 l                  x          x
        # p         5----------14xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx22---------33
        #                      |                                    |
        # q               8---15                                    23--28
        #                 |    x                                    X    |
        #                 |    x                                    X    |
        #                 |    x                                    X    |
        #                 |    x                                    X    |
        #                 |    x                                    X    |
        # r               9---16                                    24--29
        #                      |                                    |
        # s                    17----------------------------------25
        #
        #
        #
        length = self.length
        height = self.height
        width = self.width

        # 1 -2
        fold_width = int(width - 2 * Design.FACTOR)

        # 1 -4
        fold_heigth = int(height - 2 * Design.FACTOR)

        # 7 -8
        flap_height = int(height - 4 * Design.FACTOR)

        # 7 - 12
        flap_width = int(10 * Design.FACTOR)

        # Y - Points
        a = self.__X_OFFSET
        b = fold_heigth
        c = b + height - flap_width
        d = b + height
        e = d + length
        f = e + flap_width
        g = e + height
        h = g + fold_heigth

        # Y - Points
        i = self.__Y_OFFSET
        j = int(i + height / 2 - flap_height / 2)
        k = int(i + height / 2 + flap_height / 2)
        m = i + height
        n = int(m + width / 2 - fold_width / 2)
        o = int(m + width / 2 + fold_width / 2)
        p = m + width
        q = int(p + height / 2 - flap_height / 2)
        r = int(p + height / 2 + flap_height / 2)
        s = p + height

        self.base_corners = [[a, n], [a, o], [b, m], [b, n], [b, o], [b, p], [c, j], [c, k], [c, q], [c, r], [d, i],
                             [d, j],
                             [d, k], [d, m], [d, p], [d, q], [d, r], [d, s], [e, i], [e, j], [e, k], [e, m], [e, p],
                             [e, q],
                             [e, r], [e, s], [f, j], [f, k], [f, q], [f, r], [g, m], [g, n], [g, o], [g, p], [h, n],
                             [h, o]]

        self.base_cutlines = [
            [0, 1, 4, 5, 14, 15, 8, 9, 16, 17, 25, 24, 29, 28, 23, 22, 33, 32, 35, 34, 31, 30, 21, 20, 27,
             26, 19, 18, 10, 11, 6, 7, 12, 13, 2, 3, 0]]
        self.base_foldlines = [[3, 4], [11, 12], [15, 16], [19, 20], [23, 24], [31, 32], [13, 14, 22, 21, 13]]

    def __init_wrap(self):
        #     a              b           c              d           e   f
        #            h            w            h             w        flap_width
        # g   0--------------2-----------4--------------6-----------8
        #     |              |           |              |           | \
        #     |              |           |              |           |  \ flap_retract
        # h   |              |           |              |           |  10
        #     |              |           |              |           |   |
        #     |  l           |           |              |           |   |
        #     |              |           |              |           |   |
        #     |              |           |              |           |   |
        # i   |              |           |              |           |  11
        #     |              |           |              |           |  /
        #     |              |           |              |           | /
        # j   1--------------3-----------5--------------7-----------9

        length = self.length
        height = self.height
        width = self.width

        flap_width = int(10 * Design.FACTOR)
        flap_retract = Design.FLAP_RETRACT

        # Y - Points
        a = self.__X_OFFSET
        b = a + height
        c = b + width
        d = c + height
        e = d + width
        f = e + flap_width

        # g = self.base_corners[25][1] + self.__Y_OFFSET
        g = self.__Y_OFFSET
        h = g + flap_retract
        i = g + length - flap_retract
        j = g + length

        self.wrap_corners = [[a, g], [a, j], [b, g], [b, j], [c, g], [c, j], [d, g], [d, j], [e, g], [e, j], [f, h],
                             [f, i]]

        self.wrap_cutlines = [[0, 1, 9, 11, 10, 8, 0]]
        self.wrap_foldlines = [[2, 3], [4, 5], [6, 7], [8, 9]]

    # TODO: create_base für ein Array von Werten. Parameter corners und lines(cut oder fold)
    # TODO: cutlines und outlines in eine eigene Methode, die dann __create_Lines (jetzt create_base) aufruft

    def __create_base_cutline(self):
        return Design.draw_paths(self.base_corners, self.base_cutlines)

    def __create_base_foldline(self):
        return Design.draw_paths(self.base_corners, self.base_foldlines)

    def __create_wrap_cutline(self):
        return Design.draw_paths(self.wrap_corners, self.wrap_cutlines)

    def __create_wrap_foldline(self):
        return Design.draw_paths(self.wrap_corners, self.wrap_foldlines)

