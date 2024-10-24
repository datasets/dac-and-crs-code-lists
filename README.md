<a href="https://datahub.io/core/dac-and-crs-code-lists"><img src="https://badgen.net/badge/icon/View%20on%20datahub.io/orange?icon=https://datahub.io/datahub-cube-badge-icon.svg&label&scale=1.25)" alt="badge" /></a>

[![goodtables.io](https://goodtables.io/badge/github/datasets/dac-and-crs-code-lists.svg)](https://goodtables.io/github/datasets/dac-and-crs-code-lists)
[![Build Status](https://travis-ci.org/datasets/dac-and-crs-code-lists.svg?branch=master)](https://travis-ci.org/datasets/dac-and-crs-code-lists)

The DAC Secretariat maintains various code lists which are used by donors to report on their aid flows to the DAC databases. In addition, these codes are used to classify information in the DAC databases.

Here you can find these codes republished in a machine readable format. They’re fetched from an Excel file [available on the OECD website](http://www.oecd.org/dac/stats/dacandcrscodelists.htm).

Preparation
-----------

You will need: python 3.x

Run the following to download and convert the data from XLS to CSV:

<pre>
pip install -r requirements.txt
python scraper.py
</pre>

License
-------

This material is licensed by its maintainers under the Public Domain Dedication and License.
