import sys
import logging
import argparse

from pyparsing import nestedExpr
from pyparsing.exceptions import ParseException


logging.basicConfig(
    stream=sys.stdout, level=logging.DEBUG, format="{levelname} - {message}", style="{"
)

parser = argparse.ArgumentParser(description="KicadChanger")
parser.add_argument("main_file", help="File kicad")
parser.add_argument('--search_name', help="Property name to find")
parser.add_argument('--search_value', help="Property value to find")
parser.add_argument('--change_name', help="Property name to change")
parser.add_argument('--change_value', help="Property value to change")
args = parser.parse_args()

if not all([args.search_value, args.search_name, args.change_name, args.change_value]):
    logging.error(f"Not found all params")
    sys.exit(2)


class KicadChanger():
    def __init__(self, data) -> None:
        self.data = data

    def change_property(self, find_name, find_value, prop_name, prop_value):
        """
        find_name: prop name searched by
        find_value: prop value searched by
        prop_name: prop name to add or change
        prop_value: prop value to add or change
        """
        changes = 0
        appends = 0
        for symbol in self.get_nodes_with_name(self.data, 'symbol'):
            find_prop = False
            for property in self.get_nodes(symbol[1:], 'property'):
                if property[0].replace('"', '') == find_name and property[1].replace('"', '') == find_value:
                    find_prop = property
                    break
            else:
                continue
            # change or add prop in founded symbol
            for node_number, property in self.get_nodes_with_name_and_nubmer(symbol[1:], 'property'):
                if property[1].replace('"', '') == prop_name:
                    property[2] = f'"{prop_value}"'
                    changes += 1
                    break
            else:
                # add property with current name and with values of searched by property
                symbol.insert(node_number+2, ['property', f'"{prop_name}"', f'"{prop_value}"'] + find_prop[2:])
                appends += 1
        logging.info(f'Changed options "{prop_name}": {changes}')
        logging.info(f'Added options "{prop_name}": {appends}')
                

    def get_nodes(self, data, node_name):
        "Find node with name and return values"
        for node in data:
            if node[0] == node_name:
                yield node[1:]

    def get_nodes_with_name(self, data, node_name):
        "Find node with name and return name and value"
        for node in data:
            if node[0] == node_name:
                yield node

    def get_nodes_with_name_and_nubmer(self, data, node_name):
        "Find node with name and return name and value"
        for number, node in enumerate(data):
            if node[0] == node_name:
                yield (number, node)


class KicadReader():
    def __init__(self, filename) -> None:
        self.filename = filename


    def read_to_lists(self):
        "Parse kicad file to the list of lists"
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
        "Convert list of list nodes to the kicad format"
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
kicad_changer.change_property(args.search_name, args.search_value, args.change_name, args.change_value)

data = kicad_reader.convert_to_str(kicad_changer.data)

with open(args.main_file, 'w') as f:
    f.write(data)
    f.write('\n')
