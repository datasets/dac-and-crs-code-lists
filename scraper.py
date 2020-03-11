import json

import dac_crs


def extract_data(crs_xls, name, mapping):
    print('Extracting {} from spreadsheet ...'.format(name))
    codelist = dac_crs.get_crs_codelist(crs_xls, mapping)
    fieldnames = [x[1] for x in mapping['cols']]
    return codelist, fieldnames


'''
Generates codelist files from CRS codelists.
'''
with open('crs_mappings.json') as f:
    crs_mappings = json.load(f)

url = 'http://www.oecd.org/dac/stats/dacandcrscodelists.htm'
dac_crs.fetch_xml(url)
xls_filepath = dac_crs.fetch_xls(url)
crs_xls = dac_crs.load_xls(xls_filepath)

for name, mapping in crs_mappings.items():
    if name.startswith('sector'):
        continue
    codelist, fieldnames = extract_data(crs_xls, name, mapping)
    print('Saving {}.csv'.format(name))
    dac_crs.save_csv(name, codelist, fieldnames)

print('Combining sectors_en and sectors_fr ...')
mapping = crs_mappings['sectors_en']
sectors_en, fieldnames = extract_data(crs_xls, 'sectors_en', mapping)
mapping = crs_mappings['sectors_fr']
sectors_fr, _ = extract_data(crs_xls, 'sectors_fr', mapping)

sectors_fr = {(x['category'], x['code'], x['voluntary_code']): x
              for x in sectors_fr}
sectors = []
for c in sectors_en:
    el = sectors_fr.get((c['category'], c['code'], c['voluntary_code']))
    if el:
        c.update(el)
    sectors.append(c)
fieldnames = fieldnames + ['name_fr', 'description_fr']
print('Saving sectors.csv')
dac_crs.save_csv('sectors', sectors, fieldnames)

print('Combining sector_categories_en and sector_categories_fr ...')
mapping = crs_mappings['sector_categories_en']
sector_categories_en, fieldnames = extract_data(
    crs_xls, 'sector_categories_en', mapping)
mapping = crs_mappings['sector_categories_fr']
sector_categories_fr, _ = extract_data(
    crs_xls, 'sector_categories_fr', mapping)

sector_categories_fr = {
    x['code']: x
    for x in sector_categories_fr
}
for c in sector_categories_en:
    el = sector_categories_fr.get(c['code'])
    if el:
        c.update(el)
fieldnames = fieldnames + ['name_fr']
print('Saving sector_categories.csv')
dac_crs.save_csv('sector_categories', sector_categories_en, fieldnames)
