"""The script scrapes https://flagma.ua/ site. It collects contact data for
each company from the specified category. The results are saved to a CSV file.

The scraping process requires dynamic IP change, for the site has anti-scrape
protection (IP ban). Therefore the script uses free TOR proxy. In order to
make things working the TOR Windows Expert Bundle should be downloaded and
installed from here:

https://www.torproject.org/download/tor/

And then the constant TOR_EXECUTABLE_PATH in ./utils/tor_proxy.py should be
modified accordingly.
"""
import base64
import logging
import re
import os

from bs4 import BeautifulSoup

from utils.http_request import HttpRequest, PROXY_TYPE_FREE, PROXY_TYPE_TOR
from utils.scraping_utils import (
    FATAL_ERROR_STR,

    setup_logging,
    fix_filename,
    remove_umlauts,
    clean_text,

    save_last_page,
    load_last_page,

    save_items_csv,
    load_items_csv,

    save_items_json,
    load_items_json,
)

CSV_FILENAME = 'items.csv'
JSON_FILENAME = 'items.json'

COLUMNS = [
    'name',
    'phones',
    'link',
]

BASE_URL = 'https://flagma.ua/companies/remont-pk-i-orgtehniki-kompanii/'
PAGE_URL = BASE_URL + 'page-{}/'

ENCODED_HTML_RE = re.compile(
    r'var str = "(.+)"; \$\(this\)\.parent\(\)\.html\("<em>"'
    + r'\+Base64\.decode\(str\)\+"</em>"\);'
)

PHONE_RE = re.compile(r'tel:(.+)')

setup_logging()
request = HttpRequest(proxies=PROXY_TYPE_TOR)

def get_html(url: str) -> str:
    r = request.get(url)
    if r == None:
        return None
    return r.text

def scrape_item(url: str) -> dict:
    html = get_html(url)
    if not html:
        return None

    item = {
        'name': '',
        'phones': '',
        'link': url,
    }

    try:
        item['name'] = clean_text(
            BeautifulSoup(html, 'lxml').find('h1', itemprop='name').get_text())
    except AttributeError:
        logging.exception('Error while parsing company name.')
        return None

    phones = []
    matches = re.findall(ENCODED_HTML_RE, clean_text(html))
    if len(matches) > 0:
        soup = BeautifulSoup(str(base64.b64decode(matches[0]), 'utf-8'),
                             'lxml')
        for phone_link in soup.find_all('a', class_='tel'):
            phone_matches = re.findall(PHONE_RE, phone_link.get('href', ''))
            if len(phone_matches) > 0:
                phones.append(phone_matches[0])

    item['phones'] = '; '.join(phones)

    return item

def get_page_count() -> int:
    html = get_html(BASE_URL)
    if not html:
        return None

    try:
        page_count = int(
            BeautifulSoup(html, 'lxml')
            .find('li', class_='page notactive').span.get_text())
    except (AttributeError, ValueError):
        logging.exception('Error while parsing page count.')
        return None

    return page_count

# First page index is 1 (not 0), last page index is page count
def get_item_links(page: int) -> list:
    html = get_html(PAGE_URL.format(page))
    if not html:
        return None

    links = []

    try:
        item_header_divs = BeautifulSoup(html, 'lxml').find_all(
            'div', class_='page-list-item-header')

        for item_header_div in item_header_divs:
            links.append(item_header_div.div.a['href'])

    except (AttributeError, KeyError):
        logging.exception('Error while parsing item links.')
        return None

    return links

def item_is_scraped(items: list, link: str) -> bool:
    for item in items:
        if item['link'] == link:
            logging.info(f'The item {link} is already scraped. Skipping.')
            return True
    return False

# The items parameter may contain previous scraping result
def scrape_page_items(items: list = [], page: int = 1) -> list:
    logging.info(f'Scraping items for page {page}.')

    links = get_item_links(page)
    if links == None:
        return items

    for link in links:
        if item_is_scraped(items, link):
            continue
        item = scrape_item(link)
        if item != None:
            items.append(item)

    if save_items_json(items, JSON_FILENAME):
        result = 'OK'
    else:
        result = 'FAILURE'

    logging.info(f'Saving intermediate results for page {page}: {result}.')

    return items

def scrape_all_items() -> list:
    # Anti-bot protection workaround
    request.rotate_proxy()
    page_count = get_page_count()
    if page_count == None:
        return None
    logging.info(f'Total page count: {page_count}.')

    if os.path.exists(JSON_FILENAME):
        logging.info('Loading previous scraping result.')
        items = load_items_json(JSON_FILENAME)
    else:
        items = []

    for page in range(1, page_count + 1):
        # Anti-bot protection workaround
        request.rotate_proxy()
        items = scrape_page_items(items, page)

    return items

def main():
    logging.info('Starting scraping process.')
    items = scrape_all_items()
    if items == None:
        logging.error(FATAL_ERROR_STR)
        return

    logging.info('Scraping process complete. Now saving the results.')
    if not save_items_csv(items, COLUMNS, CSV_FILENAME):
        logging.error(FATAL_ERROR_STR)
        return
    logging.info('Saving complete.')

if __name__ == '__main__':
    main()
