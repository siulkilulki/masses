import unittest
import sys, os
#print('!!! Dawid: ' + os.path.realpath('.'))
#print(sys.path)

# sys.path.append(os.path.realpath('..'))
# sys.path.append(os.path.realpath('.'))
from scraper.parishesinfo import ParishScraper


class TestParishScraper(unittest.TestCase):
    class RequestMock(object):
        pass

    def _scrape_info(self, filename, url):
        scraper = ParishScraper()
        page = self.RequestMock()
        page.url = url
        with open(filename, 'r') as f:
            page.text = f.read()
        return scraper._retrieve_info(page)

    def test_retrieve_info_from_page_186(self):
        url = 'http://colaska.pl/index/parafia/id/186'
        result = self._scrape_info('./tests/parish_186.html', url)
        self.assertEqual(
            'Parafia pod wezwaniem Niepokalanego Poczęcia Najświętszej Maryi Panny',
            result['name'])
        self.assertEqual('Będzin', result['city'])
        self.assertEqual('', result['url'])
        self.assertEqual(url, result['meta_url'])
        self.assertEqual('ul. Pokoju 28', result['street'])
        self.assertEqual('42-504 Będzin-Łagisza', result['postal_code'])
        self.assertEqual('19.140243530273438,50.354281540838365',
                         result['gps'])

    def test_retrieve_info_from_page_2765(self):
        url = 'http://colaska.pl/index/parafia/id/2765'
        result = self._scrape_info('./tests/parish_2765.html', url)
        self.assertEqual('Parafia pod wezwaniem Św. Rocha', result['name'])
        self.assertEqual('Jasieniec', result['city'])
        self.assertEqual('http://www.parafia-jasieniec.pl', result['url'])
        self.assertEqual(url, result['meta_url'])
        self.assertEqual('ul. Warecka 37', result['street'])
        self.assertEqual('05-604 Jasieniec k/Grójca', result['postal_code'])
        self.assertEqual(',', result['gps'])

    def test_retrieve_info_from_page_4(self):
        url = 'http://colaska.pl/index/parafia/id/4'
        result = self._scrape_info('./tests/parish_4.html', url)
        self.assertEqual('Parafia pod wezwaniem św.Jana Chrzciciela',
                         result['name'])
        self.assertEqual('Adamów', result['city'])
        self.assertEqual('', result['url'])
        self.assertEqual(url, result['meta_url'])
        self.assertEqual('', result['street'])
        self.assertEqual('27-300 Brody Iłżeckie', result['postal_code'])
        self.assertEqual(',', result['gps'])


if __name__ == '__main__':
    unittest.main()
