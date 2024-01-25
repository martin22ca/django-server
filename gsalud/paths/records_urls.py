from django.urls import path
from gsalud.views.recordsViews import getRecords,getRecordsInfos,getUserRecords,addRecordtoUser,updateRecordtoUser,saveRecordtoUser,removeRecordUser

urlpatterns = [
    path('', getRecords),
    path('info', getRecordsInfos),
    path('userInfo', getUserRecords),
    path('addrecord', addRecordtoUser),
    path('updaterecord', updateRecordtoUser),
    path('saverecords', saveRecordtoUser),
    path('removeuserecord', removeRecordUser),
]