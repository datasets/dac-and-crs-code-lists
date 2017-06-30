import csv
from glob import glob
from os.path import join
from os import environ, remove
import re
import shutil

from bs4 import BeautifulSoup as bs
import requests
import xlrd
from git import Repo


output_dir = 'output'
data_dir = join(output_dir, 'data')
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
    xls_filepath = join(data_dir, 'DAC-CRS-CODES.xls')
    xls_url = soup.find(class_='document').find('a')['href']
    if xls_url.startswith('/'):
        xls_url = base_url + xls_url
    save_from_url(xls_url, xls_filepath)

    # Open CRS codelist
    return xlrd.open_workbook(xls_filepath)

def get_crs_codelist(book, mapping):
    def to_str(val):
        if type(val) is float:
            if val == val // 1:
                return str(int(val))
        return str(val).replace('\n', '\r\n').strip()

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

    merge_down = mapping.get('merge_down')
    if merge_down:
        merged_row_data = {}

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
        if relevant_row(mapping, row_data):
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

def init_git_repo():
    shutil.rmtree(output_dir, ignore_errors=True)
    git = Repo.init(output_dir).git
    git.remote('add', 'origin', 'https://{}@github.com/andylolz/dac-crs-codes.git'.format(environ.get('MORPH_GH_API_KEY')))
    try:
        git.pull('origin', 'update')
    except:
        git.pull('origin', 'gh-pages')
        git.checkout(b='update')
    for to_remove in glob(join(data_dir, '*.csv')):
        remove(to_remove)

def push_to_github():
    url = 'https://api.github.com/repos/andylolz/dac-crs-codes/pulls'
    git = Repo.init(output_dir).git
    _ = git.add('.')
    if git.diff('HEAD') == '':
        print('No changes since last update.')
        return
    git.config('user.email', environ.get('MORPH_GH_EMAIL'))
    git.config('user.name', environ.get('MORPH_GH_USERNAME'))
    git.commit(m='Update')
    git.push('origin', 'update')
    payload = {
        'title': 'Merge in latest codelist changes',
        'body': 'This is an auto- pull request, sent from ' \
            '[the morph.io scraper](https://morph.io/andylolz/dac-crs-codes).' \
            '\n\nPinging @andylolz to review.',
        'head': 'update',
        'base': 'gh-pages',
    }
    r = requests.post(url, json=payload, auth=(environ.get('MORPH_GH_USERNAME'), environ.get('MORPH_GH_API_KEY')))
    shutil.rmtree(output_dir, ignore_errors=True)
