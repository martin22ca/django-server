from rest_framework import serializers
from gsalud.models import User, Config, Provider, ReceiptType, RecordType, Lot, Role, Feedback 
from gsalud.models import Record, RecordInfo, RecordsInfoUsers, Particularity


class DynamicFieldsSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class ConfigsSerializer(DynamicFieldsSerializer):
    class Meta:
        model = Config
        fields = '__all__'


class UsersSerializer(DynamicFieldsSerializer):
    class Meta:
        model = User
        fields = '__all__'


class ProvidersSerializer(DynamicFieldsSerializer):
    class Meta:
        model = Provider
        fields = '__all__'


class ReceitTypesSerializer(DynamicFieldsSerializer):
    class Meta:
        model = ReceiptType
        fields = '__all__'


class RecordTypesSerializer(DynamicFieldsSerializer):
    class Meta:
        model = RecordType
        fields = '__all__'


class ParticularitiesSerializer(DynamicFieldsSerializer):
    class Meta:
        model = Particularity
        fields = '__all__'


class RecordSerializer(DynamicFieldsSerializer):

    class Meta:
        model = Record
        fields = '__all__'


class RecordInfoSerializer(DynamicFieldsSerializer):

    class Meta:
        model = RecordInfo
        fields = '__all__'


class RecordsUsersSerializer(DynamicFieldsSerializer):

    class Meta:
        model = RecordsInfoUsers
        fields = '__all__'


class LotsSerializer(DynamicFieldsSerializer):

    class Meta:
        model = Lot
        fields = '__all__'


class RolesSerializer(DynamicFieldsSerializer):

    class Meta:
        model = Role
        fields = '__all__'

class FeedbackSerializer(DynamicFieldsSerializer):

    class Meta:
        model = Feedback
        fields = '__all__'