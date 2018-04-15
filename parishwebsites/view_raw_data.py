#!/usr/bin/env python3
import jsonlines
import sys
import html2text
import pprint


def convert_html_to_text(parish, text_maker):
    html = parish['content']
    text = text_maker.handle(html)
    parish['content'] = text
    return parish


def main():
    text_maker = html2text.HTML2Text()
    text_maker.ignore_links = True
    text_maker.ignore_images = True
    writer = jsonlines.Writer(sys.stdout)
    # text_maker.wrap_links = False
    text_maker.strong_mark = ''
    with jsonlines.open(sys.argv[1]) as reader:
        for parish in reader:
            parish = convert_html_to_text(parish, text_maker)
            parish_content = parish.pop('content')
            pprint.pprint(parish)
            print(parish_content)

if __name__ == '__main__':
    main()
