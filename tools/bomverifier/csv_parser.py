import csv
from collections import OrderedDict

from bomverifier.elitan import Elitan
from bomverifier.promelec import Promelec
from bomverifier.lcsc import LCSC
from bomverifier.api import ApiClient


class MissingDataException(Exception):
    pass


class ArgsException(Exception):
    pass


class ApiException(Exception):
    pass


PROVIDER_CLASSES = {
    'promelec': Promelec,
    'elitan': Elitan,
    'lcsc': LCSC
}


def read_csv_rows(filename):
    print(f'Read {filename}')
    with open(filename, newline='', encoding='utf-8') as csvfile:
        rows = csv.reader(csvfile)
        header = next(rows)
        header = [title.lower() for title in header]
        
        for row in rows:
            yield OrderedDict(zip(header, row))


def update_row_with_providers(row, qty, providers, row_number):
    
    # print(f'Строка {row_number}, чтение')
    try:
        qty_total = qty * int(row['qty'])
    except ValueError:
        raise MissingDataException('\033[31mERROR\033[0m: Invalid `qty` value')

    row['qty_total'] = qty_total

    api_client = ApiClient()
    for provider in providers:
        Tab_char = "\t"
        print(f'INFO: ({row_number}) [{provider["name"]}]{Tab_char}pn:{row["pn"]}{Tab_char}{Tab_char}comment:{row["comment"]}')
        provider_class = PROVIDER_CLASSES.get(provider['name'])
        try:
            row_provider = provider_class(api_client, row, qty_total, search_type=provider['search_type'], **provider['options'])
            row_provider.validate()
            row_provider.update_with_data()
            #time.sleep(2)  
        except MissingDataException:
            print(f'\033[33mWARN\033[0m: ({row_number}) [{provider["name"]}]{Tab_char}Component not found')
            row_provider.fill_with_empty_values()
        except ArgsException as e:
            print(f'\033[31mERROR\033[0m: ({row_number}) [{provider["name"]}]{Tab_char}Invalid argument: {e}')
        except ApiException as e:
            row_provider.fill_with_empty_values()
            print(f'\033[31mERROR\033[0m: ({row_number}) [{provider["name"]}]{Tab_char}API is broken: {e}')


def write_rows(output_file, rows):

    # print('Запись строк')
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        if rows:
            writer = csv.DictWriter(csvfile, rows[0].keys(), delimiter=',', dialect=csv.unix_dialect)
            writer.writeheader()
            # print('Запись в файл')
            for row in rows:
                writer.writerow(row)
            print(f'INFO: Number of lines written: {len(rows)}')
        else:
            print('\033[33mWARN\033[0m: No data to record')