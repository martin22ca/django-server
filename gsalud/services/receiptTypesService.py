from ..models import ReceiptTypes
from ..serializers import ReceitTypesSerializer


def getTypesObj():
    ReceiptTypesObj = {}
    objs = ReceiptTypes.objects
    serializer = ReceitTypesSerializer(objs, many=True)
    for iType in serializer.data:
        ReceiptTypesObj[iType['receipt_short']] = iType['id']
    return ReceiptTypesObj
