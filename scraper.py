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

crs_xls = dac_crs.fetch_xls()

### TODO
# send PR to branch `data`
# include a link to https://docs.google.com/viewer?url=https://rawgit.com/andylolz/dac-crs-codes/data/DAC-CRS-CODES.xls

for name, mapping in crs_mappings.items():
    print('Getting mapping {}'.format(name))
    codelist = dac_crs.get_crs_codelist(crs_xls, mapping)
    scraperwiki.sqlite.save(['code'], codelist, name)

sectors_en = scraperwiki.sqlite.select('* from sector_en')
for sector in sectors_en:
    fr_data = scraperwiki.sqlite.select('`name_fr`, `description_fr` from sector_fr where `code` = "{}"'.format(sector['code']))
    if len(fr_data) == 0:
        sector.update(fr_data[0])
scraperwiki.sqlite.save(['code'], sectors_en, 'sector')

for name in crs_mappings.keys():
    dac_crs.save_csv(name)
