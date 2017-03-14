"""
Generates codelist files from CRS codelists.
Note that it doesn't handle removed / historical codes.
"""

from lxml import etree as ET
import xlrd
import crslib
crs_mappings = crslib.CRS_MAPPINGS
from crslib import make_str

# Open CRS codelist
crs_xls = xlrd.open_workbook("source/CRS-codelists.xls")

def get_crs_codelist(book, mapping):
    def relevant_row(mapping, rowdata):
        for eb in mapping["exclude_blank"]:
            if str(rowdata[eb]).strip() == "": return False
        return True

    # Get sheet and create array for this codelist
    cl = book.sheet_by_name(mapping["sheet_name"])
    cldata = []

    # Some values apply to following rows; we save them in `fill_down_vals`
    fill_down_vals = {}
    for i in range (mapping["start_row"], cl.nrows):

        # Map columns to values
        rowdata = {}
        for j in mapping["cols"].keys():
            rowdata[mapping["cols"][j]] = make_str(cl.cell_value(i,j))

        # Check whether we should ignore this row based on `exclude_blank`
        if relevant_row(mapping, rowdata):
            if fill_down_vals:
                rowdata.update(fill_down_vals)
            cldata.append(rowdata)
        else:
            if mapping.get("fill_down") and (rowdata[mapping["fill_down"]] != ""):
                fill_down_vals[mapping["fill_down"]] = rowdata[mapping["fill_down"]]

    return cldata

codelists = {}
for name, mapping in crs_mappings.items():
    print "Getting mapping %s" % name
    codelists[name] = get_crs_codelist(crs_xls, mapping)

# Purpose codes reformatting to combine two sheets
pcfr = dict(map(lambda x: (x["code"], x), codelists["SectorFR"]))
for key, row in enumerate(codelists["Sector"]):
    frcodes = pcfr[row["code"]]
    codelists["Sector"][key].update(frcodes)
codelists.pop("SectorFR", None)

# Finished collecting data from spreadsheet, now start writing XML

# Write for each template
for codelist_name, data in codelists.items():
    print "Writing codelist for %s" % codelist_name
    template = ET.parse('templates/%s.xml' % codelist_name, ET.XMLParser(remove_blank_text=True))
    codelist_items = template.find('codelist-items')
    for code_data in data:
        codelist_item = ET.Element('codelist-item')

        code = ET.Element('code')
        code.text = code_data["code"]
        codelist_item.append(code)

        name = ET.Element('name')
        codelist_item.append(name)

        narrative_en = ET.Element('narrative')
        narrative_en.text = code_data["name_en"]
        name.append(narrative_en)

        narrative_fr = ET.Element('narrative')
        narrative_fr.set('{http://www.w3.org/XML/1998/namespace}lang', "fr")
        narrative_fr.text = code_data["name_fr"]
        name.append(narrative_fr)

        if code_data.get("description_en"):
            description = ET.Element('description')
            codelist_item.append(description)

            narrative_en = ET.Element('narrative')
            narrative_en.text = code_data["description_en"]
            description.append(narrative_en)

            narrative_fr = ET.Element('narrative')
            narrative_fr.set('{http://www.w3.org/XML/1998/namespace}lang', "fr")
            narrative_fr.text = code_data["description_fr"]
            description.append(narrative_fr)

        if code_data.get("category"):
            category = ET.Element('category')
            category.text = code_data["category"]
            codelist_item.append(category)

        codelist_items.append(codelist_item)
    crslib.reindent(template)
    template.write('xml/%s.xml' % codelist_name, pretty_print=True, encoding="UTF-8", xml_declaration=True)
