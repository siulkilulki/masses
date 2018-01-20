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
    page.encoding = 'iso-8859-2'
    soup = BeautifulSoup(page.text, 'html.parser')
    info = soup.find(class_='info')
    masses = soup.find(text=re.compile('.*niedziel.*'))
    parish_url = soup.find(text=re.compile('.*www:.*'))
    try:
        parish_url = parish_url.find_parent('td').find(
            href=re.compile('^http.*'))['href'] if parish_url else ''
    except:
        logging.warning(page.url)
        return False
    if masses and info:
        info_text = info.get_text(separator='\n', strip=True)
        info_text = ' '.join(info_text.split())
        masses = masses.find_parent().find_parent()
        masses_table = masses.text.split('\n')
        try:
            sunday_masses = [el for el in masses_table if 'niedziel' in el][0]
            everyday_masses = [el for el in masses_table if 'powszed' in el][0]
            sunday_masses = ' '.join(sunday_masses.split())
            everyday_masses = ' '.join(everyday_masses.split())
            print('\t'.join([
                info_text, parish_url, sunday_masses, everyday_masses, page.url
            ]))
        except:
            logging.warning(page.url)
            return False
        return True
    else:
        logging.warning(page.url)
        return False


def main():
    base_url = 'http://www.archpoznan.pl/'
    start_url = base_url + 'content/view/155/82/'
    key = 'component/option,com_contact/'
    page = requests.get(start_url, timeout=10)
    links = [
        base_url + link.rstrip('"')
        for link in re.findall(key + '.*?"', page.text)
    ]
    links = list(OrderedDict.fromkeys(links))
    print(
        '\t'.join(['Parafia', 'url', 'niedzielne', 'powszednie', 'debug_url']))
    i = 0
    for link in links:
        if process_page(link):
            i += 1
            logging.info(i)


if __name__ == '__main__':
    main()
