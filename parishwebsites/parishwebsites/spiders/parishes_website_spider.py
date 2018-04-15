import scrapy
import tldextract
import re
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import requests
from scrapy import signals
from scrapy.http import HtmlResponse
from binaryornot.helpers import is_binary_string
import logging
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import time

def requests_retry_session(
    retries=3,
    backoff_factor=1,
    status_forcelist=(500, 502, 503, 504, 408, 400, 404, 429, 401),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def get_redirected_url(url):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    t0 = time.time()
    final_url = None
    try:
        final_url = requests_retry_session().get(
            url,
            timeout=30
        ).url
    except Exception as e:
        logger.debug('Getting redirect url failed: {}'.format(e))
    else:
        logger.debug(f'Redirect url: {final_url}')
    finally:
        t1 = time.time()
        logger.debug('Getting redirect url took: {} seconds'.format(t1 - t0))
        return final_url

def _get_allowed_domains(urls):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    def extract_domain(url):
        ext = tldextract.extract(url)
        domain = '.'.join(ext).lstrip('.').rstrip('.')
        domain = re.sub('www.', '', domain)
        return domain
    domains = set() 
    for url in urls:
        domain = extract_domain(url)
        domains.add(domain)
        redirected_domain = extract_domain(get_redirected_url(url))
        if redirected_domain:
            domains.add(redirected_domain)
    domains = list(domains)
    logger.debug('Allowed domains: {}'.format(domains))
    return domains

def get_deny_domains():
    with open('domain-blacklist.txt') as f:
        blacklisted_domains = [line.rstrip('\n') for line in f]
    return blacklisted_domains

def configure_loggers():
    logger = logging.getLogger('chardet.charsetprober')
    logger.setLevel(logging.INFO)

    logger = logging.getLogger('scrapy.core.scraper')
    logger.setLevel(logging.INFO)

    logger = logging.getLogger('binaryornot.helpers')
    logger.setLevel(logging.INFO)

    logger = logging.getLogger('scrapy.spidermiddlewares.depth')
    logger.setLevel(logging.INFO)


class ParishesSpider(CrawlSpider):
    name = "parishes"
    rules = (Rule(
        LinkExtractor(deny_domains=get_deny_domains()),
        callback='parse_start_url',
        follow=True), )

    def __init__(self, *args, **kwargs):
        configure_loggers()
        super(ParishesSpider, self).__init__(*args, **kwargs)
        self.start_urls = [kwargs.get('url')]
        self.filename = kwargs.get('filename')
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
        fileinfo = '{}\t{}'.format(self.start_urls[0], self.filename)
        if reason == 'finished':
            with open('./processed.txt', mode='a', encoding='utf-8') as f:
                print(fileinfo, file=f)
        else:
            with open('./not-processed.txt', mode='a', encoding='utf-8') as f:
                print(fileinfo, file=f)
