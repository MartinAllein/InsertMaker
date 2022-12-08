import argparse
import sys
from classes.Config import Config
import importlib


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


def single_file():
    """ Single config file design

    :return:
    """

    # configuration section is mandatory
    if not args.c:
        print("No section for config file\n-c <config-file> -C <section of config file>")
        sys.exit()

    # read config file and extract the style to dynamically load the class
    style = Config.get_style(args.c, args.C)

    # Import the style from the config file and load the same named class
    try:
        module = importlib.import_module("classes." + style)
        class_ = getattr(module, style)
    except ModuleNotFoundError:
        print(f"Unknown style \"{style}\" in config file {args.c} section {args.C}")
        sys.exit()
    except Exception as inst:
        print("Unknown Error")
        print(type(inst))  # the exception instance
        print(inst.args)  # arguments stored in .args
        print(inst)
        sys.exit()

        # invoke creation of the item
    design = class_()

    # execute the content
    design.create()


def project_file():
    """ Project with multiple configurations

    """
    # -p argument is mandatory
    if not args.p:
        print("No project file.\n-p <project-file>")
        sys.exit()

    # Test if "Project" section exists in project file
    sections = Config.get_sections(args.p)
    if not Config.section_exists(sections, "Project"):
        print(f"Missing section Project in file {args.p}")

    # read Project section

    # read names of all other sections
    for section in sections:
        if not section == "Project":
            print(section)


if __name__ == "__main__":
    outfile = ""

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
    if args.v:
        verbose = True

    # configuration file
    if args.c:
        single_file()
    else:
        if args.p:
            project_file()

    # cardsheet = CardSheet()
    # cardsheet.create()
