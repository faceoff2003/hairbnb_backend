from django.urls import path

from hairbnb.views.cart_serialisers_views import get_cart, add_to_cart, remove_from_cart, clear_cart
from hairbnb.views.geolocation_serializers_views import coiffeuses_proches
from hairbnb.views.paiement_serializers_views import create_payment_intent
from hairbnb.views.rdvs_serializers_views import create_rendez_vous
from hairbnb.views.salon_services_serializers_views import get_services_by_coiffeuse, \
    update_service, delete_service, add_service_to_coiffeuse, create_promotion
from hairbnb.views.users_serializers_views import get_coiffeuse_by_uuid, get_client_by_uuid, update_coiffeuse, \
    update_client, get_current_user, get_coiffeuses_info

urlpatterns = [
    path('get_coiffeuse_by_uuid/<str:uuid>/', get_coiffeuse_by_uuid, name='get_coiffeuse_by_uuid'),
    path('get_client_by_uuid/<str:uuid>/', get_client_by_uuid, name='get_client_by_uuid'),
    path('update_coiffeuse/<str:uuid>/', update_coiffeuse, name='update_coiffeuse'),
    path('update_client/<str:uuid>/', update_client, name='update_client'),
    path('get_services_by_coiffeuse/<int:coiffeuse_id>/', get_services_by_coiffeuse, name='get_services_by_coiffeuse'),
    path('add_service_to_coiffeuse/<int:coiffeuse_id>/', add_service_to_coiffeuse, name='add_service_to_coiffeuse'),
    path('update_service/<int:service_id>/', update_service, name='update_service'),
    path('delete_service/<int:service_id>/', delete_service, name='delete_service'),
    path('coiffeuses_proches/', coiffeuses_proches, name='coiffeuses_proches'),
    path('get_current_user/<str:uuid>/', get_current_user, name='get_current_user'),
    path('get_coiffeuses_info/', get_coiffeuses_info, name="get_coiffeuses_info"),
    path('get_cart/<int:user_id>/', get_cart, name="get_cart" ),
    path('add_to_cart/', add_to_cart, name="add_to_cart"),
    path('remove_from_cart/', remove_from_cart, name="remove_from_cart"),
    path('clear_cart/', clear_cart, name="clear_cart"),
    path('create_promotion/<int:service_id>/', create_promotion, name="create_promotion"),
    path('create_rendez_vous/', create_rendez_vous, name="create_rendez_vous"),
    path("create_payment/", create_payment_intent, name="create_payment"),

]
