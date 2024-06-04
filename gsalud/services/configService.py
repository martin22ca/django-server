from gsalud.serializers import ConfigsSerializer
from gsalud.models import Configs
from datetime import datetime


def handle_config(id, newValue):
    """Updates an existing Config or creates a new one if it doesn't exist.

    Args:
        id (int): The ID of the Config to update or create.
        newValue: The new value to assign to the Config.

    Returns:
        tuple: A tuple containing two elements:
            - The updated or created Config object.
            - A boolean indicating success (True) or failure (False).
    """

    try:
        new_date = datetime.now()
        config_obj, created = Configs.objects.get_or_create(
            id=id, defaults={'value': newValue, 'mod_date': new_date})
        if not created:
            # Update existing Config
            config_obj.value = newValue
            serializer = ConfigsSerializer(
                instance=config_obj, data={'value': newValue, 'mod_date': new_date})
            if serializer.is_valid():
                serializer.save()
                return True
            else:
                print('Error:', serializer.error_messages)
                return False
        else:
            # Create new Config
            return True

    except Configs.DoesNotExist:
        print('Error: Config with ID', id, 'does not exist.')
        return False

    # Handle other potential exceptions (e.g., database errors) here
