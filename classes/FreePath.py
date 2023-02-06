import sys
from datetime import datetime
from classes.Design import Design
from classes.Template import Template


class FreePath(Design):
    # Default values
    __DEFAULT_FILENAME: str = "FreePath"
    __DEFAULT_TEMPLATE: str = "FreePath.svg"
    __DEFAULT_TEMPLATE_GROUP: str = "FreePathGroup.svg"

    # set defaults to A4 paper size
    __DEFAULT_MAX_X = 210
    __DEFAULT_MAX_Y = 297
    __DEFAULT_UNIT = "mm"

    def __init__(self, config_file: str, section: str, verbose=False, **kwargs):
        super().__init__(kwargs)

        self.settings.update({'paths': [],
                              'max x': self.__DEFAULT_MAX_X,
                              'max y': self.__DEFAULT_MAX_Y,
                              'template name': self.__DEFAULT_TEMPLATE,
                              'template group': self.__DEFAULT_TEMPLATE_GROUP
                              })

        self.add_settings_measures(["max x", "max y"])

        self.settings[
            "title"] = f"{'' if self.settings['project name'] is None else self.settings['project name']}" \
                       f"{self.__DEFAULT_FILENAME}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        # : encloses config values to replace
        self.load_settings(config_file, section, verbose)

        self.convert_measures_to_tdpi()

    def create(self):
        self.__init_design()

        # list of path elements with their method for indirect function call
        functions = {'R': self.__rectangle,
                     'C': self.__circle,
                     'F': self.__color,
                     'D': self.__dasharray,
                     'L': self.__line}

        output = ""
        card_template = Template.load_template(self.settings['template group'])
        id_count = 1

        path_groups = self.settings["path_groups"] = self.settings["paths"].split("\n\n")

        for pathlist in path_groups:
            # split path list for a group by carrage return
            # there is only one command per line allowed
            paths = [i.upper() for i in pathlist.split('\n')]
            group_output = ""
            items = {"color": self.settings["stroke color"],
                     "dasharray": self.settings["stroke dasharray"]
                     }

            for path in paths:
                # find in configuration entry the occurance of first ' '
                # left of ' ' is the command, right of ' ' is the data for the command
                split_index = path.find(' ')

                command = path
                data = ""
                if split_index != -1:
                    # split config line only if there is at least one ' ' in the line
                    command = path[0:split_index]
                    data = path[split_index + 1:]

                if command in functions:
                    # call the function inderectly that serves the command
                    # group_output += functions[command](data)
                    result = functions[command](data)
                    if type(result) is dict:
                        # https://stackoverflow.com/questions/61225806/how-do-you-find-the-first-item-in-a-dictionary
                        items[next(iter(result))] = next(iter(result.values()))
                    else:
                        group_output += result

            if group_output != "":
                a = card_template
                a = a.replace("$ID$", f"{id_count}")
                a = a.replace("$COLOR$", self.settings['stroke color'])
                a = a.replace("$DASHARRAY$", self.settings['stroke dasharray'])

                id_count += 1
                group_output = a.replace("$SVGPATH$", group_output)

                output += group_output

        self.template["$SVGPATH$"] = output

        self.template["VIEWBOX_X"] = self.settings['max x_tdpi']
        self.template["VIEWBOX_Y"] = self.settings['max y_tdpi']

        self.write_to_file(self.template)
        print(f"FreePath \"{self.settings['filename']}\" created")

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
            sys.exit(-1)

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
            sys.exit(-1)

        start_x = self.to_dpi(float(start_xy[0]) + self.settings['x offset'])
        start_y = self.to_dpi(float(start_xy[1]) + self.settings['y offset'])
        width = self.to_dpi(float(parameter[2]))
        height = self.to_dpi(float(parameter[4]))

        return f"M {start_x} {start_y} h {width} v {height} h {-width} z "

    def __circle(self, command: str) -> str:
        error = ""
        parameter = command.split(" ")

        # test on validity
        if len(parameter) != 2:
            print('Number of parameters is wrong in C ' + command)
            sys.exit(-1)

        start_xy = parameter[0].split(",")
        if len(start_xy) != 2:
            print('Start point of rectangle must be x,y\n')
            sys.exit(-1)

        if not [float(f) for f in start_xy]:
            print("All parameter must be of type float. C " + command)
            sys.exit(-1)

        start_x = self.to_dpi(float(start_xy[0]) + self.settings['x offset'])
        start_y = self.to_dpi(float(start_xy[1]) + self.settings['y offset'])
        radius = self.to_dpi(float(parameter[1]))
        start_x_left = start_x - radius

        # https: // www.mediaevent.de / tutorial / svg - circle - arc.html
        return f"M {start_x_left} {start_y} a {radius} {radius} 0 1 1 0 1 z "

    def __color(self, command: str) -> dict:
        return {"color": command}

    def __dasharray(self, command: str) -> dict:
        return {"dasharray": command}

    def __line(self, command: str) -> str:
        error = ""
        parameter = command.split(" ")

        # test on validity
        if len(parameter) != 2:
            print('Number of parameters is wrong in L ' + command)
            sys.exit(-1)

        start = parameter[0].split(",")
        end = parameter[1].split(",")

        if len(start) != 2:
            print('Start point of rectangle must be x,y\n')
            sys.exit(-1)

        if len(end) != 2:
            print('End point of rectangle must be x,y\n')
            sys.exit(-1)

        if not [float(f) for f in start]:
            print("Start parameter must be of type float. C " + command)
            sys.exit(-1)

        if not [float(f) for f in end]:
            print("End parameter must be of type float. C " + command)
            sys.exit(1)

        start_x = self.to_dpi(float(start[0]) + self.settings['x offset'])
        start_y = self.to_dpi(float(start[1]) + self.settings['y offset'])
        end_x = self.to_dpi(float(end[0]) + self.settings['x offset'])
        end_y = self.to_dpi(float(end[1]) + self.settings['y offset'])

        return f"M {start_x} {start_y} L {end_x} {end_y}"
