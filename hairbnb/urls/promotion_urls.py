from django.urls import path

from hairbnb.views.salon_services_serializers_views import create_promotion

urlpatterns = [
    path('create_promotion/<int:service_id>/', create_promotion, name="create_promotion"),
]