#!/usr/bin/env python3
import urllib
import logging
import redis
from utils import iterator
from extractor.find_hours import hours_iterator
import re
import pickle


# r = redis.StrictRedis(host='localhost', port=6379, db=0)
class Utterance():
    def __init__(self, utterance, url, button_text, depth, filename, line_no):
        "docstring"
        self.utterance = utterance
        self.url = url
        self.button_text = button_text
        self.depth = depth
        self.filename = filename
        self.line_no = line_no


def add_utterances(parish_page, parish_path, utterances):
    utterances_nr = 0
    content = parish_page['content']
    for utterances_nr, utterance in enumerate(hours_iterator(content)):
        utterance_inst = Utterance(
            utterance, parish_page['url'], parish_page['button_text'],
            parish_page['depth'], parish_path, parish_page['line_no'])
        utterances.append(utterance_inst)
    return utterances_nr


def has_mass_metadata(url, button_text, page):
    path = urllib.parse.urlparse(url).path
    url_suffix = path.rsplit('/', 1)[1] if '/' in path else path
    regex = re.compile(
        'msze|nabo[żz]e[ńn]stw(a|(?=\W\d)|$)|porz[ąa]dek($|\.htm)|porz[aą]dek.(liturgi|mszy)|(rozk[lł]ad|plan|godziny|uk[lł]ad|harmonogram|grafik|rozpiska).mszy',
        flags=re.IGNORECASE)
    bad_regex = re.compile(
        'nabo[zż]e[nń]stwa.(majowe|wielk|czerwcowe|maryjne|pasyjne|pokutne|fatimskie|do|ro[żz]a|czterdzie|w.wielk)',
        re.IGNORECASE)
    url_match = regex.search(url_suffix)
    bad_url_match = bad_regex.search(url_suffix)
    button_match = regex.search(button_text)
    bad_button_match = bad_regex.search(button_text)
    if url_match and button_match and not (bad_button_match or bad_url_match):
        # print('both - url_metch: {}'.format(url_match.group(0)))
        # print('button_metch: {}'.format(button_match.group(0)))
        return True
    elif url_match and not bad_url_match:
        # print('url_match: {}'.format(url_match.group(0)))
        return True
    elif button_match and not button_match:
        # print('button_match: {}'.format(button_match.group(0)))
        return True
    return False


def remove_http_www(url):
    url = re.sub('^https?://', '', url)
    return re.sub('^www\.', '', url)


def gather_parish_pages(parish_path, unique_urls):
    parish_pages = {}
    for page_nr, parish_page in enumerate(
            iterator.parish_page_iterator(parish_path, html=False)):
        url = remove_http_www(parish_page['url'])
        button_text = parish_page['button_text']
        if url not in unique_urls and has_mass_metadata(
                url, button_text, parish_page):
            unique_urls.add(url)
            parish_page['line_no'] = page_nr
            parish_pages[url] = parish_page
    return parish_pages


def get_best_parish_pages(parish_pages, n=3):
    def pop_best_and_clear(pages):
        shortest_url = min(parish_pages.keys(), key=lambda x: len(x))
        best = pages.pop(shortest_url)
        for key in list(parish_pages.keys()):
            if key.startswith(shortest_url):
                del pages[key]
        return best

    best_n = []
    for i in range(n):
        if parish_pages:
            best_n.append(pop_best_and_clear(parish_pages))
    return best_n


def remove_duplicates(utterances):
    seen = set()
    res = []
    for utt in utterances:
        if utt.utterance not in seen:
            res.append(utt)
            seen.add(utt.utterance)
    return res


def load_parishes(directory, extracted_by_rules):
    utterances = []
    utterances_count = 0
    last = 0
    maximum = 0
    unique_urls = set()
    for file_nr, parish_path in enumerate(
            iterator.parish_path_iterator(directory)):
        if parish_path in extracted_by_rules:
            continue
        # print(parish_path)
        metadata_count = 0
        file_utterances = 0
        parish_pages_dict = gather_parish_pages(parish_path, unique_urls)
        parish_pages = get_best_parish_pages(parish_pages_dict)
        maximum = max(len(parish_pages), maximum)
        for pages_count, parish_page in enumerate(parish_pages):
            new_utterances = add_utterances(parish_page, parish_path,
                                            utterances)
            # if new_utterances > 100: # TODO: in future check this value if it's to big then dont add new_utterances
            #     pass
            utterances_count += new_utterances
            file_utterances += new_utterances
            url = parish_page['url']  # TODO delete
            button_text = parish_page['button_text']  # TODO: delete
            logging.warning('{}\t||| {} ||| {} ||| {}'.format(
                new_utterances, url, button_text, parish_page['depth']))

            if utterances_count != last:
                curr_str = 'file: {}, page: {}, utterances: {}'.format(
                    file_nr, parish_page['line_no'], utterances_count)
                print(curr_str)
            last = utterances_count
    print(maximum)
    return remove_duplicates(utterances)


def get_extracted_by_rules(filename):
    extracted_by_rules = set()
    with open(filename) as f:
        for line in f:
            extracted_by_rules.add(line.rstrip('\n'))
    return extracted_by_rules


def main():
    extracted_by_rules = get_extracted_by_rules('./extracted-by-rules.txt')
    utterances = load_parishes('./parishwebsites/text-data',
                               extracted_by_rules)
    print(len(utterances))
    with open('utterances.pkl', 'wb') as f:
        pickle.dump(utterances, f, pickle.HIGHEST_PROTOCOL)
    # r.set('foo', 'bar')
    # print(r.get('foo'))


if __name__ == '__main__':
    main()
