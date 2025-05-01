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
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from hairbnb import views, urls

from hairbnb.views import create_user_profile, home, check_user_profile, ServicesListView, add_or_update_service, \
    coiffeuse_services, list_coiffeuses, get_user_profile, UpdateUserProfileView, add_service_to_salon
from hairbnb.views.users_serializers_views import get_coiffeuse_by_uuid
from hairbnb_backend import settings

urlpatterns = [
    #path('', home, name='home'),  # Route pour la page d'accueil
    path('ghost/', admin.site.urls),
    path('api/create-profile/', create_user_profile, name='create_user_profile'),
    path('api/check-user-profile/', views.views.check_user_profile, name='check_user_profile'),
    path('api/create_salon/', views.views.create_salon, name='create_salon'),
    path('api/services/', ServicesListView, name='services-list'),
    #path('api/add_or_update_service/', add_or_update_service, name='add_or_update_service'),
    path('api/add_or_update_service/<int:service_id>/', views.add_or_update_service, name='add_or_update_service'),
    path('api/add_or_update_service/', views.views.add_or_update_service, name='add_or_update_service_without_id'),
    path('api/coiffeuse_services/<int:coiffeuse_id>/', coiffeuse_services, name='coiffeuse_services'),
    path('api/list_coiffeuses/', list_coiffeuses, name='list_coiffeuses'),
    path('api/get_user_profile/<str:userUuid>/', views.views.get_user_profile, name='get_user_profile'),
    path('api/update_user_profile/<str:uuid>/', UpdateUserProfileView.as_view(), name='update_user_profile'),
    path('api/get_id_and_type_from_uuid/<str:uuid>/', views.views.get_id_and_type_from_uuid, name='get_id_and_type_from_uuid'),
    path('api/add_service_to_salon/', add_service_to_salon, name='add_service_to_salon'),
    path('api/', include('hairbnb.urls.serializers_urls')),  # Inclure les routes de serializers_urls.py
    path('api/', include('hairbnb.promotion.promotion_urls')),  # Inclure les routes de promotion_urls.py
    path('api/', include('hairbnb.publicSalonDetail.urls')),  # Inclure les routes de publicSalonDetail_urls.py
    path('api/', include('hairbnb.gallery.gallery_urls')),  # Inclure les routes de gallery_urls.py
    path('api/', include('hairbnb.favorites.favorites_urls')),  # Inclure les routes de favorites_urls.py
    path('api/', include('hairbnb.currentUser.currentUser_urls')),  # Inclure les routes de currentUser_urls.py
    path('api/', include('hairbnb.card.card_urls')),  # Inclure les routes de card_urls.py
    path('api/', include('hairbnb.payment.payment_urls')),  # Inclure les routes de payment_urls.py
    path('api/', include('hairbnb.order.order_urls')),  # Inclure les routes de order_urls.py
    path('api/', include('hairbnb.emails.email_urls')),  # Inclure les routes de email_urls.py
]
