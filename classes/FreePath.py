import sys
from datetime import datetime
from classes.Design import Design
from classes.Template import Template
from classes.ConfigConstants import ConfigConstantsText as Ct
from classes.ConfigConstants import ConfigConstantsTemplate as Cm


class C:
    paths = 'paths'
    max_x = 'max x'
    max_y = 'max y'
    # template_name = 'template name'
    template_group = 'template group'

    max_x_tdpi = f'{max_x}{Ct.tdpi}'
    max_y_tdpi = f'{max_y}{Ct.tdpi}'


class FreePath(Design):
    # Default values
    __DEFAULT_FILENAME: str = 'FreePath'
    __DEFAULT_TEMPLATE_FILE: str = 'FreePath.svg'
    __DEFAULT_TEMPLATE_FILE_GROUP: str = 'FreePathGroup.svg'

    # set defaults to A4 paper size
    __DEFAULT_MAX_X = 210
    __DEFAULT_MAX_Y = 297

    def __init__(self, **kwargs):
        super().__init__(kwargs)

        self.settings.update({Ct.template_file: self.__DEFAULT_TEMPLATE_FILE})

        self.settings.update({C.paths: [],
                              C.max_x: self.__DEFAULT_MAX_X,
                              C.max_y: self.__DEFAULT_MAX_Y,
                              # Ct.template_name: self.__DEFAULT_TEMPLATE_FILE,
                              C.template_group: self.__DEFAULT_TEMPLATE_FILE_GROUP
                              })

        self.add_settings_measures([C.max_x, C.max_y])

        self.settings[
            Ct.title] = f'{"" if self.settings.get(Ct.project_name) is None else self.settings.get(Ct.project_name)}' \
                        f'{self.__DEFAULT_FILENAME}-{datetime.now().strftime("%Y%m%d-%H%M%S")}'

        # : encloses config values to replace
        self.load_settings(self.config_file_and_section)

        self.convert_settings_measures_to_tdpi()

    def create(self):
        self.__init_design()

        # list of path elements with their method for indirect function call
        functions = {'R': self.__rectangle,
                     'C': self.__circle,
                     'F': self.__color,
                     'D': self.__dasharray,
                     'L': self.__line}

        output = ""
        card_template = Template.load_template(self.settings.get(C.template_group))
        id_count = 1

        path_groups = self.settings.get(C.paths).split("\n\n")

        for pathlist in path_groups:
            # split path list for a group by carrage return
            # there is only one command per line allowed
            paths = [i.upper() for i in pathlist.split('\n')]
            group_output = ''
            items = {'color': self.settings['stroke color'],
                     'dasharray': self.settings['stroke dasharray']
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

            if group_output != '':
                a = card_template
                a = a.replace(Cm.id, f'{id_count}')
                a = a.replace(Cm.color, self.settings.get(Ct.stroke_color))
                a = a.replace(Cm.dasharray, self.settings.get(Ct.stroke_dasharray))

                id_count += 1
                group_output = a.replace(Cm.svgpath, group_output)

                output += group_output
        self.template_variables[Ct.template_file] = self.__DEFAULT_TEMPLATE_FILE
        self.template_variables[Cm.svgpath] = output

        self.template_variables[Cm.viewbox_x] = self.settings.get(C.max_x_tdpi)
        self.template_variables[Cm.viewbox_y] = self.settings.get(C.max_y_tdpi)

        self.write_to_file(self.template_variables)
        print(f'FreePath "{self.settings.get(Ct.filename)}" created')

    def __init_design(self):
        pass

    def __print_variables(self):
        print(self.__dict__)

    def __rectangle(self, command: str) -> str:
        error = ''
        parameter = command.split(' ')

        # test on validity
        if len(parameter) != 5:
            print('Number of parameters is wrong\n')
            sys.exit(-1)

        if parameter[1] != 'W' and parameter[3] != 'H':
            error = 'W and/or H not on correct position\n'

        if not self.is_float(parameter[2]) or not self.is_float(parameter[4]):
            error += 'Width and/or height not a float\n'

        start_xy = parameter[0].split(',')
        if len(start_xy) != 2:
            error += 'Start point of rectangle must be x,y\n'

        if not self.is_float(start_xy[0]) or not self.is_float(start_xy[1]):
            error += 'x and y of start must be of type float'

        if error:
            print('Error in config file R ' + command + '\n' + error)
            sys.exit(-1)

        start_x = self.unit_to_dpi(float(start_xy[0]) + self.settings.get(Ct.x_offset))
        start_y = self.unit_to_dpi(float(start_xy[1]) + self.settings.get(Ct.y_offset))
        width = self.unit_to_dpi(float(parameter[2]))
        height = self.unit_to_dpi(float(parameter[4]))

        return f'M {start_x} {start_y} h {width} v {height} h {-width} z '

    def __circle(self, command: str) -> str:
        error = ''
        parameter = command.split(' ')

        # test on validity
        if len(parameter) != 2:
            print('Number of parameters is wrong in C ' + command)
            sys.exit(-1)

        start_xy = parameter[0].split(',')
        if len(start_xy) != 2:
            print('Start point of rectangle must be x,y\n')
            sys.exit(-1)

        if not [float(f) for f in start_xy]:
            print('All parameter must be of type float. C ' + command)
            sys.exit(-1)

        start_x = self.unit_to_dpi(float(start_xy[0]) + self.settings.get(Ct.x_offset))
        start_y = self.unit_to_dpi(float(start_xy[1]) + self.settings.get(Ct.y_offset))
        radius = self.unit_to_dpi(float(parameter[1]))
        start_x_left = start_x - radius

        # https: // www.mediaevent.de / tutorial / svg - circle - arc.html
        return f'M {start_x_left} {start_y} a {radius} {radius} 0 1 1 0 1 z '

    def __color(self, command: str) -> dict:
        return {'color': command}

    def __dasharray(self, command: str) -> dict:
        return {'dasharray': command}

    def __line(self, command: str) -> str:
        error = ''
        parameter = command.split(' ')

        # test on validity
        if len(parameter) != 2:
            print('Number of parameters is wrong in L ' + command)
            sys.exit(-1)

        start = parameter[0].split(',')
        end = parameter[1].split(',')

        if len(start) != 2:
            print('Start point of rectangle must be x,y\n')
            sys.exit(-1)

        if len(end) != 2:
            print('End point of rectangle must be x,y\n')
            sys.exit(-1)

        if not [float(f) for f in start]:
            print('Start parameter must be of type float. C ' + command)
            sys.exit(-1)

        if not [float(f) for f in end]:
            print('End parameter must be of type float. C ' + command)
            sys.exit(1)

        start_x = self.unit_to_dpi(float(start[0]) + self.settings.get(Ct.x_offset))
        start_y = self.unit_to_dpi(float(start[1]) + self.settings.get(Ct.y_offset))
        end_x = self.unit_to_dpi(float(end[0]) + self.settings.get(Ct.x_offset))
        end_y = self.unit_to_dpi(float(end[1]) + self.settings.get(Ct.y_offset))

        return f' M {start_x} {start_y} L {end_x} {end_y}'
