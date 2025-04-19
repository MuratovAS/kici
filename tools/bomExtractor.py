import csv
import sys
import argparse

def check_string_in_list(lst, str):
    return str in lst

def get_qty(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            qty = int(row['qty_total'])/int(row['qty'])
            break;
    return qty
        
def filter_bom(file_name, designators, fieldnames):
    if check_string_in_list(fieldnames, 'qty_total'):
        qtyALL = get_qty(file_name)
    with open(file_name, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        filtered_data = []
        for row in reader:
            designator_list = [x.strip() for x in row['designator'].split(',')]
            if any(designator in designators.split(',') for designator in designator_list):
                new_row = row.copy()
                new_row['qty'] = '1'
                if len(designator_list) > 1:
                    new_row['designator'] = [designator for designator in designator_list if designator in designators.split(',')]
                    qtyInRow = len(new_row['designator'])
                    new_row['qty'] = qtyInRow
                    new_row['designator'] = ','.join(new_row['designator'])
                    
                    if check_string_in_list(fieldnames, 'qty_total'):
                        new_row['qty_total'] = qtyInRow * int(qtyALL)
                    
                    if check_string_in_list(fieldnames, 'promelec_stock'):
                        if row['promelec_stock'] != '':
                            if int(row['promelec_stock']) > qtyInRow:
                                new_row['promelec_enough'] = True
                            else:
                                new_row['promelec_enough'] = False

                    if check_string_in_list(fieldnames, 'lcsc_stock'):
                        if row['lcsc_stock'] != '':
                            if int(row['lcsc_stock']) > qtyInRow:
                                new_row['lcsc_enough'] = True
                            else:
                                new_row['lcsc_enough'] = False
                        
                filtered_data.append(new_row)
        return filtered_data

def get_columns(file_name):
    columns = []
    with open(file_name, 'r') as file:
        for i, line in enumerate(file):
            if i == 0: # первая строка - заголовок
                columns = line.strip().replace("'", "").replace('"', '').split(',')
            else:
                break
    return columns

def expand_arg(arg):
    result = []
    for column in arg.split(','):
        if '-' in column:
            start, end = column.split('-')
            row_start = int(''.join(filter(str.isdigit, start)))
            row_end = int(''.join(filter(str.isdigit, end)))
            col_name = ''.join(filter(str.isalpha, start))
            result.extend([col_name + str(i) for i in range(row_start, row_end+1)])
        else:
            result.append(column)
    return ','.join(result)

def remove_duplicates(input_str):
    elements = input_str.split(',')
    unique_elements = []
    for element in elements:
        if element not in unique_elements:
            unique_elements.append(element)
    return ','.join(unique_elements)

parser = argparse.ArgumentParser(description='BOM Extractor')
parser.add_argument('input', help='Input file [*.csv]')
parser.add_argument('designators', help='Designators that need to be extracted from the file ["C1,C10,C5-C7"]')
parser.add_argument('-o', '--output', help='Output file name')
args = parser.parse_args()


def main():
    designators = remove_duplicates(expand_arg(args.designators))
    fieldnames = get_columns(args.input)
    filtered_bom = filter_bom(args.input, designators, fieldnames)
    with open(args.output, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, dialect=csv.unix_dialect)
        writer.writeheader()
        for row in filtered_bom:
            writer.writerow(row)

if __name__ == "__main__":
    main()