from django.urls import path

from hairbnb.payment.paiement_views import create_payment_intent

urlpatterns = [
    path('paiement/create_payment_intent/', create_payment_intent, name='create_payment_intent'),

]