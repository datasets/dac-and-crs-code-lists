import csv
from os.path import join, exists
from os import makedirs

from bs4 import BeautifulSoup as bs
import requests
import xlrd


output_dir = 'output'
if not exists(output_dir):
    makedirs(output_dir)

def fetch_xls():
    base_url = 'http://www.oecd.org'
    codelists_url = base_url + '/dac/stats/dacandcrscodelists.htm'
    xls_filepath = join(output_dir, 'DAC-CRS-CODES.xls')

    r = requests.get(codelists_url)
    soup = bs(r.text, 'html.parser')

    xls_url = soup.find(class_='document').find('a')['href']
    if xls_url.startswith('/'):
        xls_url = base_url + xls_url

    with open(xls_filepath, 'wb') as f:
        r = requests.get(xls_url, stream=True)
        if not r.ok:
            raise
        for block in r.iter_content(1024):
            _ = f.write(block)

    # Open CRS codelist
    return xlrd.open_workbook(xls_filepath)

def get_crs_codelist(book, mapping):
    def to_str(val):
        if type(val) is float:
            if val == val // 1:
                return str(int(val))
        return str(val).strip()

    def relevant_row(mapping, row_data):
        for eb in mapping.get('exclude_blank', []):
            if str(row_data[eb]).strip() == '': return False
        return True

    # Get sheet and create array for this codelist
    cl = book.sheet_by_name(mapping['sheet_name'])
    cldata = []

    # Some values apply to following rows; we save them in `fill_down_vals`
    fill_down_vals = {}
    for row_num in range(mapping['start_row'], cl.nrows):
        # Map columns to values
        row_data = {}
        for col_nums, col_name in mapping['cols']:
            if type(col_nums) is not list:
                col_nums = [col_nums]

            # if we're merging multiple columns,
            # take the first one that isn't blank
            for col_num in col_nums:
                row_data[col_name] = to_str(cl.cell_value(row_num, col_num))
                if row_data[col_name].strip() != '':
                    break

        # if the value for a given column is in `ignore`
        # then ignore this row
        skip_row = False
        for ig_key, ig_val in mapping.get('ignore', []):
            if row_data[ig_key] == ig_val:
                skip_row = True
                break
        if skip_row:
            continue

        # Check whether we should ignore this row based on `exclude_blank`
        if relevant_row(mapping, row_data):
            if fill_down_vals:
                row_data.update(fill_down_vals)
            cldata.append(row_data)

        if mapping.get('fill_down') and (row_data[mapping['fill_down']] != ''):
            fill_down_vals[mapping['fill_down']] = row_data[mapping['fill_down']]

    return cldata

def save_csv(name, codelist, fieldnames):
    with open(join(output_dir, name + '.csv'), 'w') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in codelist:
            writer.writerow(row)
