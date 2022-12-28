import re
import sys
from datetime import datetime
from classes.Design import Design
from classes.Template import Template


class FreePath(Design):
    # Default values
    __DEFAULT_FILENAME: str = "FreePath"
    __DEFAULT_TEMPLATE: str = "FreePath.svg"
    __DEFAULT_TEMPLATE_GROUP: str = "FreePathGroup.svg"

    __DEFAULT_MAX_X = 210
    __DEFAULT_MAX_Y = 297
    __DEFAULT_UNIT = "mm"

    def __init__(self, config_file: str, section: str, verbose=False, **kwargs):
        super().__init__(kwargs)

        payload = {}

        payload['default_values'] = {'paths': [],
                                     'max x': self.__DEFAULT_MAX_X,
                                     'max y': self.__DEFAULT_MAX_Y,
                                     'template': self.__DEFAULT_TEMPLATE,
                                     'template group': self.__DEFAULT_TEMPLATE_GROUP
                                     }

        project_name = self.get_project_name(postfix="-")

        # : encloses config values to replace
        payload['default_name'] = f"{project_name}{self.__DEFAULT_FILENAME}-" \
                                  f"{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        config = super().configuration(config_file, section, verbose, payload)

        # Paths are enclosed with "". split config string into parts with "..." and strip the ""
        self.path_groups = config.get(section, 'paths').split("\n\n")
        self.paths = [i[1:-1].upper() for i in re.findall('".*?"', config.get(section, 'paths'))]

        self.max_x = config.get(section, 'max x')
        self.max_y = config.get(section, 'max y')
        self.template_group_name = config.get(section, 'template group')

        # list of path elements with their method for indirect function call
        self.functions = {'R': self.__rectangle,
                          'C': self.__circle}

        # Convert all measures to thousands dpi
        to_convert = ['max_x', 'max_y']
        self.convert_all_to_thoudpi(to_convert)

    def create(self):
        self.__init_design()

        output = ""
        card_template = Template.load_template(self.template_group_name)
        id_count = 1

        for pathlist in self.path_groups:
            paths = [i[1:-1].upper() for i in re.findall('".*?"', pathlist)]
            group_output = ""
            for path in paths:
                command = path[0]
                if command in self.functions:
                    f = self.functions[command]
                    group_output += f(path[2:])

            if group_output != "":
                a = card_template
                a = a.replace("$ID$", f"{id_count}")
                id_count += 1
                group_output = a.replace("$CUT$", group_output)

                output += group_output

        self.template["$CUT$"] = output

        self.template["VIEWBOX_X"] = self.max_x
        self.template["VIEWBOX_Y"] = self.max_y

        self.write_to_file(self.template)
        print(f"FreePath \"{self.outfile}\" created")

    def __init_design(self):
        pass

    def __print_variables(self):
        print(self.__dict__)

    def __rectangle(self, command: str) -> str:
        error = ""
        parameter = command.split(" ")

        # test on validity
        if len(parameter) != 5:
            print('Number of parameters is wrong\n')
            sys.exit()

        if parameter[1] != 'W' and parameter[3] != 'H':
            error = 'W and/or H not on correct position\n'

        if not self.is_float(parameter[2]) or not self.is_float(parameter[4]):
            error += 'Width and/or height not a float\n'

        start_xy = parameter[0].split(",")
        if len(start_xy) != 2:
            error += 'Start point of rectangle must be x,y\n'

        if not self.is_float(start_xy[0]) or not self.is_float(start_xy[1]):
            error += 'x and y of start must be of type float'

        if error:
            print('Error in config file R ' + command + '\n' + error)
            sys.exit(1)

        start_x = Design.mm_to_dpi(float(start_xy[0]))
        start_y = Design.mm_to_dpi(float(start_xy[1]))
        width = Design.mm_to_dpi(float(parameter[2]))
        height = Design.mm_to_dpi(float(parameter[4]))

        return f"M {start_x} {start_y} h {width} v {height} h {-width} z "

    def __circle(self, command: str) -> str:
        error = ""
        parameter = command.split(" ")

        # test on validity
        if len(parameter) != 2:
            print('Number of parameters is wrong in C ' + command)
            sys.exit()

        start_xy = parameter[0].split(",")
        if len(start_xy) != 2:
            print('Start point of rectangle must be x,y\n')
            sys.exit(1)

        if not [float(f) for f in start_xy]:
            print("All parameter must be of type float. C " + command)
            sys.exit(1)

        start_x = Design.mm_to_dpi(float(start_xy[0]))
        start_y = Design.mm_to_dpi(float(start_xy[1]))
        radius = Design.mm_to_dpi(float(parameter[1]))
        start_x_left = start_x - radius

        # https: // www.mediaevent.de / tutorial / svg - circle - arc.html
        return f"M {start_x_left} {start_y} a {radius} {radius} 0 1 1 0 1 z "
