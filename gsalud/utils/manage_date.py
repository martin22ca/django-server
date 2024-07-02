from datetime import datetime
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
