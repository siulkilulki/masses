import scrapy
import tldextract
import re
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import requests
from scrapy import signals
from scrapy.http import HtmlResponse
from binaryornot.helpers import is_binary_string

def _get_allowed_domains(urls):
    domains = []
    for url in urls:
        ext = tldextract.extract(url)
        domain = '.'.join(ext).lstrip('.').rstrip('.')
        domain = re.sub('www.', '', domain)
        domains.append(domain)
    return domains

def get_deny_domains():
    with open('domain-blacklist.txt') as f:
        blacklisted_domains = [line.rstrip('\n') for line in f]
    return blacklisted_domains

class ParishesSpider(CrawlSpider):
    name = "parishes"
    rules = (Rule(
        LinkExtractor(deny_domains=get_deny_domains()),
        callback='parse_start_url',
        follow=True), )

    def __init__(self, *args, **kwargs):
        super(ParishesSpider, self).__init__(*args, **kwargs)
        self.start_urls = [kwargs.get('url')]
        self.allowed_domains = _get_allowed_domains(self.start_urls)

    def parse_start_url(self, response):
        link_text = response.meta[
            'link_text'] if 'link_text' in response.meta else ''
        previous_url = response.meta[
            'previous_url'] if 'previous_url' in response.meta else ''

        if not is_binary_string(response.body[:2048]):
            yield {
                "url": response.url,
                "depth": response.meta['depth'],
                "button_text": link_text,
                "previous_url": previous_url,
                "start_url": self.start_urls[0],
                "domain": self.allowed_domains[0],
                "content": response.text
            }
        else:
            self.logger.info('Content at {} is not text.'.format(response.url))

    def _requests_to_follow(self, response):
        if not isinstance(response, HtmlResponse):
            return
        seen = set()
        for n, rule in enumerate(self._rules):
            links = [
                lnk for lnk in rule.link_extractor.extract_links(response)
                if lnk not in seen
            ]
            if links and rule.process_links:
                links = rule.process_links(links)
            for link in links:
                seen.add(link)
                r = self._build_request(n, link)
                r.meta.update(previous_url=response.url)
                yield rule.process_request(r)

    def closed(self, reason):
        if reason == 'finished':
            with open('./processed.txt', mode='a', encoding='utf-8') as f:
                print(self.start_urls[0], file=f)
        else:
            with open('./not-processed.txt', mode='a', encoding='utf-8') as f:
                print(self.start_urls[0], file=f)
