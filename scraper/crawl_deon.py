#!/usr/bin/env python3
import requests
from string import Template
import re
from bs4 import BeautifulSoup
import unicodedata


def process_parish(url, parish_name):
    page = requests.get(url, timeout=10)
    soup = BeautifulSoup(page.text, 'html.parser')
    # address = soup.find(class_='adres adres2')
    # description = soup.find(class_='tytul5 clear').find_next(class_='row')
    match = re.search('<b>www:</b> (.*?)<br', str(soup))
    if match:
        parish_url = match.group(1)
        print('\t'.join([url, parish_name, parish_url]))
    else:
        if re.search('www:', str(soup)):
            print(url)

    # TODO: regexy lub soup


def process_page(url):
    page = requests.get(url, timeout=10)
    soup = BeautifulSoup(page.text, 'html.parser')
    for td in soup.find_all('td', class_='temat'):
        href = td.a['href']
        parish_name = td.a['title']
        parish_name = ' '.join(
            unicodedata.normalize("NFKD", parish_name).split())
        process_parish(href, parish_name)


def main():
    base_url = 'https://www.deon.pl/parafie-koscioly/'
    suffix = Template('strona,${page}.html')

    process_page(base_url)
    for i in range(2, 1014):  # TODO: add search for last page nr on deon
        url = base_url + suffix.substitute(page=str(i))
        process_page(url)


if __name__ == '__main__':
    main()
