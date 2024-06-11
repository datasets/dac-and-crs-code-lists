from scrapers.excel import scrape_excel
from scrapers.xml import scrape_xml
from parsers.excel import parse_excel

#scrape_xml("source/codelists.xml")
scrape_excel("source/codelists.xls")

parse_excel("source/codelists.xls", "data")
