from gsalud.models import Lots
from django.db import IntegrityError


def getLotfromKey(lot_key):
    try:
        # Try to get an existing Lots instance with the provided lot_key
        lot_instance = Lots.objects.get(lot_key=lot_key)
        return lot_instance
    except Lots.DoesNotExist:
        try:
            # If the instance doesn't exist, create a new one
            new_lot_instance = Lots.objects.create(
                lot_key=lot_key, status=True)
            return new_lot_instance
        except IntegrityError as e:
            # Handle any potential integrity error (e.g., duplicate key)
            print(e)
            return None
    except Exception as e:
        # Handle other exceptions
        print(e)
        return None
