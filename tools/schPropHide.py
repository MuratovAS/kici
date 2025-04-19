from pyparsing import nestedExpr
from pyparsing.exceptions import ParseException
import sys
import os
import logging
import argparse

logging.basicConfig(
    stream=sys.stdout, level=logging.DEBUG, format="{levelname} - {message}", style="{"
)

parser = argparse.ArgumentParser(description="KicadChanger")
parser.add_argument("main_file", help="File kicad")
parser.add_argument("prop_names", help="Property name")
parser.add_argument("prop_value", help="Property value")
args = parser.parse_args()

if not os.path.isfile(args.main_file):
    logging.error(f"Input path to file is required")
    sys.exit(2)

if args.prop_value not in ['yes', 'no']:
    logging.error('Prop value should be "yes" or "no"')
    sys.exit(2)


class KicadChanger():
    def __init__(self, data) -> None:
        self.data = data

    def change_hide_prop(self, prop_name, value):
        if value not in ['yes', 'no']:
            raise Exception('hide prop must be yes or no')

        appends = 0
        changes = 0
        for symbol in self.get_nodes(self.data, 'symbol'):
            for property in self.get_nodes(symbol, 'property'):
                if property[0].replace('"', '') == prop_name:
                    effects = next(self.get_nodes_with_name( property[1:], 'effects'))
                    for param in effects[1:]:
                        if param[0] == 'hide':
                            param[1] = value
                            changes += 1
                            break
                    else:
                        appends += 1
                        effects = effects.append(['hide', value])
        logging.info(f'Changed options "{prop_name}": {changes}')
        logging.info(f'Added options "{prop_name}": {appends}')


    def get_nodes(self, data, node_name):
        "find node with name and return values"
        for node in data:
            if node[0] == node_name:
                yield node[1:]

    def get_nodes_with_name(self, data, node_name):
        "find node with name and return name and value"
        for node in data:
            if node[0] == node_name:
                yield node


class KicadReader():
    def __init__(self, filename) -> None:
        self.filename = filename


    def read_to_lists(self):
        "parse kicad file to the list of lists"
        try:
            with open(self.filename) as f:
                data = f.read()
                parser = nestedExpr(opener='(', closer=')')
                data = parser.parseString(data).asList()[0]

                return data
        except ParseException:
            logging.error('Incorrect file')
            sys.exit(1)

    def convert_to_str(self, node, tab_count=0):
        "convert list of list nodes to the kicad format"
        s = '('
        tab_count += 1
        if isinstance(node, list):
            for number, item in enumerate(node):
                # check if node has node as next element
                list_is_next = isinstance(node[number+1], list) if number < len(node)-1 else False
                # check if node have nodes (in any places)
                list_exists = any([isinstance(item, list) for item in node])
                if isinstance(item, str):
                    s += item
                    s += ' ' if number != len(node)-1 and not list_is_next else ''
                if isinstance(item, list):
                    # some nodes need to be without \n
                    if node[0] == 'pts' and number >= 2:
                        s += ' '
                    else:
                        # most of nodes need \n
                        s += '\n' + '\t'* tab_count
                    s +=   self.convert_to_str(item, tab_count)
                
                if number == len(node)-1:
                    tab = ''
                    if list_exists:
                        tab =  '\n' + '\t' * (tab_count-1)
                    s += tab + ')'
        return s



kicad_reader = KicadReader(args.main_file)
data = kicad_reader.read_to_lists()

kicad_changer = KicadChanger(data)

prop_names = args.prop_names.split(',')
for prop in prop_names:
    kicad_changer.change_hide_prop(prop.strip(), args.prop_value.strip())

data = kicad_reader.convert_to_str(kicad_changer.data)

with open(args.main_file, 'w') as f:
    f.write(data)
    f.write('\n')
