import csv
from glob import glob
from os.path import join
from os import remove
import shutil

from bs4 import BeautifulSoup as bs
import requests
import scraperwiki
import xlrd
from git import Repo


output_dir = 'output'
data_dir = join(output_dir, 'data')

def fetch_xls():
    base_url = 'http://www.oecd.org'
    codelists_url = base_url + '/dac/stats/dacandcrscodelists.htm'
    xls_filepath = join(data_dir, 'DAC-CRS-CODES.xls')

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
        for ebs in mapping.get('exclude_blank', []):
            if type(ebs) is not list:
                ebs = [ebs]
            ignore = True
            for eb in ebs:
                if str(row_data[eb]).strip() != '':
                    ignore = False
            if ignore:
                return False
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
            for col_name, fill_down_val in fill_down_vals.items():
                if row_data[col_name].strip() == '':
                    row_data[col_name] = fill_down_val
            row_data['withdrawn'] = False
            cldata.append(row_data)

        if mapping.get('fill_down'):
            for fill_down_col in mapping['fill_down']:
                if row_data[fill_down_col] != '':
                    fill_down_vals[fill_down_col] = row_data[fill_down_col]

    return cldata

def save_csv(name, codelist, fieldnames):
    fieldnames += ['withdrawn']
    with open(join(data_dir, name + '.csv'), 'w') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in codelist:
            writer.writerow(row)

def init_git_repo():
    shutil.rmtree(output_dir, ignore_errors=True)
    git = Repo.init(output_dir).git
    git.remote('add', 'origin', 'https://github.com/andylolz/dac-crs-codes.git')
    try:
        git.pull('origin', 'pr')
    except:
        git.pull('origin', 'gh-pages')
        git.checkout(b='pr')
    for to_remove in glob(join(data_dir, '*')):
        remove(to_remove)

def mark_all_as_withdrawn(name, key):
    try:
        codelist = scraperwiki.sqlite.select('* from {}'.format(name))
        for row_data in codelist:
            row_data['withdrawn'] = True
        scraperwiki.sqlite.save(key, codelist, name)
    except:
        pass

def push_to_github():
    git = Repo.init(output_dir).git
    # shutil.rmtree(output_dir, ignore_errors=True)
