#!/usr/bin/env python3
import jsonlines
import sys
import html2text
import pprint
import re
import logging


class Parish2Text():
    def __init__(self):
        '''Don't use this object for long period of time, because convertion
        will slowdown. Destroy it after every convertion.'''
        self.text_maker = html2text.HTML2Text()
        self.text_maker.ignore_links = True
        self.text_maker.ignore_images = True
        self.text_maker.images_to_alt = True
        self.text_maker.strong_mark = ''
        self.text_maker.ul_item_mark = ''
        self.text_maker.emphasis_mark = ''
        self.text_maker.ignore_tables = True

    def convert(self, parish):
        parish['content'] = self.text_maker.handle(parish['content'])
        parish['button_text'] = self.text_maker.handle(parish['button_text'])
        parish['button_text'] = ' '.join(
            re.sub('[\W_]+', ' ', parish['button_text']).split())
        return parish


def main():
    writer = jsonlines.Writer(sys.stdout)
    # text_maker.wrap_links = False
    reader = jsonlines.Reader((line.rstrip('\n') for line in sys.stdin))
    for page_nr, parish_page in enumerate(reader):
        parish2text = Parish2Text()
        try:
            parish_page = parish2text.convert(parish_page)
        except Exception:
            logging.warning('page: {},url: {}'.format(page_nr,
                                                      parish_page['url']))
            continue
        writer.write(parish_page)
        # parish_content = parish_page.pop('content')
        # pprint.pprint(parish_page)
        # print(parish_content)
    reader.close()


if __name__ == '__main__':
    main()
