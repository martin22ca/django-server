from django.http import JsonResponse
from rest_framework.decorators import api_view
from gsalud.serializers import FeedbackSerializer
from rest_framework.response import Response
from rest_framework import status
from gsalud.models import Feedback
from gsalud.services.ORM_filters import apply_filters
from datetime import datetime


@api_view(['GET'])
def get_feeback(request):
    try:
        base_queryset = Feedback.objects.all().values()
        return apply_filters(request, base_queryset)

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})

@api_view(['POST'])
def register_feedback(request):
    try:
        data = request.data
        data['date_report'] = datetime.now().date()
        serializer = FeedbackSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'message': 'Reportado!'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})
    

@api_view(['PUT'])
def update_feedback(request):
    """
    Update an existing feedback's details in a Django application.

    Args:
        request: Django Request object containing user update data.

    Returns:
        JSON response indicating success or failure of the update operation.
    """
    try:
        data = request.data
        id_feedback = data.get('id_feedback')

        if not id_feedback:
            return Response({'success': False, 'error': 'Feedback ID is required for updating.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            feedback_instance = Feedback.objects.get(pk=id_feedback)
        except Feedback.DoesNotExist:
            return Response({'success': False, 'error': 'Feedback not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = FeedbackSerializer(
            instance=feedback_instance, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        print(e)
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
def remove_feedback(request):
    try:
        data = request.data
        id_feedback = data.get('id_feedback')

        if id_feedback is None:
            return Response({'success': False, 'error': 'Feedback ID is required for Deletion.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user exists
        try:
            feedback_instance = Feedback.objects.get(pk=id_feedback)
        except Feedback.DoesNotExist:
            return Response({'success': False, 'error': 'Feedback no Existe.'}, status=status.HTTP_404_NOT_FOUND)

        # Delete the user
        feedback_instance.delete()

        return Response({'success': True}, status=status.HTTP_200_OK)

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})