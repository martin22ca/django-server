from django.urls import path
from gsalud.views.lots import getLots

urlpatterns = [
    path('', getLots)
]
