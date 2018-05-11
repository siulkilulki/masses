#!/usr/bin/env python3
import redis
from utils import iterator
from extractor.find_hours import hours_iterator
import re

# r = redis.StrictRedis(host='localhost', port=6379, db=0)


def add_utterances(content, utterances):
    utterances_nr = 0
    for utterances_nr, utterance in enumerate(hours_iterator(content)):
        utterances.append(utterance)
    return utterances_nr


def has_mass_metadata(url, button_text):
    regex = re.compile('msz[eay]|nabo[żz]e[ńn]stw|porz[ąa]dek')
    url_match = regex.search(url)
    button_match = regex.search(button_text)
    if url_match and button_match:
        print('both - url_metch: {}'.format(url_match.group(0)))
        print('button_metch: {}'.format(button_match.group(0)))
        return True
    elif url_match:
        print('url_match: {}'.format(url_match.group(0)))
        return True
    elif button_match:
        print('button_match: {}'.format(button_match.group(0)))
        return True
    return False


def load_parishes(directory):
    utterances = []
    utterances_count = 0
    for file_nr, parish_path in enumerate(
            iterator.parish_path_iterator(directory)):
        print(parish_path)
        metadata_count = 0
        for page_nr, parish_page in enumerate(
                iterator.parish_page_iterator(parish_path)):
            content = parish_page.pop('content')
            # if page_nr == 0 or has_mass_metadata(parish_page['url'], parish_page['button_text']):
            if page_nr == 0:
                utterances_count += add_utterances(content, utterances)
            if has_mass_metadata(parish_page['url'],
                                 parish_page['button_text']):
                metadata_count += 1
                utterances_count += add_utterances(content, utterances)

            if metadata_count == 1:
                break

            if page_nr == 100:
                print(utterances_count)
                break
            print('file: {}, page: {}, utterances: {}'.format(
                file_nr, page_nr, utterances_count))
    return {}


utterances = {}


def main():
    load_parishes('./parishwebsites/data')
    # r.set('foo', 'bar')
    # print(r.get('foo'))


if __name__ == '__main__':
    main()
