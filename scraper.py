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

soup = dac_crs.fetch_html()
crs_xls = dac_crs.fetch_xls(soup)

for name, mapping in crs_mappings.items():
    key = mapping.get('key', ['code'])
    print('Extracting {} from spreadsheet ...'.format(name))
    codelist = dac_crs.get_crs_codelist(crs_xls, mapping)
    scraperwiki.sqlite.save(key, codelist, name)
    fieldnames = [x[1] for x in mapping['cols']]
    print('Saving {}.csv'.format(name))
    dac_crs.save_csv(name, codelist, fieldnames)

print('Combining sector_en and sector_fr ...')
sectors_en = scraperwiki.sqlite.select('* from sectors_en')
for sector in sectors_en:
    fr_data = scraperwiki.sqlite.select('`name_fr`, `description_fr` from sectors_fr where `code` = "{code}" and `voluntary_code` = "{voluntary_code}"'.format(
        code=sector['code'],
        voluntary_code=sector['voluntary_code']
    ))
    if len(fr_data) == 1:
        sector.update(fr_data[0])
scraperwiki.sqlite.save(['code', 'voluntary_code'], sectors_en, 'sectors')
fieldnames = [x[1] for x in crs_mappings['sectors_en']['cols']] + ['name_fr', 'description_fr']
print('Saving sectors.csv')
dac_crs.save_csv('sectors', sectors_en, fieldnames)

print('Deriving Common Code codelist from sectors ...')
fieldnames = ['category', 'code', 'name_en', 'description_en', 'name_fr', 'description_fr']
# these codes are a bit too broad. Voluntary codes should be used instead
parent_codes = list({x['code']: None for x in sectors_en if x['voluntary_code'] != ''}.keys())
# these codes are unmappable because they are very broad.
# These are the "Not classifiable (multisectoral)" codes from:
# http://www.aidtransparency.net/wp-content/uploads/2013/05/Annex-4-Common-Code-and-CRS-Spreadsheet.xls
unmappable_codes = ['43010', '43050', '43081', '43082', '52010', '99810']
common_codes = []
for sector in sectors_en:
    common_code = {f: sector[f] for f in fieldnames}
    if sector['voluntary_code'] != '':
        common_code['code'] = sector['voluntary_code']
    if common_code['code'] in unmappable_codes:
        common_code['budget_status'] = 'unmappable'
    elif common_code['code'] in parent_codes:
        common_code['budget_status'] = 'insufficiently granular'
    else:
        common_code['budget_status'] = ''
    common_codes.append(common_code)
scraperwiki.sqlite.save(['code'], common_codes, 'sector_for_budget_alignment')
print('Saving sector_for_budget_alignment.csv')
fieldnames.insert(2, 'budget_status')
dac_crs.save_csv('sector_for_budget_alignment', common_codes, fieldnames)

print('Combining sector_categories_en and sector_categories_fr ...')
sector_categories_en = scraperwiki.sqlite.select('* from sector_categories_en')
all_sector_categories = []
for idx, sector_category in enumerate(sector_categories_en):
    fr_data = scraperwiki.sqlite.select('`name_fr` from sector_categories_fr where `code` = "{code}"'.format(code=sector_category['code']))
    sector_category.update(fr_data[0])
    description_data = scraperwiki.sqlite.select('`description_en`, `description_fr` from sectors where `category` = "{code}" ORDER BY `code` ASC LIMIT 1'.format(code=sector_category['code']))
    if description_data == []:
        continue
    sector_category.update(description_data[0])
    all_sector_categories.append(sector_category)
print('Saving sector_categories.csv')
fieldnames = ['code', 'name_en', 'description_en', 'name_fr', 'description_fr']
dac_crs.save_csv('sector_categories', all_sector_categories, fieldnames)

if environ.get('MORPH_PUSH_TO_GITHUB'):
    dac_crs.push_to_github()
