from django.urls import path
from gsalud.views.records_views import get_records_db, get_records_assigned, get_records_info, get_user_records
from gsalud.views.records_views import get_records_audit, add_record_to_user, update_record_to_user, save_record_to_user
from gsalud.views.records_views import remove_record_user

urlpatterns = [
    path('', get_records_db),
    path('assigned', get_records_assigned),
    path('audit', get_records_audit),
    path('info', get_records_info),
    path('userInfo', get_user_records),
    path('addrecord', add_record_to_user),
    path('updaterecord', update_record_to_user),
    path('saverecords', save_record_to_user),
    path('removeuserecord', remove_record_user),
]
