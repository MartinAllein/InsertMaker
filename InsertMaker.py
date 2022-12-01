from classes.CardSheet import CardSheet
import argparse
import sys
from classes.Config import Config
import importlib
from classes.Design import Design


def parse_arguments():
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument('-c', type=str, help="Config File")
    parser.add_argument('-C', type=str, help="Config Section")
    parser.add_argument('-p', type=str, help="Project File")
    parser.add_argument('-P', type=str, help="Project Section")
    parser.add_argument('-v', action="store_true", help="verbose")

    return parser.parse_args()


def single_file():
    """ Only a single file has to be created"""
    # configuration section is mandatory
    if not args.c:
        print("No section for config file\n-c <config-file> -C <section of config file>")
        sys.exit()

    # read config file and extract the style to dynamically load the class
    style = Config.get_style(args.c, args.C)

    if style is None:
        print(f"No style in config file {args.c} Section {args.C}")
        sys.exit()

    module = importlib.import_module("classes." + style)
    class_ = getattr(module, style)

    # invoke creation of the item
    class_().create()


def project_file():
    """ In a Project file there are multiple projects"""

    # configuration section is mandatory
    if not args.p:
        print("No project file.\n-p <project-file>")
        sys.exit()

    sections = Config.get_sections(args.p)
    if not Config.section_exists(sections, "Project"):
        print(f"Missing section Project in file {args.p}")

    # read Project section

    # read all other sections
    for section in sections:
        if not section == "Project":
            print(section)

    def __config_from_file(self, filename: str, section: str):
        defaults = {'x offset': Design.__DEFAULT_X_OFFSET,
                    'y offset': self.__DEFAULT_Y_OFFSET,
                    'vertical separation': self.__DEFAULT_VERTICAL_SEPARATION,
                    'slot width': self.__DEFAULT_SLOT_WIDTH, 'corner_gap': self.__DEFAULT_CORNER_GAP,
                    'funnel top width': self.__DEFAULT_FUNNEL_TOP_WIDTH,
                    'funnel bottom width': self.__DEFAULT_FUNNEL_BOTTOM_WIDTH,
                    'funnel neck height': self.__DEFAULT_FUNNEL_NECK_HEIGHT, 'thickness': self.__DEFAULT_THICKNESS,
                    'center nose width': self.__DEFAULT_CENTER_NOSE_WIDTH,
                    'length': 0,
                    'width': 0,
                    'height': 0,
                    'project': "",
                    'filename': "",
                    'title': "",
                    'thumbhole': False,
                    'funnel': 'dual with holes',
                    }

        config_file = 'config/' + filename + ".config"
        # Read default values from the config file
        if not os.path.isfile(config_file):
            print("Config file config/" + filename + ".config not found")
            sys.exit()

        # read entries from the configuration file
        config = configparser.ConfigParser(defaults=defaults)
        config.read(config_file)

        if not config.has_section(section):
            print("Section " + section + " in config file config/" + filename + ".config not found")
            sys.exit()

        self.project = config[section]['project'].strip('"')
        self.outfile = config[section]['filename'].strip('"')
        self.title = config[section]['title'].strip('"')
        self.x_offset = int(config[section]['x offset'])
        self.y_offset = int(config[section]['y offset'])
        self.vertical_separation = int(config[section]['vertical separation'])
        self.slot_width = int(config[section]['slot width'])
        self.corner_gap = int(config[section]['corner gap'])
        self.funnel_top_width = int(config[section]['funnel top width'])
        self.funnel_bottom_width = int(config[section]['funnel bottom width'])
        self.funnel_neck_height = int(config[section]['funnel neck height'])
        self.thickness = float(config[section]['thickness'])
        self.center_nose_width = int(config[section]['center nose width'])

        if config.has_option(section, 'funnel'):
            funnel = config[section]['funnel']
            if funnel == "single with hole" or funnel == "single with holes":
                self.thumbhole = True
                self.singlethumbhole = True
                self.singlefunnel = True
            elif funnel == "dual with hole":
                self.thumbhole = True
                self.singlethumbhole = True
                self.singlefunnel = False
            elif funnel == "dual with holes":
                self.thumbhole = True
                self.singlethumbhole = False
                self.singlefunnel = False

        if config.has_option(section, 'enforce design'):
            design = config[section]['enforce design']

            if design == 'small':
                self.enforce_small_design = True
                self.enforce_large_design = False
            elif design == 'large':
                self.enforce_small_design = False
                self.enforce_large_design = True

        self.length = float(config[section]['length'])
        self.width = float(config[section]['width'])
        self.height = float(config[section]['height'])


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
