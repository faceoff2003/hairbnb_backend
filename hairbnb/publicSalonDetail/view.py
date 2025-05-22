from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SalonDetailSerializer
from ..models import TblSalon, TblCoiffeuseSalon
import logging

# Configurer le logger
logger = logging.getLogger(__name__)


class PublicSalonDetailsView(APIView):
    """
    Vue API pour obtenir les détails publics d'un salon
    """

    def get(self, request, salon_id=None):
        try:
            # Si salon_id est fourni, récupérer ce salon spécifique
            if salon_id:
                salon = TblSalon.objects.get(idTblSalon=salon_id)
                serializer = SalonDetailSerializer(salon, context={'request': request})
                return Response(serializer.data)
            # Sinon, récupérer tous les salons avec pagination
            else:
                # Paramètres de pagination
                limit = int(request.query_params.get('limit', 10))
                offset = int(request.query_params.get('offset', 0))

                # Filtres optionnels
                coiffeuse_id = request.query_params.get('coiffeuse_id')
                est_proprietaire = request.query_params.get('est_proprietaire') == 'true'

                # Base de la requête
                queryset = TblSalon.objects.all()

                # Appliquer le filtre par coiffeuse si demandé
                if coiffeuse_id:
                    # Récupérer les salons liés à cette coiffeuse
                    salon_ids = TblCoiffeuseSalon.objects.filter(
                        coiffeuse__idTblUser__idTblUser=coiffeuse_id
                    )

                    # Si on veut uniquement les salons dont la coiffeuse est propriétaire
                    if est_proprietaire:
                        salon_ids = salon_ids.filter(est_proprietaire=True)

                    # Récupérer les IDs des salons
                    salon_ids = salon_ids.values_list('salon_id', flat=True)

                    # Filtrer les salons par ces IDs
                    queryset = queryset.filter(idTblSalon__in=salon_ids)

                # Appliquer la pagination
                paginated_queryset = queryset[offset:offset + limit]

                # Sérialiser les données
                serializer = SalonDetailSerializer(
                    paginated_queryset,
                    many=True,
                    context={'request': request}
                )

                # Infos de pagination
                total_count = queryset.count()

                return Response({
                    'count': total_count,
                    'next': offset + limit < total_count,
                    'previous': offset > 0,
                    'results': serializer.data
                })

        except TblSalon.DoesNotExist:
            logger.warning(f"Salon avec ID {salon_id} non trouvé")
            return Response(
                {"detail": "Salon non trouvé"},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            # Gérer les erreurs de conversion des paramètres limit/offset
            logger.warning(f"Erreur de paramètre: {str(e)}")
            return Response(
                {"detail": "Paramètres de pagination invalides"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des détails du salon: {str(e)}", exc_info=True)
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )






# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from .serializers import SalonDetailSerializer
# from ..models import TblSalon
# import logging
#
# # Configurer le logger
# logger = logging.getLogger(__name__)
#
#
# class PublicSalonDetailsView(APIView):
#     """
#     Vue API pour obtenir les détails publics d'un salon
#     """
#
#     def get(self, request, salon_id=None):
#         try:
#             # Si salon_id est fourni, récupérer ce salon spécifique
#             if salon_id:
#                 salon = TblSalon.objects.get(idTblSalon=salon_id)
#                 serializer = SalonDetailSerializer(salon, context={'request': request})
#                 return Response(serializer.data)
#             # Sinon, récupérer tous les salons
#             else:
#                 # Par défaut, limiter le nombre de salons retournés pour éviter un trop grand jeu de données
#                 limit = int(request.query_params.get('limit', 10))
#                 offset = int(request.query_params.get('offset', 0))
#
#                 salons = TblSalon.objects.all()[offset:offset + limit]
#                 serializer = SalonDetailSerializer(salons, many=True, context={'request': request})
#
#                 # Pour pagination : inclure le nombre total
#                 total_count = TblSalon.objects.count()
#
#                 return Response({
#                     'count': total_count,
#                     'next': offset + limit < total_count,
#                     'previous': offset > 0,
#                     'results': serializer.data
#                 })
#
#         except TblSalon.DoesNotExist:
#             logger.warning(f"Salon avec ID {salon_id} non trouvé")
#             return Response(
#                 {"detail": "Salon non trouvé"},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#         except ValueError as e:
#             # Gérer les erreurs de conversion des paramètres limit/offset
#             logger.warning(f"Erreur de paramètre: {str(e)}")
#             return Response(
#                 {"detail": "Paramètres de pagination invalides"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         except Exception as e:
#             logger.error(f"Erreur lors de la récupération des détails du salon: {str(e)}", exc_info=True)
#             return Response(
#                 {"detail": str(e)},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
#











# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from .serializers import SalonDetailSerializer
# from ..models import TblSalon
#
#
# class PublicSalonDetailsView(APIView):
#     """
#     Vue API pour obtenir les détails publics d'un salon
#     """
#
#     def get(self, request, salon_id=None):
#         try:
#             # Si salon_id est fourni, récupérer ce salon spécifique
#             if salon_id:
#                 salon = TblSalon.objects.get(idTblSalon=salon_id)
#                 serializer = SalonDetailSerializer(salon)
#                 return Response(serializer.data)
#
#             # Sinon, récupérer tous les salons
#             else:
#                 salons = TblSalon.objects.all()
#                 serializer = SalonDetailSerializer(salons, many=True)
#                 return Response(serializer.data)
#
#         except TblSalon.DoesNotExist:
#             return Response(
#                 {"detail": "Salon non trouvé"},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#         except Exception as e:
#             return Response(
#                 {"detail": str(e)},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
