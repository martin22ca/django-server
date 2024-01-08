from django.urls import path
from gsalud.views.admission import is_auth, login

urlpatterns = [
    path('', is_auth),
    path('login', login)
]
