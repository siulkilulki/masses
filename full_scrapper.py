import dill
from duckduckgo import DuckDuckGo
from urllib.parse import urlparse
import time
import random

tsv = ''
urls = ''


def check(parish, duck):
    global urls
    global tsv
    links = _urls(parish, duck)
    for link in links:
        parish_root_url = urlparse(parish.url).netloc
        if parish_root_url == urlparse(link).netloc:
            urls += parish_root_url + '\n'
            tsv += parish.name + '\t' + parish.city + '\t' + parish.street + '\t' + parish.postal_code + '\t' + parish_root_url + '\t' + parish.meta_url + '\t' + parish.gps + '\n'
            print('added')
            # TODO: save links to txt file, one per line
            # TODO: wget -r -i file all links
            # TODO: save parishes to jsonline format
            return True  # mark as ok url
    return False


def _urls(parish, duck):
    query = parish.name + ' ' + parish.street + ' ' + parish.postal_code
    links = duck.links(query)
    time.sleep(1)
    while not links:
        print('retry')
        random.randint(3, 10)
        time.sleep(10)
        links = duck.links(query)
    return links


def find_url(parish):
    links = _urls(parish)
    import ipdb
    ipdb.set_trace()
    print(links)


def main():
    parishes = []
    with open('./parishes.dill', 'rb') as f:
        parishes = dill.load(f)

    duck = DuckDuckGo(language='pl-pl')
    print('Downloading proxies')
    duck.download_proxies()
    i = 0
    for parish in parishes:
        print(str(i / len(parishes)) + '% done. Nr: ' + str(i))
        i += 1
        if parish.url:
            check(parish, duck)
    with open('urls.txt', 'w') as f:
        f.write(urls)
    with open('parishes.tsv', 'w') as f:
        f.write(tsv)


if __name__ == "__main__":
    main()
