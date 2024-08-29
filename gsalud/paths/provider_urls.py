from django.urls import path
from gsalud.views.providers_views import get_providers, register_porvider, update_porvider

urlpatterns = [
    path('', get_providers),
    path('update', update_porvider)
]
