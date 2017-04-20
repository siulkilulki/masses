import requests
# from bs4 import BeautifulSoup
import re
from collections import namedtuple
import time
import dill


class ParishScraper(object):
    """Documentation for ParishScraper

    """

    def __init__(self):
        self.website_prefix = 'http://colaska.pl/index/parafia/id/'

    def _scrap(self):
        parishes = []
        for page_nr in range(1, 11000):
            page = self._get_page_stubbornly(page_nr)
            if 'id' in page.url:
                page_nr += 1
                parish = self._retrieve_info(page)
                print(parish)
                print('\n')
                parishes.append(parish)
        return parishes

    def _get_page_stubbornly(self, page_nr):
        sleep_time = 1
        while True:
            try:
                page = requests.get(
                    self.website_prefix + str(page_nr), timeout=10)
                if page.status_code == 500:
                    print('Status code 500 error')
                    raise ConnectionError
                return page
            except:
                sleep_time = sleep_time * 2 if sleep_time < 60 else 60
                print('Waiting ' + str(sleep_time) + ' sec')
                time.sleep(sleep_time)
                continue

    def _retrieve_info(self, page):
        page.encoding = 'utf-8'
        html_doc = page.text
        meta_url = page.url
        print(meta_url)
        try:
            search_result = re.search(
                'pHead rel">[\w\W]*?<p class="title">(.*?)</p>[\w\W]*?class="city">(.*?)</span>[\w\W]*?<p>(.*?)<br />(.*?)</p>',
                html_doc)
            if search_result is None:
                search_result = re.search(
                    'pHead rel">[\w\W]*?<p class="title">(.*?)</p>[\w\W]*?class="city">(.*?)</span>[\w\W]*?<p>(.*?)</p>',
                    html_doc)
                street = ''
                postal_code = search_result.group(3)
            else:
                street = search_result.group(3)
                postal_code = search_result.group(4)

            name = search_result.group(1)
            city = search_result.group(2)

            url_search = re.search('link mt10"><a href="(.*?)">', html_doc)
            url = '' if url_search is None else url_search.group(1)

            gps = re.search('id="tabsmaps" gps="(.*?)"><span',
                            html_doc).group(1)
            Parish = namedtuple('Parish', [
                'meta_url', 'url', 'name', 'city', 'street', 'postal_code',
                'gps'
            ])

            parish = Parish(meta_url, url, name, city, street, postal_code,
                            gps)
        except AttributeError:
            import ipdb
            ipdb.set_trace()
        return parish

    def scrap_and_save(self):
        parishes = self._scrap()
        with open('parishes.dill', 'wb') as f:
            dill.dump(parishes, f, dill.HIGHEST_PROTOCOL)
        pass


def main():
    parish_scraper = ParishScraper()
    parish_scraper.scrap_and_save()


if __name__ == "__main__":
    main()
