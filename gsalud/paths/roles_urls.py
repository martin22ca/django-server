from django.urls import path
from gsalud.views.rolesViews import getUsersWithRoles

urlpatterns = [
    path('useroles', getUsersWithRoles),
]
