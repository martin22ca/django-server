from django.http import JsonResponse
from gsalud.services.ORM_filters import execute_query_with_filters
from rest_framework.decorators import api_view
from gsalud.serializers import ProvidersSerializer
from rest_framework.response import Response
from rest_framework import status
from gsalud.models import  Provider
from django.db.models import Prefetch, F

@api_view(['GET'])
def get_providers(request):
    try:
        base_queryset = Provider.objects.select_related(
            'id_particularity'
        ).annotate(
            part_g_salud=F('id_particularity__part_g_salud'),
            part_prevencion=F('id_particularity__part_prevencion'),
            mod_prevencion=F('id_particularity__mod_prevencion'),
            mod_g_salud=F('id_particularity__mod_g_salud')
        ).values(
            'id_provider','id_coordinator','cuit','address','business_location', 'business_name',
            'priority','observation','id_particularity', 'part_g_salud',
            'part_prevencion', 'mod_prevencion', 'mod_g_salud'
        )
        data = execute_query_with_filters(request, base_queryset)
        return JsonResponse({'success': True, 'data': data})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['POST'])
def registerProvider(request):
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
