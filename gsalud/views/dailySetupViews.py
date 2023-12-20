from logging import config
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
from gsalud.utils.manageDate import handleDateDMY, handleDatetimeToDate
from gsalud.services.recordInfoService import insertRecordsCases, updateRecordsCases
from gsalud.services.providersService import insertProviders, updateProviders, handlePriority


@api_view(['POST'])
def post_assignment(request):
    try:
        if request.method == 'POST' and 'file' in request.FILES:
            configData = string_to_obj(Configs.objects.get(pk=3).value)
            print(configData)
            receiptTypesObj = getTypesObj()
            uploaded_file = request.FILES['file']
            df = pd.read_excel(uploaded_file)
            df = df.replace({np.nan: None})

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
                if row[configData['id_record']] == "Total general":
                    break

                id_record = int(row[configData['id_record']])
                id_provider = int(row[configData['id_provider']])
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
                        'bruto': row[configData['bruto']], 'receipt_num': row[configData['receipt_num']], 'receipt_date': None, 'audit_group': row[configData['audit_group']],
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
            configData = string_to_obj(Configs.objects.get(pk=4).value)
            print(configData)
            receiptTypesObj = getTypesObj()
            uploaded_file = request.FILES['file']
            df = pd.read_excel(uploaded_file)
            df = df.replace({np.nan: None})

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
                totalVal = sum(filter(None, [row.exento, row.gravado, row.iva_factu, row.iva_perce, row.iibb]))
                totalVal = round(totalVal, 2)

                rowRecord = {
                    'id': row.expe, 'id_provider': row.prestad, 'id_receipt_type': receiptTypesObj[row.compro_tipo],
                    'date_liquid': handleDatetimeToDate(row.liqui_fecha), 'date_recep': handleDatetimeToDate(row.recep_fecha), 'date_audi_vto': handleDatetimeToDate(row.audi_vto),
                    'date_period': handleDatetimeToDate(row.perio), 'record_type': row.tipo_d, 'totcal': row.totcal, 'bruto': row.bruto, 'ivacal': row.ivacal,
                    'prestac_grava': row.prestac_grava, 'debcal': row.debcal, 'inter_debcal': row.inter_debcal, 'debito': row.debito, 'debtot': row.debtot,
                    'a_pagar': row.a_pagar, 'debito_iva': row.debito_iva, 'receipt_num': row.compro_nro, 'receipt_date': handleDatetimeToDate(row.fecha), 'exento': row.exento,
                    'gravado': row.gravado, 'iva_factu': row.iva_factu, 'iva_perce': row.iva_perce, 'iibb': row.iibb, 'record_total': totalVal,
                    'neto_impues': row.neto_impues, 'resu_liqui': row.resu_liqui, 'cuenta': row.cuenta, 'ambu_total': row.ambu_total,
                    'inter_total': row.inter_total, 'audit_group': row[configData['audit_group']], 'date_vto_carga': handleDatetimeToDate(row.fecha_vto_carga),
                    'status': row.estado, 'assigned_user': row.usuario, 'avance': row.avance
                }
                # Extract values and concatenate them into a single string
                sorted_keys = sorted(rowRecord.keys())
                joined_vals = ''.join(
                    str(rowRecord[key]) for key in sorted_keys)
                hash_object = hashlib.sha256(joined_vals.encode()).hexdigest()
                rowRecord['hashedVal'] = hash_object

                if row.prestad not in existingProviders:
                    existingProviders.add(row.prestad)
                    newProviders.append(
                        {'id': row.prestad, 'business_name': row.razon, 'business_location': row.loca, 'sancor_zone': row.zona_sancor})

                if row.expe not in existing_records:
                    existing_records.add(row.expe)
                    newRecords.append(rowRecord)
                    if row[configData['audit_group']] == 61:
                        newCases.append(
                            {'id_record': row.expe, 'date_assignment': None}
                        )
                else:
                    updateRecordsIds.append(row.expe)
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


def string_to_obj(string_data):
    array_data = json.loads(string_data)
    new_dict = {item['identifier']: item['order'] for item in array_data}
    return new_dict
