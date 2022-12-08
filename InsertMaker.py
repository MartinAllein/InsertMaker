import argparse
import sys
from classes.Project import Project
from classes.Single import Single


def parse_arguments():
    """ Parse arguments

    :return: parsed arguments from command line
    """
    # https://stackoverflow.com/questions/25626109/python-argparse-conditionally-required-arguments/70716254#70716254
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument('-c', type=str, help="Config File")
    parser.add_argument('-C', type=str, required='-c' in sys.argv, help="Config Section")
    parser.add_argument('-p', type=str, help="Project File")
    # parser.add_argument('-P', type=str, required='-p' in sys.argv, help="Project Section")
    parser.add_argument('-v', action="store_true", help="verbose")

    return parser.parse_args()


if __name__ == "__main__":
    outfile = ""

    # https://stackoverflow.com/questions/3430372/how-do-i-get-the-full-path-of-the-current-files-directory
    # print(os.path.abspath(os.getcwd()))

    # -l141 -w 97 -h 17.5 -d 5 -s 1.5 -o mbox
    # itembox = ItemBox("-c ItemBox -C ITEMBOX -v")
    # itembox.create()

    # -l90 -w 60 -h 25.5  -b -f 20 -F 30 -u 5 -n 6 -o cardBox -c CardBox -C CARDBOX -v
    # cardbox = CardBox("-c CardBox -C CARDBOX")
    # cardbox.create()

    # -c and -C indicate single item

    # -p Project file that consits of multiple single items

    # parse vom cli
    args = parse_arguments()

    # Verbose output
    verbose = False

    if args.v:
        verbose = True

    # configuration file
    if args.c:
        # single_file()
        single = Single.create(args.c, args.C, verbose)
        sys.exit(0)

    if args.p:
        project = Project(args.p, verbose)
        project.create()
        sys.exit(0)

