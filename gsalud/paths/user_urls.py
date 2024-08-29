from django.urls import path
from gsalud.views.user_views import getUsers, registerUser, update_user, deleteUser, get_user_by_role

urlpatterns = [
    path('', getUsers),
    path('byrole', get_user_by_role),
    path('update', update_user),
    path('register', registerUser),
    path('remove', deleteUser)
]
