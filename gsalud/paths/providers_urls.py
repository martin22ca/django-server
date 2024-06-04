from django.urls import path
from gsalud.views.providersViews import get_providers,get_priorities

urlpatterns = [
    path('', get_providers),
    path('priorities', get_priorities)
]
