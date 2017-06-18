import requests
import re
from collections import namedtuple
import time
import pickle
from lxml import html
import html as python_html


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
            html_tree = html.document_fromstring(html_doc)
            url = html_tree.xpath('//p[@class="link mt10"]/a/@href')
            url = url[0] if url else ''
            name = html_tree.xpath(
                '//div[@class="pHead rel"]/p[@class="title"]/text()')[0]
            city = html_tree.xpath('//span[@class="city"]/text()')[0]
            street_and_postal_code = html_tree.xpath(
                '//span[@class="city"]/following-sibling::p[1]')[0]
            street_and_postal_code_string = html.tostring(
                street_and_postal_code).decode('utf-8')
            street_and_postal_code_string = python_html.unescape(
                street_and_postal_code_string)
            if '<br>' in street_and_postal_code_string:
                search_result = re.search('<p>(.*?)<br>(.*?)</p>',
                                          street_and_postal_code_string)
                street = search_result.group(1)
                postal_code = search_result.group(2)
            else:
                postal_code = street_and_postal_code.text_content()
                street = ''
            gps = html_tree.xpath('//@gps')[0].replace(' ', '')
            parish = {
                'name': name,
                'city': city,
                'url': url,
                'meta_url': meta_url,
                'street': street,
                'postal_code': postal_code,
                'gps': gps
            }
        except:
            import ipdb
            ipdb.set_trace()
        return parish

    def scrap_and_save(self):
        parishes = self._scrap()
        with open('parishes.pickle', 'wb') as f:
            pickle.dump(parishes, f, pickle.HIGHEST_PROTOCOL)
        pass


def main():
    parish_scraper = ParishScraper()
    parish_scraper.scrap_and_save()


if __name__ == "__main__":
    main()
