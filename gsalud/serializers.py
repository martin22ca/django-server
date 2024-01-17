from rest_framework import serializers
from .models import Users, Configs, Providers, ReceiptTypes,RecordTypes, Records, RecordInfo,Priorities,RecordsInfoUsers,Particularity


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
        model = Configs
        fields = '__all__'


class UsersSerializer(DynamicFieldsSerializer):
    class Meta:
        model = Users
        fields = '__all__'


class ProvidersSerializer(DynamicFieldsSerializer):
    class Meta:
        model = Providers
        fields = '__all__'


class ReceitTypesSerializer(DynamicFieldsSerializer):
    class Meta:
        model = ReceiptTypes
        fields = '__all__'

class RecordTypesSerializer(DynamicFieldsSerializer):
    class Meta:
        model = RecordTypes
        fields = '__all__'

class PrioritiesSerializer(DynamicFieldsSerializer):
    class Meta:
        model = Priorities
        fields = '__all__'

class ParticularitiesSerializer(DynamicFieldsSerializer):
    class Meta:
        model = Particularity
        fields = '__all__'


class RecordSerializer(DynamicFieldsSerializer):

    class Meta:
        model = Records
        fields = '__all__'


class RecordInfoSerializer(DynamicFieldsSerializer):

    class Meta:
        model = RecordInfo
        fields = '__all__'

class RecordsUsersSerializer(DynamicFieldsSerializer):

    class Meta:
        model = RecordsInfoUsers
        fields = '__all__'