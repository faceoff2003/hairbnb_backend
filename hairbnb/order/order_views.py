from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from decorators.decorators import firebase_authenticated, is_owner
from hairbnb.models import TblUser, TblClient, TblRendezVous
from hairbnb.order.order_serializes import CommandeSerializer

#@firebase_authenticated
@api_view(['GET'])
def mes_commandes(request, idUser):
    """
    Récupère toutes les commandes (rendez-vous payés) d'un utilisateur
    """
    try:
        # Récupérer l'utilisateur et son client associé
        user = TblUser.objects.get(idTblUser=idUser)
        client = TblClient.objects.get(idTblUser=user)

        # Récupérer tous les rendez-vous payés de l'utilisateur
        commandes = TblRendezVous.objects.filter(
            client=client,
            # Utiliser la relation inverse depuis TblPaiement
            tblpaiement__isnull=False,
            tblpaiement__statut__code="payé"  # ou "Payé" selon votre configuration
        ).select_related(
            'salon', 'coiffeuse', 'coiffeuse__idTblUser'
        ).prefetch_related(
            'rendez_vous_services', 'rendez_vous_services__service',
            'tblpaiement_set'  # Utilisez le nom correct de la relation inverse
        ).order_by('-tblpaiement__date_paiement')  # Les plus récents d'abord

        # Serializer les données
        serializer = CommandeSerializer(commandes, many=True)
        return Response(serializer.data)
    except TblUser.DoesNotExist:
        return Response({"detail": "Utilisateur non trouvé."}, status=status.HTTP_404_NOT_FOUND)
    except TblClient.DoesNotExist:
        return Response({"detail": "Client non trouvé pour cet utilisateur."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("ERREUR :", e)
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#
# @api_view(['GET'])
# #@firebase_authenticated
# #@is_owner(param_name="idUser")
# def mes_commandes(request, idUser):
#     """
#     Récupère toutes les commandes (rendez-vous payés) d'un utilisateur
#     """
#     try:
#         # Récupérer l'utilisateur et son client associé
#         user = TblUser.objects.get(idTblUser=idUser)
#         client = TblClient.objects.get(idTblUser=user)
#
#         # Récupérer tous les rendez-vous payés de l'utilisateur
#         commandes = TblRendezVous.objects.filter(
#             client=client,
#             # S'assurer qu'il y a un paiement et que son statut est "payé"
#             paiement__isnull=False,
#             paiement__statut__code="Payé"  # Utilisez le code correspondant à "payé" dans TblPaiementStatut
#         ).select_related(
#             'salon', 'coiffeuse', 'coiffeuse__idTblUser', 'salon', 'paiement', 'paiement__methode', 'paiement__statut'
#         ).prefetch_related(
#             'rendez_vous_services', 'rendez_vous_services__service'
#         ).order_by('-paiement__date_paiement')  # Les plus récents d'abord
#
#         # Serializer les données
#         serializer = CommandeSerializer(commandes, many=True)
#         #-----------------------------------
#         print(serializer.data)
#         #-----------------------------------
#
#         return Response(serializer.data)
#
#     except TblUser.DoesNotExist:
#         return Response({"detail": "Utilisateur non trouvé."}, status=status.HTTP_404_NOT_FOUND)
#     except TblClient.DoesNotExist:
#         return Response({"detail": "Client non trouvé pour cet utilisateur."}, status=status.HTTP_404_NOT_FOUND)
#     except Exception as e:
#         #-------------------------------------
#         import traceback
#         traceback.print_exc()
#         print("ERREUR :", e)
#         #--------------------------------------
#         return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)