from django.urls import path

from .chat_views import send_message_notification, save_fcm_token

urlpatterns = [
# Ajouter ces URLs à tes patterns existants :
    path('fcm/save-token/', save_fcm_token, name='save_fcm_token'),
    path('send_message_notification/', send_message_notification, name='send_message_notification'),
    ]