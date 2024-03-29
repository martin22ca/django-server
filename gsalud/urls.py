"""
URL configuration for gsalud project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admission/', include('gsalud.paths.admission_urls')),
    path('records/', include('gsalud.paths.records_urls')),
    path('config/', include('gsalud.paths.config_urls')),
    path('users/', include('gsalud.paths.users_urls')),
    path('providers/', include('gsalud.paths.providers_urls')),
    path('lots/', include('gsalud.paths.lots_urls')),
    path('roles/', include('gsalud.paths.roles_urls')),
]
