from django.http import JsonResponse
from passlib.hash import bcrypt
from gsalud.serializers import UsersSerializer
from gsalud.services.filterTable import get_table_data
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view


def getUsers(request):
    try:
        base_query = 'SELECT * FROM users'
        return get_table_data(request, base_query)

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['POST'])
def registerUser(request):
    try:
        data = request.data
        print(data)
        hashed_password = bcrypt.hash(data['user_pass'])
        data['user_pass'] = hashed_password
        serializer = UsersSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})
