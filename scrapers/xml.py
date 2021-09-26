from urllib.parse import urlparse, urlunparse

from .helpers import fetch_html, rel_to_absolute, save_from_url


def scrape_xml(xml_filepath):
    url = 'http://www.oecd.org/dac/stats/dacandcrscodelists.htm'

    base_url = urlunparse(urlparse(url)._replace(path=''))
    soup = fetch_html(url)
    doc = soup.find(class_='document')
    xml_page_url = doc.find('a', text='XML')['href']
    xml_page_url = rel_to_absolute(xml_page_url, base_url=base_url)

    base_url = urlunparse(urlparse(xml_page_url)._replace(path=''))
    soup = fetch_html(xml_page_url)
    doc = soup.find(class_='document')
    xml_lookup_url = doc.find('a', text='DAC codelist in XML format')['href']
    xml_lookup_url = rel_to_absolute(xml_lookup_url, base_url=base_url)

    base_url = urlunparse(urlparse(xml_lookup_url)._replace(path=''))
    soup = fetch_html(xml_lookup_url)
    xml_url = soup.find('a', text='DAC-CRS-CODES.xml')['href']
    xml_url = rel_to_absolute(xml_url, base_url=base_url)

    save_from_url(xml_url, xml_filepath)
