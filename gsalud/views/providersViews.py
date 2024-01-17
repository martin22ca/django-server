from django.http import JsonResponse
from gsalud.services.filterTable import get_table_data
from rest_framework.decorators import api_view
from gsalud.serializers import ProvidersSerializer
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET'])
def getProviders(request):
    try:
        base_query = '''select p.*,p2.status,p3.part_g_salud ,p3.part_prevencion ,p3.mod_prevencion,p3.mod_g_salud from providers p 
                    left join priorities p2 on p.id_priority = p2.id 
                    left join particularities p3 on p.id_particularity = p3.id '''
        return get_table_data(request, base_query)

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
