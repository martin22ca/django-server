
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.shortcuts import get_object_or_404
from gsalud.models import User
import json


def is_auth(requestDict):
    try:
        token = requestDict['token']
        actual_path = requestDict['path'].lstrip(
            '/')  # Remove leading '/' from actual_path
        if token:
            # Validate the token
            try:
                validated_token = RefreshToken(token)
            except InvalidToken:
                # Token is invalid
                return False, "Token no valido"
            except TokenError as e:
                # Token is expired or invalid
                return False, "Token esta expirado"

            user_id = validated_token.payload['user_id']

            # Check if the user exists
            user_instance = get_object_or_404(User, pk=user_id)

            # Check if the user role is valid
            role_instance = user_instance.id_role

            if role_instance == None:
                return False, 'El usuario no tiene rol'

            # Parse the permissions for the role
            permissions = role_instance.configs
            permissions_list = json.loads(permissions)

            if role_instance.pk == 0:
                return True, 'Authorized'

            # Check if the actual_path matches any of the permissions
            if actual_path == '':
                return True, 'Authorized'
            for permission in permissions_list:
                # Strip spaces and leading '/'
                permission_route = permission['route'].strip().lstrip('/') 
                if actual_path.startswith(permission_route):
                    return True, "Authorized"

            return False, "User does not have permission for this resource"
        else:
            return False, "Token not provided"
    except Exception as e:
        return False, str(e)
