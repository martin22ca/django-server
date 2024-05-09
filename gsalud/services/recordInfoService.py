from typing import List, Dict
from django.core.exceptions import ObjectDoesNotExist
from gsalud.serializers import RecordInfoSerializer
from django.db import transaction
from gsalud.models import RecordInfo, RecordsInfoUsers, Records


def insertRecordsCases(newRecordInfoData):
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


def removeRecordFromUser(id_uxri: int) -> bool:
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


def createRecordInfo(id_record: int) -> bool:
    """
    Creates a new record information data dictionary with the given id_record and assigned set to False.
    Inserts the new record information data into the database using the insertRecordsCases function.

    Args:
        id_record (int): The ID of the record for which the record information data needs to be created.

    Returns:
        bool: True if the record information data is successfully inserted into the database, False otherwise.
    """
    try:
        Records.objects.get(pk=id_record)
    except Records.DoesNotExist:
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
