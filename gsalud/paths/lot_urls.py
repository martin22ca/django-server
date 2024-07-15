from django.urls import path
from gsalud.views.lots_views import getLots, popRecordFromLot,update_lot

urlpatterns = [
    path('', getLots),
    path('removefromlot', popRecordFromLot),
    path('update', update_lot)
]
