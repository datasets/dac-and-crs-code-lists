CRS_MAPPINGS = {
    "CollaborationType": {
        "start_row": 1,
        "cols": {
            0: "code",
            1: "name_en",
            2: "name_fr"
        },
        "exclude_blank": ["code"],
        "sheet_name": "Bi_Multi"
    },
    "FlowType": {
        "start_row": 1,
        "cols": {
            0: "code",
            1: "name_en",
            2: "description_en",
            3: "name_fr",
            4: "description_fr"
        },
        "exclude_blank": ["code"],
        "sheet_name": "Type of flow"
    },
    "FinanceType": {
        "start_row": 7,
        "cols": {
            0: "category",
            2: "code",
            3: "name_en",
            8: "name_fr"
        },
        "exclude_blank": ["code"],
        "sheet_name": "Type of finance",
        "fill_down": "category"
    },
    "AidType": {
        "start_row": 3,
        "cols": {
            0: "category",
            1: "code",
            2: "name_en",
            3: "description_en",
            7: "name_fr",
            8: "description_fr",
        },
        "exclude_blank": ["code", "name_en"],
        "sheet_name": "Type of aid",
        "fill_down": "category"
    },
    "Sector": {
        "start_row": 3,
        "cols": {
            0: "category",
            1: "code",
            2: "name_en",
            3: "description_en",
        },
        "exclude_blank": ["code"],
        "sheet_name": "Purpose code",
        "fill_down": "category"
    },
    "SectorFR": {
        "start_row": 3,
        "cols": {
            1: "code",
            2: "name_fr",
            3: "description_fr",
        },
        "exclude_blank": ["code"],
        "sheet_name": "Codes objet"
    }
}

def make_str(value):
    if (type(value) == float):
        if (value==value//1): # i.e. x.0
            return str(int(value))
        return str(value)
    return value.strip()

# Adapted from code at http://effbot.org/zone/element-lib.htm
def indent(elem, level=0, shift=2):
    i = "\n" + level*" "*shift
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + " "*shift
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1, shift)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def reindent(template):
    return indent(template.getroot(), 0, 4)
