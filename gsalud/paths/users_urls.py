from django.urls import path
from gsalud.views.userViews import getUsers, registerUser, updateUser, deleteUser, getUsersByRole, updateUserRoles

urlpatterns = [
    path('', getUsers),
    path('byrole', getUsersByRole),
    path('update', updateUser),
    path('updaterole', updateUserRoles),
    path('register', registerUser),
    path('remove', deleteUser)
]
