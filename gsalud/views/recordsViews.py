from django.db import transaction
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from gsalud.services.filterTable import get_table_data
from rest_framework.decorators import api_view
from gsalud.utils.manageDate import dateStrToDate
from gsalud.models import RecordsInfoUsers, RecordInfo, Users, Records
from gsalud.services.lotsService import getLotfromKey
from gsalud.services.recordInfoService import removeRecordFromUser, createRecordInfo
from gsalud.serializers import RecordInfoSerializer


@api_view(['GET'])
def getRecordsDB(request):
    try:
        base_query = '''
        SELECT r.*,rt.receipt_short ,rt2.record_name
        FROM records r left join receipt_types rt ON r.id_receipt_type =rt.id
        left join record_types rt2 on r.id_record_type = rt2.id '''

        return get_table_data(request, base_query)

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['GET'])
def getRecordsAssigned(request):
    try:
        base_query = '''
        SELECT r.id_record, r.id_provider, r.id_receipt_type, r.id_record_type, r.date_liquid, r.date_recep,
        r.date_audi_vto, r.date_period, r.totcal, r.bruto, r.ivacal, r.prestac_grava, r.debcal, r.inter_debcal,
        r.debito, r.debtot, r.a_pagar, r.debito_iva, r.receipt_num, r.receipt_date, r.exento, r.gravado,
        r.iva_factu, r.iva_perce, r.iibb, r.record_total, r.neto_impues, r.resu_liqui, r.cuenta,
        r.ambu_total, r.inter_total, r.audit_group, r.date_vto_carga, r.status, r.assigned_user, r.avance,
        ri.id AS id_record_info, ri.date_assignment as date_assignment_case, ri.date_entry_digital,
        ri.date_entry_physical, ri.seal_number, ri.observation, ri.date_close, ri.assigned,
        l.id AS id_lot, l.lot_key, l.status AS lot_status, l.date_asignment as date_assignment_lot, l.date_return, l.date_departure,
        rt.receipt_short ,rt2.record_name
        FROM  records r
        INNER JOIN records_info ri ON r.id_record = ri.id_record
        LEFT JOIN lots l ON ri.id_lot = l.id
        LEFT JOIN receipt_types rt ON r.id_receipt_type =rt.id
        LEFT JOIN record_types rt2 on r.id_record_type = rt2.id
                    '''
        return get_table_data(request, base_query)

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['GET'])
def getRecordsInfos(request):
    try:
        id_lot = request.GET.dict()['id_lot']
        base_query = """select ri.id_record,ri.assigned,r.id_provider,business_name,ri.id_lot, 
                        l.id_user, p.coordinator_number,r.record_total,ri.date_entry_digital,ri.date_entry_physical,ri.seal_number,
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
def getUserRecords(request):
    try:
        token = request.GET.dict()['token']
        validated_token = RefreshToken(token)
        id_user = int(validated_token.payload['user_id'])
        base_query = """select ri.id_record, uxri.id as uxri_id,uxri.worked_on,ri.assigned,r.id_provider,business_name, rt.record_name ,ri.id_lot, 
                        l.id_user, p.coordinator_number,r.record_total,ri.date_entry_digital,ri.date_entry_physical,ri.seal_number,
                        ri.observation, l.lot_key, p.id_priority, p.id_particularity, p3.status
                        from users_x_records_info uxri 
                        inner join records_info ri  on ri.id  = uxri.id_record_info
                        inner join records r ON ri.id_record  = r.id_record
                        left join record_types rt on rt.id = r.id_record_type
                        inner join providers p  on r.id_provider = p.id_provider 
                        left join particularities p2 on p2.id = p.id_particularity
                        left join priorities p3 on p3.id = p.id_priority
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

        user_instance = Users.objects.filter(id=id_user).first()
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
                    lot_instance = getLotfromKey(record_info['lot_key'])
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
