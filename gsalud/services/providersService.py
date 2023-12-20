from gsalud.serializers import ProvidersSerializer, PrioritiesSerializer
from gsalud.models import Providers, Peculiarities, Priorities
from django.db import transaction


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
        priorityInstace = Priorities.objects.filter(status__exact=queryPriority)
        if not priorityInstace.exists():
            serializer = PrioritiesSerializer(data={'status': queryPriority})
            if serializer.is_valid():
                serializer.save()
                print('Prioridad Nueva:', serializer.data['id'], queryPriority)
                return serializer.data['id']
        else:
            existing_priority = priorityInstace.first()
            return existing_priority.id
