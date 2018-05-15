import re
from colorama import Fore, Back, Style

hour_regex = re.compile(
    '(0[6-9]|1\d|2[0-2])[:.](oo|[0-5]\d)|6|7|8|9|1\d|2[0-2]')


def borders_ok(text, start, end):
    text = ' ' + text + ' '
    before_start_char = text[start]
    after_end_char = text[end + 1]
    if ((before_start_char.isspace() or before_start_char in ',(/')
            and (after_end_char.isspace() or after_end_char in ',;)/')
            and (before_start_char != '(' or after_end_char != ')')):
        return True
    else:
        return False


def delete_duplicates(text):
    text = re.sub(' +', ' ', text)
    text = re.sub(' ?\n ?', '\n', text)
    text = re.sub('\n{5,}', '\n\n\n', text)
    text = re.sub('\n\n', '\n', text)
    return text


def get_context(text, start, end, minsize):
    hour = text[start:end]
    prefix = delete_duplicates(text[:start]).rsplit(
        ' ', maxsplit=minsize + 12)[1:]
    suffix = delete_duplicates(text[end:]).split(
        ' ', maxsplit=minsize + 2)[:-1]
    return ' '.join(prefix), hour, ' '.join(suffix)


def hours_iterator(text, minsize=20, color=False):
    for hour_match in hour_regex.finditer(text):
        start = hour_match.start(0)
        end = hour_match.end(0)
        if not borders_ok(text, start, end):
            continue
        prefix, hour, suffix = get_context(text, start, end, minsize)
        if color:
            utterance = f'{prefix}&&&{hour}###{suffix}'
            yield utterance, color_hour(prefix, hour, suffix, Fore.GREEN,
                                        Style.BRIGHT)
        else:
            yield prefix, hour, suffix


# w klasyfikatorze dzielić tak aby jeszcze \n było oddzielnie


def color_hour(prefix, hour, suffix, color, style):
    return prefix + color + style + hour + Style.RESET_ALL + suffix
