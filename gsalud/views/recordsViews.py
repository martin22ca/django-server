from django.http import JsonResponse
from gsalud.services.filterTable import get_table_data

def getRecords(request):
    try:
        base_query = 'SELECT * FROM records'
        return get_table_data(request,base_query)
        
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})



def getRecordsInfos(request):
    try:
        base_query = 'SELECT * FROM records_info'
        return get_table_data(request,base_query)
        
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})