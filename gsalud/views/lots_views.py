from django.http import JsonResponse
from django.db.models import Count, Q
from django.db import transaction
from gsalud.utils.manage_date import parse_date
from gsalud.services.ORM_filters import execute_query_with_filters
from gsalud.services.users_service import get_user_by_pk
from gsalud.services.lots_service import get_lot_from_key, manage_records_from_lot
from gsalud.models import Lot
from gsalud.serializers import LotsSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from gsalud.models import RecordInfo
from datetime import datetime


@api_view(['GET'])
def get_lots(request):
    try:
        # Query for actual lots
        base_queryset = Lot.objects.annotate(
            total_records=Count('recordinfo', distinct=True)
        ).values(
            'id', 'lot_key', 'date_return', 'date_departure', 'status', 'total_records', 'observation'
        )

        # Query for unassigned records
        unassigned_count = RecordInfo.objects.filter(id_lot__isnull=True).filter(
            Q(date_entry_digital__isnull=False) |
            Q(date_entry_physical__isnull=False) |
            Q(seal_number__isnull=False)
        ).count()

        # Create a virtual "unassigned" lot
        unassigned_lot = [{
            'id': None,
            'lot_key': 'No assignado',
            'date_return': None,
            'date_departure': None,
            'status': False,
            'total_records': unassigned_count
        }]
        # Apply filters (assuming this function exists and works with lists)
        data = execute_query_with_filters(
            request, base_queryset, unassigned_lot)
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        print
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['DELETE'])
def pop_record_from_lot(request):
    try:
        # DON'T KNOW WHY I RECIVE A LIST INSTEAD OF AND OBJ HERE
        data = request.data[0]
        print(data)
        id_record = data['id_record']
        record_info_instance = RecordInfo.objects.get(id_record=id_record)

        record_info_instance.id_lot = None
        record_info_instance.save()

        return JsonResponse({'success': True, 'message': 'Expediente eliminado correctamente'})

    except RecordInfo.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'RecordInfo no existe'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['PUT'])
def update_lot(request):
    try:
        with transaction.atomic():
            data = request.data
            print(data)
            id_lot = data.get('id_lot')
            if id_lot is None:
                return Response({'success': False, 'error': 'Lot ID is required for updating.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                lot_instance = Lot.objects.get(id=id_lot)
            except Lot.DoesNotExist:
                return Response({'success': False, 'error': 'Lot with the provided ID does not exist.'}, status=status.HTTP_404_NOT_FOUND)

            lot_key = data.get('lot_key')
            edited_records = data.get('edited_records')
            if edited_records is not None:
                manage_records_from_lot(lot_key, edited_records)

            if lot_key and lot_key != lot_instance.lot_key:
                new_lot = get_lot_from_key(lot_key)
                if new_lot:
                    records_to_update = RecordInfo.objects.filter(
                        id_lot=lot_instance.pk)
                    records_to_update.update(id_lot=new_lot)
                    lot_instance.status = False
                    lot_instance.save()
                else:
                    return Response({'success': False, 'error': 'Invalid lot_key provided.'}, status=status.HTTP_400_BAD_REQUEST)
            # Remove None values and id_lot from data
            update_data = {
                'date_departure': data.get('date_departure'),
                'date_return': data.get('date_return'),
                'observation': data.get('observation')
            }
            audit = get_user_by_pk(data.get('id_auditor'))
            records_to_update = RecordInfo.objects.filter(
                id_lot=lot_instance.pk, id_auditor=None)
            records_to_update.update(id_auditor=audit, date_assignment_audit=
                data.get('date_assignment_audit'))
            serializer = LotsSerializer(
                lot_instance, data=update_data, partial=True)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'success': True, 'message': 'Lot updated successfully'})

    except Exception as e:
        print(e)
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
