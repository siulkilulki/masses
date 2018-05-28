#!/usr/bin/env python3
import sys

import argparse
import redis
from extractor.find_hours import color_hour
import pickle
from colorama import Fore, Back, Style
import time
import datetime
import re
from collections import defaultdict, Counter
import math

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


def is_cookie_index(key):
    if ':' in key and not 'jshash' in key and not '.' in key and r.type(
            key) == b'string':
        return True


def investigate_by_cookie(cookie_hash):
    cx = 0
    index_stop = None
    for key in sorted(set(r.scan_iter())):
        key = key.decode('utf-8')
        if is_cookie_index(key) and cookie_hash in key:
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
            print(annotation_info)
            action = input(
                'c: continue, cX: continue Xtimes, number: goto index\n')
            if action.isdigit():
                index_stop = int(action)
            else:
                index_stop = None
            if action[0] == 'c':
                if action[1:].isdigit():
                    cx = int(action[1:])


def pprint_utterance(index, annotation_info=None):
    if not annotation_info:
        annotation_info = ['y']
    color = Fore.GREEN if annotation_info[0] in 'yYt' else Fore.RED
    print(
        color_hour(utterances[index]['prefix'], utterances[index]['hour'],
                   utterances[index]['suffix'], color))


def print_stats():
    annotated = set()
    all_count = 0
    for key in set(r.scan_iter()):
        key = key.decode('utf-8')
        if is_cookie_index(key) and not r.sismember('banned',
                                                    key.split(':')[0]):
            all_count += 1
            index = key.split(':')[1]
            annotated.add(index)
    print('All annotations: {}'.format(all_count))
    print('Annotated utterances: {}/{}'.format(
        len(annotated), len(utterances)))


def ban(cookie):
    r.sadd('banned', cookie)
    for key in set(r.scan_iter()):
        key = key.decode('utf-8')
        if is_cookie_index(key) and cookie in key.split(':')[0]:
            user, index = key.split(':')
            annotation = r.get(key).decode('utf-8')
            if annotation[0] in 'yn':
                yesno = annotation[0].translate(str.maketrans('yn', 'tf'))
                r.setrange(key, 0, yesno)
                str_index = int(annotation.split(':')[1])
                r.setrange(index, str_index,
                           yesno)  #sets str_index to yesno value
                r.zincrby('utterance-scores', index, -1)


def users_stats():
    users_dict = defaultdict(lambda: defaultdict(list))
    users_set = set()
    for key in sorted(set(r.scan_iter())):
        key = key.decode('utf-8')
        if is_cookie_index(key):
            user = key.split(':')[0]
            users_set.add(user)
            res = r.get(key)
            res_list = res.decode('utf-8').split(':')
            if len(res_list) == 4:
                yesno, str_index, timestamp, ip_addr = res_list
            else:
                yesno, str_index, timestamp = res_list
                ip_addr = '0'
            if 'last_access' not in users_dict[user]:
                users_dict[user]['last_access'] = float(timestamp)
            else:
                users_dict[user]['last_access'] = max(
                    float(timestamp), users_dict[user]['last_access'])
            if 'yes_count' not in users_dict[user]:
                users_dict[user]['yes_count'] = 0
            if 'no_count' not in users_dict[user]:
                users_dict[user]['no_count'] = 0
            if yesno in 'yYt':
                users_dict[user]['yes_count'] += 1
            elif yesno in 'nNf':
                users_dict[user]['no_count'] += 1
            users_dict[user]['annotations'].append({
                'yesno':
                yesno,
                'str_index':
                int(str_index),
                'timestamp':
                float(timestamp),
                'ip_addr':
                ip_addr
            })
    for user in users_set:
        users_dict[user]['annotations'] = sorted(
            users_dict[user]['annotations'], key=lambda x: x['timestamp'])
    calculate_avg_annotation_time(users_dict)
    print_sorted(users_dict)


def calculate_avg_annotation_time(users_dict, max_interval=10):
    for user, user_dict in users_dict.items():
        delta_sum = 0
        divider = 0
        breaks = 0
        for ann_1, ann_2 in zip(user_dict['annotations'],
                                user_dict['annotations'][1:]):
            delta = ann_2['timestamp'] - ann_1['timestamp']
            if delta < 10:
                delta_sum += delta
                divider += 1
            else:
                breaks += 1

        if delta_sum == 0:
            user_dict['avg_time'] = math.inf
        else:
            user_dict['avg_time'] = round(delta_sum / divider, 4)
        user_dict['breaks'] = breaks


