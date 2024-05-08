
from django.db import transaction
from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.db import connection
from gsalud.models import Roles
from gsalud.serializers import RolesSerializer


@api_view(['GET'])
def getRoles(request):
    try:
        if request.method == 'GET':
            # Exclude role with ID 0
            roles = Roles.objects.exclude(id=0)
            # Serialize queryset to JSON
            serializer = RolesSerializer(roles, many=True)
            return JsonResponse({'success': True, 'data': serializer.data}, safe=False)
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})
