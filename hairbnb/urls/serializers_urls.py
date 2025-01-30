from django.urls import path

from hairbnb.views.salon_services_serializers_views import get_services_by_coiffeuse, add_service_to_coiffeuse, \
    update_service, delete_service
from hairbnb.views.users_serializers_views import get_coiffeuse_by_uuid, get_client_by_uuid, update_coiffeuse, \
    update_client

urlpatterns = [
    path('get_coiffeuse_by_uuid/<str:uuid>/', get_coiffeuse_by_uuid, name='get_coiffeuse_by_uuid'),
    path('get_client_by_uuid/<str:uuid>/', get_client_by_uuid, name='get_client_by_uuid'),
    path('update_coiffeuse/<str:uuid>/', update_coiffeuse, name='update_coiffeuse'),
    path('update_client/<str:uuid>/', update_client, name='update_client'),
    path('get_services_by_coiffeuse/<int:coiffeuse_id>/', get_services_by_coiffeuse, name='get_services_by_coiffeuse'),
    path('add_service/<int:coiffeuse_id>/', add_service_to_coiffeuse, name='add_service_to_coiffeuse'),
    path('update_service/<int:service_id>/', update_service, name='update_service'),
    path('delete_service/<int:service_id>/', delete_service, name='delete_service'),
]
