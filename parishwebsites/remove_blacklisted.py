#!/usr/bin/env python3
import sys

with open(sys.argv[1]) as f:
    blacklisted_domains = [line.rstrip('\n') for line in f]

for line in sys.stdin:
    for domain in blacklisted_domains:
        if domain not in line:
            print(line, end='')


