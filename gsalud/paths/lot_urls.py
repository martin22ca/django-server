from django.urls import path
from gsalud.views.lots_views import get_lots, popRecordFromLot,update_lot

urlpatterns = [
    path('', get_lots),
    path('removefromlot', popRecordFromLot),
    path('update', update_lot)
]
