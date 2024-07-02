from django.urls import path
from gsalud.views.records_views import get_records_db, get_records_assigned, get_records_info, get_user_records
from gsalud.views.records_views import get_records_audit, addRecordtoUser, updateRecordtoUser, saveRecordtoUser
from gsalud.views.records_views import removeRecordUser

urlpatterns = [
    path('', get_records_db),
    path('assigned', get_records_assigned),
    path('audit', get_records_audit),
    path('info', get_records_info),
    path('userInfo', get_user_records),
    path('addrecord', addRecordtoUser),
    path('updaterecord', updateRecordtoUser),
    path('saverecords', saveRecordtoUser),
    path('removeuserecord', removeRecordUser),
]
