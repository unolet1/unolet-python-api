import datetime

from dateutil import parser


def is_string_decimal(string):
    try:
        float(string)
        return '.' in string and all(char.isdigit() for char in string.split('.', 1)[1])
    except ValueError:
        return False


def string_to_date(string):
    return parser.isoparse(string)


def date_to_string(date):
    return date.isoformat()