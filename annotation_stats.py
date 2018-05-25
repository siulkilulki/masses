#!/usr/bin/env python3
import sys

import redis
from extractor.find_hours import color_hour
import pickle
from colorama import Fore, Back, Style
import time
import datetime
import re

r = redis.StrictRedis(unix_socket_path='/redis-socket/redis.sock', db=0)


def load_utterances(filename):
    with open(filename, 'rb') as f:
        utterances = pickle.load(f)
    return utterances


utterances = load_utterances(
    '/home/siulkilulki/gitrepos/mass-scraper/utterances.pkl')


def format_time(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime(
        '%H:%M:%S.%f   %Y-%m-%d')


def investigate_by_cookie(cookie_hash):
    cx = 0
    index_stop = None
    for key in sorted(set(r.scan_iter())):
        key = key.decode('utf-8')
        if ':' in key and not '.' in key and cookie_hash in key:
            if cx != 0:
                cx -= 1
                continue
            index = int(key.split(':')[1])
            if index_stop and index_stop != index:
                continue
            annotation_info = r.get(key).decode('utf-8')
            pprint_utterance(index, annotation_info)
            print(index)
            print(format_time(float(annotation_info.split(':')[2])))
            # print(annotation_info)
            action = input(
                'c: continue, cX: continue Xtimes, number: goto index\n')
            if action.isdigit():
                index_stop = int(action)
            else:
                index_stop = None
            if action[0] == 'c':
                if action[1:]:
                    cx = int(action[1:])


def pprint_utterance(index, annotation_info=None):
    if not annotation_info:
        annotation_info = ['y']
    color = Fore.GREEN if annotation_info[0] == 'y' else Fore.RED
    print(
        color_hour(utterances[index]['prefix'], utterances[index]['hour'],
                   utterances[index]['suffix'], color))


def print_stats():
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


def main():
    if sys.argv[1] == 'stats':
        print_stats()
    elif sys.argv[1] == 'investigate':
        investigate_by_cookie(sys.argv[2])
    elif sys.argv[1] == 'index':
        pprint_utterance(int(sys.argv[2]))
    elif sys.argv[1] == 'console':
        import ipdb
        ipdb.set_trace()
    elif sys.argv[1] == 'exec':
        exec('print(r.{})'.format(sys.argv[2]), {'print': print, 'r': r})


if __name__ == '__main__':
    main()
