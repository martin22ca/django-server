from gsalud.serializers import ProvidersSerializer, PrioritiesSerializer, ParticularitiesSerializer
from gsalud.models import Providers, Particularity, Priorities
from django.db import transaction
from datetime import datetime


def insertProviders(newProviders):
    with transaction.atomic():
        serializer = ProvidersSerializer(data=newProviders, many=True)
        if serializer.is_valid():
            print('Provedores Registrados')
            serializer.save()
        else:
            print("Error in serializer validation:", serializer.errors)


def updateProviders(updateProvidersIds, updateRecordsInfoData):
    with transaction.atomic():
        for update_id, update_data in zip(updateProvidersIds, updateRecordsInfoData):
            record_info_instance = Providers.objects.get(id=update_id)
            serializer = ProvidersSerializer(
                instance=record_info_instance, data=update_data)
            if serializer.is_valid():
                serializer.save()
                print("Error in serializer validation:", serializer.errors)
        print('Provedores Actualizados')


def handlePriority(queryPriority):
    with transaction.atomic():
        priorityInstace = Priorities.objects.filter(
            status__exact=queryPriority)
        if not priorityInstace.exists():
            serializer = PrioritiesSerializer(data={'status': queryPriority})
            if serializer.is_valid():
                serializer.save()
                print('Prioridad Nueva:', serializer.data['id'], queryPriority)
                return serializer.data['id']
        else:
            existing_priority = priorityInstace.first()
            return existing_priority.id


def registerParticularity(particularity):
    with transaction.atomic():
        date = datetime.today().strftime('%Y-%m-%d')
        serializer = ParticularitiesSerializer(
            data={'part_prevencion': particularity, 'mod_prevencion': date})
        if serializer.is_valid():
            serializer.save()
            print('Particularity Nueva:', serializer.data['id'], particularity)
            return serializer.data['id']


def updateParticularity(particularity, id_provider):
    try:
        with transaction.atomic():
            date = datetime.today().strftime('%Y-%m-%d')
            provider_instance = Providers.objects.get(id=id_provider)
            
            if provider_instance.id_particularity is not None:
                # Provider already has a particularity, updating it
                particularity_instance = Particularity.objects.get(id=provider_instance.id_particularity)
                particularity_instance.part_prevencion = particularity
                particularity_instance.mod_prevencion = date
                particularity_instance.save()
            else:
                # Provider doesn't have a particularity, create a new one
                new_particularity_id = registerParticularity(particularity)
                provider_instance.id_particularity = new_particularity_id
                provider_instance.save()
    
    except Providers.DoesNotExist:
        print("Provider does not exist with the given ID")
    except Particularity.DoesNotExist:
        print("Particularity does not exist")
