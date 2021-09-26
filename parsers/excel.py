from os.path import join
import json

from .helpers import load_xls, save_csv


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

    def do_replacement(replacements, col_name, val):
        for col, before, after in replacements:
            if col_name == col and before == val:
                return after
        return val

    # Get sheet and create array for this codelist
    cl = book.sheet_by_name(mapping['sheet_name'])
    cldata = []

    # Some values apply to following rows; we save them in `fill_down_vals`
    fill_down_vals = {}

    for row_num in range(mapping['start_row'], cl.nrows):
        # Map columns to values
        row_data = {}
        for col_num, col_name in mapping['cols']:
            if type(col_num) is list:
                col_nums = col_num
                for col_num in col_nums:
                    val = get_cell_contents(cl, row_num, col_num)
                    if val != '':
                        break
            else:
                val = get_cell_contents(cl, row_num, col_num)
            row_data[col_name] = do_replacement(
                mapping.get("replacements", []), col_name, val)

        # if the value for a given column is in `ignore`
        # then ignore this row
        skip_row = False
        for ig_col, ig_val in mapping.get('ignore', []):
            if get_cell_contents(cl, row_num, ig_col) == ig_val:
                skip_row = True
                break
        if skip_row:
            continue

        # Check whether we should ignore this row based on `exclude_blank`
        if relevant_row(mapping, cl, row_num):
            for col_name, fill_down_val in fill_down_vals.items():
                if row_data[col_name].strip() == '':
                    row_data[col_name] = fill_down_val
            cldata.append(row_data)

        if mapping.get('fill_down'):
            for fill_down_col in mapping['fill_down']:
                if row_data[fill_down_col] != '':
                    fill_down_vals[fill_down_col] = row_data[fill_down_col]

    # remove duplicate rows
    cldata = [
        dict(k)
        for k in {
            tuple(t.items()): None
            for t in cldata
        }.keys()]

    return cldata


def extract_data(crs_xls, name, mapping):
    print('Extracting {} from spreadsheet ...'.format(name))
    codelist = get_crs_codelist(crs_xls, mapping)
    fieldnames = [x[1] for x in mapping['cols']]
    return codelist, fieldnames


def parse_excel(xls_filepath, output_filepath):
    crs_xls = load_xls(xls_filepath)

    with open('excel_crs_mappings.json') as f:
        crs_mappings = json.load(f)

    for name, mapping in crs_mappings.items():
        if name.startswith('sector'):
            continue
        codelist, fieldnames = extract_data(crs_xls, name, mapping)
        print('Saving {}.csv'.format(name))
        save_csv(join(output_filepath, name + ".csv"), codelist, fieldnames)

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
    save_csv(
        join(output_filepath, "sectors.csv"),
        sectors, fieldnames)

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
    save_csv(
        join(output_filepath, "sector_categories.csv"),
        sector_categories_en, fieldnames)
