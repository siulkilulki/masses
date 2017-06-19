import requests
from string import Template
from random import choice
from proxy import Proxy
from bs4 import BeautifulSoup
from bs4.dammit import EncodingDetector


class DuckDuckGo(object):
    """Documentation for DuckDuckGo

    """

    def __init__(self, proxies=None, language='', external_download=True):
        self.proxy_obj = Proxy() if proxies is None else Proxy(proxies)
        self.query = Template('https://duckduckgo.com/html/?q=$query&kl=' +
                              language)
        self.falitures = 0
        self.golden_proxies = []
        self.external_download = external_download
        self.download = False

    def _get(self, query):
        query = query.replace(' ', '+')
        link = self.query.substitute(query=query)
        if self.proxy_obj.proxies:
            return self._request(link)
        return requests.post(link)

    def _request(self, link):
        proxy = self.proxy_obj.random()
        proxy_dict = self._proxy_to_dict(proxy)
        while True:
            try:
                resp = requests.post(link, proxies=proxy_dict, timeout=2)
                print(proxy_dict)
                self.golden_proxies.append(proxy)
                return resp
            except:
                print('Nr of falitures: ' + str(self.falitures) + ' Proxies: '
                      + str(len(self.proxy_obj.proxies)) + ' Golden proxies: '
                      + str(len(self.golden_proxies)))
                self.proxy_obj.proxies.remove(proxy)
                proxy = self.proxy_obj.random()
                proxy_dict = self._proxy_to_dict(proxy)

                self.falitures += 1
                total_nr_of_proxies = len(
                    self.proxy_obj.proxies) + self.falitures
                if self.falitures > 0.95 * total_nr_of_proxies:
                    if self.download:
                        self.download_proxies()
                        self.download = False
                    self.download = True
                    self.falitures = 0
                    self.proxy_obj.proxies.extend(self.golden_proxies)
                    del self.golden_proxies[:]

    def _proxy_to_dict(self, proxy):
        proxy_string = str(proxy[0]) + ':' + str(proxy[1])
        return {
            "http": 'http://' + proxy_string,
            "https": 'https://' + proxy_string
        }

    def download_proxies(self, limit=0):
        self.proxy_obj.download(limit)

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
    duck.download_proxies(1)
    proxy = duck.proxy_obj.random()
    proxy = duck._proxy_to_dict(proxy)
    print(proxy)
    link = 'https://duckduckgo.com/?q=my+ip&t=canonical&atb=v67-1&ia=answer'
    resp = requests.get(link, proxies=proxy, verify=False)
    print(resp.content)
    #link = 'http://www.whatismyproxy.com/'
    #resp = requests.get(link, proxies=proxy, verify=False)
    #print(resp.content)

    import ipdb
    ipdb.set_trace()


if __name__ == '__main__':
    main()
