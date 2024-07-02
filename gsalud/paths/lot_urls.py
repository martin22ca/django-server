from django.urls import path
from gsalud.views.lotsViews import getLots, popRecordFromLot,updateLot

urlpatterns = [
    path('', getLots),
    path('removefromlot', popRecordFromLot),
    path('update', updateLot)
]
