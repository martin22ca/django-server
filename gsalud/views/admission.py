from typing import Dict
from django.http import JsonResponse
from passlib.hash import bcrypt
from gsalud.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework.decorators import api_view
from gsalud.services.auth_service import is_auth


@api_view(['POST'])
def login(request):
    try:
        data = request.data
        userName = data['user_name']
        user_pass = data['user_pass']

        # Check if the user exists in the database
        user = User.objects.get(user_name=userName)
        user_id = user.id
        full_name = user.first_name + ' ' + user.last_name
        
        is_valid_password = bcrypt.verify(user_pass, user.user_pass)

        if is_valid_password:
            print('login successful')
            refresh = RefreshToken.for_user(user)
            token_string = str(refresh)
            return JsonResponse({'success': True, 'token': token_string, 'full_name': full_name, 'user_id': user_id, 'message': 'Login successful'})
        else:
            # Password doesn't match
            return JsonResponse({'success': False, 'error': 'Usuario y/o contraseña incorrectos'})

    except User.DoesNotExist:
        # Username doesn't exist
        return JsonResponse({'success': False, 'error': 'Usuario y/o contraseña incorrectos'})

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})


def is_authenticated(request) -> JsonResponse:
    """
    Check if a user is authenticated based on the token provided in the request.

    Args:
    - request: A Django HttpRequest object containing GET parameters 'token' and 'path'.

    Returns:
    - A JsonResponse indicating the authentication status and message.
    """
    try:
        token = request.GET.get('token')
        path = request.GET.get('path')

        valid, message = is_auth({'token': token, 'path': path})

        if valid:
            return JsonResponse({'success': True, 'message': message})
        else:
            return JsonResponse({'success': False, 'error': message})

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})
