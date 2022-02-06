import sys, getopt
import argparse
import xml.dom.minidom
from classes.Design import Design

from datetime import datetime


class Matchbox(Design):
    __DEFAULT_FILENAME = "Matchbox-"

    __X_OFFSET = Design.X_OFFSET
    __Y_OFFSET = Design.Y_OFFSET

    def __init__(self):

        self.length = 111
        self.width = 222
        self.height = 333
        self.outfile = ""
        self.title = ""
        self.outfile = ''

        self.args = self.parse_arguments()
        self.corners = []
        self.cutlines = []
        self.foldlines = []

        error = ""

        self.length = self.args.l
        self.width = self.args.w
        self.height = self.args.h

        temp_filename = Matchbox.__DEFAULT_FILENAME + \
                        f"L{self.length}-W{self.width}-H{self.height}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

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
        self.length = int(float(self.length) * Matchbox.FACTOR)
        self.width = int(float(self.width) * Matchbox.FACTOR)
        self.height = int(float(self.height) * Matchbox.FACTOR)

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
        base_cut, base_fold = self.__create_base()
        viewport = self.get_viewport()

        with open('templates/Matchbox.svg', 'r') as f:
            template = f.read()

        template = template.replace("$BASE-CUT$", base_cut)
        template = template.replace("$BASE-FOLD$", base_fold)
        template = template.replace("$VIEWPORT$", viewport)
        template = template.replace("$TITLE$", self.title)

        dom = xml.dom.minidom.parseString(template)
        template = dom.toprettyxml(newl='')

        with open(f"{self.outfile}", 'w') as f:
            f.write(template)

    def __init_design(self):
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

        self.corners = [Design.Point(a, n), Design.Point(a, o), Design.Point(b, m), Design.Point(b, n),
                        Design.Point(b, o), Design.Point(b, p), Design.Point(c, j), Design.Point(c, k),
                        Design.Point(c, q), Design.Point(c, r), Design.Point(d, i), Design.Point(d, j),
                        Design.Point(d, k), Design.Point(d, m), Design.Point(d, p), Design.Point(d, q),
                        Design.Point(d, r), Design.Point(d, s), Design.Point(e, i), Design.Point(e, j),
                        Design.Point(e, k), Design.Point(e, m), Design.Point(e, p), Design.Point(e, q),
                        Design.Point(e, r), Design.Point(e, s), Design.Point(f, j), Design.Point(f, k),
                        Design.Point(f, q), Design.Point(f, r), Design.Point(g, m), Design.Point(g, n),
                        Design.Point(g, o), Design.Point(g, p), Design.Point(h, n), Design.Point(h, o)]

        self.cutlines = [0, 1, 4, 5, 14, 15, 8, 9, 16, 17, 25, 24, 29, 28, 23, 22, 33, 32, 35, 34, 31, 30, 21, 20, 27,
                         26, 19, 18, 10, 11, 6, 7, 12, 13, 2, 3, 0]
        self.foldlines = [[3, 4], [11, 12], [13, 14], [15, 16], [19, 20], [21, 22], [23, 24], [13, 21], [14, 22],
                          [31, 32]]

    def __create_base(self):
        base_cut = ""
        base_fold = ""

        for idx, num in enumerate(self.cutlines[:-1]):
            base_cut += Design.line(self.corners[self.cutlines[idx]], self.corners[self.cutlines[idx + 1]])

        for idx_outer, num_outer in enumerate(self.foldlines):
            for idx_inner, num_inner in enumerate(num_outer[:-1]):
                base_fold += Design.line(self.corners[self.foldlines[idx_outer][idx_inner]],
                                         self.corners[self.foldlines[idx_outer][idx_inner + 1]])

        return base_cut, base_fold

    def get_viewport(self):
        return f"{Design.convert_coord(int(self.corners[34].x + 2 * Design.FACTOR))}," \
               f" {Design.convert_coord(int(self.corners[25].y + 2 * Design.FACTOR))}"
