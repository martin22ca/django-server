from gsalud.serializers import RecordInfoSerializer
from django.db import transaction
from gsalud.models import RecordInfo


def insertRecordsCases(newRecordInfoData):
    with transaction.atomic():
        serializer = RecordInfoSerializer(data=newRecordInfoData, many=True)
        if serializer.is_valid():
            serializer.save()
            print('Casos Registrados')
        else:
            print("Error in serializer validation:", serializer.errors)


def updateRecordsCases(updateRecordsInfoIds, updateRecordsInfoData):
    with transaction.atomic():
        for update_id, update_data in zip(updateRecordsInfoIds, updateRecordsInfoData):
            record_info_instance = RecordInfo.objects.get(id_record__exact=update_id)
            serializer = RecordInfoSerializer(instance=record_info_instance, data=update_data)
            if serializer.is_valid():
                serializer.save()
            else:
                print("Error in serializer validation:", serializer.errors)