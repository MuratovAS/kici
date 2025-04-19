import sys
import argparse
import os


class OptionsParser():
    PROVIDERS_LIST = ['lcsc', 'promelec', 'elitan']

    def __init__(self, options) -> None:
        self.options = options
        self._validate()

    def get_run_options(self):
        providers_to_search = []

        for name, value in self.options.items():
            if name in self.PROVIDERS_LIST and value:
                provider = {'name': name, 'search_type': value, 'options': {}}
                providers_to_search.append(provider)

                if self.options.get('lcscRW') and name == 'lcsc':
                    provider['options']['rewrite_column'] = self.options.get('lcscRW')
                
        input_file = self.options.get('input')
        output_file = self.options.get('output')
        qty = self.options.get('qty')

        return {
            'providers': providers_to_search,
            'input_file': input_file,
            'output_file': output_file,
            'qty': qty
        }

    def _validate(self):
        # print('Проверка аргументов')
        if not self.options.get('output'):
            print('CRITICAL: output path is a required argument')
            sys.exit(2)
        if self.options.get('lcscRW') and self.options.get('lcsc'):
            if self.options['lcscRW'] == self.options['lcsc']:
                print('CRITICAL: lcsc and lcscRW must not match')
                sys.exit(2)
        if self.options.get('qty') <= 0:
            print('CRITICAL: qty < 0')
            sys.exit(2)
        if not os.path.isfile(self.options['input']):
            print(f"CRITICAL: file '{self.options['input']}' not found!")
            sys.exit(1)
        # print('Все ок')



def parse_argumetns():
    parser = argparse.ArgumentParser()

    parser.add_argument('input', type=str, help='bom file')
    parser.add_argument('-o', dest='output', type=str, help='path to output file')
    parser.add_argument('-lcsc', choices=['sku', 'pn'], type=str, help='search data from distributor')
    parser.add_argument('-lcscRW', choices=['lcsc', 'pn'], type=str, help='rewrite cells according to distributor data')
    parser.add_argument('-promelec', type=str, nargs='?', const='pn', choices=['pn'], help='search data from distributor (pn only)')
    parser.add_argument('-elitan', nargs='?', const='pn', choices=['pn'], help='search data from distributor (pn only)')
    parser.add_argument('-qty', default=1, type=int, help='number of items in the order')

    args = parser.parse_args()
    args = vars(args)
    return args












