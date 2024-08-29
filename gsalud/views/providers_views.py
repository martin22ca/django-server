import datetime
from django.http import JsonResponse
from gsalud.services.ORM_filters import execute_query_with_filters
from rest_framework.decorators import api_view
from gsalud.serializers import ProvidersSerializer
from rest_framework.response import Response
from rest_framework import status
from gsalud.models import Provider, Particularity
from gsalud.services.providers_service import register_particularity
from django.db.models import Subquery, F, OuterRef


@api_view(['GET'])
def get_providers(request):
    try:
        base_queryset = Provider.objects.select_related(
            'id_particularity'
        ).annotate(
            part_g_salud=F('id_particularity__part_g_salud'),
            part_prevencion=F('id_particularity__part_prevencion'),
            mod_prevencion=F('id_particularity__mod_prevencion'),
            mod_g_salud=F('id_particularity__mod_g_salud'),
            coordinator_business_name=Subquery(
                Provider.objects.filter(id_provider=OuterRef('id_coordinator'))
                .values('business_name')[:1]
            )
        ).values(
            'id_provider', 'id_coordinator', 'cuit', 'address', 'business_location', 'business_name',
            'priority', 'observation', 'id_particularity', 'part_g_salud', 'sancor_zone',
            'part_prevencion', 'mod_prevencion', 'mod_g_salud', 'coordinator_business_name'
        )

        data = execute_query_with_filters(request, base_queryset)
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['POST'])
def register_porvider(request):
    try:
        data = request.data
        serializer = ProvidersSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['PUT'])
def update_porvider(request):
    try:
        data = request.data
        print(data)
        id_provider = data.get('id_provider')
        provider_instance = Provider.objects.get(pk=id_provider)
        part = provider_instance.id_particularity
        if part == None:
            part = Particularity(
                part_g_salud=data['part_g_salud'], mod_g_salud=datetime.datetime.today().date())
            part.save()
            provider_instance.id_particularity = part
        else:
            provider_instance.id_particularity.part_g_salud = data['part_g_salud']
            provider_instance.id_particularity.mod_g_salud = datetime.datetime.today().date()
            provider_instance.id_particularity.save()
        serializer = ProvidersSerializer(
            instance=provider_instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)
        else:
            print(serializer.errors)
            return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})
