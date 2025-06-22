from firebase_admin import messaging, db
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class FCMService:
    @staticmethod
    def send_chat_notification(sender_name, message_content, recipient_token, chat_id, sender_id, receiver_id=None):
        """Envoie une notification push pour un nouveau message de chat"""
        try:
            # Valider les paramètres d'entrée
            if not all([sender_name, recipient_token, chat_id, sender_id]):
                logger.error("Paramètres manquants pour l'envoi de notification")
                return False

            # # -------------------------------
            # # 🔒 VALIDATION: S'assurer que le token appartient au bon utilisateur
            # try:
            #     if receiver_id:
            #         token_ref = db.reference(f'fcm_tokens/{receiver_id}')
            #         stored_data = token_ref.get()
            #
            #         if stored_data and isinstance(stored_data, dict) and stored_data.get('token') != recipient_token:
            #             logger.error(f"🔒 SÉCURITÉ: Token ne correspond pas à l'utilisateur {receiver_id}")
            #             return False
            #
            #         logger.info(f"✅ Token validé pour l'utilisateur {receiver_id}")
            # except Exception as validation_error:
            #     logger.error(f"Erreur validation token: {validation_error}")
            #     return False
            # # -------------------------------

            # Tronquer le message si trop long
            truncated_message = message_content[:100] + "..." if len(message_content) > 100 else message_content

            # Construire le message de notification
            message = messaging.Message(

                notification=messaging.Notification(
                    title=f'💬 {sender_name}',
                    body=truncated_message or 'Nouveau message'
                ),
                data={
                    'route': '/messages',
                    'chat_id': str(chat_id),
                    'sender_id': str(sender_id),
                    'receiver_id': str(receiver_id) if receiver_id else '',
                    'type': 'chat_message',
                    'click_action': 'FLUTTER_NOTIFICATION_CLICK'
                },
                token=recipient_token,
                # Configuration Android
                android=messaging.AndroidConfig(
                    notification=messaging.AndroidNotification(
                        icon='@mipmap/ic_launcher',
                        color='#0083FF',
                        sound='default',
                        channel_id='chat_channel'
                    ),
                    priority='high'
                ),
                # Configuration iOS
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            alert=messaging.ApsAlert(
                                title=f'💬 {sender_name}',
                                body=truncated_message or 'Nouveau message'
                            ),
                            sound='default',
                            badge=1
                        )
                    )
                )
            )

            # Envoyer la notification
            response = messaging.send(message)
            logger.info(f'✅ Notification envoyée avec succès: {response}')
            logger.info(f'✅ Data envoyée: chat_id={chat_id}, sender_id={sender_id}')  # Debug
            return True

        except messaging.UnregisteredError:
            logger.error(f'❌ Token FCM invalide ou expiré: {recipient_token[:20]}...')
            # Optionnel: supprimer le token de la base de données
            FCMService._remove_invalid_token(recipient_token)
            return False
        except messaging.SenderIdMismatchError:
            logger.error(f'❌ Erreur Sender ID: {recipient_token[:20]}...')
            return False
        except Exception as e:
            logger.error(f'❌ Erreur envoi notification: {e}')
            return False

    @staticmethod
    def save_fcm_token(user_id, token):
        """Sauvegarde le token FCM d'un utilisateur"""
        try:
            if not user_id or not token:
                logger.error("User ID ou token manquant")
                return False

            ref = db.reference(f'fcm_tokens/{user_id}')
            ref.set({
                'token': token,
                'timestamp': int(datetime.now().timestamp() * 1000),
                'active': True
            })
            logger.info(f'✅ Token FCM sauvegardé pour {user_id}')
            return True
        except Exception as e:
            logger.error(f'❌ Erreur sauvegarde token: {e}')
            return False

    @staticmethod
    def _remove_invalid_token(token):
        """Supprime un token invalide de la base de données"""
        try:
            logger.info(f"Token à supprimer: {token[:20]}...")
        except Exception as e:
            logger.error(f"Erreur suppression token: {e}")













