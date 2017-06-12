import requests
from string import Template
from random import choice
from proxy import Proxy
from bs4 import BeautifulSoup
from bs4.dammit import EncodingDetector


class DuckDuckGo(object):
    """Documentation for DuckDuckGo

    """

    def __init__(self, proxies=None, language=''):
        self.proxy_obj = Proxy() if proxies is None else Proxy(proxies)
        self.query = Template('https://duckduckgo.com/html/?q=$query&kl=' +
                              language)

    def _get(self, query):
        query = query.replace(' ', '+')
        link = self.query.substitute(query=query)
        if self.proxy_obj.proxies:
            proxy = self.proxy_obj.random()
            print(proxy)
            return requests.post(link, proxies=proxy)
        return requests.post(link)

    def _proxy_to_dict(self, proxy):
        proxy_string = str(proxy[0]) + ':' + str(proxy[1])
        return {"http": proxy_string, "https": proxy_string}

    def download_proxies(self):
        self.proxy_obj.download()

    def _soup(self, query):
        resp = self._get(query)
        content_type = resp.headers.get('content-type', '').lower()
        http_encoding = resp.encoding if 'charset' in content_type else None
        html_encoding = EncodingDetector.find_declared_encoding(
            resp.content, is_html=True)
        encoding = html_encoding or http_encoding
        return BeautifulSoup(resp.content, 'lxml', from_encoding=encoding)

    def html(self, query):
        soup = self._soup(query)
        return soup.prettify()

    def links(self, query):
        soup = self._soup(query)
        return [
            link.get('href')
            for link in soup.find_all('a', class_='result__snippet')
        ]


def main():
    duck = DuckDuckGo(language='pl-pl')
    links = duck.links('koscioly polska')
    print(links)


if __name__ == '__main__':
    main()
