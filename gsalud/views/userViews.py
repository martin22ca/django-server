from django.http import JsonResponse
from passlib.hash import bcrypt
from gsalud.models import Users, Roles
from gsalud.serializers import UsersSerializer
from gsalud.services.filterTable import get_table_data
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from gsalud.services.authService import is_auth


def getUsers(request):
    try:
        base_query = 'SELECT * FROM users'
        return get_table_data(request, base_query)

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['GET'])
def getUsersByRole(request):
    try:
        id_role = request.GET.get('id_role')
        users = Users.objects.filter(id_role=id_role)
        serializer = UsersSerializer(users, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)
    except Users.DoesNotExist:
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
def updateUser(request):
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
            user_instance = Users.objects.get(pk=user_id)
        except Users.DoesNotExist:
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


@api_view(['PUT'])
def updateUserRoles(request):
    """
    Update the role of multiple users in a Django application.

    Args:
        request: Django Request object containing user IDs and new role ID.

    Returns:
        JSON response indicating success or failure of the update operation.
    """
    try:
        data = request.data
        users_ids = data.get('users_ids')
        id_role = data.get('id_role')

        if not users_ids or not id_role:
            return Response({'success': False, 'error': 'User IDs and id_role are required for updating.'}, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(users_ids, list):
            return Response({'success': False, 'error': 'User IDs should be provided as a list.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the role exists
        role_instance = Roles.objects.filter(pk=id_role).first()
        if not role_instance:
            return Response({'success': False, 'error': 'Role not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Get all users currently with the specified role
        users_with_role = Users.objects.filter(id_role=id_role)

        # Update users who currently have the role but are not in the new list of user IDs
        users_to_nullify = users_with_role.exclude(pk__in=users_ids)
        for user in users_to_nullify:
            user.id_role = None
            user.save()

        # Update the role for the users in the provided list of user IDs
        users_to_update = Users.objects.filter(pk__in=users_ids)
        if not users_to_update.exists():
            return Response({'success': False, 'error': 'No users found with the provided IDs.'}, status=status.HTTP_404_NOT_FOUND)

        updated_users = []
        for user in users_to_update:
            user.id_role = role_instance
            user.save()
            updated_users.append(UsersSerializer(user).data)

        return Response({'success': True, 'data': updated_users}, status=status.HTTP_200_OK)

    except Exception as e:
        print(e)
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
