#!/usr/bin/env python3
import jsonlines
import sys
import html2text


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
    # text_maker.strong_mark = ''
    with jsonlines.open(sys.argv[1]) as reader:
        for parish in reader:
            parish = convert_html_to_text(parish, text_maker)
            writer.write(parish)
    writer.close()


if __name__ == '__main__':
    main()
