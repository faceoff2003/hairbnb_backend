from django.urls import path

from hairbnb.promotion.views.delete_promotion import delete_promotion
from hairbnb.promotion.views.get_promotions_for_service import get_promotions_for_service
from hairbnb.views.salon_services_serializers_views import create_promotion

urlpatterns = [
    path('create_promotion/<int:service_id>/', create_promotion, name="create_promotion"),
    path('get_promotions_for_service/<int:service_id>/', get_promotions_for_service, name="get_promotions_for_service"),
    path('delete_promotion/<int:promotion_id>/', delete_promotion, name='delete_promotion'),
]