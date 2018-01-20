#!/usr/bin/env python3
from colorama import Fore, Back, Style
import os
import jsonlines
import re
import pprint


class Extractor:
    def __init__(self, page):
        "docstring"
        self.page = page
        self.content = page['content']
        self.header = self.wrap_with_name_group(
            'header',
            'porządek mszy (świętych|św|św\.)|msz[ea][ \n]+([śs]wi[eę]t[ea]|św|św\.)'
        )

        self.sunday_title = self.wrap_with_name_group(
            'sunday_title',
            'niedziel[a|e][ \n]+i[ \n]+(dni[ \n]+(świąteczne|św|św\.)|święta)'
            '|niedziel[ea]'
            '|porządek świąteczny')
        #'|święta'
        self.sunday_masses = self.wrap_with_name_group(
            'sunday_masses', '.*[^\d]\d{1,2}[^\d].*?')
        self.everyday_title = self.wrap_with_name_group(
            'everyday_title', 'dzień powszedni'
            '|dni powszednie'
            '|w tygodniu'
            '|porządek zwykły'
            '|od poniedziałku do soboty')
        self.everyday_masses = self.wrap_with_name_group(
            'everyday_masses',
            '(.*?[^\d\n]?\d{1,2}[^\d\n]?.*?\n)+')  # \n lub koniec stringa

    def wrap_with_name_group(self, name, pattern):
        return '(?P<{}>{})'.format(name, pattern)

    def extract(self, search_space=None):
        if not search_space:
            search_space = self.content
        header_match = re.search(self.header, search_space, re.I)
        if not header_match:
            return None
        search_space = search_space[header_match.end():]

        sunday_title_match = re.search(self.sunday_title, search_space, re.I)
        if not sunday_title_match:
            return None
        if re.search(self.header, search_space[:sunday_title_match.start()],
                     re.I):  # found header closer to sunday title
            return self.extract(search_space)
        if sunday_title_match.start() > 50:
            return self.extract(search_space[sunday_title_match.end()])

        everyday_title_match = re.search(self.everyday_title, search_space,
                                         re.I)
        if not everyday_title_match:
            return None
        sunday_masses_hours = search_space[sunday_title_match.end():
                                           everyday_title_match.start()]
        if not re.search(self.sunday_masses, sunday_masses_hours,
                         re.DOTALL | re.I):
            return None
        if len(sunday_masses_hours) > 500:
            return self.extract(search_space[sunday_title_match.end():])
        everyday_masses_match = re.search(
            self.everyday_masses, search_space[everyday_title_match.end():],
            re.I)
        if not everyday_masses_match:
            return None
        if everyday_masses_match.start() > 150:
            return self.extract(search_space[sunday_title_match.end():])

        whole_result = header_match.group(
            0) + search_space[:everyday_masses_match.end() +
                              everyday_title_match.end()]
        groups = (header_match.group(0), sunday_title_match.group(0),
                  sunday_masses_hours, everyday_title_match.group(0),
                  everyday_masses_match.group(0))
        # print(whole_result)
        # print(groups)
        # obsłużyć # TODO:
        # w dni powszednie (w roku szkolnym) - górny kościół
        # 6:30, 7:00, 8:00, 18:00
        # w dni powszednie (czas wakacji) - górny kościół
        # 7:00, 8:00, 18:00

        print('url: {}\ndepth: {}\nbutton: {}'.format(self.page[
            'url'], self.page['depth'], self.page['button_text']))
        return whole_result, groups


def process_directory(directory):
    found = 0
    not_found = 0
    for root, dirs, files in os.walk(directory):
        for fname in files:
            filepath = os.path.join(root, fname)
            if os.path.getsize(filepath) > 0:
                with jsonlines.open(filepath) as reader:
                    # print(filepath)
                    if process_parish(reader):
                        found += 1
                    else:
                        not_found += 1
                    # print('found: {}\nnot_found: {}'.format(found, not_found))
            else:
                pass  # empty file


def color_match(whole_match, groups, background, colors, style):
    for i in range(len(groups)):
        whole_match = whole_match.replace(
            groups[i], colors[i] + background + style + groups[i] +
            Style.RESET_ALL + background + style, 1)
    return whole_match + Style.RESET_ALL


def process_parish(reader):
    for page in sorted(reader, key=lambda x: x['depth']):  #sort by depth
        extractor = Extractor(page)
        result = extractor.extract()
        if result:
            whole_result, groups = result
            if whole_result not in page['content']:
                import ipdb
                ipdb.set_trace()
            pretty_text = page['content'].replace(
                whole_result,
                color_match(whole_result, groups, Back.BLACK, [
                    Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.MAGENTA, Fore.CYAN
                ], Style.BRIGHT))
            print(pretty_text)
            import ipdb
            ipdb.set_trace()
            return True
        else:
            return False
            # import ipdb
            # ipdb.set_trace()
            pass


def main():
    process_directory('./parishwebsites/data-final')


if __name__ == '__main__':
    main()
