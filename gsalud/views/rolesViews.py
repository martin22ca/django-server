from typing import Any

from django.db import transaction
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.exceptions import NotFound
from django.db import connection
from gsalud.models import Roles
from gsalud.serializers import RolesSerializer


@api_view(['GET'])
def getRoles(request: Any) -> JsonResponse:
    """
    Retrieves all roles from the database, excluding the role with ID 0, and returns them in JSON format.

    Args:
        request: The HTTP request object that triggers the function. Should be a Django `HttpRequest` object.

    Returns:
        JSON response with roles data or error message.
    """
    try:
        if request.method == 'GET':
            roles = Roles.objects.exclude(id=0)
            serializer = RolesSerializer(roles, many=True)
            return JsonResponse({'success': True, 'data': serializer.data}, safe=False)
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['PUT'])
def updateRole(request):
    try:
        data = request.data
        id_role = data.get('id_role')
        print(data)
        
        if not id_role:
            return JsonResponse({'success': False, 'error': 'id_role is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Try to retrieve the role instance
        try:
            role_instance = Roles.objects.get(id=id_role)
        except Roles.DoesNotExist:
            raise NotFound('Role not found')

        # Prepare the data for the update
        excluded_keys = ['id_role']
        data = {key: value for key, value in data.items() if key not in excluded_keys}
        print(data)


        # Update the role instance using the serializer
        serializer = RolesSerializer(role_instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({'success': True, 'message': 'ok'}, safe=False)
        else:
            return JsonResponse({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
