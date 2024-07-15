from django.db import transaction
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from gsalud.services.ORM_filters import apply_filters
from rest_framework.decorators import api_view
from gsalud.models import RecordsInfoUsers, RecordInfo, User, Record
from gsalud.services.lots_service import get_lot_from_key
from gsalud.services.record_info_service import removeRecordFromUser, createRecordInfo
from django.db.models import Prefetch, F
from django.db.models import Case, When, Value, BooleanField


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
        return apply_filters(request, base_queryset)

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['GET'])
def get_records_assigned(request):
    try:
        base_queryset = Record.objects.select_related('id_receipt_type', 'id_record_type').prefetch_related(
            Prefetch('recordinfo',
                     queryset=RecordInfo.objects.select_related('id_lot'))
        ).annotate(
            id_record_info=F('recordinfo__id'),
            date_assignment_case=F('recordinfo__date_assignment'),
            date_entry_digital=F('recordinfo__date_entry_digital'),
            date_entry_physical=F('recordinfo__date_entry_physical'),
            seal_number=F('recordinfo__seal_number'),
            observation=F('recordinfo__observation'),
            date_close=F('recordinfo__date_close'),
            assigned=F('recordinfo__assigned'),
            id_lot=F('recordinfo__id_lot__id'),
            lot_key=F('recordinfo__id_lot__lot_key'),
            lot_status=F('recordinfo__id_lot__status'),
            date_assignment_lot=F('recordinfo__id_lot__date_asignment'),
            date_return=F('recordinfo__id_lot__date_return'),
            date_departure=F('recordinfo__id_lot__date_departure'),
            receipt_short=F('id_receipt_type__receipt_short'),
            record_name=F('id_record_type__record_name')
        ).values(
            'id', 'record_key', 'id_provider', 'id_receipt_type', 'id_record_type', 'date_liquid', 'date_recep', 'date_audi_vto', 'date_period',
            'totcal', 'bruto', 'ivacal', 'prestac_grava', 'debcal', 'inter_debcal', 'debito', 'debtot', 'a_pagar', 'debito_iva',
            'receipt_num', 'receipt_date', 'exento', 'gravado', 'iva_factu', 'iva_perce', 'iibb', 'record_total', 'neto_impues',
            'resu_liqui', 'cuenta', 'ambu_total', 'inter_total', 'audit_group', 'date_vto_carga', 'status', 'assigned_user', 'avance',
            'id_record_info', 'date_assignment_case', 'date_entry_digital', 'date_entry_physical', 'seal_number', 'observation',
            'date_close', 'assigned', 'id_lot', 'lot_key', 'lot_status', 'date_assignment_lot', 'date_return', 'date_departure',
            'receipt_short', 'record_name'
        )
        return apply_filters(request, base_queryset)
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
            date_asignment=F('recordinfo__id_lot__date_asignment'),
            observation=F('recordinfo__observation'),
            id_user=F('recordinfo__id_lot__id_user')
        ).filter(
            recordinfo__id_lot__id_user=id_user
        ).values(
            'id', 'record_key', 'part_g_salud', 'part_prevencion', 'priority', 'id_provider_key', 'lot_key',
            'business_name', 'business_location', 'id_coordinator', 'record_total',
            'date_asignment', 'observation', 'id_user'
        )

        return apply_filters(request, base_queryset)
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['GET'])
def get_records_info(request):
    try:
        id_lot = request.GET.dict()['id_lot']
        base_queryset = RecordInfo.objects.select_related(
            'id_record__id_provider',
            'id_record__id_record_type',
            'id_record__id_receipt_type',
        ).annotate(
            record_key=F('id_record__record_key'),
            id_provider=F('id_record__id_provider__id_provider'),
            business_name=F('id_record__id_provider__business_name'),
            lot_user=F('id_auditor__user_name'),
            id_coordinator=F('id_record__id_provider__id_coordinator'),
            record_total=F('id_record__record_total'),
            lot_key=F('id_lot__lot_key'),
            receipt_short=F('id_record__id_receipt_type__receipt_short'),
            record_name=F('id_record__id_record_type__record_name')
        ).filter(
            id_lot=id_lot
        ).values(
            'id_record', 'record_key', 'assigned', 'id_provider', 'business_name', 'id_lot',
            'lot_user', 'id_coordinator', 'record_total', 'date_entry_digital',
            'date_entry_physical', 'seal_number', 'observation', 'lot_key',
            'receipt_short', 'record_name'
        )

        return apply_filters(request, base_queryset)

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['GET'])
def get_user_records(request):
    try:
        token = request.GET.dict()['token']
        validated_token = RefreshToken(token)
        id_user = int(validated_token.payload['user_id'])
        base_queryset = RecordsInfoUsers.objects.select_related(
            'id_record_info__id_record',
            'id_record_info__id_record__id_provider',
            'id_record_info__id_record__id_record_type',
            'id_record_info__id_lot',
            'id_record_info__id_record__id_provider__id_particularity',
            'id_record_info__id_auditor'
        ).annotate(
            record_key=F('id_record_info__id_record__record_key'),
            uxri_id=F('id'),
            assigned=F('id_record_info__assigned'),
            id_provider=F(
                'id_record_info__id_record__id_provider__id_provider'),
            business_name=F(
                'id_record_info__id_record__id_provider__business_name'),
            record_name=F(
                'id_record_info__id_record__id_record_type__record_name'),
            id_lot=F('id_record_info__id_lot__id'),
            id_auditor=F('id_record_info__id_auditor'),
            auditor=F('id_record_info__id_auditor__user_name'),
            priority=F('id_record_info__id_record__id_provider__priority'),
            id_coordinator=F(
                'id_record_info__id_record__id_provider__id_coordinator'),
            record_total=F('id_record_info__id_record__record_total'),
            date_entry_digital=F('id_record_info__date_entry_digital'),
            date_entry_physical=F('id_record_info__date_entry_physical'),
            seal_number=F('id_record_info__seal_number'),
            observation=F('id_record_info__observation'),
            lot_key=F('id_record_info__id_lot__lot_key'),
            part_prevencion=Case(
                When(id_record_info__id_record__id_provider__id_particularity__part_prevencion__isnull=False, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            ),
            part_g_salud=Case(
                When(
                    id_record_info__id_record__id_provider__id_particularity__part_g_salud__isnull=False, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        ).filter(
            id_user=id_user
        ).values(
            'id', 'record_key', 'uxri_id', 'worked_on', 'assigned', 'id_provider', 'business_name',
            'record_name', 'id_lot', 'id_auditor', 'auditor', 'priority', 'id_coordinator', 'record_total',
            'date_entry_digital', 'date_entry_physical', 'seal_number', 'observation',
            'lot_key', 'part_prevencion', 'part_g_salud'
        )
        return apply_filters(request, base_queryset)

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['POST'])
def add_record_to_user(request):
    try:
        warning = ''
        token = request.data['token']
        validated_token = RefreshToken(token)
        record_key = request.data['record_key'],
        id_user = int(validated_token.payload['user_id'])

        if record_key is None:
            return JsonResponse({'success': False, 'error': 'El id no existe'})

        # BUG
        record_key = record_key[0]
        # Check if the record exists
        record_instance = Record.objects.filter(record_key=str(record_key))
        if not record_instance.exists():
            return JsonResponse({'success': False, 'error': 'El expediente no existe'})

        record_info_instance = RecordInfo.objects.filter(
            id_record=record_instance.first().pk)
        if not record_info_instance.exists():
            res = createRecordInfo(record_instance.first().pk)
            if res:
                warning = '- El expediente no estaba asignado'
            else:
                return JsonResponse({'success': False, 'error': 'El expediente no existe'})

        user_instance = User.objects.filter(id=id_user).first()
        record_info_id = record_info_instance.first().pk

        record_user_exists = RecordsInfoUsers.objects.filter(
            id_record_info=record_info_id, id_user=id_user).exists()
        if not record_user_exists:
            RecordsInfoUsers.objects.create(id_record_info=record_info_instance.first(
            ), id_user=user_instance, worked_on=False)
            return JsonResponse({'success': True, 'message': 'Nuevo Expediente ' + warning})
        else:
            return JsonResponse({'success': False, 'error': 'Expediente ya en la Tabla'})

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['PUT'])
def update_record_to_user(request):
    try:
        request_dict = request.data
        token = request_dict['token']
        validated_token = RefreshToken(token)
        new_record_key = request_dict['new_record_key']
        old_record_key = request_dict['old_record_key'],

        # BUG
        old_record_key = old_record_key[0]
        id_user = int(validated_token.payload['user_id'])

        # Check if the new record exists
        new_record_instance = Record.objects.filter(
            record_key=str(new_record_key))
        if not new_record_instance.exists():
            return JsonResponse({'success': False, 'error': 'El expediente no existe'})

        new_record_info_instance = RecordInfo.objects.filter(
            id_record=new_record_instance.first().pk)
        if not new_record_info_instance.exists():
            res = createRecordInfo(new_record_instance.first().pk)
            if res:
                warning = '- El expediente no estaba asignado'
            else:
                return JsonResponse({'success': False, 'error': 'El expediente no existe'})

        # Check already active on use
        if (RecordsInfoUsers.objects.filter(id_record_info=new_record_info_instance.first().pk, id_user=id_user).exists()):
            return JsonResponse({'success': False, 'error': 'Ya Expediente ya en la Tabla'})

        old_record_instance = Record.objects.filter(
            record_key=str(old_record_key))
        if not old_record_instance.exists():
            return JsonResponse({'success': False, 'error': 'El viejo expediente no existe'})
        id_old_record_info = RecordInfo.objects.filter(
            id_record=old_record_instance.first().pk).first().pk

        old_Records_Info_Users_instance = RecordsInfoUsers.objects.filter(
            id_record_info=id_old_record_info, id_user=id_user).first()
        old_Records_Info_Users_instance.id_record_info = new_record_info_instance.first()
        old_Records_Info_Users_instance.save()

        return JsonResponse({'success': True, 'message': 'Actualizado Expediente'})

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['PUT'])
def save_record_to_user(request):
    """
    Update user record information in a transactional manner.

    Args:
        request: The HTTP request object containing a dictionary of record information.

    Returns:
        A JSON response indicating success or failure.
    """
    with transaction.atomic():
            requestDict = request.data
            values_to_save = requestDict['values']

            for id_record_info, record_info in values_to_save.items():
                uxri_instance = RecordsInfoUsers.objects.filter(
                    id=record_info['uxri_id']).first()
                if uxri_instance is None:
                    return JsonResponse({'success': False, 'error': f'UXRI instance with id {record_info["uxri_id"]} not found.'}, status=400)
                uxri_instance.worked_on = False
                uxri_instance.save()

                record_info_instance = RecordInfo.objects.filter(id=uxri_instance.id_record_info.pk).first()
                if record_info_instance is None:
                    return JsonResponse({'success': False, 'error': f'RecordInfo instance with id {id_record_info} not found.'}, status=400)

                for field in ['date_entry_digital', 'date_entry_physical', 'seal_number', 'observation']:
                    if field in record_info:
                        setattr(record_info_instance,
                                field, record_info[field])

                if 'lot_key' in record_info and record_info['lot_key'] is not None:
                    lot_instance = get_lot_from_key(record_info['lot_key'])
                    record_info_instance.id_lot = lot_instance

                record_info_instance.save()

    return JsonResponse({'success': True, 'message': 'Guardados Cambios Expediente'})



@api_view(['PUT'])
def remove_record_user(request):
    try:
        request_dict = request.data
        token = request_dict['token']
        validated_token = RefreshToken(token)
        record_key = request_dict['record_key'],
        id_user = int(validated_token.payload['user_id'])

        # BUG
        record_key = record_key[0]

        record_instance = Record.objects.filter(record_key=record_key).first()
        record_info_instance = RecordInfo.objects.filter(
            id_record=record_instance.pk)
        if not record_info_instance.exists():
            return JsonResponse({'success': False, 'error': 'El expediente no existe'})

        record_info_x_user_instance = RecordsInfoUsers.objects.filter(
            id_record_info=record_info_instance.first().pk, id_user=id_user)
        if not record_info_x_user_instance.exists():
            return JsonResponse({'success': False, 'error': 'Expediente no assignado'})

        if removeRecordFromUser(record_info_x_user_instance.first().pk):
            return JsonResponse({'success': True, 'message': 'Expediente desasignado'})
        else:
            return JsonResponse({'success': False, 'error': 'No se pudo desasignar el expediente'})

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})
