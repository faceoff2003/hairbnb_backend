# hairbnb/revenus/urls.py

from django.urls import path

from hairbnb.revenus.revenus_views import get_revenus_coiffeuse

urlpatterns = [
    path('revenus_coiffeuse/', get_revenus_coiffeuse, name='get_revenus_coiffeuse'),
]