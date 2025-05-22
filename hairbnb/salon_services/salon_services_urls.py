from django.urls import path

from hairbnb.salon_services.salon_services_views import add_service_to_salon

urlpatterns = [
    path('add_service_to_salon/', add_service_to_salon, name='add_service_to_salon'),

]