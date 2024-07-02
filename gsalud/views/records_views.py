from django.db import transaction
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from gsalud.services.filterTable import get_table_data
from gsalud.services.ORM_filters import apply_filters
from rest_framework.decorators import api_view
from gsalud.models import RecordsInfoUsers, RecordInfo, User, Record
from gsalud.services.lots_service import get_lot_from_key
from gsalud.services.record_info_service import removeRecordFromUser, createRecordInfo
from django.db.models import Prefetch, F


@api_view(['GET'])
def get_records_db(request):
    try:
        base_queryset = Record.objects.select_related('id_receipt_type', 'id_record_type').annotate(
            receipt_short=F('id_receipt_type__receipt_short'),
            record_name=F('id_record_type__record_name')
        ).values(
            'id_record', 'id_provider', 'id_receipt_type', 'id_record_type', 'date_liquid', 'date_recep', 'date_audi_vto', 'date_period',
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
            'id_record', 'id_provider', 'id_receipt_type', 'id_record_type', 'date_liquid', 'date_recep', 'date_audi_vto', 'date_period',
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
            'id_provider__id_priority',
            'recordinfo__id_lot'
        ).annotate(
            part_g_salud=F('id_provider__id_particularity__part_g_salud'),
            part_prevencion=F(
                'id_provider__id_particularity__part_prevencion'),
            priority_status=F('id_provider__id_priority__status'),
            id_provider_key=F('id_provider__id_provider'),
            lot_key=F('recordinfo__id_lot__lot_key'),
            business_name=F('id_provider__business_name'),
            business_location=F('id_provider__business_location'),
            id_coordinator=F('id_provider__id_coordinator'),
            date_asignment=F('recordinfo__id_lot__date_asignment'),
            observation=F('recordinfo__observation'),
            id_user=F('recordinfo__id_lot__id_user')
        ).filter(
            recordinfo__id_lot__id_user=16
        ).values(
            'id_record', 'part_g_salud', 'part_prevencion','priority_status', 'id_provider_key', 'lot_key',
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
        base_query = """select ri.id_record,ri.assigned,r.id_provider,business_name,ri.id_lot, 
                        l.id_user, p.id_coordinator,r.record_total,ri.date_entry_digital,ri.date_entry_physical,ri.seal_number,
                        ri.observation, l.lot_key, rt2.receipt_short ,rt.record_name
                        from records_info ri 
                        left join records r ON ri.id_record  = r.id_record
                        left join record_types rt on rt.id = r.id_record_type
                        left join providers p  on r.id_provider = p.id_provider 
                        left join lots l on ri.id_lot = l.id
                        LEFT JOIN receipt_types rt2 ON r.id_receipt_type =rt2.id
                        """
        if id_lot:
            modifier = f'ri.id_lot = {id_lot}'
            return get_table_data(request, base_query, [modifier])
        else:
            return get_table_data(request, base_query)

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['GET'])
def get_user_records(request):
    try:
        token = request.GET.dict()['token']
        validated_token = RefreshToken(token)
        id_user = int(validated_token.payload['user_id'])
        base_query = """select ri.id_record, uxri.id as uxri_id,uxri.worked_on,ri.assigned,r.id_provider,business_name, rt.record_name ,ri.id_lot, 
                        l.id_user,p.priority, p.id_coordinator,r.record_total,ri.date_entry_digital,ri.date_entry_physical,ri.seal_number,
                        ri.observation, l.lot_key, p.id_particularity
                        from users_x_records_info uxri 
                        inner join records_info ri  on ri.id  = uxri.id_record_info
                        inner join records r ON ri.id_record  = r.id_record
                        left join record_types rt on rt.id = r.id_record_type
                        inner join providers p  on r.id_provider = p.id_provider 
                        left join particularities p2 on p2.id = p.id_particularity
                        left join lots l on ri.id_lot = l.id """
        modifier = f'uxri.id_user = {id_user}'
        return get_table_data(request, base_query, [modifier])

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['POST'])
def addRecordtoUser(request):
    try:
        warning = ''
        requestDict = request.data
        token = requestDict['token']
        validated_token = RefreshToken(token)
        id_record = requestDict['id_record'],
        id_user = int(validated_token.payload['user_id'])

        # Check if the record exists
        record_info_instance = RecordInfo.objects.filter(id_record=id_record)
        if not record_info_instance.exists():
            res = createRecordInfo(requestDict['id_record'])
            if res:
                warning = '- El expediente no estaba asignado'
            else:
                return JsonResponse({'success': False, 'error': 'El expediente no existe o no esta asignado'})

        user_instance = User.objects.filter(id=id_user).first()
        record_info_id = record_info_instance.first().id

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
def updateRecordtoUser(request):
    try:
        requestDict = request.data
        token = requestDict['token']
        validated_token = RefreshToken(token)
        id_record_new = requestDict['id_record_new']
        id_record_old = requestDict['id_record_old'],
        id_user = int(validated_token.payload['user_id'])

        # Check if the new record exists
        new_record_info_instance = RecordInfo.objects.filter(
            id_record=id_record_new)
        if not new_record_info_instance.exists():
            return JsonResponse({'success': False, 'error': 'El expediente no existe'})

        # Check already active on use
        if (RecordsInfoUsers.objects.filter(id_record_info=new_record_info_instance.first().id, id_user=id_user).exists()):
            return JsonResponse({'success': False, 'error': 'Ya Expediente ya en la Tabla'})

        id_old_record_info = RecordInfo.objects.filter(
            id_record=id_record_old).first().id

        old_Records_Info_Users_instance = RecordsInfoUsers.objects.filter(
            id_record_info=id_old_record_info, id_user=id_user).first()
        old_Records_Info_Users_instance.id_record_info = new_record_info_instance.first()
        old_Records_Info_Users_instance.save()

        return JsonResponse({'success': True, 'message': 'Actualizado Expediente'})

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['PUT'])
def saveRecordtoUser(request):
    """
    Update user record information in a transactional manner.

    Args:
        request: The HTTP request object containing a dictionary of record information.

    Returns:
        A JSON response indicating success or failure.
    """
    try:
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

                record_info_instance = RecordInfo.objects.filter(
                    id=uxri_instance.id_record_info.id).first()
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

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['PUT'])
def removeRecordUser(request):
    try:
        requestDict = request.data
        id_uxri = requestDict['id_uxri']
        if removeRecordFromUser(id_uxri):
            return JsonResponse({'success': True, 'message': 'Expediente desasignado'})
        else:
            return JsonResponse({'success': False, 'error': 'No se pudo desasignar el expediente'})

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})
