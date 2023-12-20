import json
from django.http import JsonResponse
from rest_framework.decorators import api_view
from gsalud.models import Configs
from gsalud.serializers import ConfigsSerializer
from gsalud.services.configService import updateConfig
from gsalud.services.filterTable import filters


@api_view(['GET'])
def config_list(request):
    objs = Configs.objects.filter(id__in=[1, 2])
    serializer = ConfigsSerializer(objs, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
def config_cols(request):
    try:
        data = request.GET.dict()
        id_config = data['id']
        obj = Configs.objects.get(pk=id_config)
        serializer = ConfigsSerializer(obj, many=False)
        return JsonResponse(serializer.data)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['POST'])
def set_config_cols(request):
    try:
        config = json.dumps(request.data['data'])
        id = request.data['id']
        res = updateConfig(id, config)
        return JsonResponse({'success': res})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['GET'])
def getFilterOptions(req):
    return JsonResponse(data=filters, safe=False)
