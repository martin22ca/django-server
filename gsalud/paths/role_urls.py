from django.urls import path
from gsalud.views.roles_views import getRoles, updateRole, get_role_user

urlpatterns = [
    path('', getRoles),
    path('getrole', get_role_user),
    path('update', updateRole)
]
