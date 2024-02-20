from django.http import JsonResponse
from passlib.hash import bcrypt
from gsalud.models import Users
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


@api_view(['PUT'])
def updateUser(request):
    try:
        data = request.data
        user_id = data.get('user_id')

        if user_id is None:
            return Response({'success': False, 'error': 'User ID is required for updating.'}, status=status.HTTP_400_BAD_REQUEST)

        data = {key: value for key, value in data.items() if value is not None}
        excluded_keys = ['user_id']
        data = {key: value for key,value in data.items() if key not in excluded_keys}

        user_instance = Users.objects.get(pk=user_id)
        serializer = UsersSerializer(
            instance=user_instance, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['DELETE'])
def deleteUser(request):
    try:
        data = request.data
        print(data)
        user_id = data.get('id')

        if user_id is None:
            return Response({'success': False, 'error': 'User ID is required for Deletion.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user exists
        try:
            user_instance = Users.objects.get(pk=user_id)
        except Users.DoesNotExist:
            return Response({'success': False, 'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Delete the user
        user_instance.delete()

        return Response({'success': True}, status=status.HTTP_200_OK)

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})
