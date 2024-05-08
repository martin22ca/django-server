from django.urls import path
from gsalud.views.rolesViews import getRoles

urlpatterns = [
    path('', getRoles),
]
