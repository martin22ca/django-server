from datetime import datetime
from pandas import Timestamp


def handleDateDMY(dateVal):
    if dateVal:
        if isinstance(dateVal, Timestamp):
            # Convert Pandas Timestamp to datetime and extract the date
            date_object = dateVal.to_pydatetime().date()
            return date_object
        elif isinstance(dateVal, (int, float)):
            # Check if it's a timestamp (numeric)
            return datetime.utcfromtimestamp(dateVal).date()
        else:
            try:
                # Attempt to parse as a string date in format '%d/%m/%Y'
                date_object = datetime.strptime(dateVal, '%d/%m/%Y').date()
                return date_object
            except ValueError:
                return None  # Return None if parsing fails
    else:
        return None


def dateStrToDate(dateVal):
    if dateVal:
        return datetime.strptime(dateVal, '%Y-%M-%d').date()
    else:
        return None
