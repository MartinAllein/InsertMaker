import sys, getopt
import argparse
import xml.dom.minidom

from datetime import datetime
from collections import namedtuple

length = 0
width = 0
height = 0
outfile = ""
title = ""

FACTOR = 720000 / 25.4
X_OFFSET = int(1 * FACTOR)
Y_OFFSET = int(1 * FACTOR)
DEFAULT_FILENAME = "Matchbox-"

xml_line = '<line x1="%s"  y1="%s"  x2="%s" y2="%s" />\n'

corners = []

Point = namedtuple('Point', 'x y')


def main(argv):
    global length
    global width
    global height
    global outfile
    global title

    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument('-l', type=float, required=True, help="length of the matchbox")
    parser.add_argument('-w', type=float, required=True, help="width of the matchbox")
    parser.add_argument('-h', type=float, required=True, help="height of the matchbox")
    parser.add_argument('-o', type=str, help="output filename")
    parser.add_argument('-t', type=str, help="title of the matchbox")

    args = parser.parse_args()

    infile = ''
    outfile = ''
    error = ""

    length = args.l
    width = args.w
    height = args.h

    temp_filename = DEFAULT_FILENAME + f"L{length}-W{width}-H{height}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    if not args.o:
        outfile = temp_filename
    else:
        outfile = args.o

    if not args.t:
        title = temp_filename
    else:
        title = args.t

    if outfile[-4:] != '.svg':
        outfile += '.svg'

    # Convert int 123.5 to 1235000 to avoid decimal places. 4 decimal places used
    length = int(float(length) * FACTOR)
    width = int(float(width) * FACTOR)
    height = int(float(height) * FACTOR)

    error += check_length(length)
    error += check_width(width)
    error += check_height(height)

    if not error:
        print(error)

    return


def check_length(value):
    return check_value('Length', value)


def check_width(value):
    return check_value('Width', value)


def check_height(value):
    return check_value('Height', value)


def check_value(description, value):
    string = ""
    if not value:
        string += f" missing {description}\n"
    elif int(value) <= 0:
        string += f"{description} must be greater than zero (Is:{value})"

    return string


def convert_coord(coord):
    if coord == 0:
        value = "00000"
    else:
        value = str(coord)

    return value[:-4] + "." + value[-4:]


def line(start, end):
    start_x = convert_coord(start.x)
    start_y = convert_coord(start.y)
    end_x = convert_coord(end.x)
    end_y = convert_coord(end.y)

    return xml_line % (start_x, start_y, end_x, end_y)


def create_base():
    pass


def write_to_file():
    pass


if __name__ == "__main__":
    main(sys.argv[1:])

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

    # 1 -2
    foldWidth = int(width - 2 * FACTOR)

    # 1 -4
    foldHeigth = int(height - 2 * FACTOR)

    # 7 -8
    flapHeight = int(height - 4 * FACTOR)

    # 7 - 12
    flapWidth = int(10 * FACTOR)

    # Y - Points
    a = X_OFFSET
    b = foldHeigth
    c = b + height - flapWidth
    d = b + height
    e = d + length
    f = e + flapWidth
    g = e + height
    h = g + foldHeigth

    # Y - Points
    i = Y_OFFSET
    j = int(i + height / 2 - flapHeight / 2)
    k = int(i + height / 2 + flapHeight / 2)
    m = i + height
    n = int(m + width / 2 - foldWidth / 2)
    o = int(m + width / 2 + foldWidth / 2)
    p = m + width
    q = int(p + height / 2 - flapHeight / 2)
    r = int(p + height / 2 + flapHeight / 2)
    s = p + height

    corners = [Point(a, n), Point(a, o), Point(b, m), Point(b, n), Point(b, o), Point(b, p),
               Point(c, j), Point(c, k), Point(c, q), Point(c, r), Point(d, i), Point(d, j),
               Point(d, k), Point(d, m), Point(d, p), Point(d, q), Point(d, r), Point(d, s),
               Point(e, i), Point(e, j), Point(e, k), Point(e, m), Point(e, p), Point(e, q),
               Point(e, r), Point(e, s), Point(f, j), Point(f, k), Point(f, q), Point(f, r),
               Point(g, m), Point(g, n), Point(g, o), Point(g, p), Point(h, n), Point(h, o)]

    cutlines = [0, 1, 4, 5, 14, 15, 8, 9, 16, 17, 25, 24, 29, 28, 23, 22, 33, 32, 35, 34, 31, 30, 21, 20, 27, 26, 19,
                18, 10, 11, 6, 7, 12, 13, 2, 3, 0]
    foldlines = [[3, 4], [11, 12], [13, 14], [15, 16], [19, 20], [21, 22], [23, 24], [13, 21], [14, 22], [31, 32]]

    base_cut = ""
    base_fold = ""

    for idx, num in enumerate(cutlines[:-1]):
        base_cut += line(corners[cutlines[idx]], corners[cutlines[idx + 1]])

    for idx_outer, num_outer in enumerate(foldlines):
        for idx_inner, num_inner in enumerate(num_outer[:-1]):
            base_fold += line(corners[foldlines[idx_outer][idx_inner]], corners[foldlines[idx_outer][idx_inner + 1]])

    viewport = f"{convert_coord(int(corners[34].x + 2 * FACTOR))}, {convert_coord(int(corners[25].y + 2 * FACTOR))}"

    with open('Matchbox.svg', 'r') as f:
        template = f.read()

    template = template.replace("$BASE-CUT$", base_cut)
    template = template.replace("$BASE-FOLD$", base_fold)
    template = template.replace("$VIEWPORT$", viewport)
    template = template.replace("$TITLE$", title)

    dom = xml.dom.minidom.parseString(template)  # or xml.dom.minidom.parseString(xml_string)
    template = dom.toprettyxml(newl='')

    with open(f"{outfile}", 'w') as f:
        f.write(template)
