#!/usr/bin/env python3
import jsonlines
import sys
import html2text
import pprint
import re

class Parish2Text():
    def __init__(self):
        "docstring"
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
        parish['button_text'] = ' '.join(re.sub('[\W_]+', ' ', parish['button_text']).split())
        return parish


def main():
    parish2text = Parish2Text()
    writer = jsonlines.Writer(sys.stdout)
    # text_maker.wrap_links = False
    reader = jsonlines.Reader((line.rstrip('\n') for line in sys.stdin))
    for parish in reader:
        parish = parish2text.convert(parish)
        parish_content = parish.pop('content')
        pprint.pprint(parish)
        print(parish_content)
    reader.close()

if __name__ == '__main__':
    main()
