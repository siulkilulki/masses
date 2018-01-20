#!/usr/bin/env python3
import requests
from string import Template
import re
from bs4 import BeautifulSoup
import unicodedata
import logging

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


def get_address(url):
    page = requests.get(url, timeout=10)
    soup = BeautifulSoup(page.text, 'html.parser')
    address = soup.find(class_='adres adres2').find_next('div', class_='row')
    return '|'.join(list(address.stripped_strings))

    # description = soup.find(class_='tytul5 clear').find_next(class_='row')
    # match = re.search('<b>www:</b> (.*?)<br', str(soup))


def process_page(url):
    page = requests.get(url, timeout=10)
    soup = BeautifulSoup(page.text, 'html.parser')
    for td in soup.find_all('td', class_='temat'):
        href = td.a['href']
        parish_name = td.a.get_text(strip=True)
        # parish_name = ' '.join(
        #     unicodedata.normalize("NFKD", parish_name).split())
        td_city = td.find_next('td')
        td_province = td_city.find_next('td')
        td_diocese = td_province.find_next('td')
        td_decanate = td_diocese.find_next('td')
        address = get_address(href)
        print('\t'.join([
            parish_name, td_city.get_text(strip=True),
            address, td_diocese.get_text(strip=True), td_decanate.get_text(
                strip=True), td_province.get_text(strip=True)
        ]))


def main():
    base_url = 'https://www.deon.pl/parafie-koscioly/'
    suffix = Template('strona,${page}.html')

    print('\t'.join([
        'Parafia', 'Miejscowość', 'Adres', 'Diecezja', 'Dekanat', 'Województwo'
    ]))
    process_page(base_url)
    for i in range(2, 1014):  # TODO: add search for last page nr on deon
        url = base_url + suffix.substitute(page=str(i))
        process_page(url)
        logging.info(i)


if __name__ == '__main__':
    main()