# from firebase_admin import messaging, db
# import logging
# from datetime import datetime
#
# logger = logging.getLogger(__name__)
#
#
# class FCMService:
#     @staticmethod
#     def send_chat_notification(sender_name, message_content, recipient_token, chat_id, sender_id, receiver_id=None):
#         """Envoie une notification push pour un nouveau message de chat"""
#         try:
#             # Valider les paramètres d'entrée
#             if not all([sender_name, recipient_token, chat_id, sender_id]):
#                 logger.error("Paramètres manquants pour l'envoi de notification")
#                 return False
#
#             # Tronquer le message si trop long
#             truncated_message = message_content[:100] + "..." if len(message_content) > 100 else message_content
#
#             # Construire le message de notification
#             message = messaging.Message(
#
#                 notification=messaging.Notification(
#                     title=f'💬 {sender_name}',
#                     body=truncated_message or 'Nouveau message'
#                 ),
#                 data={
#                     'route': '/messages',
#                     'chat_id': str(chat_id),
#                     'sender_id': str(sender_id),
#                     'receiver_id': str(receiver_id) if receiver_id else '',
#                     'type': 'chat_message',
#                     'click_action': 'FLUTTER_NOTIFICATION_CLICK'
#                 },
#                 token=recipient_token,
#                 # Configuration Android
#                 android=messaging.AndroidConfig(
#                     notification=messaging.AndroidNotification(
#                         icon='@mipmap/ic_launcher',
#                         color='#0083FF',
#                         sound='default',
#                         channel_id='chat_channel'
#                     ),
#                     priority='high'
#                 ),
#                 # Configuration iOS
#                 apns=messaging.APNSConfig(
#                     payload=messaging.APNSPayload(
#                         aps=messaging.Aps(
#                             alert=messaging.ApsAlert(
#                                 title=f'💬 {sender_name}',
#                                 body=truncated_message or 'Nouveau message'
#                             ),
#                             sound='default',
#                             badge=1
#                         )
#                     )
#                 )
#             )
#
#             # Envoyer la notification
#             response = messaging.send(message)
#             logger.info(f'✅ Notification envoyée avec succès: {response}')
#             logger.info(f'✅ Data envoyée: chat_id={chat_id}, sender_id={sender_id}')  # Debug
#             return True
#
#         except messaging.UnregisteredError:
#             logger.error(f'❌ Token FCM invalide ou expiré: {recipient_token[:20]}...')
#             # Optionnel: supprimer le token de la base de données
#             FCMService._remove_invalid_token(recipient_token)
#             return False
#         except messaging.SenderIdMismatchError:
#             logger.error(f'❌ Erreur Sender ID: {recipient_token[:20]}...')
#             return False
#         except Exception as e:
#             logger.error(f'❌ Erreur envoi notification: {e}')
#             return False
#
#     @staticmethod
#     def save_fcm_token(user_id, token):
#         """Sauvegarde le token FCM d'un utilisateur"""
#         try:
#             if not user_id or not token:
#                 logger.error("User ID ou token manquant")
#                 return False
#
#             ref = db.reference(f'fcm_tokens/{user_id}')
#             ref.set({
#                 'token': token,
#                 'timestamp': int(datetime.now().timestamp() * 1000),
#                 'active': True
#             })
#             logger.info(f'✅ Token FCM sauvegardé pour {user_id}')
#             return True
#         except Exception as e:
#             logger.error(f'❌ Erreur sauvegarde token: {e}')
#             return False
#
#     @staticmethod
#     def _remove_invalid_token(token):
#         """Supprime un token invalide de la base de données"""
#         try:
#             logger.info(f"Token à supprimer: {token[:20]}...")
#         except Exception as e:
#             logger.error(f"Erreur suppression token: {e}")