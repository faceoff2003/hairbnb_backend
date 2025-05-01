from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from decorators.decorators import firebase_authenticated
from hairbnb.models import TblUser, TblClient, TblRendezVous, TblCoiffeuse
from hairbnb.order.order_serializes import CommandeSerializer, UpdateRendezVousSerializer, CommandeCoiffeuseSerializer


@firebase_authenticated
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


@firebase_authenticated
@api_view(['GET'])
def commandes_coiffeuse(request, idUser):
    """
    Récupère toutes les commandes (rendez-vous) reçues par une coiffeuse,
    par défaut filtrées sur statut 'en attente'
    """
    try:
        # Récupérer l'utilisateur et la coiffeuse associée
        user = TblUser.objects.get(idTblUser=idUser)
        coiffeuse = TblCoiffeuse.objects.get(idTblUser=user)

        # Récupérer le filtre de statut (par défaut 'en attente')
        statut = request.query_params.get('statut', 'en attente')

        # Filtrer les rendez-vous par statut
        commandes = TblRendezVous.objects.filter(
            coiffeuse=coiffeuse,
            statut=statut
        ).select_related(
            'client', 'client__idTblUser', 'salon'
        ).prefetch_related(
            'rendez_vous_services', 'rendez_vous_services__service',
            'tblpaiement_set'
        ).order_by('date_heure')  # Tri par date/heure

        # Serializer les données
        serializer = CommandeCoiffeuseSerializer(commandes, many=True)
        return Response(serializer.data)

    except TblUser.DoesNotExist:
        return Response({"detail": "Utilisateur non trouvé."}, status=status.HTTP_404_NOT_FOUND)
    except TblCoiffeuse.DoesNotExist:
        return Response({"detail": "Coiffeuse non trouvée pour cet utilisateur."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("ERREUR :", e)
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@firebase_authenticated
@api_view(['PATCH'])
def update_statut_commande(request, idRendezVous):
    """
    Permet à une coiffeuse de modifier le statut d'une commande
    """
    try:
        # Récupérer le rendez-vous
        rendez_vous = TblRendezVous.objects.get(idRendezVous=idRendezVous)

        # Vérifier que l'utilisateur connecté est bien la coiffeuse de ce rendez-vous
        user = request.user
        coiffeuse = TblCoiffeuse.objects.get(idTblUser=user)

        if rendez_vous.coiffeuse.idTblUser.idTblUser != user.idTblUser:
            return Response({"detail": "Vous n'êtes pas autorisé à modifier ce rendez-vous."},
                            status=status.HTTP_403_FORBIDDEN)

        # Mise à jour du statut uniquement
        serializer = UpdateRendezVousSerializer(rendez_vous, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(CommandeCoiffeuseSerializer(rendez_vous).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except TblRendezVous.DoesNotExist:
        return Response({"detail": "Rendez-vous non trouvé."}, status=status.HTTP_404_NOT_FOUND)
    except TblCoiffeuse.DoesNotExist:
        return Response({"detail": "Coiffeuse non trouvée pour cet utilisateur."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@firebase_authenticated
@api_view(['PATCH'])
def update_date_heure_commande(request, idRendezVous):
    """
    Permet à une coiffeuse de modifier la date et l'heure d'une commande
    """
    try:
        # Récupérer le rendez-vous
        rendez_vous = TblRendezVous.objects.get(idRendezVous=idRendezVous)

        # Vérifier que l'utilisateur connecté est bien la coiffeuse de ce rendez-vous
        user = request.user
        coiffeuse = TblCoiffeuse.objects.get(idTblUser=user)

        if rendez_vous.coiffeuse.idTblUser.idTblUser != user.idTblUser:
            return Response({"detail": "Vous n'êtes pas autorisé à modifier ce rendez-vous."},
                            status=status.HTTP_403_FORBIDDEN)

        # Vérifier que le rendez-vous n'est pas déjà annulé ou terminé
        if rendez_vous.statut in ['annulé', 'terminé']:
            return Response(
                {"detail": f"Impossible de modifier un rendez-vous avec le statut '{rendez_vous.statut}'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Mise à jour de la date et l'heure uniquement
        serializer = UpdateRendezVousSerializer(rendez_vous, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(CommandeCoiffeuseSerializer(rendez_vous).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except TblRendezVous.DoesNotExist:
        return Response({"detail": "Rendez-vous non trouvé."}, status=status.HTTP_404_NOT_FOUND)
    except TblCoiffeuse.DoesNotExist:
        return Response({"detail": "Coiffeuse non trouvée pour cet utilisateur."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)