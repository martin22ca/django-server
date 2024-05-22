from django.urls import path
from gsalud.views.rolesViews import getRoles, updateRole

urlpatterns = [
    path('', getRoles),
    path('update', updateRole)
]
