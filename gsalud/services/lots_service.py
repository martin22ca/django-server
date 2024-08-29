from django.db import IntegrityError, transaction
from gsalud.models import Lot, RecordInfo, Record
from gsalud.serializers import LotsSerializer
from gsalud.services.users_service import get_user_by_username
from gsalud.utils.manage_date import parse_date
from datetime import datetime


def get_lot_from_key(lot_key):
    try:
        key = str(lot_key)
        key = key.upper()
        # Try to get an existing Lots instance with the provided lot_key
        lot_instance = Lot.objects.get(lot_key=key)
        return lot_instance
    except Lot.DoesNotExist:
        try:
            # If the instance doesn't exist, create a new one
            new_lot_instance = Lot(lot_key=key,
                                   status=True)
            new_lot_instance.save()
            return new_lot_instance
        except IntegrityError as e:
            # Handle any potential integrity error (e.g., duplicate key)
            print(e)
        return None
    except Exception as e:
        # Handle other exceptions
        print(e)
        return None


def insert_new_lots(values):
    # Print the incoming values for debugging
    print(values)

    # Validate and serialize the input data
    serializer = LotsSerializer(data=values, many=True)

    # Check if the data is valid
    if serializer.is_valid():
        try:
            # Perform bulk create within a transaction
            with transaction.atomic():
                Lot.objects.bulk_create([
                    Lot(lot_key=item['lot_key'], status=True)
                    for item in values
                ], ignore_conflicts=True)  # ignore_conflicts=True to avoid integrity errors on duplicate keys
            return {'status': 'success', 'message': 'Lots inserted successfully'}
        except IntegrityError as e:
            print(e)
            return {'status': 'error', 'message': str(e)}
        except Exception as e:
            print(e)
            return {'status': 'error', 'message': str(e)}
    else:
        return {'status': 'error', 'message': 'Invalid data', 'errors': serializer.errors}


def manage_records_from_lot(original_key, edited_records):
    for record_key, record_data in edited_records.items():
        try:
            record = Record.objects.get(record_key=record_key)
            record_info = RecordInfo.objects.select_related(
                'id_record', 'id_auditor', 'id_lot').get(id_record=record)

            # Update lot
            if 'lot_key' in record_data:
                lot_key = record_data['lot_key']
                if lot_key is None:
                    record_info.id_lot = None
                elif original_key != lot_key:
                    lot = Lot.objects.get(lot_key=lot_key)
                    record_info.id_lot = lot

            # Handle date_assignment_audit
            if 'date_assignment_audit_formatted' in record_data:
                date_str = record_data['date_assignment_audit_formatted']
                if date_str is None:
                    record_info.date_assignment_audit = None
                else:
                    record_info.date_assignment_audit = parse_date(date_str)

            # Update auditor
            if 'user_name' in record_data:
                user_name = record_data['user_name']
                if user_name is None:
                    record_info.id_auditor = None
                    record_info.date_assignment_audit = None
                else:
                    auditor = get_user_by_username(user_name)
                    record_info.id_auditor = auditor
                    if record_info.date_assignment_audit is None:
                        record_info.date_assignment_audit = datetime.now().date()

            # Set assigned based on whether an auditor is assigned
            record_info.assigned = record_info.id_auditor is not None

            # Save the changes
            record_info.save()

        except RecordInfo.DoesNotExist:
            print(f"RecordInfo for record_key {record_key} does not exist.")
        except Lot.DoesNotExist:
            print(f"Lot with key {lot_key} does not exist.")
        except Exception as e:
            print(
                f"An error occurred while updating record {record_key}: {str(e)}")
