<a className="gh-badge" href="https://datahub.io/core/dac-and-crs-code-lists"><img src="https://badgen.net/badge/icon/View%20on%20datahub.io/orange?icon=https://datahub.io/datahub-cube-badge-icon.svg&label&scale=1.25" alt="badge" /></a>

# DAC and CRS code lists

The DAC Secretariat of the OECD maintains various code lists which are used by donors to report on their aid flows to the DAC databases. In addition, these codes are used to classify information in the DAC databases. This repository republishes the lists as CSV files, in a machine-readable format.

Column definitions and types are in `datapackage.json`.

## Data

All files are in `data/`, as CSV with a header row. Every value is quoted. Most files have English (`name_en`) and French (`name_fr`) names.

| File | What it lists |
|------|---------------|
| `dac_members.csv` | Donor codes and names of DAC members |
| `multilateral_donors.csv` | Donor codes and names of multilateral donors |
| `non_dac_donors.csv` | Donor codes and names of non-DAC donors |
| `private_donors.csv` | Donor codes and names of private donors |
| `agencies.csv` | Agencies of each donor (agency code, names, acronym) |
| `recipients.csv` | Recipient countries and territories, with income group and geography |
| `channel_codes.csv` | Channels of delivery |
| `nature_of_submission.csv` | Nature of submission |
| `collaboration_types.csv` | Bilateral / multilateral collaboration types |
| `flow_types.csv` | Types of flow (for example ODA) |
| `finance_types.csv`, `finance_type_categories.csv` | Types of finance and their categories |
| `aid_types.csv`, `aid_type_categories.csv` | Types of aid (co-operation modalities) and their categories |
| `sectors.csv`, `sector_categories.csv` | Purpose (sector) codes and their categories |

The columns are:

| Column | Meaning |
|---|---|
| `code` | The code the file lists. In the donor files, `agencies.csv` and `recipients.csv` it is the donor or recipient code, for example `1` for Austria in `dac_members.csv`. In `aid_types.csv` it can contain letters, for example `A01` |
| `name_en`, `name_fr` | Name in English and in French |
| `description_en`, `description_fr` | Longer description, where the OECD gives one (flow types, finance types, aid types, sectors) |
| `category` | The category a code belongs to: a code in `finance_type_categories.csv` (for `finance_types.csv`), in `aid_type_categories.csv` (for `aid_types.csv`) or in `sector_categories.csv` (for `sectors.csv`; the OECD heads this column "DAC 5 code" although it holds the shorter category codes, for example `111`). In `channel_codes.csv` it is the code of the parent channel; top-level channels are their own parent |
| `voluntary_code` | In `sectors.csv`, the voluntary code of a purpose, where it has one. Blank for most rows |
| `acronym`, `acronym_en`, `acronym_fr` | Acronym of an agency (`agencies.csv`) or of a channel in English and French (`channel_codes.csv`) |
| `donor_name_en`, `donor_name_fr` | In `agencies.csv`, name of the donor that the agency belongs to. `code` is the donor code |
| `agency_code`, `agency_name_en`, `agency_name_fr` | In `agencies.csv`, code and names of the agency |
| `income_group` | In `recipients.csv`, the DAC income group, for example `LDCs` or `UMICs` |
| `geography` | In `recipients.csv`, the region the OECD places the recipient in, for example `Eastern Africa` or `Europe` |

### Known limitations

* Codes are text. They can contain letters (`A01` in `aid_types.csv`), and many lists have blank cells. Read the files as text, so that codes are not turned into numbers and blank cells stay blank:

  ```python
  import pandas as pd
  df = pd.read_csv("data/sectors.csv", dtype=str, keep_default_na=False)
  ```

