
from django.http import JsonResponse
from rest_framework.decorators import api_view
from gsalud.services.reports_service import reports
from gsalud.services.ORM_filters import execute_query_with_filters
from gsalud.models import Report
from gsalud.serializers import ReportsSerializer


@api_view(['GET'])
def get_all_reports(request):
    try:
        reports = Report.objects.filter()
        serializer = ReportsSerializer(reports, many=True)
        return JsonResponse({'success': True, 'data': serializer.data})
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['GET'])
def get_report(request):
    try:
        id_report = request.GET.dict()['id_report']
        print(request.GET.dict())
        base_queryset = reports.get(id_report)()
        data = execute_query_with_filters(request, base_queryset)
        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'error': str(e)})
