from rest_framework.decorators import api_view
from rest_framework.response import Response
from decorators.decorators import firebase_authenticated
from firebase_auth_services.firebase_notifications.fcm_service import FCMService
from firebase_admin import db
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@firebase_authenticated
def save_fcm_token(request):
    """Endpoint pour sauvegarder le token FCM d'un utilisateur"""
    try:
        data = request.data
        user_id = str(request.user.idTblUser)
        token = data.get('token')

        if not token:
            return Response({'error': 'token requis'}, status=400)

        success = FCMService.save_fcm_token(user_id, token)

        if success:
            return Response({'message': 'Token sauvegardé'})
        else:
            return Response({'error': 'Erreur sauvegarde'}, status=500)

    except Exception as e:
        logger.error(f"Erreur save_fcm_token: {str(e)}")
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@firebase_authenticated
def send_message_notification(request):
    """Endpoint pour envoyer une notification de nouveau message"""
    try:
        data = request.data
        chat_id = data.get('chat_id')
        sender_id = str(request.user.idTblUser)
        sender_name = data.get('sender_name', f"User {sender_id}")
        message_content = data.get('message_content')

        # S'assurer qu'on utilise l'UUID du destinataire, pas l'ID numérique
        recipient_id = data.get('recipient_id')
        if not recipient_id:
            return Response({'error': 'recipient_id requis'}, status=400)

        # Validation que c'est bien un UUID (format attendu)
        if len(str(recipient_id)) < 10:  # Les UUIDs sont plus longs
            logger.error(f"recipient_id semble être un ID numérique au lieu d'un UUID: {recipient_id}")
            return Response({'error': 'recipient_id doit être un UUID'}, status=400)

        # Log des données reçues
        logger.info(f"Données reçues: chat_id={chat_id}, sender_id={sender_id}, recipient_id={recipient_id}")

        if not all([chat_id, message_content, recipient_id]):
            logger.error("Paramètres manquants")
            return Response({
                'error': 'chat_id, message_content et recipient_id requis'
            }, status=400)

        # Récupérer le token FCM du destinataire avec vérification
        try:
            # 🔧 CORRECTION: Utiliser la bonne URL de la database
            ref = db.reference(f'fcm_tokens/{recipient_id}')
            token_data = ref.get()

            logger.info(f"Token data récupéré pour {recipient_id}: {token_data}")

            if not token_data or not isinstance(token_data, dict) or not token_data.get('token'):
                logger.warning(f"Token non trouvé pour {recipient_id}")
                return Response({
                    'error': 'Token destinataire non trouvé'
                }, status=404)

        except Exception as db_error:
            logger.error(f"Erreur Firebase DB: {db_error}")
            return Response({
                'error': f'Erreur accès base de données: {str(db_error)}'
            }, status=500)

        recipient_token = token_data['token']
        logger.info(f"Token destinataire trouvé: {recipient_token[:20]}...")

        # #------------------------------------------------------------------------------
        #
        # # 🔒 SÉCURITÉ: Vérifier que l'expéditeur n'envoie pas à lui-même
        # if sender_id == recipient_id:
        #     logger.warning(f"Tentative d'envoi de message à soi-même: {sender_id}")
        #     return Response({'error': 'Impossible d\'envoyer un message à soi-même'}, status=400)
        #
        # # 🔒 LOG de sécurité pour tracer les envois
        # logger.info(f"🔒 ENVOI NOTIFICATION: {sender_id} → {recipient_id} (token: {recipient_token[:20]}...)")
        #
        # #------------------------------------------------------------------------------

        # Envoyer la notification
        success = FCMService.send_chat_notification(
            sender_name,
            message_content,
            recipient_token,
            chat_id,
            sender_id
        )

        if success:
            logger.info("Notification envoyée avec succès")
            return Response({'status': 'success', 'message': 'Notification envoyée'})
        else:
            logger.error("Échec envoi notification")
            return Response({'error': 'Erreur envoi notification'}, status=500)

    except Exception as e:
        logger.error(f"Erreur send_message_notification: {str(e)}")
        return Response({'error': str(e)}, status=500)