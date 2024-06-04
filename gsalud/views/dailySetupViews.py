import re
import numpy as np
import pandas as pd
import hashlib
import time
import json

from datetime import datetime
from django.http import JsonResponse
from rest_framework.decorators import api_view

from gsalud.models import Configs, Providers, Records, Lots
from gsalud.services.typesService import getReceiptTypes, registerNewReceiptType, getRecordTypes, registerNewRecordType
from gsalud.services.recordService import insertRecords, update_records
from gsalud.utils.manageDate import handleDateDMY
from gsalud.services.recordInfoService import insertRecordsCases, updateRecordsCases
from gsalud.services.providersService import insertProviders, updateProviders, register_priority, registerParticularity, updateParticularity, update_priority


def string_to_obj(string_data, index_empty):
    array_data = json.loads(string_data)
    return {
        item['identifier']: index_empty if item['order'] is None else item['order']
        for item in array_data
    }


def file_to_df(file):
    df = pd.read_excel(file)
    df = df.replace({np.nan: None})
    df['emptyCol'] = None
    return df, df.columns.get_loc('emptyCol')


def has_non_numeric_chars(text):
    return bool(re.search(r'[^0-9]', str(text)))


def handle_uploaded_file(request, config_id):
    uploaded_file = request.FILES['file']
    df, id_empty = file_to_df(uploaded_file)
    config_data = string_to_obj(
        Configs.objects.get(pk=config_id).value, id_empty)
    return df, config_data


def process_providers_data(row, config_data, existing_providers, new_providers, update_providers_data, update_providers_ids):
    id_provider = int(row[config_data['id_provider']])

    if id_provider in existing_providers:
        if row[config_data['provider_particularity']]:
            updateParticularity(
                row[config_data['provider_particularity']], id_provider)
        if row[config_data['provider_priority']]:
            update_priority(row[config_data['provider_priority']], id_provider)
        if row[config_data['id_coordinator']] is not None:
            id_coordinator = int(row[config_data['id_coordinator']])
            update_providers_ids.append(id_provider)
            update_providers_data.append(
                {'coordinator_number': id_coordinator})
            if id_coordinator not in existing_providers:
                existing_providers.add(id_coordinator)
                new_providers.append({
                    'id_provider': id_coordinator,
                    'business_name': row[config_data['coordinator_business_name']],
                    'business_location': None,
                    'sancor_zone': None
                })
    else:
        new_provider = {
            'id_provider': id_provider,
            'business_name': row[config_data['business_name']],
            'business_location': row[config_data['business_location']],
            'sancor_zone': row[config_data['sancor_zone']]
        }
        existing_providers.add(id_provider)
        new_providers.append(new_provider)
        if row[config_data['provider_priority']]:
            new_provider['id_priority'] = register_priority(
                row[config_data['provider_priority']])
        if row[config_data['provider_particularity']]:
            new_provider['provider_particularity'] = registerParticularity(
                row[config_data['provider_particularity']])
        if row[config_data['id_coordinator']] is not None:
            id_coordinator = int(row[config_data['id_coordinator']])
            if id_coordinator not in existing_providers:
                existing_providers.add(id_coordinator)
                new_providers.append({
                    'id_provider': id_coordinator,
                    'business_name': row[config_data['coordinator_business_name']],
                    'business_location': None,
                    'sancor_zone': None
                })


