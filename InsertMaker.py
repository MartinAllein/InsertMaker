import argparse
import sys
from classes.Project import Project
from classes.Single import Single


def parse_arguments():
    """ Parse arguments

    :return: parsed arguments from command line
    """
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument('-c', type=str, help="Config File")
    parser.add_argument('-C', type=str, required='-c' in sys.argv, help="Config Section")
    parser.add_argument('-p', type=str, help="Project File")
    # parser.add_argument('-P', type=str, required='-p' in sys.argv, help="Project Section")
    parser.add_argument('-v', action="store_true", help="verbose")

    return parser.parse_args()


if __name__ == "__main__":
    outfile = ""

    # parse vom cli
    args = parse_arguments()

    # Verbose output
    verbose = False

    if args.v:
        verbose = True

    # test if insertmaker.config exists

    # configuration file
    if args.c:
        # single_file()
        single = Single.create(args.c, args.C, verbose)
        sys.exit(0)

    if args.p:
        project = Project(args.p, verbose)
        project.create()
        sys.exit(0)

