import csv

import xlrd


def load_xls(xls_filepath):
    # Open CRS codelist
    return xlrd.open_workbook(xls_filepath)


def save_csv(output_filepath, codelist, fieldnames):
    with open(output_filepath, 'w', encoding='utf-8') as f:
        writer = csv.DictWriter(
            f, fieldnames=fieldnames,
            quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for row in codelist:
            writer.writerow(row)
