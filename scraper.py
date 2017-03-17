import json
from os import environ

# hack to override sqlite database filename
# see: https://help.morph.io/t/using-python-3-with-morph-scraperwiki-fork/148
environ['SCRAPERWIKI_DATABASE_NAME'] = 'sqlite:///data.sqlite'
import scraperwiki

import dac_crs

'''
Generates codelist files from CRS codelists.
'''

with open('crs_mappings.json') as f:
    crs_mappings = json.load(f)

dac_crs.init_git_repo()

crs_xls = dac_crs.fetch_xls()

for name, mapping in crs_mappings.items():
    key = mapping.get('key', ['code'])
    print('Extracting {} from spreadsheet ...'.format(name))
    dac_crs.mark_all_as_withdrawn(name, key)

    codelist = dac_crs.get_crs_codelist(crs_xls, mapping)
    scraperwiki.sqlite.save(key, codelist, name)
    codelist = scraperwiki.sqlite.select('* from {}'.format(name))
    fieldnames = [x[1] for x in mapping['cols']]
    print('Saving {}.csv'.format(name))
    dac_crs.save_csv(name, codelist, fieldnames)

print('Combining sector_en and sector_fr ...')
dac_crs.mark_all_as_withdrawn('sector', ['code', 'voluntary_code'])
sectors_en = scraperwiki.sqlite.select('* from sector_en')
for sector in sectors_en:
    fr_data = scraperwiki.sqlite.select('`name_fr`, `description_fr` from sector_fr where `code` = "{code}" and `voluntary_code` = "{voluntary_code}"'.format(
        code=sector['code'],
        voluntary_code=sector['voluntary_code']
    ))
    if len(fr_data) == 1:
        sector.update(fr_data[0])
scraperwiki.sqlite.save(['code', 'voluntary_code'], sectors_en, 'sector')
sectors = scraperwiki.sqlite.select('* from sector')
fieldnames = [x[1] for x in crs_mappings['sector_en']['cols']] + ['name_fr', 'description_fr']
print('Saving sector.csv')
dac_crs.save_csv('sector', sectors, fieldnames)

dac_crs.push_to_github()
