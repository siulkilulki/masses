#!/usr/bin/env python3
import traceback
import sys
from googleplaces import GooglePlaces, lang, GooglePlacesError, Place
# import jsonlines
import argparse
import logging
from enum import Enum, auto
from collections import namedtuple
logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


class Result(Enum):
    OK = auto()
    # WITHOUT_WEBSITE = 'WITHOUT_WEBSITE'
    AMBIGUOUS = auto()
    NOT_FOUND = auto()


def _retrieve_parish_info(row, google_places, detailed=True):
    parish_name = row[0]
    city = row[1]
    address = row[2]
    street = address.split('|')[1]
    if detailed:
        query = '{} {} {}'.format(parish_name, street, city)
    else:
        query = '{} {}'.format(parish_name, city)
    query_result = google_places.text_search(
        query, language=lang.POLISH, radius=None)
    if len(query_result.places) == 1:
        place = query_result.places[0]
        place.get_details()
        return place, Result.OK
    elif len(query_result.places) > 1:
        # place = query_result.places[0]
        # place.get_details()
        tmp_row = row[:]
        tmp_row.insert(0, 'AMBIGUOUS')
        tmp_row.insert(1, query)
        tmp_row.append(str(query_result.places))
        logging.info('\t' + '\t'.join(tmp_row))
        place = query_result.places[0]
        place.get_details()
        return place, Result.AMBIGUOUS
    else:
        if detailed:
            return _retrieve_parish_info(row, google_places, detailed=False)
        else:
            tmp_row = row[:]
            tmp_row.insert(0, 'NOT_FOUND')
            tmp_row.insert(1, query)
            logging.info('\t' + '\t'.join(tmp_row))
            return None, Result.NOT_FOUND


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-a',
        '--apikey',
        dest='apikey',
        type=argparse.FileType(encoding='utf-8'),
        help='File with apikey inside',
        required=True)
    # nargs='?',
    # default=sys.stdin)
    parser.add_argument(
        '-p',
        '--parishes',
        dest='parishes',
        type=argparse.FileType(encoding='utf-8'),
        nargs='?',
        default=sys.stdin,
        help='Tsv parishes file',
        required=True)

    # parser.add_argument(
    #     '-n',
    #     '--not-found',
    #     type=argparse.FileType('w+', encoding='utf-8'),
    #     help='Output file of not found parishes',
    #     required=True)

    # parser.add_argument(
    #     '-a',
    #     '--ambiguous',
    #     type=argparse.FileType('w+', encoding='utf-8'),
    #     help='Output file of ambiguous parishes',
    #     required=True)

    return parser.parse_args()


def add_parish_info(row, parish, result):
    url = parish.website if parish.website else ''
    row.insert(2, url)
    row.append(parish.place_id)
    row.append(result.name)


def write_last_line_to_file(filepath, line_nr):
    with (open(filepath), 'w+') as f:
        print(line_nr, file=f)


def count_file_number_of_lines(filepath):
    try:
        with open(filepath) as f:
            return sum(1 for _ in f)
    except FileNotFoundError:
        return 0


def main():
    # writer = jsonlines.Writer(sys.stdout)

    args = get_args()
    apikey = args.apikey.read().rstrip('\n')  # TODO: should be apikey file
    args.apikey.close()

    outputfile_path = './parishes-with-urls.tsv' # TODO: move to parameters
    nr_of_outputfile_lines = count_file_number_of_lines(outputfile_path)

    header = next(args.parishes).rstrip('\n').split('\t')
    header.insert(2, 'url')
    if nr_of_outputfile_lines == 0:
        print('\t'.join(header) + '\tplace_id')
    google_places = GooglePlaces(apikey)
    for line_nr, line in enumerate(args.parishes):
        if line_nr + 1 < nr_of_outputfile_lines:
            continue
        row = line.rstrip('\n').split('\t')
        try:
            parish, result = _retrieve_parish_info(row, google_places)
            if not parish:
                NullPlace = namedtuple('NullPlace', ['website', 'place_id'])
                parish = NullPlace('', '')
        except Exception as e:
            traceback.print_stack()
            logging.info('Probably limit exceeded. Exiting.\nException: {}'.format(e))
            # write_last_line_to_file(outputfile_path, line_nr)
            return
        add_parish_info(row, parish, result)
        print('\t'.join(row), flush=True)

    # write_last_line_to_file(outputfile_path, 0)
    args.parishes.close()


if __name__ == '__main__':
    main()
