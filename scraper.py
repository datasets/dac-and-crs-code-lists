import csv
import json
from os.path import join

from bs4 import BeautifulSoup as bs
import requests
from lxml import etree
import xlrd


'''
Generates codelist files from CRS codelists.
'''

with open('crs_mappings.json') as f:
    crs_mappings = json.load(f)

base_url = 'http://www.oecd.org'

codelists_url = base_url + '/dac/stats/dacandcrscodelists.htm'
r = requests.get(codelists_url)
soup = bs(r.text, 'lxml')

xls_filepath = join('output', 'DAC-CRS-CODES.xls')
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
crs_xls = xlrd.open_workbook(xls_filepath)

def get_crs_codelist(book, mapping):
    def to_str(val):
        if type(val) is float:
            if val == val // 1:
                return str(int(val))
        return str(val).strip()

    def relevant_row(mapping, row_data):
        for eb in mapping['exclude_blank']:
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

for name, mapping in crs_mappings.items():
    print('Getting mapping {}'.format(name))
    codelist = get_crs_codelist(crs_xls, mapping)
    with open(join('output', name + '.csv'), 'w') as f:
        fieldnames = [c[1] for c in mapping['cols']]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for c in codelist:
            _ = writer.writerow(c)

# Purpose codes reformatting to combine two sheets
sectors = {}
for lang in ['en', 'fr']:
    with open(join('output', 'sector_{}.csv'.format(lang))) as f:
        reader = csv.DictReader(f)
        sectors[lang] = [row for row in reader]
fr_lookup = {row['code']: row for row in sectors['fr']}
for row in sectors['en']:
    row.update(fr_lookup[row['code']])

fieldnames = ['category', 'code', 'name_en', 'description_en', 'name_fr', 'description_fr']
with open(join('output', 'sector.csv'), 'w') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for c in sectors['en']:
        _ = writer.writerow(c)
