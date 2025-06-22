from django.urls import path
from .admin_views import list_users, manage_user

urlpatterns = [
    path('gestion-utilisateurs/', list_users, name='admin_list_users'),
    path('gestion-utilisateurs/action/', manage_user, name='admin_manage_user'),
]