from django.db import transaction
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from gsalud.services.ORM_filters import execute_query_with_filters, execute_query
from rest_framework.decorators import api_view
from gsalud.models import RecordsInfoUsers, RecordInfo, User, Record
from gsalud.utils.manage_date import ToChar, parse_date
from gsalud.services.record_service import get_filtered_user_records
from gsalud.services.lots_service import get_lot_from_key
from gsalud.services.record_info_service import remove_record_from_user, create_record_info, get_records_from_lot
from django.db.models import Prefetch, F
import traceback


@api_view(['GET'])
def get_records_db(request):
    try:
        base_queryset = Record.objects.select_related('id_receipt_type', 'id_record_type').annotate(
            receipt_short=F('id_receipt_type__receipt_short'),
            record_name=F('id_record_type__record_name')
        ).values(
            'id', 'record_key', 'id_provider', 'id_receipt_type', 'id_record_type', 'date_liquid', 'date_recep', 'date_audi_vto', 'date_period',
            'totcal', 'bruto', 'ivacal', 'prestac_grava', 'debcal', 'inter_debcal', 'debito', 'debtot', 'a_pagar',
            'debito_iva', 'receipt_num', 'receipt_date', 'exento', 'gravado', 'iva_factu', 'iva_perce', 'iibb',
            'record_total', 'neto_impues', 'resu_liqui', 'cuenta', 'ambu_total', 'inter_total', 'audit_group',
            'date_vto_carga', 'status', 'assigned_user', 'avance',
            'receipt_short', 'record_name'
        )
        data = execute_query_with_filters(request, base_queryset)
        return JsonResponse({'success': True, 'data': data})

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})


def format_date(date_obj):
    return date_obj.strftime('%d/%m/%Y') if date_obj else None


