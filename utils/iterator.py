import os
import jsonlines
import random
from parishwebsites.parish2text import Parish2Text


def parish_path_iterator(directory):
    for root, dirs, files in os.walk(directory):
        for fname in sorted(files):
            filepath = os.path.join(root, fname)
            if os.path.getsize(filepath) > 0:
                yield filepath


def parish_page_iterator(filepath, html=True):
    with jsonlines.open(filepath) as parish_reader:
        for parish_page in parish_reader:
            if 'Maximum execution time of 30 seconds exceeded in' in parish_page[
                    'content']:
                continue
            if html:
                parish2text = Parish2Text()
                yield parish2text.convert(parish_page)
            else:
                yield parish_page
