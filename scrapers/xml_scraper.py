import dac_crs


def scrape_xml():
    url = 'http://www.oecd.org/dac/stats/dacandcrscodelists.htm'
    dac_crs.fetch_xml(url)
