"""
URL configuration for hairbnb_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path

from hairbnb import views
from hairbnb.views import create_user_profile, home, check_user_profile

urlpatterns = [
    path('', home, name='home'),  # Route pour la page d'accueil
    path('admin/', admin.site.urls),
    path('api/create-profile/', create_user_profile, name='create_user_profile'),
    path('api/check-user-profile/', views.check_user_profile, name='check_user_profile'),
]
