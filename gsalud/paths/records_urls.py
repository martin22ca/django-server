from django.urls import path
from gsalud.views.recordsViews import getRecords,getRecordsInfos,getUserRecords,addRecordtoUser,updateRecordtoUser,saveRecordtoUser

urlpatterns = [
    path('', getRecords),
    path('info', getRecordsInfos),
    path('userInfo', getUserRecords),
    path('addrecord', addRecordtoUser),
    path('updaterecord', updateRecordtoUser),
    path('saverecords', saveRecordtoUser)
]