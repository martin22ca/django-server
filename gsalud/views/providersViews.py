from django.http import JsonResponse
from gsalud.services.filterTable import get_table_data


def getProviders(request):
    try:
        base_query = 'SELECT * FROM PROVIDERS'
        return get_table_data(request,base_query)
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
