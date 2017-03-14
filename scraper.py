import csv
import json
from os.path import join
from os import environ

from bs4 import BeautifulSoup as bs
import requests
from lxml import etree
import xlrd
# hack to override sqlite database filename
# see: https://help.morph.io/t/using-python-3-with-morph-scraperwiki-fork/148
environ['SCRAPERWIKI_DATABASE_NAME'] = 'sqlite:///data.sqlite'
import scraperwiki


'''
Generates codelist files from CRS codelists.
'''

with open('crs_mappings.json') as f:
    crs_mappings = json.load(f)

base_url = 'http://www.oecd.org'
output_dir = 'output'

codelists_url = base_url + '/dac/stats/dacandcrscodelists.htm'
r = requests.get(codelists_url)
soup = bs(r.text, 'lxml')

xls_filepath = join(output_dir, 'DAC-CRS-CODES.xls')
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
    scraperwiki.sqlite.save(['code'], codelist, name)

sectors_en = scraperwiki.sqlite.select('* from sector_en')
for sector in sectors_en:
    fr_data = scraperwiki.sqlite.select('`name_fr`, `description_fr` from sector_fr where `code` = "{}"'.format(sector['code']))
    if len(fr_data) > 0:
        sector.update(fr_data[0])
scraperwiki.sqlite.save(['code'], sectors_en, 'sector')
