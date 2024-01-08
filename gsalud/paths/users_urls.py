from django.urls import path
from gsalud.views.userViews import getUsers,registerUser

urlpatterns = [
    path('', getUsers),
    path('register', registerUser)
]