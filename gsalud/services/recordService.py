from concurrent.futures import ThreadPoolExecutor, as_completed
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


def update_single_record(update_id, update_data,force = True):
    try:
        record_instance = Records.objects.get(id_record=update_id)
        new_record_hash = update_data['hashed_val']
        existing_record_hash = record_instance.hashed_val
        if new_record_hash != existing_record_hash or force:
            # The hashes don't match, update the record
            serializer = RecordSerializer(
                instance=record_instance, data=update_data)
            if serializer.is_valid():
                serializer.save()
            else:
                print(
                    f"Error in serializer validation for record {update_id}:", serializer.errors)
    except Records.DoesNotExist:
        print(f"Record with id {update_id} does not exist.")
    except Exception as e:
        print(f"Error updating record {update_id}: {e}")


def update_records(updateRecordsIds, updateRecordsData):
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(update_single_record, update_id, update_data)
            for update_id, update_data in zip(updateRecordsIds, updateRecordsData)
        ]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error in future result: {e}")
