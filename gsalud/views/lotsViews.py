from django.http import JsonResponse
from gsalud.services.filterTable import get_table_data
from gsalud.models import Lot
from gsalud.serializers import LotsSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from gsalud.models import RecordInfo


@api_view(['GET'])
def getLots(request):
    try:
        base_query = '''select l.*,MAX(u.user_name) AS user_name,COUNT(DISTINCT ri.id) as total_records from lots l
                        left join users u ON l.id_user = u.id  
                        left join records_info ri ON l.id  = ri.id_lot 
                        '''
        return get_table_data(request, base_query, group_by='l.id')

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['DELETE'])
def popRecordFromLot(request):
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
def updateLot(request):
    try:
        data = request.data
        # Using get() to avoid KeyError if 'id_lot' is not in data
        id_lot = data.get('id_lot')

        if id_lot is None:
            return Response({'success': False, 'error': 'Lot ID is required for updating.'}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the Lot instance to update
        lot_instance = Lot.objects.get(id=id_lot)
        data = {key: value for key, value in data.items() if value is not None}
        data.pop('id_lot')

        if "id_user" not in data:
            data['id_user'] = None

        serializer = LotsSerializer(lot_instance, data=data, partial=True)

        # Validate the data
        if serializer.is_valid():
            # Save the validated data (i.e., update the instance)
            serializer.save()
            return Response({'success': True, 'message': 'Lot updated successfully'})
        else:
            return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    except Lot.DoesNotExist:
        return Response({'success': False, 'error': 'Lot with the provided ID does not exist.'}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
