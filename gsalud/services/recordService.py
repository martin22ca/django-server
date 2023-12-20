from gsalud.serializers import RecordSerializer
from gsalud.models import Records
from django.db import transaction


def insertRecords(newRecords):
    with transaction.atomic():
        serializer = RecordSerializer(data=newRecords, many=True)
        if serializer.is_valid():
            serializer.save()
            print('Expedientes Registrados')
        else:
            print("Error in serializer validation:", serializer.errors)


def updateRecords(updateRecordsIds, updateRecordsData):
    with transaction.atomic():
        for update_id, update_data in zip(updateRecordsIds, updateRecordsData):
            record_instance = Records.objects.get(id=update_id)
            serializer = RecordSerializer(
                instance=record_instance, data=update_data)

            new_record_hash = update_data['hashedVal']
            existing_record_hash = record_instance.hashedVal
            if new_record_hash != existing_record_hash:
                # The hashes don't match, update the record
                print("Hashes don't match, update for record ID:", update_id)
                serializer = RecordSerializer(instance=record_instance, data=update_data)

                if serializer.is_valid():
                    serializer.save()
                else:
                    print("Error in serializer validation:", serializer.errors)
