from concurrent.futures import ThreadPoolExecutor, as_completed
from gsalud.serializers import RecordSerializer
from gsalud.models import Record
from django.db import transaction


def insert_update_bulk_records(records, list_fields, match_field):
    with transaction.atomic():
        Record.objects.bulk_update_or_create(
            records, list_fields, match_field=match_field)
        return

def insert_bulk_records(records):
    with transaction.atomic():
        Record.objects.bulk_create(records)

def record_exists(id_record):
    return Record.objects.filter(id_record=id_record).exists()

def update_single_record(record_instance, force=False):
    try:
        with transaction.atomic():
            update_id = record_instance.pk
            existing_record_instance = Record.objects.select_for_update().get(id_record=update_id)
            new_record_hash = record_instance.hashed_val
            existing_record_hash = existing_record_instance.hashed_val
            if new_record_hash != existing_record_hash or force:
                # The hashes don't match, update the record
                existing_record_instance.__dict__.update(record_instance.__dict__)
                existing_record_instance.save()
        return True, f"Updated record {update_id}"
    except Record.DoesNotExist:
        return False, f"Record with id {update_id} does not exist."
    except Exception as e:
        return False, f"Error updating record {update_id}: {e}"

def update_bulk_records(record_instances, max_workers=5):
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_record = {executor.submit(update_single_record, record): record for record in record_instances}
        for future in as_completed(future_to_record):
            record = future_to_record[future]
            try:
                success, message = future.result()
                results.append((success, message))
            except Exception as exc:
                results.append((False, f"Record {record.pk} generated an exception: {exc}"))
    return results