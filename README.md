DAC CRS Codelist scraper
========================

This code scrapes the DAC CRS codelist excel file [available on the OECD website](http://www.oecd.org/dac/stats/dacandcrscodelists.htm).

The scraper [runs on morph.io](https://morph.io/andylolz/dac-crs-codes). You can view or download the output in various formats there.

It pushes its output to [the `gh-pages` branch of github.com/andylolz/dac-crs-codes](https://github.com/andylolz/dac-crs-codes/tree/gh-pages).

Installation
------------

You will need: python 3.x

```
export MORPH_API_KEY=[your API key]
pip install -r requirements.txt
python scraper.py
```
