from django.http import JsonResponse
from rest_framework.decorators import api_view

from gsalud.services.config_service import update_date_config
from gsalud.utils.exel_upload import handle_uploaded_file
from gsalud.services.file_upload_service import manage_lots, manage_db,manage_assignment


@api_view(['POST'])
def post_lots(request):
    try:
        print('Start Lot creation')
        if request.method == 'POST' and 'file' in request.FILES:
            file_path = handle_uploaded_file(request=request)
            manage_lots(file_path)
            return JsonResponse({'success': True, 'message': 'Archivo en proceso'})
        else:
            update_date_config(5,None)
            return JsonResponse({'success': False, 'error': 'Wrong Type of request'})
    except Exception as e:
        update_date_config(5,None)
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['POST'])
def post_assignment(request):
    try:
        if request.method == 'POST' and 'file' in request.FILES:
            file_path = handle_uploaded_file(request=request)
            manage_assignment(file_path)
            return JsonResponse({'success': True})
        else:
            update_date_config(4,None)
            return JsonResponse({'success': False, 'error': 'Wrong Type of request'})
    except Exception as e:
        update_date_config(4,None)
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['POST'])
# This should insert new providers for the records, Create new records and update those existing
def post_db(request):
    try:
        if request.method == 'POST' and 'file' in request.FILES:
            file_path = handle_uploaded_file(request=request)
            manage_db(file_path)

            return JsonResponse({'success': True})
        else:
            update_date_config(3,None)
            return JsonResponse({'success': False, 'error': 'Wrong Type of request'})
    except Exception as e:
        print(e)
        update_date_config(3,None)
        return JsonResponse({'success': False, 'error': str(e)})
