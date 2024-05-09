from django.urls import path
from gsalud.views.recordsViews import getRecordsDB, getRecordsAssigned, getRecordsInfos, getUserRecords, addRecordtoUser, updateRecordtoUser, saveRecordtoUser, removeRecordUser

urlpatterns = [
    path('', getRecordsDB),
    path('assigned', getRecordsAssigned),
    path('info', getRecordsInfos),
    path('userInfo', getUserRecords),
    path('addrecord', addRecordtoUser),
    path('updaterecord', updateRecordtoUser),
    path('saverecords', saveRecordtoUser),
    path('removeuserecord', removeRecordUser),
]
