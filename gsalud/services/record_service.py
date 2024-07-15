from concurrent.futures import ThreadPoolExecutor, as_completed
from gsalud.serializers import RecordSerializer
from gsalud.models import Record
from django.db import IntegrityError, transaction


def insert_update_bulk_records(records, list_fields, match_field):
    with transaction.atomic():
        Record.objects.bulk_update_or_create(
            records, list_fields, match_field=match_field)
        return


def insert_bulk_records(records):
    with transaction.atomic():
        Record.objects.bulk_create(records)


def record_exists(record_key):
    return Record.objects.filter(record_key=record_key).exists()


def get_record_by_key(record_key):
    return Record.objects.get(record_key=record_key)


def update_single_record(record_instance: Record, force=False):
    try:
        with transaction.atomic():
            update_record_key = record_instance.record_key
            try:
                existing_record_instance = Record.objects.select_for_update().get(
                    record_key=update_record_key)
            except Record.DoesNotExist:
                return False, f"Record with id {update_record_key} does not exist."

            new_record_hash = record_instance.hashed_val
            existing_record_hash = existing_record_instance.hashed_val

            if new_record_hash != existing_record_hash or force:
                # The hashes don't match, update the record
                for field in record_instance._meta.fields:
                    if field.name != 'id' and field.name != 'record_key':
                        setattr(existing_record_instance, field.name,
                                getattr(record_instance, field.name))

                try:
                    existing_record_instance.save()
                    return True, f"Updated record {update_record_key}"
                except IntegrityError as ie:
                    return False, f"Integrity error updating record {update_record_key}: {ie}"
            else:
                return True, f"No update needed for record {update_record_key}"

    except Exception as e:
        return False, f"Error updating record {update_record_key}: {e}"


def update_bulk_records(record_instances, max_workers=5):
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_record = {executor.submit(
            update_single_record, record): record for record in record_instances}
        for future in as_completed(future_to_record):
            record = future_to_record[future]
            try:
                success, message = future.result()
                results.append((success, message))
            except Exception as exc:
                results.append(
                    (False, f"Record {record.pk} generated an exception: {exc}"))
    for succes, msj in results:
        if not succes:
            print(msj)
