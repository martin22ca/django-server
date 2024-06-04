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
            record_info_instance = Providers.objects.get(id_provider=update_id)
            serializer = ProvidersSerializer(
                instance=record_info_instance, data=update_data)
            if serializer.is_valid():
                serializer.save()
                print("Error in serializer validation:", serializer.errors)
        print('Provedores Actualizados')


def register_priority(queryPriority):
    with transaction.atomic():
        priorityInstace = Priorities.objects.filter(
            status__exact=queryPriority)
        if not priorityInstace.exists():
            serializer = PrioritiesSerializer(data={'status': queryPriority})
            if serializer.is_valid():
                serializer.save()
                print('Prioridad Nueva:', serializer.data['id'], queryPriority)
                return serializer.data['id']
            else: print(serializer.error_messages)
        else:
            existing_priority = priorityInstace.first()
            return existing_priority.id

def update_priority(priority_name, id_provider):
    with transaction.atomic():
        provider_instance = Providers.objects.get(pk=id_provider)
        priority_instace = Priorities.objects.filter(
            status__exact=priority_name)
        if not priority_instace.exists():
            serializer = PrioritiesSerializer(data={'status': priority_name})
            if serializer.is_valid():
                serializer.save()
                new_priority =Priorities.objects.get(pk=serializer.data['id'])
                provider_instance.id_priority = new_priority
                provider_instance.save()
            else:
                print(serializer.error_messages)
        else:
            provider_instance.id_priority = priority_instace.first() 
            provider_instance.save()


def registerParticularity(particularity):
    with transaction.atomic():
        date = datetime.today().date()
        serializer = ParticularitiesSerializer(
            data={'part_prevencion': particularity, 'mod_prevencion': date})
        if serializer.is_valid():
            serializer.save()
            print('Particularity Nueva:', serializer.data['id'], particularity)
            new_particularity = Particularity.objects.get(pk=serializer.data['id'])
            return new_particularity
        else: print(serializer.errors)
        


def updateParticularity(particularity, id_provider):
    try:
        with transaction.atomic():
            date = datetime.today().date()
            provider_instance = Providers.objects.get(id_provider=id_provider)
            
            if provider_instance.id_particularity is not None:
                # Provider already has a particularity, updating it
                particularity_instance = provider_instance.id_particularity
                particularity_instance.part_prevencion = particularity
                particularity_instance.mod_prevencion = date
                particularity_instance.save()
            else:
                # Provider doesn't have a particularity, create a new one
                new_particularity = registerParticularity(particularity)
                provider_instance.id_particularity = new_particularity
                provider_instance.save()
    
    except Providers.DoesNotExist:
        print("Provider does not exist with the given ID")
    except Particularity.DoesNotExist:
        print("Particularity does not exist")
