from typing import Union
from typing import Tuple
from gsalud.serializers import UsersSerializer
from gsalud.models import Role, User
from django.db import transaction
from passlib.hash import bcrypt
from datetime import datetime


def insert_update_bulk_users(users, list_fields, match_field):
    with transaction.atomic():
        User.objects.bulk_update_or_create(
            users, list_fields, match_field=match_field)
        return


def insert_new_user(data: dict, password: str = None) -> Tuple[bool, dict]:
    """
    Attempts to create a new user in the database.

    Args:
        data (dict): A dictionary containing user information.
        password (str, optional): An optional parameter for the user's password.

    Returns:
        tuple: A tuple containing a boolean indicating success and either the user data or error messages.
    """
    try:
        with transaction.atomic():
            if not password:
                return False, "Password is required."
            else:
                hashed_password = bcrypt.hash(password)
                data['user_pass'] = hashed_password

            serializer = UsersSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return True, serializer.data
            else:
                return False, serializer.errors
    except Exception as e:
        print(e)
        return False, str(e)


def get_audit_by_user_name(user_name, role) -> Tuple[bool, dict]:
    try:
        try:
            return User.objects.get(user_name=user_name)
        except User.DoesNotExist:
            user = User(
                user_name=user_name,
                first_name=user_name,
                last_name=user_name,
                user_pass=bcrypt.hash('Gsalud1234'),
                start_date=datetime.now().date(),
                id_role=role
            )
            user.save()
            return user
    except Exception as e:
        print(e)
        return False, str(e)


def get_user_by_username(user_name):
    try:
        return User.objects.get(user_name=user_name)
    except Exception as e:
        print(e)
        return False, str(e)


def get_user_by_pk(id_user):
    if id_user == None:
        return None
    else:
        return User.objects.get(pk=id_user)


def get_all_usernames() -> Union[dict, bool]:
    """
    Retrieves all users from the database and returns a dictionary mapping each user's username to their ID.

    Returns:
        dict: A dictionary mapping usernames to user IDs.
        boolean: Containing False and the error message if an exception occurs.
    """
    try:
        with transaction.atomic():
            users_obj = {user['user_name']: user['id']
                         for user in User.objects.all().values('id', 'user_name')}
            return users_obj
    except Exception as e:
        print(e)
        return False

def update_users_role(id_users,id_role):
    """
    Update the role of multiple users in a Django application.

    Args:
        request: Django Request object containing user IDs and new role ID.

    Returns:
        JSON response indicating success or failure of the update operation.
    """
    try:
        if not id_users or not id_role:
            return False, 'User IDs and id_role are required for updating'

        if not isinstance(id_users, list):
            return False, 'User IDs should be provided as a list.'
        # Check if the role exists
        role_instance = Role.objects.filter(pk=id_role).first()
        if not role_instance:
            return False, 'Role not found.'

        # Get all users currently with the specified role
        users_with_role = User.objects.filter(id_role=id_role)

        # Update users who currently have the role but are not in the new list of user IDs
        users_to_nullify = users_with_role.exclude(pk__in=id_users)
        for user in users_to_nullify:
            user.id_role = None
            user.save()

        # Update the role for the users in the provided list of user IDs
        users_to_update = User.objects.filter(pk__in=id_users)
        if not users_to_update.exists():
            return False, 'No users found with the provided IDs.'

        updated_users = []
        for user in users_to_update:
            user.id_role = role_instance
            user.save()
            updated_users.append(UsersSerializer(user).data)

        return True, 'success'

    except Exception as e:
        print(e)
        return False, str(e)
