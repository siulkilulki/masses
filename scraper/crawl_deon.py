#!/usr/bin/env python3
from time import sleep
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
    page = requests.get(url, timeout=30)
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
def retry_download(url, sleep_time = 0):
    try:
        process_page(url)
    except Exception as e:
        if sleep_time == 0:
            sleep_time = 1.5 
        logging.info(e)
        logging.info('Waiting {}s.\n'.format(sleep_time))
        sleep(sleep_time)
        retry_download(url, sleep_time * 1.5)

def main():
    base_url = 'https://www.deon.pl/parafie-koscioly/'
    suffix = Template('strona,${page}.html')

    print('\t'.join([
        'Parafia', 'Miejscowość', 'Adres', 'Diecezja', 'Dekanat', 'Województwo'
    ]))
    retry_download(base_url)
    for i in range(2, 1014):  # TODO: add search for last page nr on deon
        url = base_url + suffix.substitute(page=str(i))
        retry_download(url)
        logging.info(i)


if __name__ == '__main__':
    main()
