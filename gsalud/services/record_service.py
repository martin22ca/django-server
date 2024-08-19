from concurrent.futures import ThreadPoolExecutor, as_completed
from gsalud.utils.manage_date import ToChar
from gsalud.models import Record, RecordsInfoUsers
from django.db import IntegrityError, transaction
from django.db.models import F,Q, Case, When, Value, BooleanField


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


def get_filtered_user_records(id_user, record_keys=None):
    try:
        base_queryset = RecordsInfoUsers.objects.select_related(
            'id_record_info__id_record',
            'id_record_info__id_record__id_provider',
            'id_record_info__id_record__id_record_type',
            'id_record_info__id_lot',
            'id_record_info__id_record__id_provider__id_particularity',
            'id_record_info__id_auditor'
        ).annotate(
            record_key=F('id_record_info__id_record__record_key'),
            uxri_id=F('id'),
            assigned=F('id_record_info__assigned'),
            id_provider=F(
                'id_record_info__id_record__id_provider__id_provider'),
            business_name=F(
                'id_record_info__id_record__id_provider__business_name'),
            record_name=F(
                'id_record_info__id_record__id_record_type__record_name'),
            id_lot=F('id_record_info__id_lot__id'),
            id_auditor=F('id_record_info__id_auditor'),
            auditor=F('id_record_info__id_auditor__user_name'),
            priority=Case(
                When(id_record_info__id_record__id_provider__priority__isnull=False, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            ),
            id_coordinator=F(
                'id_record_info__id_record__id_provider__id_coordinator'),
            record_total=F('id_record_info__id_record__record_total'),
            date_entry_digital=ToChar(F('id_record_info__date_entry_digital')),
            date_entry_physical=ToChar(F('id_record_info__date_entry_physical')),
            seal_number=F('id_record_info__seal_number'),
            observation=F('id_record_info__observation'),
            lot_key=F('id_record_info__id_lot__lot_key'),
            particularity=Case(
                When(
                    Q(id_record_info__id_record__id_provider__id_particularity__part_prevencion__isnull=False) |
                    Q(id_record_info__id_record__id_provider__id_particularity__part_g_salud__isnull=False),
                    then=Value(True)
                ),
                default=Value(False),
                output_field=BooleanField()
            )
        ).filter(id_user=id_user)

        if record_keys:
            base_queryset = base_queryset.filter(record_key__in=record_keys)

        return base_queryset.values(
            'id', 'record_key', 'uxri_id', 'worked_on', 'assigned', 'id_provider', 'business_name',
            'record_name', 'id_lot', 'id_auditor', 'auditor', 'priority', 'id_coordinator', 'record_total',
            'date_entry_digital', 'date_entry_physical', 'seal_number', 'observation',
            'lot_key', 'particularity'
        )
    except Exception as e:
        print(e)
        return None

