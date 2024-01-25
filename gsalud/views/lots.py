from django.http import JsonResponse
from gsalud.services.filterTable import get_table_data
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET'])
def getLots(request):
    try:
        base_query = '''select l.*,MAX(u.user_name) AS user_name,COUNT(DISTINCT ri.id) as total_records from lots l
                        left join users u ON l.id_user = u.id  
                        left join records_info ri ON l.id  = ri.id_lot 
                        '''
        return get_table_data(request, base_query, group_by='l.id')

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
