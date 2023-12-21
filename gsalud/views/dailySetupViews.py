import re
import numpy as np
import pandas as pd
import hashlib
import time
import json

from datetime import datetime
from django.http import JsonResponse
from rest_framework.decorators import api_view

from gsalud.models import Configs, Providers, Records
from gsalud.services.configService import updateConfig
from gsalud.services.receiptTypesService import getTypesObj
from gsalud.services.recordService import insertRecords, updateRecords
from gsalud.utils.manageDate import handleDateDMY
from gsalud.services.recordInfoService import insertRecordsCases, updateRecordsCases
from gsalud.services.providersService import insertProviders, updateProviders, handlePriority


@api_view(['POST'])
def post_assignment(request):
    try:
        if request.method == 'POST' and 'file' in request.FILES:
            receiptTypesObj = getTypesObj()
            uploaded_file = request.FILES['file']
            df, id_empty = file_to_df(uploaded_file)
            configData = string_to_obj(
                Configs.objects.get(pk=4).value, id_empty)

            # --- EXISTING DATA ----
            existingRecords = set(Records.objects.values_list('id', flat=True))
            existingProviders = set(
                Providers.objects.values_list('id', flat=True))

            # --- NEW DATA ----
            newRecords = []
            newCases = []
            updateCases = []
            updateCasesId = []
            newProviders = []
            updateProvidersdata = []
            updateProvidersIds = []

            for row in df.itertuples(index=False):
                # --- End of the file ----
                if isinstance(row[configData['id_record']], str) and has_non_numeric_chars(row[configData['id_record']]):
                    # Perform action or stop reading the file
                    print(f"Found non-numeric value '{row[configData['id_record']]}")
                    break  # You may want to use break or some other action to stop reading

                id_record = int(row[configData['id_record']])
                id_provider = int(row[configData['id_provider']])
                if row[configData['audit_group']]:
                    audit_group = int(row[configData['audit_group']])
                # --- Record exists ----
                if id_record in existingRecords:
                    updateCasesId.append(id_record)
                    updateCases.append(
                        {'id_record': id_record, 'date_assignment': handleDateDMY(row[configData['date_assignment']]), 'assigned': True})
                else:
                    existingRecords.add(id_record)
                    newRecords.append({
                        'id': id_record, 'id_provider': id_provider, 'id_receipt_type': receiptTypesObj[row[configData['id_receipt_type']]],
                        'date_liquid': None, 'date_recep': handleDateDMY(row[configData['date_recep']]), 'date_audi_vto': handleDateDMY(row[configData['date_audi_vto']]),
                        'date_period': handleDateDMY(row[configData['date_period']]), 'record_type': row[configData['record_type']],
                        'bruto': row[configData['gross_amount']],'iva_factu': row[configData['invoiced_amount']], 'receipt_num': row[configData['receipt_num']], 'receipt_date': None, 'audit_group': audit_group,
                        'date_vto_carga': handleDateDMY(row[configData['date_audi_vto']]), 'assigned_user': row[configData['entry_user']],
                    })
                    newCases.append(
                        {'id_record': id_record, 'date_assignment': handleDateDMY(row[configData['date_assignment']]), 'assigned': True})

                newProvider = {'id': id_provider, 'business_name': row[configData['business_name']],
                               'business_location': row[configData['business_location']], 'sancor_zone': row[configData['sancor_zone']]}

                # ----- Existing Provider  ------
                if id_provider in existingProviders:
                    # ----- Check Coordinator  ------
                    if row[configData['id_coordinator']] != None:
                        id_coordinator = int(row[configData['id_coordinator']])
                        updateProvidersIds.append(id_provider)
                        updateProvidersdata.append(
                            {'coordinator_number': id_coordinator})
                        if id_coordinator not in existingProviders:
                            existingProviders.add(id_coordinator)
                            newProviders.append({
                                'id': id_coordinator, 'business_name': row[configData['coordinator_business_name']], 'business_location': None, 'sancor_zone': None
                            })
                else:
                    # ----- New Provider  ------
                    existingProviders.add(id_provider)
                    newProviders.append(newProvider)

                    # ----- Check Priority  ------
                    if row[configData['provider_priority']]:
                        idPriority = handlePriority(
                            row[configData['provider_priority']])
                        newProvider['id_priority'] = idPriority

                    # ----- Check Coordinator  ------
                    if row[configData['id_coordinator']] != None:
                        id_coordinator = int(row[configData['id_coordinator']])
                        if id_coordinator not in existingProviders:
                            newProviders.append({
                                'id': id_coordinator, 'business_name': row[configData['coordinator_business_name']], 'business_location': None, 'sancor_zone': None})

            # ----- Insert Providers  --------
            insertProviders(newProviders)
            # ----- Update Existing Providers  --------
            updateProviders(updateProvidersIds, updateProvidersdata)
            # ----- Insert new Records --------
            insertRecords(newRecords)
            # ----- Insert New Record Info ------
            insertRecordsCases(newCases)
            # ----- Update Existing Records Info --------
            updateRecordsCases(updateCasesId, updateCases)
            updateConfig(2, str(datetime.now().strftime("%Y-%m-%d %H:%M")))
            return JsonResponse({'success': True, })

        return JsonResponse({'success': False, 'error': 'Invalid request'})
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': e})


