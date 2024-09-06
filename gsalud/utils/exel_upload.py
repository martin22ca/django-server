import re
import os
import uuid
import numpy as np
import pandas as pd
import json
import hashlib
from datetime import datetime

from gsalud.models import Config

def safe_record_key(input_value):
    # Check if the input is an integer or a float
    if isinstance(input_value, (int, float)):
        return str(input_value)
    
    # Check if the input is a string
    elif isinstance(input_value, str):
        # Remove spaces from the string
        input_value = input_value.replace(' ', '')

        # Remove everything after the last number found in the string
        match_end = re.search(r'(\d+)([^\d]*)$', input_value)
        if match_end:
            input_value = input_value[:match_end.end(1)]
        
        # Remove everything before the first 'i' or number
        match_start = re.search(r'([iI]|\d)', input_value)
        if match_start:
            input_value = input_value[match_start.start():]
        
        # Check if the string is all numbers
        if input_value.isdigit():
            return input_value
        
        # Check if the string starts with 'i' followed by numbers
        if input_value.lower().startswith('i') and input_value[1:].isdigit():
            return input_value.upper()
    
    # If conditions are not met, return None
    print(type(input_value),input_value)
    return None

def string_to_obj(string_data, index_empty):
    array_data = json.loads(string_data)
    return {
        item['identifier']: index_empty if item['order'] is None else item['order']
        for item in array_data
    }

def has_non_numeric_chars(text):
    return bool(re.search(r'[^0-9]', str(text)))


def handle_uploaded_file(request):
    uploaded_file = request.FILES['file']

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]  # Use first 8 characters of UUID
    file_extension = os.path.splitext(uploaded_file.name)[1]
    new_filename = f"{timestamp}_{unique_id}{file_extension}"
    
    # Save the file to the shared volume with the new filename
    shared_data_dir = '/app/shared_data'
    os.makedirs(shared_data_dir, exist_ok=True)
    file_path = os.path.join(shared_data_dir, new_filename)
    
    with open(file_path, 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)

    return file_path

def get_file_from_path(file_path, config_id):
    df = pd.read_excel(file_path)
    df = df.replace({np.nan: None})
    df['emptyCol'] = None
    id_empty = df.columns.get_loc('emptyCol')
    config_data = string_to_obj(
        Config.objects.get(pk=config_id).value, id_empty)
    return df, config_data

def calculate_hash(record_instance):
    # Convert the instance to a dictionary, excluding the 'hashed_val' field if it exists
    record_dict = {
        'record_key': record_instance.record_key,
        'id_provider': record_instance.id_provider.pk,
        'id_receipt_type': record_instance.id_receipt_type.pk,
        'date_liquid': record_instance.date_liquid,
        'date_recep': record_instance.date_recep,
        'date_audi_vto': record_instance.date_audi_vto,
        'date_period': record_instance.date_period,
        'id_record_type': record_instance.id_record_type.pk,
        'totcal': record_instance.totcal,
        'bruto': record_instance.bruto,
        'ivacal': record_instance.ivacal,
        'prestac_grava': record_instance.prestac_grava,
        'debcal': record_instance.debcal,
        'inter_debcal': record_instance.inter_debcal,
        'debito': record_instance.debito,
        'debtot': record_instance.debtot,
        'a_pagar': record_instance.a_pagar,
        'debito_iva': record_instance.debito_iva,
        'receipt_num': record_instance.receipt_num,
        'receipt_date': record_instance.receipt_date,
        'exento': record_instance.exento,
        'gravado': record_instance.gravado,
        'iva_factu': record_instance.iva_factu,
        'iva_perce': record_instance.iva_perce,
        'iibb': record_instance.iibb,
        'record_total': record_instance.record_total,
        'neto_impues': record_instance.neto_impues,
        'resu_liqui': record_instance.resu_liqui,
        'cuenta': record_instance.cuenta,
        'ambu_total': record_instance.ambu_total,
        'inter_total': record_instance.inter_total,
        'audit_group': record_instance.audit_group,
        'date_vto_carga': record_instance.date_vto_carga,
        'status': record_instance.status,
        'assigned_user': record_instance.assigned_user,
        'avance': record_instance.avance
    }

    # Sort the keys and concatenate their string representations
    sorted_keys = sorted(record_dict.keys())
    joined_vals = ''.join(str(record_dict[key]) for key in sorted_keys)
    
    # Calculate the hash
    hashed_val = hashlib.sha256(joined_vals.encode()).hexdigest()
    
    return hashed_val