@api_view(['GET'])
def get_records_assigned(request):
    try:
        base_queryset = Record.objects.select_related('id_receipt_type', 'id_record_type').prefetch_related(
            Prefetch('recordinfo',
                     queryset=RecordInfo.objects.select_related('id_lot'))
        ).annotate(
            id_record_info=F('recordinfo__id'),
            date_assignment_prev=F('recordinfo__date_assignment_prev'),
            date_assignment_audit=F('recordinfo__date_assignment_audit'),
            date_entry_digital=F('recordinfo__date_entry_digital'),
            date_entry_physical=F('recordinfo__date_entry_physical'),
            seal_number=F('recordinfo__seal_number'),
            observation=F('recordinfo__observation'),
            date_close=F('recordinfo__date_close'),
            assigned=F('recordinfo__assigned'),
            id_lot=F('recordinfo__id_lot__id'),
            lot_key=F('recordinfo__id_lot__lot_key'),
            lot_status=F('recordinfo__id_lot__status'),
            date_return=F('recordinfo__id_lot__date_return'),
            date_departure=F('recordinfo__id_lot__date_departure'),
            receipt_short=F('id_receipt_type__receipt_short'),
            record_name=F('id_record_type__record_name')
        ).values(
            'id', 'record_key', 'id_provider', 'id_receipt_type', 'id_record_type', 'date_liquid', 'date_recep', 'date_audi_vto', 'date_period',
            'totcal', 'bruto', 'ivacal', 'prestac_grava', 'debcal', 'inter_debcal', 'debito', 'debtot', 'a_pagar', 'debito_iva',
            'receipt_num', 'receipt_date', 'exento', 'gravado', 'iva_factu', 'iva_perce', 'iibb', 'record_total', 'neto_impues',
            'resu_liqui', 'cuenta', 'ambu_total', 'inter_total', 'audit_group', 'date_vto_carga', 'status', 'assigned_user', 'avance',
            'id_record_info', 'date_assignment_prev', 'date_entry_digital', 'date_entry_physical', 'seal_number', 'observation',
            'date_close', 'assigned', 'id_lot', 'lot_key', 'lot_status', 'date_assignment_audit', 'date_return', 'date_departure',
            'receipt_short', 'record_name'
        )
        data = execute_query_with_filters(request, base_queryset)
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['GET'])
def get_records_audit(request):
    try:
        token = request.GET.dict()['token']
        validated_token = RefreshToken(token)
        id_user = int(validated_token.payload['user_id'])
        base_queryset = Record.objects.select_related(
            'id_provider__id_particularity',
            'recordinfo__id_lot'
        ).annotate(
            part_g_salud=F('id_provider__id_particularity__part_g_salud'),
            part_prevencion=F(
                'id_provider__id_particularity__part_prevencion'),
            id_provider_key=F('id_provider__id_provider'),
            priority=F('id_provider__priority'),
            lot_key=F('recordinfo__id_lot__lot_key'),
            business_name=F('id_provider__business_name'),
            business_location=F('id_provider__business_location'),
            id_coordinator=F('id_provider__id_coordinator'),
            date_asignment=ToChar(F('recordinfo__id_lot__date_asignment')),
            observation=F('recordinfo__observation'),
            id_user=F('recordinfo__id_lot__id_user')
        ).filter(
            recordinfo__id_lot__id_user=id_user
        ).values(
            'id', 'record_key', 'part_g_salud', 'part_prevencion', 'priority', 'id_provider_key', 'lot_key',
            'business_name', 'business_location', 'id_coordinator', 'record_total',
            'date_asignment', 'observation', 'id_user'
        )

        data = execute_query_with_filters(request, base_queryset)
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['GET'])
def get_records_info(request):
    try:
        id_lot = None
        if 'id_lot' in request.GET.dict():
            id_lot = request.GET.dict()['id_lot']
        base_queryset = get_records_from_lot(id_lot=id_lot)
        data = execute_query_with_filters(request, base_queryset)
        return JsonResponse({'success': True, 'data': data})

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['GET'])
def get_user_records(request):
    try:
        token = request.GET.dict()['token']
        validated_token = RefreshToken(token)
        id_user = int(validated_token.payload['user_id'])
        base_queryset = get_filtered_user_records(id_user)
        data = execute_query_with_filters(request, base_queryset)
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        error_line = tb[-1][1]  # Get the line number of the last frame
        print(f"Exception occurred on line {error_line}: {e}")
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['POST'])
def add_record_to_user(request):
    try:
        token = request.data['token']
        validated_token = RefreshToken(token)
        records = request.data['records']
        id_user = int(validated_token.payload['user_id'])

        if not records:
            return JsonResponse({'success': False, 'error': 'No record keys provided'})

        user_instance = User.objects.filter(id=id_user).first()
        if not user_instance:
            return JsonResponse({'success': False, 'error': 'User not found'})

        added_records = []
        errors = []

        for record_obj in records:
            record_key = record_obj['value']
            # Check if the record exists
            record_instance = Record.objects.filter(
                record_key=str(record_key)).first()
            if not record_instance:
                errors.append(record_key)
                continue

            record_info_instance = RecordInfo.objects.filter(
                id_record=record_instance.pk).first()
            if not record_info_instance:
                res = create_record_info(record_instance.pk)
                if res:
                    record_info_instance = RecordInfo.objects.filter(
                        id_record=record_instance.pk).first()
                else:
                    errors.append(record_key)
                    continue

            record_user_exists = RecordsInfoUsers.objects.filter(
                id_record_info=record_info_instance.pk, id_user=id_user).exists()

            if not record_user_exists:
                RecordsInfoUsers.objects.create(
                    id_record_info=record_info_instance,
                    id_user=user_instance,
                    worked_on=False
                )
                added_records.append(record_key)
            else:
                errors.append(record_key)

        if added_records.__len__() > 0:
            base_query_set = get_filtered_user_records(id_user, added_records)
            query_result = execute_query(base_query_set)
        else:
            query_result = []

        response = {
            'success': True,
            'added_records': query_result,
            'errors': errors,
        }

        return JsonResponse(response)

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['PUT'])
def update_records_to_user(request):
    try:
        token = request.data['token']
        validated_token = RefreshToken(token)
        id_user = int(validated_token.payload['user_id'])
        # This should be an array of objects
        records_to_update = request.data['records']

        updated_record_keys = []
        errors = []

        with transaction.atomic():
            for record in records_to_update:
                new_record_key = record['new_record_key']
                old_record_key = record['old_record_key']

                # Check if the new record exists
                new_record_instance = Record.objects.filter(
                    record_key=str(new_record_key)).first()
                if not new_record_instance:
                    errors.append(new_record_key)
                    continue

                new_record_info_instance = RecordInfo.objects.filter(
                    id_record=new_record_instance.pk).first()
                if not new_record_info_instance:
                    res = create_record_info(new_record_instance.pk)
                    if not res:
                        errors.append(new_record_key)
                        continue
                    new_record_info_instance = RecordInfo.objects.get(
                        id_record=new_record_instance.pk)

                # Check if already active in use
                if RecordsInfoUsers.objects.filter(id_record_info=new_record_info_instance.pk, id_user=id_user).exists():
                    errors.append(new_record_key)
                    continue

                old_record_instance = Record.objects.filter(
                    record_key=str(old_record_key)).first()
                if not old_record_instance:
                    errors.append(new_record_key)
                    continue

                id_old_record_info = RecordInfo.objects.filter(
                    id_record=old_record_instance.pk).first().pk
                old_Records_Info_Users_instance = RecordsInfoUsers.objects.filter(
                    id_record_info=id_old_record_info, id_user=id_user).first()

                if old_Records_Info_Users_instance:
                    old_Records_Info_Users_instance.id_record_info = new_record_info_instance
                    old_Records_Info_Users_instance.save()
                    updated_record_keys.append(new_record_key)
                else:
                    errors.append(new_record_key)
                    

        if updated_record_keys.__len__() > 0:
            base_query_set = get_filtered_user_records(
                id_user, updated_record_keys)
            query_result = execute_query(base_query_set)
        else:
            query_result = []

        response = {
            'success': True,
            'modified_records': query_result,
            'errors': errors,
        }
        return JsonResponse(response)

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['DELETE'])
def remove_record_user(request):
    try:
        token = request.data['token']
        validated_token = RefreshToken(token)
        records = request.data['records']
        id_user = int(validated_token.payload['user_id'])

        success_count = 0
        failed_count = 0
        failed_records = []

        for record_obj in records:
            record_key = record_obj['value']
            record_instance = Record.objects.filter(
                record_key=record_key).first()
            if not record_instance:
                failed_count += 1
                failed_records.append(record_key)
                continue

            record_info_instance = RecordInfo.objects.filter(
                id_record=record_instance.pk).first()
            if not record_info_instance:
                failed_count += 1
                failed_records.append(record_key)
                continue

            record_info_x_user_instance = RecordsInfoUsers.objects.filter(
                id_record_info=record_info_instance.pk, id_user=id_user
            ).first()

            if not record_info_x_user_instance:
                failed_count += 1
                failed_records.append(record_key)
                continue

            if remove_record_from_user(record_info_x_user_instance.pk):
                success_count += 1
            else:
                failed_count += 1
                failed_records.append(record_key)

        response = {
            'success': success_count > 0,
            'message': f'{success_count} expediente(s) desasignado(s) exitosamente',
            'failed_count': failed_count,
            'failed_records': failed_records
        }

        if failed_count > 0:
            response['error'] = f'No se pudieron desasignar {failed_count} expediente(s)'

        return JsonResponse(response)

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})


