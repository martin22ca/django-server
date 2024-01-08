from gsalud.models import ReceiptTypes, RecordTypes
from gsalud.serializers import ReceitTypesSerializer, RecordTypesSerializer


# --------- ReceiptTypes ----------

def getReceiptTypes():
    ReceipsObj = {}
    objs = ReceiptTypes.objects
    serializer = ReceitTypesSerializer(objs, many=True)
    for iType in serializer.data:
        ReceipsObj[iType['receipt_short']] = iType['id']
    return ReceipsObj


def registerNewReceiptType(short):
    if short == '':
        return

    newType = ReceiptTypes()

    newType.receipt_short = short
    newType.receipt_text = short

    newType.save()
    return None


# --------- ReceiptTypes ----------

def getRecordTypes():
    RecordsObj = {}
    objs = RecordTypes.objects
    serializer = RecordTypesSerializer(objs, many=True)
    for iType in serializer.data:
        RecordsObj[iType['record_name']] = iType['id']
    return RecordsObj


def registerNewRecordType(name):
    if name == '':
        return
    newType = RecordTypes()

    newType.record_name = name
    newType.record_desc = name

    newType.save()
    print('saved')
    return None
