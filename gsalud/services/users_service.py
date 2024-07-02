from typing import Union
from typing import Tuple
from gsalud.serializers import UsersSerializer
from gsalud.models import User
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
