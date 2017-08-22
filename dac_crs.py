import csv
from os.path import join

from bs4 import BeautifulSoup as bs
import requests
import xlrd


source_dir = 'source'
data_dir = 'data'
base_url = 'http://www.oecd.org'

def save_from_url(url, filepath):
    with open(filepath, 'wb') as f:
        r = requests.get(url, stream=True)
        if not r.ok:
            raise
        for block in r.iter_content(1024):
            _ = f.write(block)

def fetch_html():
    codelists_url = base_url + '/dac/stats/dacandcrscodelists.htm'
    r = requests.get(codelists_url)
    soup = bs(r.text, 'html.parser')
    return soup

def fetch_xls(soup):
    xls_filepath = join(source_dir, 'codelists.xls')
    xls_url = soup.find(class_='document').find('a')['href']
    if xls_url.startswith('/'):
        xls_url = base_url + xls_url
    save_from_url(xls_url, xls_filepath)

    # Open CRS codelist
    return xlrd.open_workbook(xls_filepath)

def get_crs_codelist(book, mapping):
    def get_cell_contents(cl, row_num, col_num):
        val = cl.cell_value(row_num, col_num)
        if type(val) is float:
            if val == val // 1:
                return str(int(val))
        return str(val).replace('\n', '\r\n').strip()

    def relevant_row(mapping, cl, row_num):
        for ebs in mapping.get('exclude_blank', []):
            if type(ebs) is not list:
                ebs = [ebs]
            ignore = True
            for eb in ebs:
                if get_cell_contents(cl, row_num, eb) != '':
                    ignore = False
            if ignore:
                return False
        for ef in mapping.get('exclude_filled', []):
            if get_cell_contents(cl, row_num, ef) != '':
                return False
        return True

    # Get sheet and create array for this codelist
    cl = book.sheet_by_name(mapping['sheet_name'])
    cldata = []

    merge_down = mapping.get('merge_down')
    if merge_down:
        merged_row_data = {}

    # Some values apply to following rows; we save them in `fill_down_vals`
    fill_down_vals = {}

    for row_num in range(mapping['start_row'], cl.nrows):
        # Map columns to values
        row_data = {}
        for col_num, col_name in mapping['cols']:
            row_data[col_name] = get_cell_contents(cl, row_num, col_num)

        # if the value for a given column is in `ignore`
        # then ignore this row
        skip_row = False
        for ig_col, ig_val in mapping.get('ignore', []):
            if get_cell_contents(cl, row_num, ig_col) == ig_val:
                skip_row = True
                break
        if skip_row:
            continue

        if merge_down and merged_row_data != {}:
            do_merge_down = True
            for k, v in row_data.items():
                if k in merge_down:
                    continue
                if v.strip() != '':
                    do_merge_down = False
            if do_merge_down:
                for k in merge_down:
                    if row_data[k].strip() != '':
                        merged_row_data[k] += '\r\n' + row_data[k]
                continue
            else:
                cldata.append(merged_row_data)
                merged_row_data = {}

        # Check whether we should ignore this row based on `exclude_blank`
        if relevant_row(mapping, cl, row_num):
            for col_name, fill_down_val in fill_down_vals.items():
                if row_data[col_name].strip() == '':
                    row_data[col_name] = fill_down_val
            if merge_down:
                merged_row_data = row_data
            else:
                cldata.append(row_data)

        if mapping.get('fill_down'):
            for fill_down_col in mapping['fill_down']:
                if row_data[fill_down_col] != '':
                    fill_down_vals[fill_down_col] = row_data[fill_down_col]

    if merge_down and merged_row_data != {}:
        cldata.append(merged_row_data)

    return cldata

def save_csv(name, codelist, fieldnames):
    with open(join(data_dir, name + '.csv'), 'w', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for row in codelist:
            writer.writerow(row)
