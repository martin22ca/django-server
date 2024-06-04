from django.urls import path
from gsalud.views.admission import is_authenticated, login

urlpatterns = [
    path('', is_authenticated),
    path('login', login)
]
