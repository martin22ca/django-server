from typing import List, Dict
from django.core.exceptions import ObjectDoesNotExist
from gsalud.serializers import RecordInfoSerializer
from django.db import transaction
from gsalud.models import RecordInfo, RecordsInfoUsers, Record
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.exceptions import ValidationError
from django.db.models import F,Q
from gsalud.utils.manage_date import ToChar



def insert_update_bulk_records_info(records_info, list_fields, match_field):
    with transaction.atomic():
        RecordInfo.objects.bulk_update_or_create(
            records_info, list_fields, match_field=match_field)
        return


def insert_bulk_cases(cases):
    with transaction.atomic():
        RecordInfo.objects.bulk_create(cases)


def exist_record_info(id_record):
    return RecordInfo.objects.filter(id_record=id_record).exists()


def update_single_case(new_case_instance, force=False):
    try:
        with transaction.atomic():
            id_record = new_case_instance.id_record
            old_case_instance = RecordInfo.objects.select_for_update().get(id_record=id_record)

            # Get all field names for the model
            fields = [
                field.name for field in RecordInfo._meta.fields if field.name != 'id']

            # Update each field individually
            for field in fields:
                setattr(old_case_instance, field,
                        getattr(new_case_instance, field))

            # Validate the model before saving
            old_case_instance.full_clean()
            old_case_instance.save()

            return True, f"Updated record {old_case_instance.pk}"
    except RecordInfo.DoesNotExist:
        return False, f"Record with id {id_record} does not exist."
    except ValidationError as e:
        return False, f"Validation error updating record {id_record}: {e}"
    except Exception as e:
        return False, f"Error updating record {id_record}: {e}"


def update_bulk_cases(case_instances, max_workers=5):
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_record = {executor.submit(
            update_single_case, case): case for case in case_instances}
        for future in as_completed(future_to_record):
            record = future_to_record[future]
            try:
                success, message = future.result()
                results.append((success, message))
            except Exception as exc:
                results.append(
                    (False, f"Record {record.pk} generated an exception: {exc}"))
    for i, j in results:
        if i == False:
            print(j)


def insertRecordsCases(newRecordInfoData: List[dict]):
    """
    Insert new record information data into the database.

    Args:
        newRecordInfoData (list): A list of dictionaries containing new record information data.

    Returns:
        Boolean

    """
    with transaction.atomic():
        serializer = RecordInfoSerializer(data=newRecordInfoData, many=True)
        if serializer.is_valid():
            serializer.save()
            print('Caso/s Registrados')
            return True
        else:
            print("Error in serializer validation:", serializer.errors)
            return False


def updateRecordsCases(updateRecordsInfoIds: List[int], updateRecordsInfoData: List[Dict[str, str]]) -> None:
    """
    Updates the RecordInfo instances in the database based on the provided updateRecordsInfoIds and updateRecordsInfoData.
    If a RecordInfo instance with the given update_id is found, it is updated with the provided data using the RecordInfoSerializer.
    If the instance is not found, a new RecordInfo instance is inserted.

    Args:
    - updateRecordsInfoIds: A list of integers representing the IDs of the RecordInfo instances to be updated.
    - updateRecordsInfoData: A list of dictionaries containing the updated data for each RecordInfo instance.

    Returns:
    - None
    """
    with transaction.atomic():
        for update_id, update_data in zip(updateRecordsInfoIds, updateRecordsInfoData):
            try:
                record_info_instance = RecordInfo.objects.get(
                    id_record__exact=update_id)
            except ObjectDoesNotExist:
                record_info_instance = RecordInfo()
            serializer = RecordInfoSerializer(
                instance=record_info_instance, data=update_data)
            if serializer.is_valid():
                serializer.save()
            else:
                print("Error in serializer validation:", serializer.errors)


def remove_record_from_user(id_uxri: int) -> bool:
    """
    Removes a record from a user in the database.

    Args:
        id_uxri (int): The primary key of the RecordsInfoUsers instance to be removed.

    Returns:
        bool: True if the record was successfully removed, False if the record does not exist.
    """
    try:
        uxri_instance = RecordsInfoUsers.objects.get(pk=id_uxri)
    except RecordsInfoUsers.DoesNotExist:
        return False

    # Delete the UXRI
    uxri_instance.delete()
    return True


def create_record_info(id_record: int) -> bool:
    """
    Creates a new record information data dictionary with the given id_record and assigned set to False.
    Inserts the new record information data into the database using the insertRecordsCases function.

    Args:
        id_record (int): The ID of the record for which the record information data needs to be created.

    Returns:
        bool: True if the record information data is successfully inserted into the database, False otherwise.
    """
    try:
        Record.objects.get(pk=id_record)
    except Record.DoesNotExist:
        return None

    newRecordInfoData = {'id_record': id_record, 'assigned': False}
    with transaction.atomic():
        serializer = RecordInfoSerializer(data=newRecordInfoData)
        if serializer.is_valid():
            serializer.save()
            print('Caso Registrado')
            return True
        else:
            print("Error in serializer validation:", serializer.errors)
            return False


def get_records_from_lot(id_lot):
    try:
        base_queryset = RecordInfo.objects.annotate(
            record_key=F('id_record__record_key'),
            id_provider=F('id_record__id_provider__id_provider'),
            business_name=F('id_record__id_provider__business_name'),
            id_coordinator=F('id_record__id_provider__id_coordinator'),
            record_total=F('id_record__record_total'),
            lot_key=F('id_lot__lot_key'),
            receipt_short=F('id_record__id_receipt_type__receipt_short'),
            record_name=F('id_record__id_record_type__record_name'),
            date_entry_digital_formatted=ToChar('date_entry_digital'),
            date_entry_physical_formatted=ToChar('date_entry_physical'),
            date_assignment_audit_formatted=ToChar('date_assignment_audit'),
            user_name=F('id_auditor__user_name')
        )

        if id_lot is None:
            # Query for unassigned records
            base_queryset = base_queryset.filter(
                id_lot__isnull=True
            ).filter(
                Q(date_entry_digital__isnull=False) |
                Q(date_entry_physical__isnull=False) |
                Q(seal_number__isnull=False)
            )
        else:
            # Query for records in the specified lot
            base_queryset = base_queryset.filter(id_lot=id_lot)

        return base_queryset.values(
            'id_record', 'record_key', 'assigned', 'id_provider', 'business_name', 'id_lot', 'user_name',
            'id_auditor', 'id_coordinator', 'record_total', 'date_entry_digital_formatted','date_assignment_audit_formatted',
            'date_entry_physical_formatted', 'seal_number', 'observation', 'lot_key',
            'receipt_short', 'record_name'
        )
    except Exception as e:
        print(e)
        return None
