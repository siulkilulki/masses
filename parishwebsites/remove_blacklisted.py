#!/usr/bin/env python3
import sys

def is_blacklisted(line, blacklisted_domains):
    for domain in blacklisted_domains:
        if domain in line:
            return True
    return False


with open(sys.argv[1]) as f:
    blacklisted_domains = [line.rstrip('\n') for line in f]

for line in sys.stdin:
    if not is_blacklisted(line, blacklisted_domains):
        print(line, end='')


