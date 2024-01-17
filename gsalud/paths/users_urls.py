from django.urls import path
from gsalud.views.userViews import getUsers, registerUser, updateUser, deleteUser

urlpatterns = [
    path('', getUsers),
    path('update', updateUser),
    path('register', registerUser),
    path('remove', deleteUser)
]
