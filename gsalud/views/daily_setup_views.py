from datetime import datetime
import time

from django.http import JsonResponse
from rest_framework.decorators import api_view

from gsalud.models import Provider, Record, RecordInfo, Role, Lot
from gsalud.utils.exel_upload import handle_uploaded_file, calculate_hash, safe_record_key
from gsalud.services.types_service import get_receipt_by_short, get_record_type_by_name
from gsalud.services.record_service import insert_update_bulk_records, update_bulk_records, insert_bulk_records, get_record_by_key
from gsalud.services.users_service import get_audit_by_user_name
from gsalud.utils.manage_date import handle_date_DMY
from gsalud.services.record_info_service import insert_bulk_cases, update_bulk_cases, insert_update_bulk_records_info, exist_record_info
from gsalud.services.lots_service import get_lot_from_key
from gsalud.services.providers_service import insert_update_bulk_providers, insert_update_particularity_by_provider
from gsalud.services.config_service import update_date_config


@api_view(['POST'])
def post_lots(request):
    try:
        print('Start Lot creation')
        if request.method == 'POST' and 'file' in request.FILES:
            df, config_data = handle_uploaded_file(request, config_id=5)

            audit_role = Role.objects.get(pk=3)
            types_records = {}
            users = {}
            providers = {}
            new_records = []
            cases = []
            new_cases = []
            existing_cases = []
            lots = {}

            records_keys = set(
                df.iloc[:, config_data['record_key']].dropna().tolist())
            processed_records_keys = {
                safe_record_key(key) for key in records_keys}
            processed_records_keys = {
                key for key in processed_records_keys if key is not None}

            existing_key_records = set(Record.objects.filter(
                record_key__in=processed_records_keys).values_list('record_key', flat=True))

            for row in df.itertuples(index=False):
                record_key = safe_record_key(row[config_data['record_key']])
                if record_key is None:
                    continue

                # ============== Provider ==============
                id_provider = row[config_data['id_provider']]
                id_coordinator = row[config_data['id_coordinator']]

                if id_coordinator == 0:
                    id_coordinator = None

                if id_provider is None:
                    continue

                provider = None
                if id_provider not in providers:
                    provider = Provider(
                        id_provider=id_provider,
                        business_name=row[config_data['business_name']],
                        id_coordinator=row[config_data['id_coordinator']]
                    )
                    providers[id_provider] = provider
                else:
                    provider = providers[id_provider]
                # ============== Users ==============
                user_name = row[config_data['audit_user']]
                auditor = None
                if user_name is not None:
                    if user_name not in users:
                        users[user_name] = get_audit_by_user_name(
                            user_name, audit_role)
                    auditor = users[user_name]
                # ============== Lots ==============
                lot_key = str(row[config_data['lot_key']])
                lot_key = lot_key.upper()
                lot = None
                if row[config_data['lot_key']] != None:
                    if lot_key not in lots:
                        lot = get_lot_from_key(lot_key)
                        lots[lot_key] = lot
                    else:
                        lot = lots[lot_key]
                # ============== Types ==============
                type_name = row[config_data['record_type']]
                record_type = None
                if type_name:
                    if not type_name in types_records:
                        record_type = get_record_type_by_name(type_name)
                        types_records[type_name] = record_type
                    else:
                        record_type = types_records[type_name]
                # ============== Records ==============
                record = Record(
                    record_key=record_key,
                    id_provider=provider,
                    id_record_type=record_type,
                    record_total = row[config_data['record_total']]
                )
                if record_key not in existing_key_records:
                    new_records.append(record)
                    existing_key_records.add(record_key)
                # ============== Cases ==============
                cases.append(RecordInfo(
                    id_record=record,
                    id_lot=lot,
                    id_auditor=auditor,
                    date_assignment_audit=handle_date_DMY(
                        row[config_data['date_assignment_audit']]),
                    date_entry_digital=handle_date_DMY(
                        row[config_data['date_entry_digital']]),
                    date_entry_physical=handle_date_DMY(
                        row[config_data['date_entry_physical']]),
                    seal_number=row[config_data['seal_number']],
                    observation=row[config_data['observation']],
                    assigned=False))

            start = time.time()
            insert_update_bulk_providers(
                list(providers.values()), ['business_name', 'id_coordinator'], 'id_provider')
            print('*- Providers inserted/updated:',
                  len(list(providers.values())))
            print('*- Auditors inserted/updated:', len(list(users.values())))
            insert_bulk_records(new_records)
            print('*- New Records inserted:', len(new_records))

            existing_records = {
                record.record_key: record
                for record in Record.objects.filter(record_key__in=existing_key_records)}

            existing_record_cases = set(RecordInfo.objects.filter(
                id_record__in=[record.pk for record in existing_records.values()]).values_list('id_record', flat=True))

            for case in cases:
                record_key = case.id_record.record_key
                if record_key in existing_records:
                    record = existing_records[record_key]
                    case.id_record = record
                    if getattr(record, 'pk') in existing_record_cases:
                        existing_cases.append(case)
                    else:
                        new_cases.append(case)
                else:
                    new_cases.append(case)

            insert_bulk_cases(new_cases)
            print('*- New Records infos inserted:', len(new_cases))
            update_bulk_cases(existing_cases)
            print('*- Records infos updated:', len(existing_cases))
            end = time.time()
            print('Elapsed Time: ', end - start)
            update_date_config(5)
            return JsonResponse({'success': True})

        return JsonResponse({'success': False, 'error': 'Invalid request'})
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['POST'])
def post_assignment(request):
    try:
        print('Start Assignment')
        if request.method == 'POST' and 'file' in request.FILES:
            df, config_data = handle_uploaded_file(request, config_id=4)

            types_receipts = {}
            types_records = {}
            providers = {}
            records = []
            cases = []

            for row in df.itertuples(index=False):
                record_key = safe_record_key(row[config_data['record_key']])
                if record_key is None:
                    continue

                id_provider = int(row[config_data['id_provider']])
                provider = None

                if not id_provider:
                    return

                if id_provider not in providers:
                    particularity = None
                    part_prev = row[config_data['provider_particularity']]
                    if part_prev:
                        particularity = insert_update_particularity_by_provider(
                            id_provider, part_prev)

                    provider = Provider(
                        id_provider=id_provider,
                        business_name=row[config_data['business_name']],
                        business_location=row[config_data['business_location']],
                        sancor_zone=row[config_data['sancor_zone']],
                        priority=row[config_data['provider_priority']],
                        id_particularity=particularity
                    )
                    providers[id_provider] = provider
                else:
                    provider = providers[id_provider]
                # ============== Provider ==============

                reciet_short = row[config_data['id_receipt_type']]
                reciet_type = None
                if reciet_short:
                    if not reciet_short in types_receipts:
                        reciet_type = get_receipt_by_short(reciet_short)
                        types_receipts[reciet_short] = reciet_type
                    else:
                        reciet_type = types_receipts[reciet_short]

                type_name = row[config_data['record_type']]
                record_type = None
                if type_name:
                    if not type_name in types_records:
                        record_type = get_record_type_by_name(type_name)
                        types_records[type_name] = record_type
                    else:
                        record_type = types_records[type_name]
                # ============== Types ==============
                audit_group = int(
                    row[config_data['audit_group']]) if row[config_data['audit_group']] else None

                record = Record(
                    record_key=record_key,
                    id_provider=provider,
                    id_receipt_type=reciet_type,
                    date_recep=handle_date_DMY(row[config_data['date_recep']]),
                    date_audi_vto=handle_date_DMY(
                        row[config_data['date_audi_vto']]),
                    date_period=handle_date_DMY(
                        row[config_data['date_period']]),
                    id_record_type=record_type,
                    bruto=row[config_data['gross_amount']],
                    iva_factu=row[config_data['invoiced_amount']],
                    receipt_num=row[config_data['receipt_num']],
                    audit_group=audit_group,
                    date_vto_carga=handle_date_DMY(
                        row[config_data['date_audi_vto']]),
                    assigned_user=row[config_data['entry_user']],
                )
                records.append(record)
        start = time.time()
        insert_update_bulk_providers(list(providers.values()), [
            'business_name', 'business_location', 'sancor_zone', 'priority', 'id_particularity'], 'id_provider')
        insert_update_bulk_records(records, [
                                   'record_key', 'id_provider', 'id_receipt_type', 'date_recep', 'date_audi_vto',
                                   'date_period', 'id_record_type', 'bruto', 'iva_factu', 'receipt_num', 'audit_group',
                                   'date_vto_carga', 'assigned_user'], 'record_key')
        for row in df.itertuples(index=False):
            # ============== Cases ==============
            record_key = safe_record_key(row[config_data['record_key']])
            if record_key is None:
                continue
            record = get_record_by_key(record_key=record_key)

            cases.append(RecordInfo(id_record=record,
                                    date_assignment_prev=handle_date_DMY(
                                        row[config_data['date_assignment_prev']]),
                                    assigned=True))

        insert_update_bulk_records_info(
            cases, ['id_record', 'date_assignment_prev', 'assigned'], 'id_record')
        end = time.time()
        print('Elapsed Time for assignment: ', end - start)
        update_date_config(4)
        return JsonResponse({'success': True})
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['POST'])
# This should insert new providers for the records, Create new records and update those existing
def post_db(request):
    print('Start Post DB')
    if request.method == 'POST' and 'file' in request.FILES:
        df, config_data = handle_uploaded_file(request, config_id=3)

        types_receipts = {}
        types_records = {}
        providers = {}
        exisitng_records = []
        new_records = []
        cases = []

        records_keys = set(
            df.iloc[:, config_data['record_key']].dropna().tolist())
        processed_records_keys = {safe_record_key(key) for key in records_keys}
        processed_records_keys = {
            key for key in processed_records_keys if key is not None}
        existing_records_keys = set(Record.objects.filter(
            record_key__in=processed_records_keys).values_list('record_key', flat=True))

        for row in df.itertuples(index=False):
            record_key = safe_record_key(row[config_data['record_key']])
            if record_key is None:
                continue
            id_provider = int(row[config_data['id_provider']])
            provider = None

            if not id_provider:
                return

            if id_provider not in providers:
                provider = Provider(
                    id_provider=id_provider,
                    business_name=row[config_data['business_name']],
                    business_location=row[config_data['business_location']],
                    sancor_zone=row[config_data['zona_sancor']]
                )
                providers[id_provider] = provider
            else:
                provider = providers[id_provider]
            # ============== Provider ==============
            reciet_short = row[config_data['id_receipt_type']]
            reciet_type = None
            if reciet_short:
                if not reciet_short in types_receipts:
                    reciet_type = get_receipt_by_short(reciet_short)
                    types_receipts[reciet_short] = reciet_type
                else:
                    reciet_type = types_receipts[reciet_short]

            type_name = row[config_data['record_type']]
            record_type = None
            if type_name:
                if not type_name in types_records:
                    record_type = get_record_type_by_name(type_name)
                    types_records[type_name] = record_type
                else:
                    record_type = types_records[type_name]
            # ============== Types ==============
            audit_group = int(
                row[config_data['audit_group']]) if row[config_data['audit_group']] else None
            total_val = round(sum(filter(None, [row[config_data['exento']], row[config_data['gravado']],
                                                row[config_data['iva_factu']], row[config_data['iva_perce']], row[config_data['iibb']]])), 2)

            record = Record(
                record_key=str(record_key),
                id_provider=provider,
                id_receipt_type=reciet_type,
                date_liquid=handle_date_DMY(row[config_data['date_liquid']]),
                date_recep=handle_date_DMY(row[config_data['date_recep']]),
                date_audi_vto=handle_date_DMY(
                    row[config_data['date_audi_vto']]),
                date_period=handle_date_DMY(row[config_data['date_period']]),
                id_record_type=record_type,
                totcal=row[config_data['totcal']],
                bruto=row[config_data['bruto']],
                ivacal=row[config_data['ivacal']],
                prestac_grava=row[config_data['prestac_grava']],
                debcal=row[config_data['debcal']],
                inter_debcal=row[config_data['inter_debcal']],
                debito=row[config_data['debito']],
                debtot=row[config_data['debtot']],
                a_pagar=row[config_data['a_pagar']],
                debito_iva=row[config_data['debito_iva']],
                receipt_num=row[config_data['receipt_num']],
                receipt_date=handle_date_DMY(
                    row[config_data['receipt_date']]),
                exento=row[config_data['exento']],
                gravado=row[config_data['gravado']],
                iva_factu=row[config_data['iva_factu']],
                iva_perce=row[config_data['iva_perce']],
                iibb=row[config_data['iibb']],
                record_total=total_val,
                neto_impues=row[config_data['neto_impues']],
                resu_liqui=row[config_data['resu_liqui']],
                cuenta=row[config_data['cuenta']],
                ambu_total=row[config_data['ambu_total']],
                inter_total=row[config_data['inter_total']],
                audit_group=audit_group,
                date_vto_carga=handle_date_DMY(
                    row[config_data['date_vto_carga']]),
                status=row[config_data['status']],
                assigned_user=row[config_data['assigned_user']],
                avance=row[config_data['avance']]
            )
            hash_val = calculate_hash(record)
            record.hashed_val = hash_val

            if str(record_key) not in existing_records_keys:
                new_records.append(record)
            else:
                exisitng_records.append(record)
            # ============== Records ==============
        start = time.time()
        insert_update_bulk_providers(list(providers.values()), [
                                     'business_name', 'business_location', 'sancor_zone'], 'id_provider')
        print('*- Providers inserted/updated:', len(list(providers.values())))
        insert_bulk_records(new_records)
        print('*- New Records inserted:', len(new_records))
        update_bulk_records(exisitng_records)
        print('*- Records updated:', len(exisitng_records))

        for row in df.itertuples(index=False):
            # ============== Cases ==============
            record_key = safe_record_key(row[config_data['record_key']])
            if record_key is None:
                continue
            audit_group = int(
                row[config_data['audit_group']]) if row[config_data['audit_group']] else None
            if audit_group == 61:
                record = get_record_by_key(record_key=record_key)
                cases.append(RecordInfo(id_record=record, assigned=False))

        insert_update_bulk_records_info(
            cases, ['id_record', 'assigned'], 'id_record')
        print('*- Records Cases Inserted/updated:', len(cases))
        end = time.time()
        print('Elapsed Time: ', end - start)
        update_date_config(3)
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Wrong Type of request'})