def process_records_data(row, config_data, existing_records, types_receipts, types_records, new_records, update_cases, update_cases_ids, new_cases):
    id_record = int(row[config_data['id_record']])
    id_provider = int(row[config_data['id_provider']])
    audit_group = int(row[config_data['audit_group']]
                      ) if row[config_data['audit_group']] else None

    if not row[config_data['id_receipt_type']] in types_receipts:
        registerNewReceiptType(row[config_data['id_receipt_type']])
        types_receipts = getReceiptTypes()

    if not row[config_data['record_type']] in types_records:
        registerNewRecordType(row[config_data['record_type']])
        types_records = getRecordTypes()

    if id_record in existing_records:
        update_cases_ids.append(id_record)
        update_cases.append({
            'id_record': id_record,
            'date_assignment': handleDateDMY(row[config_data['date_assignment']]),
            'assigned': True
        })
    else:
        existing_records.add(id_record)
        new_records.append({
            'id_record': id_record,
            'id_provider': id_provider,
            'id_receipt_type': types_receipts[row[config_data['id_receipt_type']]],
            'date_liquid': None,
            'date_recep': handleDateDMY(row[config_data['date_recep']]),
            'date_audi_vto': handleDateDMY(row[config_data['date_audi_vto']]),
            'date_period': handleDateDMY(row[config_data['date_period']]),
            'id_record_type': types_records[row[config_data['record_type']]],
            'bruto': row[config_data['gross_amount']],
            'iva_factu': row[config_data['invoiced_amount']],
            'receipt_num': row[config_data['receipt_num']],
            'receipt_date': None,
            'audit_group': audit_group,
            'date_vto_carga': handleDateDMY(row[config_data['date_audi_vto']]),
            'assigned_user': row[config_data['entry_user']],
        })
        new_cases.append({
            'id': id_record,
            'date_assignment': handleDateDMY(row[config_data['date_assignment']]),
            'assigned': True
        })


@api_view(['POST'])
def post_assignment(request):
    try:
        print('Start Assignment')
        if request.method == 'POST' and 'file' in request.FILES:
            df, config_data = handle_uploaded_file(request, config_id=4)

            existing_records = set(
                Records.objects.values_list('id_record', flat=True))
            types_receipts = getReceiptTypes()
            types_records = getRecordTypes()
            new_records = []
            new_cases = []
            update_cases = []
            update_cases_ids = []

            existing_providers = set(
                Providers.objects.values_list('id_provider', flat=True))
            new_providers = []
            update_providers_data = []
            update_providers_ids = []

            for row in df.itertuples(index=False):
                if isinstance(row[config_data['id_record']], str) and has_non_numeric_chars(row[config_data['id_record']]):
                    print(
                        f"Found non-numeric value '{row[config_data['id_record']]}")
                    break

                process_records_data(row, config_data, existing_records, types_receipts,
                                     types_records, new_records, update_cases, update_cases_ids, new_cases)
                process_providers_data(row, config_data, existing_providers,
                                       new_providers, update_providers_data, update_providers_ids)

            insertProviders(new_providers)
            updateProviders(update_providers_ids, update_providers_data)
            insertRecords(new_records)
            insertRecordsCases(new_cases)
            updateRecordsCases(update_cases_ids, update_cases)

            return JsonResponse({'success': True})

        return JsonResponse({'success': False, 'error': 'Invalid request'})
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})
    