@api_view(['POST'])
def post_db(request):
    try:
        if request.method == 'POST' and 'file' in request.FILES:
            receiptTypesObj = getTypesObj()
            uploaded_file = request.FILES['file']
            df, id_empty = file_to_df(uploaded_file)
            configData = string_to_obj(
                Configs.objects.get(pk=3).value, id_empty)

            existingProviders = set(
                Providers.objects.values_list('id', flat=True))
            newProviders = []

            existing_records = set(
                Records.objects.values_list('id', flat=True))
            newRecords = []
            newCases = []

            updateRecordsData = []
            updateRecordsIds = []
            for row in df.itertuples(index=False):
                if row[configData['audit_group']]:
                    audit_group = int(row[configData['audit_group']])
                totalVal = sum(filter(None, [row[configData['exento']], row[configData['gravado']],
                               row[configData['iva_factu']], row[configData['iva_perce']], row[configData['iibb']]]))
                totalVal = round(totalVal, 2)

                rowRecord = {
                    'id': row[configData['id_record']], 'id_provider': row[configData['id_provider']], 'id_receipt_type': receiptTypesObj[row[configData['id_receipt_type']]],
                    'date_liquid': handleDateDMY(row[configData['date_liquid']]), 'date_recep': handleDateDMY(row[configData['date_recep']]),
                    'date_audi_vto': handleDateDMY(row[configData['date_audi_vto']]), 'date_period': handleDateDMY(row[configData['date_period']]),
                    'record_type': row[configData['record_type']], 'totcal': row[configData['totcal']], 'bruto': row[configData['bruto']], 'ivacal': row[configData['ivacal']],
                    'prestac_grava': row[configData['prestac_grava']], 'debcal': row[configData['debcal']], 'inter_debcal': row[configData['inter_debcal']],
                    'debito': row[configData['debito']], 'debtot': row[configData['debtot']], 'a_pagar': row[configData['a_pagar']], 'debito_iva': row[configData['debito_iva']],
                    'receipt_num': row[configData['receipt_num']], 'receipt_date': handleDateDMY(row[configData['receipt_date']]), 'exento': row[configData['exento']],
                    'gravado': row[configData['gravado']], 'iva_factu': row[configData['iva_factu']], 'iva_perce': row[configData['iva_perce']],
                    'iibb': row[configData['iibb']], 'record_total': totalVal, 'neto_impues': row[configData['neto_impues']], 'resu_liqui': row[configData['resu_liqui']],
                    'cuenta': row[configData['cuenta']], 'ambu_total': row[configData['ambu_total']], 'inter_total': row[configData['inter_total']], 'audit_group': audit_group,
                    'date_vto_carga': handleDateDMY(row[configData['date_vto_carga']]), 'status': row[configData['status']], 'assigned_user': row[configData['assigned_user']],
                    'avance': row[configData['avance']]
                }
                # Extract values and concatenate them into a single string

                sorted_keys = sorted(rowRecord.keys())
                joined_vals = ''.join(
                    str(rowRecord[key]) for key in sorted_keys)
                hash_object = hashlib.sha256(joined_vals.encode()).hexdigest()
                rowRecord['hashedVal'] = hash_object

                if row[configData['id_provider']] not in existingProviders:
                    existingProviders.add(row[configData['id_provider']])
                    newProviders.append(
                        {'id': row[configData['id_provider']], 'business_name': row[configData['business_name']], 'business_location': row[configData['business_location']],
                         'sancor_zone': row[configData['sancor_zone']]})

                if row[configData['id_record']] not in existing_records:
                    existing_records.add(row[configData['id_record']])
                    newRecords.append(rowRecord)
                    if audit_group == 61:
                        newCases.append(
                            {'id_record': row[configData['id_record']],
                                'date_assignment': None}
                        )
                else:
                    updateRecordsIds.append(row[configData['id_record']])
                    updateRecordsData.append(rowRecord)

            start = time.time()
            # ----- Insert Providers  --------
            insertProviders(newProviders)

            # ----- Insert new Records --------
            insertRecords(newRecords)

            # ----- Insert New Record Info ------
            insertRecordsCases(newCases)

            # ----- Update Existing Records --------
            updateRecords(updateRecordsIds, updateRecordsData)

            end = time.time()
            print('Elapsed Time: ', end - start)
            updateConfig(1, str(datetime.now().strftime("%Y-%m-%d %H:%M")))

            return JsonResponse({'success': True, })
        else:
            return JsonResponse({'success': False, 'error': 'Wrong Type of request'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': e})


def string_to_obj(string_data, index_empty):
    array_data = json.loads(string_data)
    new_dict = {
        item['identifier']: index_empty if item['order'] is None else item['order']
        for item in array_data
    }
    print('Dict:', new_dict)
    return new_dict


def file_to_df(file):
    df = pd.read_excel(file)
    df = df.replace({np.nan: None})
    df['emptyCol'] = None
    index_of_empty_col = df.columns.get_loc('emptyCol')
    return df, index_of_empty_col

def has_non_numeric_chars(text):
    return bool(re.search(r'[^0-9]', str(text)))