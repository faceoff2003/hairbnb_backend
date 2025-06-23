# hairbnb/revenus/views.py
import traceback

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from decorators.decorators import firebase_authenticated, is_owner_coiffeuse
from .revenus_serializers import (
    RevenusRequestSerializer,
    RevenusCoiffeuseSerializer,
    RevenusErrorSerializer
)
from .revenus_business_logic import RevenusService


@api_view(['GET'])
@firebase_authenticated
@is_owner_coiffeuse
def get_revenus_coiffeuse(request):
    """
    Vue pour récupérer les revenus d'une coiffeuse selon différentes périodes.
    """

    try:  # ← AJOUTEZ ÇA
        # Validation des paramètres d'entrée
        serializer = RevenusRequestSerializer(data=request.GET)

        if not serializer.is_valid():
            error_serializer = RevenusErrorSerializer({
                'success': False,
                'error': f"Paramètres invalides: {serializer.errors}"
            })
            return Response(error_serializer.data, status=status.HTTP_400_BAD_REQUEST)

        # Extraction des paramètres validés
        validated_data = serializer.validated_data
        periode = validated_data.get('periode', 'mois')
        date_debut = validated_data.get('date_debut')
        date_fin = validated_data.get('date_fin')
        salon_id = validated_data.get('salon_id')

        # Récupération de l'ID de la coiffeuse connectée
        coiffeuse_id = request.user.idTblUser

        # Appel du service métier
        result = RevenusService.get_revenus_coiffeuse(
            coiffeuse_id=coiffeuse_id,
            periode=periode,
            date_debut=date_debut,
            date_fin=date_fin,
            salon_id=salon_id
        )

        # Traitement de la réponse
        if result.get('success'):
            # Succès : sérialisation des données de revenus
            revenus_serializer = RevenusCoiffeuseSerializer(result)
            return Response(revenus_serializer.data, status=status.HTTP_200_OK)
        else:
            # Erreur : sérialisation du message d'erreur
            error_serializer = RevenusErrorSerializer(result)
            return Response(error_serializer.data, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        # Capture de toutes les erreurs avec détail
        error_detail = traceback.format_exc()
        return Response({
            'success': False,
            'error': f'Erreur serveur: {str(e)}',
            'detail': error_detail
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)








# # # hairbnb/revenus/views.py
# #
# # from rest_framework.decorators import api_view
# # from rest_framework.response import Response
# # from rest_framework import status
# # import traceback
# #
# # from decorators.decorators import firebase_authenticated, is_owner_coiffeuse
# # from .revenus_serializers import (
# #     RevenusRequestSerializer,
# #     RevenusCoiffeuseSerializer,
# #     RevenusErrorSerializer
# # )
# # from .revenus_business_logic import RevenusService
# #
# #
# # @api_view(['GET'])
# # @firebase_authenticated
# # @is_owner_coiffeuse
# # def get_revenus_coiffeuse(request):
# #     """
# #     Vue pour récupérer les revenus d'une coiffeuse selon différentes périodes.
# #     """
# #
# #     try:
# #         # Validation des paramètres d'entrée
# #         serializer = RevenusRequestSerializer(data=request.GET)
# #
# #         if not serializer.is_valid():
# #             error_serializer = RevenusErrorSerializer({
# #                 'success': False,
# #                 'error': f"Paramètres invalides: {serializer.errors}"
# #             })
# #             return Response(error_serializer.data, status=status.HTTP_400_BAD_REQUEST)
# #
# #         # Extraction des paramètres validés
# #         validated_data = serializer.validated_data
# #         periode = validated_data.get('periode', 'mois')
# #         date_debut = validated_data.get('date_debut')
# #         date_fin = validated_data.get('date_fin')
# #         salon_id = validated_data.get('salon_id')
# #
# #         # Récupération de l'ID de la coiffeuse connectée
# #         coiffeuse_id = request.user.id
# #
# #         # Appel du service métier
# #         result = RevenusService.get_revenus_coiffeuse(
# #             coiffeuse_id=coiffeuse_id,
# #             periode=periode,
# #             date_debut=date_debut,
# #             date_fin=date_fin,
# #             salon_id=salon_id
# #         )
# #
# #         # Traitement de la réponse
# #         if result.get('success'):
# #             # Succès : sérialisation des données de revenus
# #             revenus_serializer = RevenusCoiffeuseSerializer(result)
# #             return Response(revenus_serializer.data, status=status.HTTP_200_OK)
# #         else:
# #             # Erreur : sérialisation du message d'erreur
# #             error_serializer = RevenusErrorSerializer(result)
# #             return Response(error_serializer.data, status=status.HTTP_400_BAD_REQUEST)
# #
# #     except Exception as e:
# #         # Capture de toutes les erreurs avec détail
# #         error_detail = traceback.format_exc()
# #         return Response({
# #             'success': False,
# #             'error': f'Erreur serveur: {str(e)}',
# #             'detail': error_detail
# #         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# #
# #
# #
#
#
#
#
#
#
#
#
# # hairbnb/revenus/views.py
#
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from rest_framework import status
#
# from decorators.decorators import firebase_authenticated, is_owner_coiffeuse
# from .revenus_serializers import (
#     RevenusRequestSerializer,
#     RevenusCoiffeuseSerializer,
#     RevenusErrorSerializer
# )
# from .revenus_business_logic import RevenusService
#
#
# @api_view(['GET'])
# @firebase_authenticated
# @is_owner_coiffeuse
# def get_revenus_coiffeuse(request):
#     """
#     Vue pour récupérer les revenus d'une coiffeuse selon différentes périodes.
#
#     Paramètres GET acceptés:
#     - periode: "jour", "semaine", "mois", "annee", "custom" (défaut: "mois")
#     - date_debut: Format YYYY-MM-DD (requis si periode="custom")
#     - date_fin: Format YYYY-MM-DD (requis si periode="custom")
#     - salon_id: ID du salon (optionnel)
#
#     Retourne les revenus détaillés avec résumé et statistiques.
#     """
#
#     # Validation des paramètres d'entrée
#     serializer = RevenusRequestSerializer(data=request.GET)
#
#     if not serializer.is_valid():
#         error_serializer = RevenusErrorSerializer({
#             'success': False,
#             'error': f"Paramètres invalides: {serializer.errors}"
#         })
#         return Response(error_serializer.data, status=status.HTTP_400_BAD_REQUEST)
#
#     # Extraction des paramètres validés
#     validated_data = serializer.validated_data
#     periode = validated_data.get('periode', 'mois')
#     date_debut = validated_data.get('date_debut')
#     date_fin = validated_data.get('date_fin')
#     salon_id = validated_data.get('salon_id')
#
#     # Récupération de l'ID de la coiffeuse connectée
#     #coiffeuse_id = request.user.id
#
#     coiffeuse_id = request.user.idTblUser
#
#     # Appel du service métier
#     result = RevenusService.get_revenus_coiffeuse(
#         coiffeuse_id=coiffeuse_id,
#         periode=periode,
#         date_debut=date_debut,
#         date_fin=date_fin,
#         salon_id=salon_id
#     )
#
#     # Traitement de la réponse
#     if result.get('success'):
#         # Succès : sérialisation des données de revenus
#         revenus_serializer = RevenusCoiffeuseSerializer(result)
#         return Response(revenus_serializer.data, status=status.HTTP_200_OK)
#     else:
#         # Erreur : sérialisation du message d'erreur
#         error_serializer = RevenusErrorSerializer(result)
#         return Response(error_serializer.data, status=status.HTTP_400_BAD_REQUEST)
#