* `code` is not a unique key in every file. In `agencies.csv` the donor `code` repeats for each agency; the key is `code` with `agency_code`. In `sectors.csv` the purpose `code` repeats for each `voluntary_code` under it; the key is `code` with `voluntary_code`.
* Some cells are blank. For example `acronym` in `agencies.csv`, the descriptions in `finance_types.csv` and `sectors.csv`, and some French names in `channel_codes.csv` and `finance_types.csv`. `geography` is blank for a few recipients.
* `geography` mixes broad and narrow regions: some recipients are placed in `Africa` or `Asia`, others in a narrower region such as `Eastern Africa`.
* A description cell can contain a line break inside the quotes. CSV readers handle this; tools that work line by line do not.
* `recipients.csv` keeps only the DAC income group. The spreadsheet has more columns (for example the World Bank income group and flags such as landlocked), which are not kept.

## Data sources

* The [DAC and CRS code lists](https://webfs.oecd.org/oda/DataCollection/Resources/DAC-CRS-CODES.xls), an Excel file published by the OECD DAC Secretariat and described on the [OECD page of reporting resources](https://www.oecd.org/en/data/insights/data-explainers/2024/10/resources-for-reporting-development-finance-statistics.html). Used under the [OECD Terms and Conditions](https://www.oecd.org/en/about/terms-conditions.html), which allow commercial use, adaptation and sharing with credit to the OECD. The exact name of the licence for code lists is unclear (see [License](#license)). The OECD site refuses automated requests, so those two links may not open from a script.

Changes made to the source data: `scraper.py` downloads the Excel file (and the OECD's XML version of the lists, which is stored but not used for the CSV files) into `source/` unchanged. `parsers/excel.py` then reads the sheets and columns named in `excel_crs_mappings.json`, converts every cell to text, removes surrounding spaces, skips header and empty rows, fills down category values where the sheet leaves them blank, removes duplicate rows, joins the English and French sector lists, and writes one CSV file per list. A few cells are replaced by fixed values listed in `excel_crs_mappings.json`. Columns of the sheets that are not in the mapping are not kept.

Not endorsed by, or affiliated with, the OECD.

## Preparation

You need Python 3 (`runtime.txt` and the workflow file say which versions are used) and access to `webfs.oecd.org`:

```
pip install -r requirements.txt
python scraper.py
```

`scraper.py` downloads the latest OECD files into `source/` and rebuilds all the CSV files in `data/`. The sheet and columns of each list are set in `excel_crs_mappings.json`. If the OECD changes the layout of its spreadsheet, the mappings must be changed to match.

A GitHub Action (`.github/workflows/scrape.yml`) runs `scraper.py` every day at 02:00 UTC, and on every push. On `main`, when the result differs, it opens or updates a pull request called "Automated update". Nothing reaches `main` until that pull request is merged.

## License

The code lists are published by the OECD. The OECD Terms and Conditions (section 3, "Data") say:

> you can extract from, download, copy, adapt, print, distribute, share and embed Data for any purpose, even for commercial use. You must give appropriate credit to the OECD by using the citation associated with the relevant Data

and that anyone who shares or licenses work made with the Data must "include the same acknowledgment requirement in any sub-licenses that you grant". The same terms add that Data "may be subject to restrictions beyond the scope of these Terms and Conditions, either because specific terms apply to those Data or because third parties may have ownership interests".

What was checked, and what could not be established:

* The OECD terms page refuses automated requests. The quotes above were read on an [archived copy dated 31 December 2025](https://web.archive.org/web/20251231101330/https://www.oecd.org/en/about/terms-conditions.html), which says it was last updated in July 2024. The live page may differ.
* The OECD names the Creative Commons Attribution 4.0 licence (CC BY 4.0) only for its "written content". The terms do not say whether a code list counts as "Data" or as written content, so the exact licence is unclear. Both readings allow commercial use, adaptation and sharing, need credit to the OECD, and do not require share-alike. For adapted written content the OECD also asks for a disclaimer, which is included in `ATTRIBUTION.txt`.
* The Excel file and the XML file carry no licence notice of their own, in the sheets and elements we looked at.
* We found no third-party notice in the file, but did not read every cell.

The maintainers place only their own work (the scraper, the column mappings and the CSV layout) under the [Public Domain Dedication and License (PDDL)](https://opendatacommons.org/licenses/pddl/1.0/). This does not cover the OECD's code lists, in `data/` or in `source/`. See [ATTRIBUTION.txt](ATTRIBUTION.txt) for the credit to give when you use the data.
