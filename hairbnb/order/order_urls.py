from django.urls import path

from hairbnb.order.order_views import mes_commandes

urlpatterns = [
    path('mes-commandes/<int:idUser>/', mes_commandes, name='mes_commandes'),
]