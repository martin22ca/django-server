from datetime import datetime
from django.db.models import Func, CharField
from django.forms import ValidationError
import pandas as pd


def handle_date_DMY(date_param):
    if date_param is None:
        return None
    if isinstance(date_param, datetime):
        return date_param.date()
    elif isinstance(date_param, str):
        try:
            return datetime.strptime(date_param, '%d/%m/%Y').date()
        except ValueError:
            print("Invalid date string format. Expected DD/MM/YYYY")
            return None
    else:
        return None


def dateStrToDate(dateVal):
    if dateVal:
        if dateVal != '':
            return datetime.strptime(dateVal, '%Y-%M-%d').date()
        else:
            return None
    else:
        return None
    
def parse_date(date_str):
    """
    Convert a date string from 'day/month/year' format to 'YYYY-MM-DD' format.
    """
    try:
        # Convert the date string to a datetime object
        parsed_date = datetime.strptime(date_str, '%d/%m/%Y')
        # Return the date in 'YYYY-MM-DD' format
        return parsed_date.strftime('%Y-%m-%d')
    except ValueError:
        raise ValidationError(f'Invalid date format: {date_str}. Expected format is "day/month/year".')



class ToChar(Func):
    function = 'TO_CHAR'
    template = "%(function)s(%(expressions)s, 'DD/MM/YYYY')"
    output_field = CharField()
