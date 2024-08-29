from gsalud.serializers import ProvidersSerializer, ParticularitiesSerializer
from gsalud.models import Provider, Particularity
from django.db import transaction
from datetime import datetime


def insert_update_bulk_providers(providers, list_fields, match_field):
    with transaction.atomic():
        Provider.objects.bulk_update_or_create(
            providers, list_fields, match_field=match_field)
        return


def insert_update_bulk_particularities(particularities, list_fields, match_field):
    with transaction.atomic():
        Particularity.objects.bulk_update_or_create(
            particularities, list_fields, match_field=match_field)
        return


def update_providers(update_providers_data):
    with transaction.atomic():
        for update_data in update_providers_data:
            record_info_instance = Provider.objects.get(
                id_provider=update_data['id_provider'])
            print(record_info_instance)
            serializer = ProvidersSerializer(
                instance=record_info_instance, data=update_data)
            if serializer.is_valid():
                serializer.save()
            else:
                print("Error in serializer validation:", serializer.errors)

        print('Provedores Actualizados')


def register_particularity(particularity):
    with transaction.atomic():
        date = datetime.today().date()
        serializer = ParticularitiesSerializer(
            data={'part_prevencion': particularity, 'mod_prevencion': date})
        if serializer.is_valid():
            serializer.save()
            print('Particularity Nueva:', serializer.data['id'], particularity)
            new_particularity = Particularity.objects.get(
                pk=serializer.data['id'])
            return new_particularity
        else:
            print(serializer.errors)


def update_particularity(particularity, id_provider):
    try:
        with transaction.atomic():
            date = datetime.today().date()
            provider_instance = Provider.objects.get(id_provider=id_provider)

            if provider_instance.id_particularity is not None:
                # Provider already has a particularity, updating it
                particularity_instance = provider_instance.id_particularity
                particularity_instance.part_prevencion = particularity
                particularity_instance.mod_prevencion = date
                particularity_instance.save()
            else:
                # Provider doesn't have a particularity, create a new one
                new_particularity = register_particularity(particularity)
                provider_instance.id_particularity = new_particularity
                provider_instance.save()

    except Provider.DoesNotExist:
        print("Provider does not exist with the given ID")
    except Particularity.DoesNotExist:
        print("Particularity does not exist")


def insert_update_particularity_by_provider(id_provider, new_particularity):
    try:
        try:
            date = datetime.today().date()
            id_particularity = Provider.objects.get(
                pk=id_provider).pk
            try:
                particularity = Particularity.objects.get(pk=id_particularity)
                if particularity.part_prevencion != new_particularity:
                    particularity.part_prevencion = new_particularity
                    particularity.mod_prevencion=date

                particularity.save()
                return particularity
            except Particularity.DoesNotExist:
                particularity = Particularity(
                    mod_prevencion=date,
                    part_prevencion=new_particularity
                )
                particularity.save()
            return particularity
        except Provider.DoesNotExist:
            return
    except Exception as e:
        print(e)
        return False, str(e)
