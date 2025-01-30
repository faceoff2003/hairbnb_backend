from django.urls import path
from hairbnb.views.users_serializers_views import get_coiffeuse_by_uuid, get_client_by_uuid, update_coiffeuse, \
    update_client

urlpatterns = [
    path('get_coiffeuse_by_uuid/<str:uuid>/', get_coiffeuse_by_uuid, name='get_coiffeuse_by_uuid'),
    path('get_client_by_uuid/<str:uuid>/', get_client_by_uuid, name='get_client_by_uuid'),
    path('update_coiffeuse/<str:uuid>/', update_coiffeuse, name='update_coiffeuse'),
    path('update_client/<str:uuid>/', update_client, name='update_client'),
]