def update_record_info(record_info_instance, record_info):
    for field in ['date_entry_digital', 'date_entry_physical', 'seal_number', 'observation']:
        if field in record_info:
            value = record_info[field]
            if 'date' in field:
                # Convert date from 'day/month/year' to 'YYYY-MM-DD'
                value = parse_date(value)
            setattr(record_info_instance, field, value)

    if 'lot_key' in record_info and record_info['lot_key'] is not None:
        lot_instance = get_lot_from_key(record_info['lot_key'])
        record_info_instance.id_lot = lot_instance

    record_info_instance.save()


@api_view(['PUT'])
def save_record_to_user(request):
    """
    Update user record information in a transactional manner.

    Args:
        request: The HTTP request object containing a dictionary of record information.

    Returns:
        A JSON response indicating success or failure.
    """
    try:
        request_data = request.data
        token = request_data.get('token')
        if not token:
            return JsonResponse({'success': False, 'error': 'Token is missing'}, status=400)

        validated_token = RefreshToken(token)
        user_id = int(validated_token.payload['user_id'])

        values_to_save = request_data.get('values')
        if not values_to_save:
            return JsonResponse({'success': False, 'error': 'No values to save'}, status=400)

        with transaction.atomic():
            for id_record_info, record_info in values_to_save.items():
                uxri_instance = RecordsInfoUsers.objects.filter(
                    id=record_info['uxri_id']).first()
                if uxri_instance is None:
                    return JsonResponse({'success': False, 'error': f'UXRI instance with id {record_info["uxri_id"]} not found.'}, status=400)

                uxri_instance.worked_on = False
                uxri_instance.save()

                record_info_instance = RecordInfo.objects.filter(
                    id=uxri_instance.id_record_info.pk).first()
                if record_info_instance is None:
                    return JsonResponse({'success': False, 'error': f'RecordInfo instance with id {id_record_info} not found.'}, status=400)

                update_record_info(record_info_instance, record_info)

        return JsonResponse({'success': True, 'message': 'Guardados Cambios Expediente'})

    except KeyError as e:
        return JsonResponse({'success': False, 'error': f'Missing key: {str(e)}'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'An error occurred: {str(e)}'}, status=500)


@api_view(['DELETE'])
def remove_all_assigned_records(request):
    try:
        # Extract the token from the request data
        token = request.data.get('token')
        if not token:
            return JsonResponse({'success': False, 'error': 'Token is missing'}, status=400)

        # Validate the token and extract the user ID
        try:
            validated_token = RefreshToken(token)
            id_user = int(validated_token['user_id'])
        except Exception as e:
            return JsonResponse({'success': False, 'error': 'Invalid token'}, status=401)

        # Query and delete the records associated with the user
        rec_objs = RecordsInfoUsers.objects.filter(id_user=id_user)
        deleted_count, _ = rec_objs.delete()

        return JsonResponse({'success': True, 'message': f'{deleted_count} records unassigned'}, status=200)
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        error_line = tb[-1][1]  # Get the line number of the last frame
        print(f"Exception occurred on line {error_line}: {e}")
        return JsonResponse({'success': False, 'error': str(e)})