def print_sorted(users_dict, sortby='annotations max'):
    print('\t'.join([
        'cookie', 'annotations', 'yes', 'no', 'avg_time', 'breaks', 'status',
        'last_access'
    ]))
    if sortby == 'annotations max':
        keyfunc = lambda x: len(x[1]['annotations'])
    for user, user_dict in sorted(
            users_dict.items(), key=keyfunc, reverse=True):
        if user_dict['yes_count'] + user_dict['no_count'] != len(
                user_dict['annotations']):
            import ipdb
            ipdb.set_trace()
        status = 'uncertain'
        if r.sismember('banned', user):
            status = 'banned'
        elif r.sismember('trusted', user):
            status = 'trusted'
        elif r.sismember('trusted-checked', user):
            status = 'trusted-checked'
        print('\t'.join([
            user,
            str(len(user_dict['annotations'])),
            str(user_dict['yes_count']),
            str(user_dict['no_count']),
            str(user_dict['avg_time']),
            str(user_dict['breaks']), status,
            format_time(user_dict['last_access'])
        ]))


def redis2tsv():
    print('\t'.join([
        'prefix', 'hour', 'suffix', 'is_mass', 'yes_count', 'no_count', 'url',
        'button_text', 'depth', 'filepath', 'line_no'
    ]))
    for index, utterance in enumerate(utterances):
        utterance_annotations = r.get(index)
        if utterance_annotations:
            utterance_annotations = utterance_annotations.decode('utf-8')
        if utterance_annotations and re.search('[yYnN]',
                                               utterance_annotations):
            annotations_counts = Counter(utterance_annotations.lower())
            if annotations_counts['y'] > annotations_counts['n']:
                is_mass = 'no'
            elif annotations_counts['y'] < annotations_counts['n']:
                is_mass = 'yes'
            else:
                continue
            trans_table = str.maketrans({'\x00': '', '\n': '\\n'})
            print('\t'.join([
                utterance['prefix'].translate(trans_table),
                utterance['hour'].translate(trans_table),
                utterance['suffix'].translate(trans_table), is_mass,
                str(annotations_counts['y']),
                str(annotations_counts['n']), utterance['url'],
                utterance['button_text'],
                str(utterance['depth']), utterance['filepath'],
                str(utterance['line_no'])
            ]))


def get_args():
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest='cmd')
    parser_stats = subparser.add_parser('stats', help='Show annotation stats.')
    parser_investigate = subparser.add_parser(
        'investigate', help='investigate cookie.')
    parser_investigate.add_argument('cookie', help='User cookie string')
    parser_index = subparser.add_parser('index', help='Print utterance.')
    parser_index.add_argument('index', type=int, help='Utterance index')
    subparser.add_parser('ipdb', help='Get into ipdb.')
    parser_exec = subparser.add_parser('exec', help='Execute redis command.')
    parser_exec.add_argument(
        'redis_command',
        help=
        'Redis command (lowercased). e.g. to get r.zrangebyscore("key", "-inf", "inf", start=0, num=1) pass \'zrangebyscore("key", "-inf", "inf", start=0, num=1)\''
    )
    parser_users = subparser.add_parser('users', help='User statistics')
    parser_ban = subparser.add_parser('ban', help='Ban user')
    parser_ban.add_argument('cookie', help='Cookie.')

    parser_2tsv = subparser.add_parser('2tsv', help='Convert data to tsv')
    return parser, parser.parse_args()


def main():
    parser, args = get_args()
    if args.cmd == 'stats':
        print_stats()
    elif args.cmd == 'investigate':
        investigate_by_cookie(args.cookie)
    elif args.cmd == 'users':
        users_stats()
    elif args.cmd == 'index':
        pprint_utterance(args.index)
    elif args.cmd == 'ban':
        ban(args.cookie)
    elif args.cmd == '2tsv':
        redis2tsv()
    elif args.cmd == 'ipdb':
        import ipdb
        ipdb.set_trace()
    elif args.cmd == 'exec':
        exec('print(r.{})'.format(args.redis_command), {
            'print': print,
            'r': r
        })
    else:
        print(parser.format_help())


if __name__ == '__main__':
    main()
