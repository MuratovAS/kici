

from bomverifier.cli_parser import parse_argumetns, OptionsParser
from bomverifier.csv_parser import read_csv_rows, update_row_with_providers, write_rows
from bomverifier.exceptions import MissingDataException

arguments = parse_argumetns()
run_options = OptionsParser(arguments).get_run_options()

updated_rows = []

for number, row in enumerate(read_csv_rows(run_options['input_file']), start=1):
    try:
        update_row_with_providers(row, run_options['qty'], run_options['providers'], number)
    except MissingDataException as e:
        print(f'\033[31mERROR\033[0m: Data error {e}')
    updated_rows.append(row)

write_rows(run_options['output_file'], updated_rows)