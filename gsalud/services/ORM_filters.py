from typing import List
from django.http import JsonResponse
from django.db import connection
from django.db.models import Q
import json

filters = [
    {'name': 'Ordenar Asc', 'function': 0, 'values_needed': 0,
        'icon': 'material-symbols-light:arrow-drop-down', 'unique': True},
    {'name': 'Ordenar Desc', 'function': 1, 'values_needed': 0,
        'icon': 'material-symbols-light:arrow-drop-up', 'unique': True},
    {'name': 'Vacio', 'function': 2, 'values_needed': 0,
        'icon': 'material-symbols-light:brightness-empty-outline'},
    {'name': 'Existe', 'function': 3, 'values_needed': 0,
        'icon': 'material-symbols-light:brightness-empty'},
    {'name': 'Si', 'function': 4, 'values_needed': 0, 'icon': 'carbon:checkmark'},
    {'name': 'No', 'function': 5, 'values_needed': 0, 'icon': 'carbon:close-large'},
    {'name': 'Mas que (>)', 'function': 6, 'values_needed': 1,
     'icon': 'material-symbols-light:brightness-empty-outline'},
    {'name': 'Mas/igual que (>=)', 'function': 7, 'values_needed': 1,
     'icon': 'material-symbols-light:brightness-empty-outline'},
    {'name': 'Menos que (<)', 'function': 8, 'values_needed': 1,
     'icon': 'material-symbols-light:brightness-empty-outline'},
    {'name': 'Menos/igual que (<=)', 'function': 9, 'values_needed': 1,
     'icon': 'material-symbols-light:brightness-empty-outline'},
    {'name': 'Igual A (=)', 'function': 10, 'values_needed': 1,
     'icon': 'material-symbols-light:brightness-empty-outline'},
    {'name': 'Distinto de (!=)', 'function': 11, 'values_needed': 1,
     'icon': 'material-symbols-light:brightness-empty-outline'},
    {'name': 'Contiene', 'function': 12, 'values_needed': 1,
        'icon': 'material-symbols-light:brightness-empty-outline'},
    {'name': 'No Contiene', 'function': 13, 'values_needed': 1,
        'icon': 'material-symbols-light:brightness-empty-outline'},
    {'name': 'Empieza con', 'function': 14, 'values_needed': 1,
        'icon': 'material-symbols-light:brightness-empty-outline'},
    {'name': 'Termina con', 'function': 15, 'values_needed': 1,
        'icon': 'material-symbols-light:brightness-empty-outline'},
]


def generate_order_by(column_name, is_asc=True):
    order = column_name if is_asc else f'-{column_name}'
    return ['Order', order]


def generate_equal_or_not_equal_filter(column_name, val, is_equal=True):
    operator = '' if is_equal else '__ne'
    return ['Where', Q(**{f'{column_name}{operator}': val})]


def generate_comparison_filter(column_name, val, operator):
    return ['Where', Q(**{f'{column_name}__{operator}': val})]


def generate_empty_filter(column_name):
    return ['Where', Q(**{f'{column_name}__isnull': True})]


def generate_exists_filter(column_name):
    return ['Where', Q(**{f'{column_name}__isnull': False})]


def generate_false_filter(column_name):
    return ['Where', Q(**{column_name: False})]


def generate_true_filter(column_name):
    return ['Where', Q(**{column_name: True})]


def generate_text_contains_filter(column_name, value):
    return ['Where', Q(**{f'{column_name}__icontains': value})]


def generate_text_not_contains_filter(column_name, value):
    return ['Where', ~Q(**{f'{column_name}__icontains': value})]


def generate_text_starts_with_filter(column_name, value):
    return ['Where', Q(**{f'{column_name}__istartswith': value})]


def generate_text_ends_with_filter(column_name, value):
    return ['Where', Q(**{f'{column_name}__iendswith': value})]


sql_generators = {
    0: lambda column, val: generate_order_by(column, is_asc=True),
    1: lambda column, val: generate_order_by(column, is_asc=False),
    2: lambda column, val: generate_empty_filter(column),
    3: lambda column, val: generate_exists_filter(column),
    4: lambda column, val: generate_true_filter(column),
    5: lambda column, val: generate_false_filter(column),
    6: lambda column, val: generate_comparison_filter(column, val, 'gt'),
    7: lambda column, val: generate_comparison_filter(column, val, 'gte'),
    8: lambda column, val: generate_comparison_filter(column, val, 'lt'),
    9: lambda column, val: generate_comparison_filter(column, val, 'lte'),
    10: lambda column, val: generate_equal_or_not_equal_filter(column, val, is_equal=True),
    11: lambda column, val: generate_equal_or_not_equal_filter(column, val, is_equal=False),
    12: lambda column, val: generate_text_contains_filter(column, val),
    13: lambda column, val: generate_text_not_contains_filter(column, val),
    14: lambda column, val: generate_text_starts_with_filter(column, val),
    15: lambda column, val: generate_text_ends_with_filter(column, val)
}


def execute_query_with_filters(request, base_queryset, extra_values=None):
    try:
        with connection.cursor() as cursor:
            dataString = request.GET.dict()['filters']
            filters = json.loads(dataString)

            where_filters = Q()
            order_by = []

            for filter in filters:
                sql_generator = sql_generators.get(filter['funct'])
                if sql_generator:
                    group, condition = sql_generator(
                        filter['col'], filter['val'])
                    if group == 'Where':
                        where_filters &= condition
                    elif group == 'Order':
                        order_by.append(condition)
                else:
                    print("Function not found or not yet implemented")

            # Apply filters
            query_set = base_queryset.filter(where_filters)

            # Apply order by
            if order_by:
                query_set = query_set.order_by(*order_by)

            # Limit the number of rows
            query_set = query_set[:5000]

            # Convert the QuerySet to a list
            if extra_values:
                query_list = list(query_set) + extra_values
            else: 
                query_list = list(query_set)

            # Return the list as a JsonResponse
            return query_list

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})


def execute_query(base_queryset, group_by=None):
    try:
        with connection.cursor() as cursor:
            query_set = base_queryset

            # Limit the number of rows
            query_set = query_set[:10000]

            # Convert the QuerySet to a list
            query_list = list(query_set)

            # Return the list as a JsonResponse
            return  query_list

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})
