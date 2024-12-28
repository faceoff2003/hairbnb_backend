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
from django.conf.urls.static import static
from django.urls import path
from hairbnb import views
from hairbnb.views import create_user_profile, home, check_user_profile, ServicesListView, add_or_update_service, \
    coiffeuse_services, list_coiffeuses
from django.conf import settings

urlpatterns = [
    path('', home, name='home'),  # Route pour la page d'accueil
    path('admin/', admin.site.urls),
    path('api/create-profile/', create_user_profile, name='create_user_profile'),
    path('api/check-user-profile/', views.check_user_profile, name='check_user_profile'),
    path('api/create_salon/', views.create_salon, name='create_salon'),
    path('api/services/', ServicesListView, name='services-list'),
    #path('api/add_or_update_service/', add_or_update_service, name='add_or_update_service'),
    path('api/add_or_update_service/<int:service_id>/', views.add_or_update_service, name='add_or_update_service'),
    path('api/add_or_update_service/', views.add_or_update_service, name='add_or_update_service_without_id'),
    path('api/coiffeuse_services/<int:coiffeuse_id>/', coiffeuse_services, name='coiffeuse_services'),
    path('api/list_coiffeuses/', list_coiffeuses, name='list_coiffeuses'),
]#+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Ajoutez les URL pour servir les fichiers médias en mode développement
if settings.DEBUG:  # Cette ligne s'assure que cela fonctionne uniquement en mode développement
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
