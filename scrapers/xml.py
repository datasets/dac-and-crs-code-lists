from urllib.parse import urlparse, urlunparse

from .helpers import fetch_html, rel_to_absolute, save_from_url


def scrape_xml(xml_filepath):
    xml_lookup_url = 'https://webfs.oecd.org/crs-iati-xml/Lookup/'

    base_url = urlunparse(urlparse(xml_lookup_url)._replace(path=''))
    soup = fetch_html(xml_lookup_url)
    xml_url = soup.find('a', text='DAC-CRS-CODES.xml')['href']
    xml_url = rel_to_absolute(xml_url, base_url=base_url)

    save_from_url(xml_url, xml_filepath)
