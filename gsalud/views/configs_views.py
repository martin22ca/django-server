import json
from django.http import JsonResponse
from rest_framework.decorators import api_view
from gsalud.models import Config
from gsalud.serializers import ConfigsSerializer
from gsalud.services.config_service import handle_config
from gsalud.services.filterTable import filters


@api_view(['GET'])
def config_list(request):
    data_string = request.GET.dict()['idList']
    config_list = json.loads(data_string)
    objs = Config.objects.filter(id__in=config_list)
    serializer = ConfigsSerializer(objs, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
def config_cols(request):
    try:
        data = request.GET.dict()
        id_config = data['id']
        obj = Config.objects.get(pk=id_config)
        serializer = ConfigsSerializer(obj, many=False)
        return JsonResponse(serializer.data)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['POST'])
def set_config_cols(request):
    try:
        config = json.dumps(request.data['data'])
        id = request.data['id']
        res = handle_config(id, config)
        return JsonResponse({'success': res})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['GET'])
def getFilterOptions(req):
    return JsonResponse(data=filters, safe=False)
