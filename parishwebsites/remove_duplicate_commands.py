#!/usr/bin/env python3
import sys
import re

d = {}
for line in sys.stdin:
    line = line.rstrip('\n')
    id_ = re.search('"(data/.*)" 2>', line).group(1)
    d[id_] = line

for line in d.values():
    print(line)

