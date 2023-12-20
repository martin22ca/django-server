import token
from django.http import JsonResponse
from passlib.hash import bcrypt
from gsalud.models import Users
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework.decorators import api_view


@api_view(['POST'])
def login(request):
    try:
        data = request.data
        userName = data['user_name']
        user_pass = data['user_pass']

        # Check if the user exists in the database
        user = Users.objects.get(user_name=userName)
        user_id = user.id
        full_name = user.first_name + ' ' + user.last_name

        # Verify the hashed password
        hashed_password = user.user_pass
        is_valid_password = bcrypt.verify(user_pass, hashed_password)

        if is_valid_password:
            print('login successful')
            refresh = RefreshToken.for_user(user)
            token_string = str(refresh)
            return JsonResponse({'success': True, 'token': token_string, 'full_name': full_name, 'user_id': user_id, 'message': 'Login successful'})
        else:
            # Password doesn't match
            return JsonResponse({'success': False, 'error': 'Usuario y/o contraseña incorrectos'})

    except Users.DoesNotExist:
        # Username doesn't exist
        return JsonResponse({'success': False, 'error': 'Usuario y/o contraseña incorrectos'})

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['GET'])
def is_auth(request):
    try:
        # Get the token from the query parameters
        tokenObj = request.GET.dict()
        token = tokenObj['token']

        # Check if the token is provided
        if token:
            try:
                # Attempt to validate the token
                validated_token = RefreshToken(token)
                # The token is valid
                return JsonResponse({'success': True, 'message': 'Token is valid'})
            except InvalidToken:
                # Token is invalid
                return JsonResponse({'success': False, 'error': 'Token No valido'})
            except TokenError as e:
                # Token is expired or invalid
                return JsonResponse({'success': False, 'error': str(e)})
        else:
            # Token is not provided
            return JsonResponse({'success': False, 'error': 'Token not provided'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
