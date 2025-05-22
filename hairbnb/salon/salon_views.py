from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from hairbnb.models import TblCoiffeuse,TblCoiffeuseSalon
import logging
from hairbnb.salon.salon_serializers import TblSalonSerializer

# Configurer le logger
logger = logging.getLogger(__name__)


@csrf_exempt
def get_salon_by_coiffeuse(request, coiffeuse_id):
    """
    Récupère le salon d'une coiffeuse (salon où elle est propriétaire)
    """
    try:
        # Vérifier que la coiffeuse existe
        coiffeuse = TblCoiffeuse.objects.get(idTblUser_id=coiffeuse_id)

        # Récupérer le(s) salon(s) dont cette coiffeuse est propriétaire via la table de jonction
        relation = TblCoiffeuseSalon.objects.filter(
            coiffeuse=coiffeuse,
            est_proprietaire=True
        ).first()

        if not relation:
            return JsonResponse({
                'exists': False,
                'message': "Cette coiffeuse n'est propriétaire d'aucun salon"
            }, status=404)

        # Récupérer le salon depuis la relation
        salon = relation.salon

        # Utiliser le sérialiseur pour formater les données
        serializer = TblSalonSerializer(salon, context={'request': request})

        return JsonResponse({
            'exists': True,
            'salon': serializer.data
        })

    except TblCoiffeuse.DoesNotExist:
        logger.warning(f"Coiffeuse avec ID {coiffeuse_id} introuvable")
        return JsonResponse({
            'exists': False,
            'message': "Coiffeuse introuvable"
        }, status=404)

    except Exception as e:
        logger.error(f"Erreur lors de la récupération du salon pour la coiffeuse {coiffeuse_id}: {str(e)}",
                     exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

# # Configurer le logger
# logger = logging.getLogger(__name__)
#
# @csrf_exempt
# def get_salon_by_coiffeuse(request, coiffeuse_id):
#     """
#     Récupère le salon d'une coiffeuse (salon où elle est propriétaire)
#     """
#     try:
#         # Vérifier que la coiffeuse existe - cette partie reste la même
#         coiffeuse = TblCoiffeuse.objects.get(idTblUser_id=coiffeuse_id)
#
#         # CHANGEMENT : Ne plus utiliser TblSalon.objects.get(coiffeuse=coiffeuse)
#         # car le champ 'coiffeuse' n'existe plus dans TblSalon
#         # À la place, utiliser la table de jonction TblCoiffeuseSalon
#         relation = TblCoiffeuseSalon.objects.filter(
#             coiffeuse=coiffeuse,
#             est_proprietaire=True
#         ).first()
#
#         if not relation:
#             return JsonResponse({
#                 'exists': False,
#                 'message': "Cette coiffeuse n'est propriétaire d'aucun salon"
#             }, status=404)
#
#         # Récupérer le salon depuis la relation
#         salon = relation.salon
#
#         # Utiliser le sérialiseur pour formater les données
#         serializer = TblSalonSerializer(salon, context={'request': request})
#
#         return JsonResponse({
#             'exists': True,
#             'salon': serializer.data
#         })
#
#     except TblCoiffeuse.DoesNotExist:
#         logger.warning(f"Coiffeuse avec ID {coiffeuse_id} introuvable")
#         return JsonResponse({
#             'exists': False,
#             'message': "Coiffeuse introuvable"
#         }, status=404)
#
#     except Exception as e:
#         logger.error(f"Erreur lors de la récupération du salon pour la coiffeuse {coiffeuse_id}: {str(e)}",
#                      exc_info=True)
#         return JsonResponse({
#             'status': 'error',
#             'message': str(e)
#         }, status=500)















# @csrf_exempt
# def get_salon_by_coiffeuse(request, coiffeuse_id):
#     try:
#         coiffeuse = TblCoiffeuse.objects.get(idTblUser_id=coiffeuse_id)
#         salon = TblSalon.objects.get(coiffeuse=coiffeuse)
#
#         salon_data = {
#             "idTblSalon": salon.idTblSalon,
#             "coiffeuse": coiffeuse.idTblUser.idTblUser,
#             "nom_salon": salon.nom_salon,
#             "slogan": salon.slogan,
#             "logo_salon": salon.logo_salon.url if salon.logo_salon else None,
#         }
#
#         return JsonResponse({'exists': True, 'salon': salon_data})
#
#     except TblCoiffeuse.DoesNotExist:
#         return JsonResponse({'exists': False, 'message': "Coiffeuse introuvable"}, status=404)
#
#     except TblSalon.DoesNotExist:
#         return JsonResponse({'exists': False, 'message': "Salon introuvable"}, status=404)
#
#     except Exception as e:
#         return JsonResponse({'status': 'error', 'message': str(e)}, status=500)