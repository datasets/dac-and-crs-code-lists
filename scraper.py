import json
from os import environ
import shutil

# hack to override sqlite database filename
# see: https://help.morph.io/t/using-python-3-with-morph-scraperwiki-fork/148
environ['SCRAPERWIKI_DATABASE_NAME'] = 'sqlite:///data.sqlite'
import scraperwiki

import dac_crs

'''
Generates codelist files from CRS codelists.
'''

shutil.rmtree('data.sqlite', ignore_errors=True)

with open('crs_mappings.json') as f:
    crs_mappings = json.load(f)

dac_crs.init_git_repo()

crs_xls = dac_crs.fetch_xls()

for name, mapping in crs_mappings.items():
    key = mapping.get('key', ['code'])
    print('Extracting {} from spreadsheet ...'.format(name))
    codelist = dac_crs.get_crs_codelist(crs_xls, mapping)
    scraperwiki.sqlite.save(key, codelist, name)
    fieldnames = [x[1] for x in mapping['cols']]
    print('Saving {}.csv'.format(name))
    dac_crs.save_csv(name, codelist, fieldnames)

print('Combining sector_en and sector_fr ...')
sectors_en = scraperwiki.sqlite.select('* from sector_en')
for sector in sectors_en:
    fr_data = scraperwiki.sqlite.select('`name_fr`, `description_fr` from sector_fr where `code` = "{code}" and `voluntary_code` = "{voluntary_code}"'.format(
        code=sector['code'],
        voluntary_code=sector['voluntary_code']
    ))
    if len(fr_data) == 1:
        sector.update(fr_data[0])
scraperwiki.sqlite.save(['code', 'voluntary_code'], sectors_en, 'sector')
fieldnames = [x[1] for x in crs_mappings['sector_en']['cols']] + ['name_fr', 'description_fr']
print('Saving sector.csv')
dac_crs.save_csv('sector', sectors_en, fieldnames)

print('Combining sector_category_en and sector_category_fr ...')
sector_categories_en = scraperwiki.sqlite.select('* from sector_category_en')
all_sector_categories = []
for idx, sector_category in enumerate(sector_categories_en):
    fr_data = scraperwiki.sqlite.select('`name_fr` from sector_category_fr where `code` = "{code}"'.format(code=sector_category['code']))
    sector_category.update(fr_data[0])
    description_data = scraperwiki.sqlite.select('`description_en`, `description_fr` from sector where `category` = "{code}" ORDER BY `code` ASC LIMIT 1'.format(code=sector_category['code']))
    if description_data == []:
        continue
    sector_category.update(description_data[0])
    all_sector_categories.append(sector_category)
print('Saving sector_category.csv')
fieldnames = ['code', 'name_en', 'description_en', 'name_fr', 'description_fr']
dac_crs.save_csv('sector_category', all_sector_categories, fieldnames)

dac_crs.push_to_github()