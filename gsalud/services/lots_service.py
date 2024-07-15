from gsalud.models import Lot
from django.db import IntegrityError,transaction
from gsalud.serializers import LotsSerializer
from datetime import datetime

def get_lot_from_key(lot_key):
    try:
        key = str(lot_key)
        key =key.upper()
        # Try to get an existing Lots instance with the provided lot_key
        lot_instance = Lot.objects.get(lot_key=key)
        return lot_instance
    except Lot.DoesNotExist:
        try:
            # If the instance doesn't exist, create a new one
            new_lot_instance = Lot(lot_key = key,
                            status = True,
                            date_asignment = datetime.now().date()) 
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