@api_view(['POST'])
def post_lots(request):
    try:
        print('Start Assignment')
        if request.method == 'POST' and 'file' in request.FILES:
            df, config_data = handle_uploaded_file(request, config_id=4)

            existing_records = set(
                Records.objects.values_list('id_record', flat=True))

            existing_lots = set(
                Lots.objects.values_list('id_provider', flat=True))
            
            new_lots = []

            for row in df.itertuples(index=False):
                if isinstance(row[config_data['id_record']], str) and has_non_numeric_chars(row[config_data['id_record']]):
                    print(
                        f"Found non-numeric value '{row[config_data['id_record']]}")
                    break


            return JsonResponse({'success': True})

        return JsonResponse({'success': False, 'error': 'Invalid request'})
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['POST'])
# This should insert new providers for the records, Create new records and update those existing
def post_db(request):
    try:
        print('Start Post DB')
        if request.method == 'POST' and 'file' in request.FILES:
            df, config_data = handle_uploaded_file(request, config_id=3)

            existing_providers = set(
                Providers.objects.values_list('id_provider', flat=True))
            new_providers = []

            types_receipts = getReceiptTypes()
            types_records = getRecordTypes()
            existing_records = set(
                Records.objects.values_list('id_record', flat=True))
            new_records = []
            new_cases = []

            update_records_data = []
            update_records_ids = []

            for row in df.itertuples(index=False):
                if isinstance(row[config_data['id_record']], str) and has_non_numeric_chars(row[config_data['id_record']]):
                    print(
                        f"Found non-numeric value '{row[config_data['id_record']]}")
                    break

                audit_group = int(
                    row[config_data['audit_group']]) if row[config_data['audit_group']] else None

                total_val = sum(filter(None, [row[config_data['exento']], row[config_data['gravado']],
                                row[config_data['iva_factu']], row[config_data['iva_perce']], row[config_data['iibb']]]))
                total_val = round(total_val, 2)

                if not row[config_data['id_receipt_type']] in types_receipts:
                    registerNewReceiptType(row[config_data['id_receipt_type']])
                    types_receipts = getReceiptTypes()

                if not row[config_data['record_type']] in types_records:
                    registerNewRecordType(row[config_data['record_type']])
                    types_records = getRecordTypes()

                row_record = {
                    'id_record': row[config_data['id_record']],
                    'id_provider': row[config_data['id_provider']],
                    'id_receipt_type': types_receipts[row[config_data['id_receipt_type']]],
                    'date_liquid': handleDateDMY(row[config_data['date_liquid']]),
                    'date_recep': handleDateDMY(row[config_data['date_recep']]),
                    'date_audi_vto': handleDateDMY(row[config_data['date_audi_vto']]),
                    'date_period': handleDateDMY(row[config_data['date_period']]),
                    'id_record_type': types_records[row[config_data['record_type']]],
                    'totcal': row[config_data['totcal']],
                    'bruto': row[config_data['bruto']],
                    'ivacal': row[config_data['ivacal']],
                    'prestac_grava': row[config_data['prestac_grava']],
                    'debcal': row[config_data['debcal']],
                    'inter_debcal': row[config_data['inter_debcal']],
                    'debito': row[config_data['debito']],
                    'debtot': row[config_data['debtot']],
                    'a_pagar': row[config_data['a_pagar']],
                    'debito_iva': row[config_data['debito_iva']],
                    'receipt_num': row[config_data['receipt_num']],
                    'receipt_date': handleDateDMY(row[config_data['receipt_date']]),
                    'exento': row[config_data['exento']],
                    'gravado': row[config_data['gravado']],
                    'iva_factu': row[config_data['iva_factu']],
                    'iva_perce': row[config_data['iva_perce']],
                    'iibb': row[config_data['iibb']],
                    'record_total': total_val,
                    'neto_impues': row[config_data['neto_impues']],
                    'resu_liqui': row[config_data['resu_liqui']],
                    'cuenta': row[config_data['cuenta']],
                    'ambu_total': row[config_data['ambu_total']],
                    'inter_total': row[config_data['inter_total']],
                    'audit_group': audit_group,
                    'date_vto_carga': handleDateDMY(row[config_data['date_vto_carga']]),
                    'status': row[config_data['status']],
                    'assigned_user': row[config_data['assigned_user']],
                    'avance': row[config_data['avance']]
                }

                sorted_keys = sorted(row_record.keys())
                joined_vals = ''.join(
                    str(row_record[key]) for key in sorted_keys)
                row_record['hashed_val'] = hashlib.sha256(
                    joined_vals.encode()).hexdigest()

                if row[config_data['id_provider']] not in existing_providers:
                    existing_providers.add(row[config_data['id_provider']])
                    new_providers.append({
                        'id_provider': row[config_data['id_provider']],
                        'business_name': row[config_data['business_name']],
                        'business_location': row[config_data['business_location']],
                        'sancor_zone': row[config_data['zona_sancor']]
                    })

                if row[config_data['id_record']] not in existing_records:
                    existing_records.add(row[config_data['id_record']])
                    new_records.append(row_record)
                    if audit_group == 61:
                        new_cases.append({
                            'id_record': row[config_data['id_record']],
                            'date_assignment': None
                        })
                else:
                    update_records_ids.append(row[config_data['id_record']])
                    update_records_data.append(row_record)

            start = time.time()
            insertProviders(new_providers)
            insertRecords(new_records)
            insertRecordsCases(new_cases)
            update_records(update_records_ids, update_records_data)
            end = time.time()
            print('Elapsed Time: ', end - start)
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Wrong Type of request'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
