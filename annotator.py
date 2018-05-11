#!/usr/bin/env python3
import jsonlines
from extractor.find_hours import hours_iterator
from parishwebsites.parish2text import Parish2Text
import os
import random

parish2text = Parish2Text()

CONTEXT = 100


def process_parish_page(parish_page):
    content = parish_page.pop('content')
    for utterance, utterance_colored in hours_iterator(content, color=True):
        print(utterance_colored)
        import ipdb
        ipdb.set_trace()


def process_parish_file(parish_reader):
    for parish_page in parish_reader:
        parish_page = parish2text.convert(parish_page)
        import ipdb
        ipdb.set_trace()
        process_parish_page(parish_page)


def process_directory(directory):
    for root, dirs, files in os.walk(directory):
        random.shuffle(files)
        for fname in files:
            filepath = os.path.join(root, fname)
            if os.path.getsize(filepath) > 0:
                with jsonlines.open(filepath) as parish_reader:
                    process_parish_file(parish_reader)


def main():
    process_directory('./parishwebsites/data')


if __name__ == '__main__':
    main()
