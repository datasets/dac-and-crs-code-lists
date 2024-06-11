from urllib.parse import urlparse, urlunparse

from .helpers import fetch_html, rel_to_absolute, save_from_url

import re

def scrape_excel(xls_filepath):
    '''
    Generate codelist files from XLS CRS codelists.
    '''
    url = 'https://webcache.googleusercontent.com/search?q=cache:https://www.oecd.org/dac/financing-sustainable-development/development-finance-standards/dacandcrscodelists.htm'
    base_url = urlunparse(urlparse(url)._replace(path=''))
    soup = fetch_html(url)
    doc = soup.find(class_='document')
    # XLS link sometimes includes a space
    xls_url = doc.find('a', string=re.compile(r'(\s*)XLS(\s*)'))['href']
    xls_url = rel_to_absolute(xls_url, base_url=base_url)
    save_from_url(xls_url, xls_filepath)
