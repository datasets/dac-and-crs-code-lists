from bs4 import BeautifulSoup as bs
import requests


def save_from_url(url, filepath):
    print('Saving: ' + url)
    with open(filepath, 'wb') as f:
        r = requests.get(url, stream=True)
        r.raise_for_status()
        for block in r.iter_content(1024):
            f.write(block)


def rel_to_absolute(url, base_url):
    if url.startswith('/'):
        url = base_url + url
    return url


def fetch_html(url):
    print('Fetching: ' + url)
    r = requests.get(url, headers={'user-agent': 'curl/7.72.0'})
    r.raise_for_status()
    soup = bs(r.text, 'html.parser')
    return soup
