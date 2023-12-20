from collections import namedtuple
from django.http import JsonResponse
from django.db import connection
import json

filters = [
    {'name':'Ordenar Asc','function': 0, 'values_needed': 0, 'icon': 'material-symbols-light:arrow-drop-down', 'unique': True},
    {'name':'Ordenar Desc','function': 1, 'values_needed': 0, 'icon': 'material-symbols-light:arrow-drop-up', 'unique': True},
    {'name':'Vacio','function': 2, 'values_needed': 0, 'icon': 'material-symbols-light:brightness-empty-outline'},
    {'name':'Existe','function': 3, 'values_needed': 0, 'icon': 'material-symbols-light:brightness-empty'},
    {'name':'Si','function': 4, 'values_needed': 0, 'icon': 'carbon:checkmark'},
    {'name':'No','function': 5, 'values_needed': 0, 'icon': 'carbon:close-large'},
    {'name':'Mas que (>)','function': 6, 'values_needed': 1, 'icon': 'material-symbols-light:brightness-empty-outline'},
    {'name':'Mas/igual que (>=)', 'function': 7, 'values_needed': 1, 'icon': 'material-symbols-light:brightness-empty-outline'},
    {'name':'Menos que (<)', 'function': 8, 'values_needed': 1, 'icon': 'material-symbols-light:brightness-empty-outline'},
    {'name':'Menos/igual que (<=)', 'function': 9, 'values_needed': 1, 'icon': 'material-symbols-light:brightness-empty-outline'},
    {'name':'Igual A (=)', 'function': 10, 'values_needed': 1, 'icon': 'material-symbols-light:brightness-empty-outline'},
    {'name':'Distinto de (!=)', 'function': 11, 'values_needed': 1, 'icon': 'material-symbols-light:brightness-empty-outline'},
    {'name':'Contiene', 'function': 12, 'values_needed': 1, 'icon': 'material-symbols-light:brightness-empty-outline'},
    {'name':'No Contiene', 'function': 13, 'values_needed': 1, 'icon': 'material-symbols-light:brightness-empty-outline'},
    {'name':'Empieza con', 'function': 14, 'values_needed': 1, 'icon': 'material-symbols-light:brightness-empty-outline'},
    {'name':'Termina con', 'function': 15, 'values_needed': 1, 'icon': 'material-symbols-light:brightness-empty-outline'},
]

def generate_order_by(column_name, val, is_asc=True,):
    order = 'ASC' if is_asc else 'DESC'
    return ['Order', f"ORDER BY {column_name} {order}"]


def generate_equal_or_not_equal_filter(column_name, val, is_equal=True):
    operator = '=' if is_equal else '!='
    return ['Where', f"{column_name} {operator} '{val}'"]


def generate_comparison_filter(column_name, val, operator):
    return ['Where', f"{column_name} {operator} '{val}'"]


def generate_empty_filter(column_name, val):
    return ['Where', f"{column_name} IS NULL"]


def generate_exists_filter(column_name, val):
    return ['Where', f"{column_name} IS NOT NULL"]


def generate_false_filter(column_name, val):
    return ['Where', f"{column_name} = false"]


def generate_true_filter(column_name, val):
    return ['Where', f"{column_name} = true"]


def generate_text_contains_filter(column_name, value):
    return ['Where', f"UPPER({column_name}) LIKE UPPER('%{value}%')"]


def generate_text_not_contains_filter(column_name, value):
    return ['Where', f"UPPER({column_name}) NOT LIKE UPPER('%{value}%')"]


def generate_text_starts_with_filter(column_name, value):
    return ['Where', f"UPPER({column_name}) LIKE UPPER('{value}%')"]


def generate_text_ends_with_filter(column_name, value):
    return ['Where', f"UPPER({column_name}) LIKE UPPER('%{value}')"]


sql_generators = {
    0: lambda column, val: generate_order_by(column, val, is_asc=True),
    1: lambda column, val: generate_order_by(column, val, is_asc=False),
    2: generate_empty_filter,
    3: generate_exists_filter,
    4: generate_true_filter,
    5: generate_false_filter,
    6: lambda column, val: generate_comparison_filter(column, val, '>'),
    7: lambda column, val: generate_comparison_filter(column, val, '>='),
    8: lambda column, val: generate_comparison_filter(column, val, '<'),
    9: lambda column, val: generate_comparison_filter(column, val, '<='),
    10: lambda column, val: generate_equal_or_not_equal_filter(column, val, is_equal=True),
    11: lambda column, val: generate_equal_or_not_equal_filter(column, val, is_equal=False),
    12: generate_text_contains_filter,
    13: generate_text_not_contains_filter,
    14: generate_text_starts_with_filter,
    15: generate_text_ends_with_filter
}

def get_table_data(request, base_query):
    try:
        with connection.cursor() as cursor:
            dataString = request.GET.dict()['filters']
            filters = json.loads(dataString)
            where_filters = []
            order_by = ''
            print(filters)

            for filter in filters:
                sql_generator = sql_generators.get(filter['funct'])
                if sql_generator:
                    group,sql = sql_generator(filter['col'], filter['val'])
                    if group == 'Where':
                        where_filters.append(sql)
                    elif group == 'Order':
                        order_by = sql
                else:
                    print("Function not found or not yet implemented")

            # Join all filter SQL strings using 'AND'
            if where_filters:
                filter_sql = ' AND '.join(where_filters)
                base_query += f' WHERE {filter_sql}'

            if order_by:
                base_query += f' {order_by}'

            cursor.execute(base_query)
            print(base_query)
            columns = [col[0] for col in cursor.description]
            Row = namedtuple('Row', columns)

            if cursor.rowcount > 0:
                rows = [Row(*row) for row in cursor.fetchall()]
                return JsonResponse(data=[dict(row._asdict()) for row in rows], safe=False)
            else:
                return JsonResponse(data=[], safe=False)
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})
