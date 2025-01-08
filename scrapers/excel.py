from urllib.parse import urlparse, urlunparse

from .helpers import fetch_html, rel_to_absolute, save_from_url

import re

def scrape_excel(xls_filepath):
    '''
    Generate codelist files from XLS CRS codelists.
    '''
    url = 'https://webfs.oecd.org/oda/DataCollection/Resources/'
    base_url = urlunparse(urlparse(url)._replace(path=''))
    soup = fetch_html(url)
    xls_url = soup.find('a', string=re.compile(r'(\s*)DAC-CRS-CODES.xls'))['href']
    xls_url = rel_to_absolute(xls_url, base_url=base_url)
    save_from_url(xls_url, xls_filepath)
