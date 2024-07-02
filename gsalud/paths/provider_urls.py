from django.urls import path
from gsalud.views.providers_views import get_providers

urlpatterns = [
    path('', get_providers),
]
