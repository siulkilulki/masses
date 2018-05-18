#!/usr/bin/env python3

import redis
r = redis.StrictRedis(host='localhost', port=6379, db=0)
annotated = set()
all_count = 0
for key in set(r.scan_iter()):
    key = key.decode('utf-8')
    if ':' in key and not '.' in key:
        all_count += 1
        index = key.split(':')[1]
        annotated.add(index)
print('All annotations: {}'.format(all_count))
print('Annotated utterances: {}'.format(len(annotated)))
