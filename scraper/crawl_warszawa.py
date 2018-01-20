#!/usr/bin/env python3
import re
from bs4 import BeautifulSoup
import requests
import logging
from collections import OrderedDict

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


def process_page(url):
    logging.info(url)
    page = requests.get(url, timeout=30)
    soup = BeautifulSoup(page.text, 'html.parser')
    parish_url = soup.find('a', class_='website')
    parish_url = parish_url['href'] if parish_url else ''
    name = soup.find('title').text
    masses = soup.find('div', class_='masses')
    if not masses:
        return
    sunday_masses = masses.find_next(
        'div', class_='column').find_next(
            'div', class_='column')
    if 'powszednie' in masses.text:
        everyday_masses = sunday_masses.find_next(
            'div', class_='column').find_next(
                'div', class_='column').text
    else:
        everyday_masses = ''
    sunday_masses = sunday_masses.text
    print('\t'.join(
        [name, parish_url, sunday_masses, everyday_masses, page.url]))


def get_all_urls():
    # urls = []
    base_url = 'http://archwwa.pl/parafie/strona/'
    for i in range(1, 23):
        page = requests.get(base_url + str(i), timeout=30)
        soup = BeautifulSoup(page.text, 'html.parser')
        for el in soup.find_all('a', class_='more-link'):
            # urls.append(el['href'])
            yield el['href']
    # return urls


def main():
    urls = get_all_urls()
    print(
        '\t'.join(['Parafia', 'url', 'niedzielne', 'powszednie', 'debug_url']))
    i = 0
    for url in urls:
        if url == 'http://archwwa.pl/parafie/strona-parafii-propozycja/':
            continue
        process_page(url)
        i += 1
        logging.info(i)


if __name__ == '__main__':
    main()
