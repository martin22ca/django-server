from django.urls import path
from gsalud.views.reports_views import get_report,get_all_reports

urlpatterns = [
    path('', get_all_reports),
    path('report', get_report),
]
