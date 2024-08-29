from django.urls import path
from gsalud.views.lots_views import get_lots, pop_record_from_lot,update_lot

urlpatterns = [
    path('', get_lots),
    path('removefromlot', pop_record_from_lot),
    path('update', update_lot)
]
