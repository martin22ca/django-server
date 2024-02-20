
from django.db import transaction
from django.http import JsonResponse
from collections import namedtuple
from rest_framework.decorators import api_view
from django.db import connection


@api_view(['GET'])
def getUsersWithRoles(request):
    try:
        with connection.cursor() as cursor:
            query = '''
                    select u.id AS "id_user", u.user_name, u.first_name, u.last_name, r.id AS "id_role" from  users u 
                    left join users_roles ur ON u.id  = ur.id_user 
                    left join roles r on ur.id_role = r.id 
                    '''
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            Row = namedtuple('Row', columns)
            if cursor.rowcount > 0:
                rows = [Row(*row) for row in cursor.fetchall()]
                return JsonResponse({'success': True, 'data': [dict(row._asdict()) for row in rows]}, safe=False)
            else:
                return JsonResponse(data=[], safe=False)

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})
