import argparse
import sys
from classes.Project import Project
from classes.Single import Single
from classes.ConfigConstants import ConfigConstants as C


def parse_arguments():
    """ Parse arguments

    :return: parsed arguments from command line
    """
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument('-c', type=str, help="Config File")
    parser.add_argument('-C', type=str, required='-c' in sys.argv, help="Config Section")
    parser.add_argument('-p', type=str, help="Project File")
    parser.add_argument('-v', action="store_true", help="verbose")
    parser.add_argument('-n', action="store_true", help="noprint")

    return parser.parse_args()


if __name__ == "__main__":
    outfile = ""

    # parse vom cli
    args = parse_arguments()

    kwargs = {}
    # Verbose output
    verbose = False
    if args.v:
        kwargs["verbose"] = True

    noprint = False
    if args.n:
        kwargs["noprint"] = True

    # test if insertmaker.config exists

    # configuration file
    if args.c:
        kwargs[C.config_file] = args.c
        kwargs[C.config_section] = args.C
        single = Single.create(**kwargs)
        sys.exit(0)

    if args.p:
        kwargs[C.config_file] = args.p
        project = Project(**kwargs)
        project.create()
        sys.exit(0)

