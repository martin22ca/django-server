from datetime import datetime


def handleDateDMY(dateVal):
    if dateVal:
        date_object = datetime.strptime(dateVal, '%d/%m/%Y').date()
        return date_object
    else:
        return None


def handleDatetimeToDate(dateVal):
    if dateVal:
        date_object = dateVal.date()
        return date_object
    else:
        return None
