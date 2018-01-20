#!/usr/bin/env python3
import requests
import os
import jsonlines
import argparse


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-a',
        '--annotated',
        dest='annotated_file',
        type=argparse.FileType(encoding='utf-8'),
        help='File with parishes, urls and masses annotations.',
        required=True)
    return parser.parse_args()


def get_crawled_urls():
    crawled_urls = set()
    for root, dirs, files in os.walk('../parishwebsites/data-final'):
        for fname in files:
            with jsonlines.open(os.path.join(root, fname)) as reader:
                for page in reader:
                    if page:
                        crawled_urls.add(page['start_url'])
                    break
    return crawled_urls


def get_annotated_urls(annotated_file):
    annotated_urls = set()
    header = next(annotated_file).rstrip('\n').split('\t')
    for line in annotated_file:
        row = line.rstrip('\n').split('\t')
        url = row[header.index('url')]
        if not url:
            continue
        try:
            # if url == 'http://maczniki.pl':
            #     import ipdb
            #     ipdb.set_trace()
            # print(url)
            response = requests.get(url, timeout=60)
            request_url = response.url
            annotated_urls.add(request_url)
        except requests.exceptions.ConnectionError:
            pass
    annotated_file.close()
    return annotated_urls


def main():
    args = get_args()
    crawled_urls = get_crawled_urls()
    annotated_urls = get_annotated_urls(args.annotated_file)
    intersection = crawled_urls & annotated_urls
    for url in intersection:
        print(url)


if __name__ == '__main__':
    main()
