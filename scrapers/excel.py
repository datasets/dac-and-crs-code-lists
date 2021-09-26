from urllib.parse import urlparse, urlunparse

from .helpers import fetch_html, rel_to_absolute, save_from_url


def scrape_excel(xls_filepath):
    '''
    Generate codelist files from XLS CRS codelists.
    '''
    url = 'http://www.oecd.org/dac/stats/dacandcrscodelists.htm'
    base_url = urlunparse(urlparse(url)._replace(path=''))
    soup = fetch_html(url)
    doc = soup.find(class_='document')
    xls_url = doc.find('a', text='XLS')['href']
    xls_url = rel_to_absolute(xls_url, base_url=base_url)
    save_from_url(xls_url, xls_filepath)
