from django.urls import path
from gsalud.views.providersViews import getProviders

urlpatterns = [
    path('', getProviders)
]
