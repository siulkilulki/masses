import requests
from string import Template
from random import choice


class DuckDuckGo(object):
    """Documentation for DuckDuckGo

    """

    def __init__(self, proxies=None, language=''):
        self.proxies = [] if proxies is None else proxies
        self.language = language
        self.query = Template('https://duckduckgo.com/html/?q=$query&kl=$lang')

    def _get(self, query, language):
        link = self.query.substitute(query=query, lang=language)
        if self.proxies:
            proxy = choice(self.proxies)
            ip_and_port = proxy[0]
            protocol = proxy[1]
            proxies = {protocol: ip_and_port}
            requests.get(link, proxies=proxies)
        return requests.get(link)

    def body(self, query, language):
        pass

    def links(self, query, language):
        pass


def main():
    pass


if __name__ == '__main__':
    main()