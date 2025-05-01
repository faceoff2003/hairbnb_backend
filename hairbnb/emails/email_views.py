# Fichier: views.py (modifié avec des logs détaillés)
import logging
import traceback

from rest_framework.decorators import permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from hairbnb.emails.email_services import EmailService
from hairbnb.emails.emails_serializers import EmailNotificationCreateSerializer, EmailNotificationSerializer
from hairbnb.models import TblUser, TblRendezVous

# Configurer le logger
logger = logging.getLogger(__name__)

class EmailNotificationAPIView(APIView):
    """API pour envoyer des emails de notification depuis l'application mobile."""
    #permission_classes = [IsAuthenticated]

    def post(self, request):
        """Traite les demandes d'envoi d'email."""
        logger.info(f"Requête de notification email reçue: {request.data}")

        # Validation des données d'entrée avec le serializer
        serializer = EmailNotificationCreateSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Données invalides: {serializer.errors}")
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Récupération des données validées
            data = serializer.validated_data
            to_email = data['toEmail']
            template_id = data['templateId']
            rendez_vous_id = data.get('rendezVousId')
            logger.info(f"Données validées: email={to_email}, template={template_id}, rdv_id={rendez_vous_id}")

            # Récupération du destinataire
            try:
                destinataire = TblUser.objects.get(email=to_email)
                logger.info(f"Destinataire trouvé: {destinataire.idTblUser}")
            except TblUser.DoesNotExist:
                logger.error(f"Utilisateur avec email {to_email} non trouvé")
                return Response(
                    {"error": f"Utilisateur avec email {to_email} non trouvé"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Récupération du rendez-vous et du salon si applicable
            rendez_vous = None
            salon = None
            if rendez_vous_id:
                try:
                    rendez_vous = TblRendezVous.objects.get(idRendezVous=rendez_vous_id)
                    salon = rendez_vous.salon
                    logger.info(
                        f"Rendez-vous trouvé: {rendez_vous.idRendezVous}, Salon: {salon.nom_salon if salon else 'None'}")
                except TblRendezVous.DoesNotExist:
                    logger.error(f"Rendez-vous avec ID {rendez_vous_id} non trouvé")
                    return Response(
                        {"error": f"Rendez-vous avec ID {rendez_vous_id} non trouvé"},
                        status=status.HTTP_404_NOT_FOUND
                    )

            # Création de la notification
            logger.info("Tentative de création de la notification...")
            try:
                notification = EmailService.create_notification(
                    destinataire=destinataire,
                    type_email_code=template_id,
                    salon=salon,
                    rendez_vous=rendez_vous
                )
                logger.info(f"Notification créée avec succès: {notification.idTblEmailNotification}")
            except Exception as create_error:
                logger.error(f"Erreur lors de la création de la notification: {str(create_error)}")
                logger.error(traceback.format_exc())
                return Response(
                    {"error": f"Erreur lors de la création de la notification: {str(create_error)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Envoi de l'email
            logger.info("Tentative d'envoi de l'email...")
            try:
                success = EmailService.send_notification(notification.idTblEmailNotification)
                logger.info(f"Résultat de l'envoi: {success}")
            except Exception as send_error:
                logger.error(f"Erreur lors de l'envoi de l'email: {str(send_error)}")
                logger.error(traceback.format_exc())
                return Response(
                    {
                        "error": f"Erreur lors de l'envoi de l'email: {str(send_error)}",
                        "notification": EmailNotificationSerializer(notification).data
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Sérialisation de la réponse
            response_serializer = EmailNotificationSerializer(notification)
            if success:
                logger.info("Email envoyé avec succès")
                return Response(
                    {
                        "message": "Email envoyé avec succès",
                        "notification": response_serializer.data
                    },
                    status=status.HTTP_200_OK
                )
            else:
                logger.error("Échec de l'envoi de l'email")
                return Response(
                    {
                        "error": "Erreur lors de l'envoi de l'email",
                        "notification": response_serializer.data
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except Exception as e:
            logger.error(f"Exception non gérée: {str(e)}")
            logger.error(traceback.format_exc())
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )




# # Fichier: views.py (ajoutez à votre fichier existant)
#
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import IsAuthenticated
#
# from hairbnb.emails.email_services import EmailService
# from hairbnb.emails.emails_serializers import EmailNotificationCreateSerializer, EmailNotificationSerializer
# from hairbnb.models import TblUser, TblRendezVous
#
#
# class EmailNotificationAPIView(APIView):
#     """API pour envoyer des emails de notification depuis l'application mobile."""
#
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request):
#         """Traite les demandes d'envoi d'email."""
#
#         # Validation des données d'entrée avec le serializer
#         serializer = EmailNotificationCreateSerializer(data=request.data)
#         if not serializer.is_valid():
#             return Response(
#                 serializer.errors,
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         try:
#             # Récupération des données validées
#             data = serializer.validated_data
#             to_email = data['toEmail']
#             template_id = data['templateId']
#             rendez_vous_id = data.get('rendezVousId')
#
#             # Récupération du destinataire
#             try:
#                 destinataire = TblUser.objects.get(email=to_email)
#             except TblUser.DoesNotExist:
#                 return Response(
#                     {"error": f"Utilisateur avec email {to_email} non trouvé"},
#                     status=status.HTTP_404_NOT_FOUND
#                 )
#
#             # Récupération du rendez-vous et du salon si applicable
#             rendez_vous = None
#             salon = None
#             if rendez_vous_id:
#                 try:
#                     rendez_vous = TblRendezVous.objects.get(idRendezVous=rendez_vous_id)
#                     salon = rendez_vous.salon
#                 except TblRendezVous.DoesNotExist:
#                     return Response(
#                         {"error": f"Rendez-vous avec ID {rendez_vous_id} non trouvé"},
#                         status=status.HTTP_404_NOT_FOUND
#                     )
#
#             # Création de la notification
#             notification = EmailService.create_notification(
#                 destinataire=destinataire,
#                 type_email_code=template_id,
#                 salon=salon,
#                 rendez_vous=rendez_vous
#             )
#
#             # Envoi de l'email
#             success = EmailService.send_notification(notification.idTblEmailNotification)
#
#             # Sérialisation de la réponse
#             response_serializer = EmailNotificationSerializer(notification)
#
#             if success:
#                 return Response(
#                     {
#                         "message": "Email envoyé avec succès",
#                         "notification": response_serializer.data
#                     },
#                     status=status.HTTP_200_OK
#                 )
#             else:
#                 return Response(
#                     {
#                         "error": "Erreur lors de l'envoi de l'email",
#                         "notification": response_serializer.data
#                     },
#                     status=status.HTTP_500_INTERNAL_SERVER_ERROR
#                 )
#
#         except Exception as e:
#             return Response(
#                 {"error": str(e)},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )