from django.urls import path
from gsalud.views.user_views import getUsers, registerUser, update_user, deleteUser, getUsersByRole, updateUserRoles

urlpatterns = [
    path('', getUsers),
    path('byrole', getUsersByRole),
    path('update', update_user),
    path('updaterole', updateUserRoles),
    path('register', registerUser),
    path('remove', deleteUser)
]
