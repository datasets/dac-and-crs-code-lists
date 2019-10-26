[![goodtables.io](https://goodtables.io/badge/github/datasets/dac-crs-codes.svg)](https://goodtables.io/github/datasets/dac-crs-codes)

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
