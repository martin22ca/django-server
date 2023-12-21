from gsalud.serializers import ConfigsSerializer
from gsalud.models import Configs


def updateConfig(id, newValue):
    config_obj = Configs.objects.get(id=id)
    config_obj.value = newValue
    serializer = ConfigsSerializer(
        instance=config_obj, data={'value': newValue})

    if serializer.is_valid():
        serializer.save()  # Save the changes to the database
        return True  # Return True upon successful update
    else:
        print('error:',serializer.error_messages)
        return False  # Return False if serializer is not valid
