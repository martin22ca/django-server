from django.http import JsonResponse
from passlib.hash import bcrypt
from gsalud.models import User, Role
from gsalud.serializers import UsersSerializer
from gsalud.services.ORM_filters import execute_query_with_filters
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view


def getUsers(request):
    try:
        base_query = User.objects.filter().values()
        data = execute_query_with_filters(request, base_query)
        return JsonResponse({'success': True, 'data': data})
    

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['GET'])
def get_user_by_role(request):
    try:
        id_role = request.GET.get('id_role')
        users = User.objects.filter(id_role=id_role)
        serializer = UsersSerializer(users, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


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
def update_user(request):
    """
    Update an existing user's details in a Django application.

    Args:
        request: Django Request object containing user update data.

    Returns:
        JSON response indicating success or failure of the update operation.
    """
    try:
        data = request.data
        user_id = data.get('user_id')

        if not user_id:
            return Response({'success': False, 'error': 'User ID is required for updating.'}, status=status.HTTP_400_BAD_REQUEST)

        excluded_keys = ['user_id']
        data = {key: value for key, value in data.items(
        ) if value is not None and key not in excluded_keys}

        try:
            user_instance = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'success': False, 'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        if 'user_pass' in data:
            data['user_pass'] = bcrypt.hash(data['user_pass'])

        serializer = UsersSerializer(
            instance=user_instance, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        print(e)
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
def deleteUser(request):
    try:
        data = request.data
        user_id = data.get('id')

        if user_id is None:
            return Response({'success': False, 'error': 'User ID is required for Deletion.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user exists
        try:
            user_instance = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'success': False, 'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Delete the user
        user_instance.delete()

        return Response({'success': True}, status=status.HTTP_200_OK)

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})
