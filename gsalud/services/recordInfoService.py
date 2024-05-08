from typing import List, Dict
from django.core.exceptions import ObjectDoesNotExist
from gsalud.serializers import RecordInfoSerializer
from django.db import transaction
from gsalud.models import RecordInfo, RecordsInfoUsers


def insertRecordsCases(newRecordInfoData):
    with transaction.atomic():
        serializer = RecordInfoSerializer(data=newRecordInfoData, many=True)
        if serializer.is_valid():
            serializer.save()
            print('Casos Registrados')
        else:
            print("Error in serializer validation:", serializer.errors)


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
                record_info_instance = RecordInfo.objects.get(id_record__exact=update_id)
            except ObjectDoesNotExist:
                record_info_instance = RecordInfo()
            serializer = RecordInfoSerializer(instance=record_info_instance, data=update_data)
            if serializer.is_valid():
                serializer.save()
            else:
                print("Error in serializer validation:", serializer.errors)


def removeRecordFromUser(id_uxri):
    with transaction.atomic():
        try:
            uxri_instance = RecordsInfoUsers.objects.get(pk=id_uxri)
        except RecordsInfoUsers.DoesNotExist:
            return False

        # Delete the UXRI
        uxri_instance.delete()
        return True
