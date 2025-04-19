import csv
import sys
import re
import os
import logging
import argparse
import math
from collections import OrderedDict

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format="{levelname} - {message}", style="{")

parser = argparse.ArgumentParser(description="CPL file corrector")
parser.add_argument("main_file", help="File requiring correction [*_cpl.csv]")
parser.add_argument("correction_file", help="File describing the fixes [correction_cpl.csv]")
parser.add_argument("-o", "--output", default="output.csv", help="Output file name")
args = parser.parse_args()

if not os.path.isfile(args.main_file):
    logging.error(f"Input path to file is required")
    sys.exit(2)

if not os.path.isfile(args.correction_file):
    logging.error(f"Corrections path to file is required")
    sys.exit(2)

if not args.output or not args.output.endswith(".csv"):
    logging.error(f"Output file must be csv")
    sys.exit(2)


def get_headers(filename):
    with open(filename,"r", newline="", encoding="utf-8") as csvfile:
        rows = csv.reader(csvfile)
        return next(rows)


def get_reader(filename):
    with open(filename,"r", newline="", encoding="utf-8") as csvfile:
        rows = csv.reader(csvfile)
        header = next(rows)
        header = [title.lower() for title in header]

        for row in rows:
            yield OrderedDict(zip(header, row))


def get_all_rows(filename):
    with open(filename, "r", newline="", encoding="utf-8") as csvfile:
        rows = csv.reader(csvfile)
        header = next(rows)
        header = [title.lower() for title in header]

        return [OrderedDict(zip(header, row)) for row in rows]


def find_matches(serach_rows, row, field):
    # find matches in the corrections rows
    res = []
    for search_row in serach_rows:
        if search_row[field]:
            # escape re symbols escept human-re: ? and *
            search_field = "".join([re.escape(item) if item not in ('?', '*') else item for item in search_row[field] ])
            # replace human-re symbols from csv to the python-re equivalents
            search_field = search_field.replace("*", ".+")
            search_field = search_field.replace("?", ".")
            match = re.search(f"^{search_field}$", row[field])
            if match:
                res.append(search_row)

    if len(res) > 1:
        logging.warning(f'[{row["designator"]}][{row["package"]}] - \033[33mFound {len(res)} matches!\033[0m')
    return res


main_reader = get_reader(args.main_file)
corrections = get_all_rows(args.correction_file)
main_headers = get_headers(args.main_file)

fixed_rows = []

# logging.info("Start processsing")
for number, row in enumerate(main_reader, start=1):

    row_by_package = find_matches(corrections, row, "package")
    row_by_designator = find_matches(corrections, row, "designator")

    if not any((row_by_package, row_by_designator)):
        # logging.info(f'[{number}][{row["package"]}] - not found')
        fixed_rows.append(row)
        continue

    if row_by_package != [] and row_by_designator != []:
        logging.warning(f'[{row["designator"]}][{row["package"]}] - \033[33mFound intersection on `package` and `designator`!\033[0m')

    # fix_row = next(row for row in (row_by_package, row_by_designator) if row)[0]
    row_package_designator = row_by_package + row_by_designator
    for fix_row in row_package_designator:
        fix_rowR = float(fix_row["rotation"]) if fix_row["rotation"] != '' else 0
        rowLTop = row["layer"] == "top"
        rowR = float(row["rotation"])
        
        if row["rotation"] and fix_row["rotation"]:
            rowR = row["rotation"] = (
                rowR * (1 if rowLTop else -1)
                + (0 if rowLTop else 180)
                + fix_rowR
            )%360

        fix_rowX = float(fix_row["mid x"]) if fix_row["mid x"] != '' else 0
        fix_rowY = float(fix_row["mid y"]) if fix_row["mid y"] != '' else 0

        rowX = float(row["mid x"])
        rowY = float(row["mid y"])

        if row["mid x"] and fix_row["mid x"]:
            rowX = row["mid x"] = (
                rowX 
                + (1 if rowLTop else -1) * fix_rowX*math.sin(math.radians(-1*rowR)) 
                - (1 if rowLTop else -1) * fix_rowY*math.cos(math.radians(-1*rowR))
            )

        if row["mid y"] and fix_row["mid y"]:
            rowY = row["mid y"] = (
                rowY 
                + fix_rowY*math.sin(math.radians(-1*rowR)) 
                + fix_rowX*math.cos(math.radians(-1*rowR))
            )

        logging.info(f'[{row["designator"]}][{row["package"]}] - updated')
    fixed_rows.append(row)


with open(args.output, "w", newline="", encoding="utf-8") as csvfile:

    writer = csv.DictWriter(csvfile, main_headers, delimiter=",", dialect=csv.unix_dialect)
    writer.writeheader()
    for row in fixed_rows:
        writer.writerow(OrderedDict(zip(main_headers, row.values())))
    logging.info(f"Write rows: {len(fixed_rows)}")
