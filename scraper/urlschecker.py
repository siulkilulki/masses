import pickle
from duckduckgo import DuckDuckGo
from parishduck import ParishDuck
import time
import random
import requests

urls_append_filename = 'urls_checked_a.txt'
parishes_append_filename = 'parishes_checked_a.txt'


class ParishUrlChecker():
    def __init__(self):
        "docstring"
        self.tsv = ''
        self.urls = ''
        self.added = 0
        self.tried_urls = 0

    def check(self, parish, duck):
        self.tried_urls += 1
        parish_duck = ParishDuck()
        links = parish_duck.urls(parish, duck)
        parish_url = self._get_true_url(parish['url'])
        if not parish_url:
            return False
        for link in links:
            link = self._get_true_url(link)
            if parish_url == link:
                t_parish_url = parish_url + '\n'
                self.urls += t_parish_url
                t_tsv = parish['name'] + '\t' + parish_url + '\t' + parish['city'] + '\t' + parish['street'] + '\t' + parish['postal_code'] + '\t' + parish['meta_url'] + '\t' + parish['gps'] + '\n'

                self.tsv += t_tsv
                with open(urls_append_filename, 'a') as file:
                    file.write(t_parish_url)
                with open(parishes_append_filename, 'a') as file:
                    file.write(t_tsv)

                self.added += 1
                print('Added: ' + parish_url)
                # TODO: save links to txt file, one per line
                # TODO: wget -r -i file all links
                # TODO: not wget, but spider
                # TODO: save parishes to jsonline format?
                return True  # mark as ok url
        #print(links)
        return False

    def _convert_url(self, url):
        if url.endswith('/'):
            url = url[:-1]
        if url.startswith('http://'):
            url = url[7:]
        if url.startswith('https://'):
            url = url[8:]
        if url.startswith('www.'):
            url = url[4:]
        return url

    def _get_true_url(self, url):
        if 'http://' not in url and 'https://' not in url:
            url = 'http://' + url
        for i in range(5):
            try:
                new_url = requests.get(url, timeout=3).url
                return new_url
            except:
                pass
        print('Falied url: ' + url)
        return ''


def main():
    with open(urls_append_filename, 'w') as file:
        pass
    with open(parishes_append_filename, 'w') as file:
        pass

    duck = DuckDuckGo(language='pl-pl')
    print('Downloading proxies')
    duck.download_proxies()
    parishes = []
    urls_checker = ParishUrlChecker()
    with open('./parishes.pickle', 'rb') as f:
        parishes = pickle.load(f)

    i = 1
    for parish in parishes:
        if parish['url']:
            urls_checker.check(parish, duck)
        else:
            print('none')
            print(
                str(i * 100 / len(parishes)) + '% done. Nr: ' + str(i) +
                '  Performance: ' + str(urls_checker.added) + '/' +
                str(urls_checker.tried_urls) + ' ' + str(
                    (urls_checker.added /
                     (urls_checker.tried_urls or 1)) * 100) + '%')
        i += 1
    with open('urls_checked.txt', 'w') as f:
        f.write(urls)
    with open('parishes_checked.tsv', 'w') as f:
        f.write(tsv)


if __name__ == "__main__":
    main()
