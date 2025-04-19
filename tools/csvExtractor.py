import csv
import sys
import argparse

parser = argparse.ArgumentParser(description='CSV file extractor')
parser.add_argument('input', help='Input file [*.csv]')
parser.add_argument('columns', help='Name of columns to be extracted ["qty,pn,..."]')
parser.add_argument('-o', '--output', help='Output file name')
args = parser.parse_args()

input_file = args.input
columns = args.columns.split(',')

with open(args.input, 'r', encoding='utf-8') as input_file:
    reader = csv.DictReader(input_file)
    result_data = []
    for row in reader:
        result_row = {}
        for column in columns:
            result_row[column] = row.get(column, '')
        result_data.append(result_row)

if args.output == None:
    writer = csv.writer(sys.stdout, dialect=csv.unix_dialect)
    writer.writerow([key for key in result_data[0].keys()])
    for row in result_data:
        writer.writerow(row.values())
else:
    with open(args.output, 'w', newline='', encoding='utf-8') as output_file:
        writer = csv.writer(output_file, dialect=csv.unix_dialect)
        writer.writerow(result_data[0].keys())
        for row in result_data:
            writer.writerow(row.values())
