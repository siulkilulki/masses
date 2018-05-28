#!/usr/bin/env python3
import csv
import sys
import re


def preprocess(prefix, hour, suffix):
    sentence = prefix + hour + suffix
    sentence = re.sub(r'\\n', r' \\n ', sentence)
    sentence = re.sub(' +', ' ', sentence)
    return sentence


def main():
    # csv.reader(sys.stdin, delimiter='\t')
    next(sys.stdin)
    for line in sys.stdin:
        prefix, hour, suffix, is_mass, yes_count, no_count, url, button_text, depth, filepath, line_no = line.rstrip(
            '\n').rsplit('\t')
        sentence = preprocess(prefix, hour, suffix)
        print(f'__label__{is_mass} {sentence}')


if __name__ == '__main__':
    main()
