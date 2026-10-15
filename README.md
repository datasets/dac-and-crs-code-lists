<a className="gh-badge" href="https://datahub.io/core/dac-and-crs-code-lists"><img src="https://badgen.net/badge/icon/View%20on%20datahub.io/orange?icon=https://datahub.io/datahub-cube-badge-icon.svg&label&scale=1.25" alt="badge" /></a>

The DAC Secretariat maintains various code lists which are used by donors to report on their aid flows to the DAC databases. In addition, these codes are used to classify information in the DAC databases.

Here you can find these codes republished in a machine readable format. They’re fetched from an Excel file [available on the OECD website](http://www.oecd.org/dac/stats/dacandcrscodelists.htm).

Data
----

All files are in `data/`, as CSV with a header row. Column names and types are in `datapackage.json`. Most files have English (`name_en`) and French (`name_fr`) names.

| File | What it lists |
|------|---------------|
| `dac_members.csv` | Donor codes and names of DAC members |
| `multilateral_donors.csv` | Donor codes and names of multilateral donors |
| `non_dac_donors.csv` | Donor codes and names of non-DAC donors |
| `private_donors.csv` | Donor codes and names of private donors |
| `agencies.csv` | Agencies of each donor (agency code, names, acronym) |
| `recipients.csv` | Recipient countries and territories, with income group and region |
| `channel_codes.csv` | Channels of delivery |
| `nature_of_submission.csv` | Nature of submission |
| `collaboration_types.csv` | Bilateral / multilateral collaboration types |
| `flow_types.csv` | Types of flow (for example ODA) |
| `finance_types.csv`, `finance_type_categories.csv` | Types of finance and their categories |
| `aid_types.csv`, `aid_type_categories.csv` | Types of aid (co-operation modalities) and their categories |
| `sectors.csv`, `sector_categories.csv` | Purpose (sector) codes and their categories |

Codes are stored as text, so read them as text (for example `dtype=str` in pandas).

`source/` holds the OECD files the data is built from: `codelists.xls` (used for the CSV files) and `codelists.xml`.

How the data is updated
-----------------------

`scraper.py` downloads the latest OECD files into `source/` and rebuilds all the CSV files in `data/`. The sheet and column of each list are set in `excel_crs_mappings.json`. If OECD changes the layout of its spreadsheet, the mappings must be changed to match.

A GitHub Action (`.github/workflows/scrape.yml`) runs `scraper.py` every day. When the result differs from `main`, it opens or updates a pull request called "Automated update". Nothing reaches `main` until that pull request is merged.

Run it yourself
---------------

You will need Python 3.

<pre>
pip install -r requirements.txt
python scraper.py
</pre>

License
-------

This material is licensed by its maintainers under the Public Domain Dedication and License.
